"""Step 5 deterministic, catalogue-grounded academic planning utilities.

No LLM, network calls, or claims about actual university eligibility.
"""
from __future__ import annotations
from .engine import tokens, recommend, validate_student, score_course


def plan_roadmap(student, courses, careers, target_course_id):
    """Build a hypothetical prerequisite pathway for one target course.

    Course target_skills may provisionally satisfy a same-named prerequisite tag.
    An unresolved tag is explicitly identified as requiring external study/verification.
    The planner never assumes a course was actually completed.
    """
    profile = validate_student(student, careers)
    by_id = {c['course_id']: c for c in courses}
    if target_course_id not in by_id:
        raise ValueError('Unknown target course ID')
    producers = {}
    for course in courses:
        for skill in tokens(course['target_skills']):
            producers.setdefault(skill, []).append(course)
    for tag in producers:
        producers[tag].sort(key=lambda c: (-score_course(c, profile)[0], c['course_id']))

    initial_available = set(profile['completed_prerequisites'])
    available = set(initial_available)
    steps, external, visiting, planned = [], set(), set(), set()

    def visit(cid):
        if cid in planned: return
        if cid in visiting:
            return
        visiting.add(cid)
        course = by_id[cid]
        for req in tokens(course['prerequisites']):
            if req in available: continue
            candidates = [c for c in producers.get(req, []) if c['course_id'] != cid and c['course_id'] not in visiting]
            if candidates:
                visit(candidates[0]['course_id'])
            if req not in available:
                external.add(req)
        missing = sorted(set(tokens(course['prerequisites'])) - available)
        produced = tokens(course['target_skills'])
        steps.append({'course_id':cid,'title':course['title'],
                      'missing_before_step':missing,'skills_from_course':produced,
                      'status':('requires external prerequisites' if missing else
                                'eligible now' if set(tokens(course['prerequisites'])).issubset(initial_available)
                                else 'ready after earlier steps')})
        # A course only unlocks downstream tags if its own prerequisites are resolved.
        if not missing:
            available.update(produced)
        planned.add(cid)
        visiting.remove(cid)

    visit(target_course_id)
    return {'target_course_id':target_course_id,'target_title':by_id[target_course_id]['title'],
            'steps':steps,'external_prerequisites':sorted(external),
            'target_ready_after_plan':set(tokens(by_id[target_course_id]['prerequisites'])).issubset(available),
            'disclaimer':'Hypothetical plan using synthetic course-to-skill mappings; not a timetable or official prerequisite equivalency.'}


def simulate_change(student, courses, careers, *, interests=None, completed_prerequisites=None,
                    skills=None, readiness=None, career_goal=None):
    """Compare original and hypothetical profiles using the same unchanged engine."""
    baseline = validate_student(student, careers)
    updated = dict(baseline)
    for key, val in {'interests':interests,'completed_prerequisites':completed_prerequisites,
                     'skills':skills,'readiness':readiness,'career_goal':career_goal}.items():
        if val is not None: updated[key] = val
    updated = validate_student(updated, careers)
    before = recommend(baseline,courses,careers,top_n=len(courses))
    after = recommend(updated,courses,careers,top_n=len(courses))
    old = {r['course_id']:r for r in before['ranked_recommendations']}
    new = {r['course_id']:r for r in after['ranked_recommendations']}
    names = {c['course_id']:c['title'] for c in courses}
    rows = []
    for cid in sorted(set(old)|set(new)):
        b,a=old.get(cid),new.get(cid)
        rows.append({'course_id':cid,'title':names[cid],
                     'before_score':b['score'] if b else None,
                     'after_score':a['score'] if a else None,
                     'score_change':round(a['score']-b['score'],4) if a and b else None,
                     'status':'newly eligible' if a and not b else 'newly blocked' if b and not a else 'eligible in both'})
    return {'before':before,'after':after,'comparison':rows,
            'disclaimer':'Counterfactual comparison of a deterministic heuristic, not a prediction of real academic outcomes.'}


def answer_question(question, student, courses, careers):
    """Constrained FAQ assistant; responses come only from catalogue + engine.

    Unknown questions are refused instead of producing unsupported advice.
    """
    import re
    profile=validate_student(student,careers)
    q=' '.join(question.lower().strip().split())
    if not q: return 'Ask a question about recommendations, eligibility, prerequisites, skills or scores.'
    result=recommend(profile,courses,careers,top_n=len(courses))
    by_id={c['course_id']:c for c in courses}
    # Course mentions are matched as whole course IDs or complete titles.
    matches=[c for c in courses if re.search(r'(?<![a-z0-9])'+re.escape(c['course_id'].lower())+r'(?![a-z0-9])',q)
             or re.search(r'(?<![a-z0-9])'+re.escape(c['title'].lower())+r'(?![a-z0-9])',q)]
    matches.sort(key=lambda c: -len(c['title']))
    course=matches[0] if matches else None
    if course:
        cid=course['course_id']
        blocked=next((r for r in result['ineligible_courses'] if r['course_id']==cid),None)
        ranked=next((r for r in result['ranked_recommendations'] if r['course_id']==cid),None)
        req=tokens(course['prerequisites'])
        status=('Not eligible under the sample rules; missing: '+', '.join(blocked['missing_prerequisites'])+'.') if blocked else 'Eligible under the sample rules.'
        if any(k in q for k in ('prereq','eligible','eligib','take','blocked','unlock','require')):
            return f"{course['title']} ({cid}): {status} Listed prerequisites: {', '.join(req) if req else 'none'}. Verify with your institution."
        if any(k in q for k in ('score','why','recommend','rank')):
            return (f"{course['title']} ({cid}): {ranked['explanation']}" if ranked else
                    f"{course['title']} ({cid}): {status} It is excluded from the eligible-course ranking.")
        return f"{course['title']} ({cid}). {status} Topics: {', '.join(tokens(course['topics']))}."
    if any(k in q for k in ('top','best','recommend','suggest','rank')):
        top=result['ranked_recommendations'][:3]
        if not top: return 'No eligible courses found for this profile. Check prerequisite tags in the Eligibility tab.'
        return 'Top eligible recommendations: '+ '; '.join(f"{r['title']} ({r['score']:.1%})" for r in top)+'. Scores are heuristic suitability, not probabilities.'
    if any(k in q for k in ('skill','learn','gap','career')):
        gaps=result['career_skill_gaps']
        return f"For {result['student']['career_label']}, the listed missing career skills are: {', '.join(gaps) if gaps else 'none'}. These are catalogue-based gaps."
    if any(k in q for k in ('score','weight','algorithm','how does','calculate')):
        return 'PathWise filters out missing prerequisites, then scores eligible courses: 40% interest match + 30% career match + 20% readiness + 10% foundation-skill match. Weights are provisional.'
    if any(k in q for k in ('prerequisite','eligibility','eligible','blocked')):
        return f"Under the sample catalogue, {result['eligible_count']} courses are eligible and {len(result['ineligible_courses'])} are blocked. Ask about a specific course for details."
    return ('I can only answer grounded questions about this sample catalogue: top recommendations, '
            'course eligibility/prerequisites, career skill gaps, or how scoring works. '
            'Try: Why is CS309 blocked?')
