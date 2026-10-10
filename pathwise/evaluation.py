"""Reproducible synthetic-profile evaluation, not a real-world accuracy study."""
from __future__ import annotations
from .engine import recommend, tokens


def evaluate_profiles(profiles, courses, careers):
    """Evaluate deterministic rule compliance, rank order and output consistency.

    No ground-truth preferred course labels exist, so precision/recall/accuracy
    for recommendation relevance are intentionally NOT reported.
    """
    records = []
    total_blocked = total_eligible = 0
    all_compliant = True
    all_ranked = True
    all_deterministic = True
    for student in profiles:
        result = recommend(student, courses, careers, top_n=len(courses))
        again = recommend(student, courses, careers, top_n=len(courses))
        completed = set(tokens(student['completed_prerequisites']))
        catalogue = {c['course_id']: c for c in courses}
        recommendations = result['ranked_recommendations']
        blocked = result['ineligible_courses']
        eligible_ok = all(set(tokens(catalogue[r['course_id']]['prerequisites'])) <= completed for r in recommendations)
        blocked_ok = all(set(r['missing_prerequisites']) == (set(tokens(catalogue[r['course_id']]['prerequisites'])) - completed) and bool(r['missing_prerequisites']) for r in blocked)
        coverage_ok = len(recommendations) + len(blocked) == len(courses)
        compliant = eligible_ok and blocked_ok and coverage_ok
        ordered = all(recommendations[i]['score'] >= recommendations[i+1]['score'] for i in range(len(recommendations)-1))
        deterministic = result == again
        total_blocked += len(blocked)
        total_eligible += len(recommendations)
        all_compliant &= compliant
        all_ranked &= ordered
        all_deterministic &= deterministic
        records.append({'student_id': student['student_id'], 'career': result['student']['career_label'],
                        'eligible': len(recommendations), 'blocked': len(blocked),
                        'top_course': recommendations[0]['title'] if recommendations else 'None',
                        'top_score': recommendations[0]['score'] if recommendations else None,
                        'prerequisite_rules_pass': compliant, 'ranking_order_pass': ordered,
                        'determinism_pass': deterministic})
    return {'profiles_evaluated': len(records), 'catalogue_courses': len(courses),
            'total_eligible_decisions': total_eligible, 'total_blocked_decisions': total_blocked,
            'prerequisite_rules_pass': bool(all_compliant), 'ranking_order_pass': bool(all_ranked),
            'determinism_pass': bool(all_deterministic), 'profile_results': records,
            'limitations': 'Synthetic profiles and catalogue. Checks internal consistency, not educational relevance or predictive accuracy.'}
