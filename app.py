"""PathWise | Streamlit dashboard connected to the existing rule-based AI engine."""
from __future__ import annotations
import json
from pathlib import Path

import streamlit as st
import pandas as pd

from pathwise import load_knowledge_base, recommend
from pathwise.engine import tokens
from pathwise.evaluation import evaluate_profiles
from pathwise.advanced import plan_roadmap, simulate_change, answer_question
from pathwise import profiles as profile_store
import html

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="PathWise 2.1 | Your Learning Future", page_icon=":mortar_board:", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family: 'DM Sans',sans-serif;}
[data-testid="stApp"] {background: radial-gradient(circle at 85% 4%,#1a2755 0%,#0a1125 37%,#080e1e 100%); color:#eaf2ff;}
[data-testid="stSidebar"] {background:#101a31;border-right:1px solid #263a60;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif !important;letter-spacing:-.025em;}
h1 {font-size:3.2rem !important;}
[data-testid="stMetric"] {background:linear-gradient(135deg,#172746,#121d35);border:1px solid #2c4168;border-radius:18px;padding:17px;}
div.stButton>button[kind="primary"] {background:linear-gradient(100deg,#15b8aa,#4e8bff);border:0;color:white;border-radius:12px;font-weight:700;}
div.stDownloadButton>button {border-radius:12px;}
.pw-hero {background:linear-gradient(115deg,#1a2850 0%,#122d45 65%,#133d4b 100%);border:1px solid #3b577b;padding:32px 36px;border-radius:24px;margin-bottom:22px;}
.pw-eyebrow {color:#68e8da;font-size:.83rem;font-weight:700;letter-spacing:.16em;}
.pw-title {font:700 3rem 'Space Grotesk',sans-serif;color:#f5fbff;margin:8px 0 10px;}
.pw-sub {color:#c3d3e8;font-size:1.08rem;}
.pw-card {border:1px solid #304667;border-radius:18px;background:#15213b;padding:20px 23px;margin:10px 0;}
.pw-rank {color:#72e8dc;font-size:.79rem;font-weight:700;letter-spacing:.11em;}
.pw-name {color:#f5f9ff;font:700 1.28rem 'Space Grotesk',sans-serif;margin:6px 0;}
.pw-muted {color:#afc3dd;font-size:.94rem;}
.pw-chip {display:inline-block;border-radius:50px;background:#173e48;color:#79e8d9;padding:5px 11px;font-size:.8rem;margin:4px 5px 4px 0;}
</style>
""", unsafe_allow_html=True)


st.markdown("""<style>
/* PathWise 2.0: animated aurora + glass surfaces */
[data-testid="stApp"] {background: radial-gradient(ellipse at 8% 6%,#24316d 0%,transparent 37%),radial-gradient(ellipse at 90% 13%,#113b56 0%,transparent 40%),#070b1c;}
[data-testid="stSidebar"] {background:rgba(12,19,44,.94);backdrop-filter:blur(20px);}
.pw-hero {position:relative;overflow:hidden;background:linear-gradient(120deg,rgba(36,39,94,.85),rgba(12,57,74,.76));box-shadow:0 12px 55px #050b1e77;animation:rise .65s ease-out;}
.pw-hero:after {content:'';position:absolute;width:220px;height:220px;right:-50px;top:-100px;background:#36f6e844;filter:blur(45px);border-radius:50%;animation:orbit 9s ease-in-out infinite alternate;pointer-events:none;}
.pw-card,[data-testid="stMetric"],[data-testid="stVerticalBlockBorderWrapper"] {backdrop-filter:blur(14px);box-shadow:0 10px 28px #02081744;transition:transform .2s,border-color .2s;}
.pw-card:hover {transform:translateY(-3px);border-color:#57e4db;}
.pw-chip {border:1px solid #46c3bc66;}
[data-testid="stTabs"] button {font-weight:650;}
[data-testid="stMetricValue"] {color:#80f3e6;}
@keyframes rise {from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes orbit {from{transform:translate(-45px,10px)}to{transform:translate(20px,65px)}}
@media(max-width:760px){.pw-hero{padding:24px 18px}.pw-title{font-size:2.1rem!important}h1{font-size:2.2rem!important}}
</style>""",unsafe_allow_html=True)

# Auth is optional for local demos. Cloud saving is only offered when configured.
if profile_store.configured():
    with st.sidebar:
        st.markdown("### My PathWise account")
        if 'pw_auth' not in st.session_state:
            with st.form('pw_auth_form'):
                auth_mode=st.radio('Account', ['Sign in','Create account'],horizontal=True)
                email=st.text_input('Email')
                password=st.text_input('Password',type='password')
                auth_submit=st.form_submit_button('Continue',use_container_width=True)
            if auth_submit:
                try:
                    if not email.strip() or len(password)<6:
                        st.error('Enter an email and a password of at least 6 characters.')
                    else:
                        response=profile_store.authenticate(email.strip(),password,auth_mode=='Create account')
                        if 'pw_auth' in st.session_state:
                            st.session_state.pop('pw_editor_loaded',None)
                            st.rerun()
                        else:
                            st.info('Account created. Check your email for a confirmation link, then sign in.')
                except Exception as exc:
                    st.error('Account request failed. Check your credentials or Supabase configuration.')
        else:
            st.success('Signed in: '+st.session_state['pw_auth']['email'])
            if st.button('Sign out',use_container_width=True):
                profile_store.logout()
                st.session_state.pop('pw_editor_loaded',None)
                st.rerun()
else:
    with st.sidebar:
        st.info('💾 Cloud profile saving is not configured yet. You can still create a profile and download a backup.')

if 'pw_auth' in st.session_state and 'pw_saved_profile' not in st.session_state:
    try:
        st.session_state['pw_saved_profile']=profile_store.load_profile()
    except Exception:
        st.session_state['pw_saved_profile']=None
        st.sidebar.warning('Could not load your saved profile. Check database settings.')

@st.cache_data(show_spinner=False)
def knowledge():
    return load_knowledge_base()

courses, careers = knowledge()
interest_options = sorted({v for c in courses for v in tokens(c["topics"])})
prereq_options = sorted({v for c in courses for v in tokens(c["prerequisites"])})
skill_options = sorted({v for c in courses for v in tokens(c["foundation_skills"] + ";" + c["target_skills"])}
                       | {v for c in careers.values() for v in c["required_skills"]})

st.markdown("""<div class="pw-hero"><div class="pw-eyebrow">✦ INTELLIGENT ACADEMIC NAVIGATION</div>
<div class="pw-title">PathWise <span style="color:#66e9dc">↗</span></div>
<div class="pw-sub">Explore electives that fit your goals. Understand eligibility. See what to learn next.</div></div>""", unsafe_allow_html=True)

# Require sign-in when cloud accounts are enabled. Offline mode uses explicit backup files.
if profile_store.configured() and 'pw_auth' not in st.session_state:
    st.markdown('### Welcome to your personal PathWise workspace')
    st.info('Create an account or sign in using the account panel in the sidebar to continue.')
    st.stop()

# Load an existing cloud profile into the editor once, without replacing live edits.
# Apply restored backups before profile widgets are created.
if 'pw_pending_restore' in st.session_state:
    incoming=st.session_state.pop('pw_pending_restore')
    st.session_state['name_personal']=incoming['name']
    st.session_state['career_personal']=incoming['career_goal']
    st.session_state['interests_personal']=[v for v in incoming['interests'] if v in interest_options]
    st.session_state['prereq_personal']=[v for v in incoming['completed_prerequisites'] if v in prereq_options]
    st.session_state['skills_personal']=[v for v in incoming['skills'] if v in skill_options]
    st.session_state['readiness_personal']=int(float(incoming['readiness'])*100)
    st.session_state['pw_editor_loaded']=True

if 'pw_editor_loaded' not in st.session_state:
    saved=st.session_state.get('pw_saved_profile') or {}
    st.session_state['name_personal']=saved.get('name','')
    st.session_state['career_personal']=saved.get('career_goal',next(iter(careers)))
    st.session_state['interests_personal']=[v for v in saved.get('interests',[]) if v in interest_options]
    st.session_state['prereq_personal']=[v for v in saved.get('completed_prerequisites',[]) if v in prereq_options]
    st.session_state['skills_personal']=[v for v in saved.get('skills',[]) if v in skill_options]
    st.session_state['readiness_personal']=int(round(saved.get('readiness',.5)*100))
    st.session_state['pw_editor_loaded']=True

with st.sidebar:
    st.markdown('### 🧭 My student profile')
    st.caption('Build your own academic pathway. No demo student profiles.')
    key_suffix='personal'
    default=None
    selected='CUSTOM'
    name=st.text_input('Your name',value=default.get('name','') if default else '',placeholder='Enter your name',key='name_'+key_suffix)
    career_keys=list(careers)
    career_default=default.get('career_goal') if default else None
    career=st.selectbox('Career goal',career_keys,index=career_keys.index(career_default) if career_default in career_keys else 0,
        format_func=lambda c:careers[c]['label'],key='career_'+key_suffix)
    interests=st.multiselect('Your interests',interest_options,default=[x for x in default.get('interests',[]) if x in interest_options] if default else [],key='interests_'+key_suffix)
    completed=st.multiselect('Completed prerequisite tags',prereq_options,default=[x for x in default.get('completed_prerequisites',[]) if x in prereq_options] if default else [],key='prereq_'+key_suffix,help='Illustrative tags, not verified university credits.')
    skills=st.multiselect('Current skills',skill_options,default=[x for x in default.get('skills',[]) if x in skill_options] if default else [],key='skills_'+key_suffix)
    readiness=st.slider('Self-assessed readiness',0,100,value=int(round(default.get('readiness',.5)*100)) if default else 50,key='readiness_'+key_suffix)
    top_n=st.slider('Number of recommendations',1,10,5)
    run=st.button('✨ Generate my pathway',type='primary',use_container_width=True)
    st.divider()
    st.markdown('#### 💾 Save your progress')
    if 'pw_auth' in st.session_state:
        if st.button('Save profile to my account',use_container_width=True):
            try:
                if not name.strip():
                    st.warning('Enter your name before saving.')
                else:
                    payload={'name':name.strip(),'career_goal':career,'interests':interests,
                        'completed_prerequisites':completed,'skills':skills,'readiness':readiness/100}
                    profile_store.save_profile(payload)
                    st.session_state['pw_saved_profile']=payload
                    st.success('Profile saved securely to your account.')
            except Exception:
                st.error('Save failed. Please try again; your current inputs are still on this page.')
    else:
        st.caption('Sign in to save across devices. Without cloud setup, download a backup instead.')
    export_profile={'name':name.strip(),'career_goal':career,'interests':interests,
        'completed_prerequisites':completed,'skills':skills,'readiness':readiness/100}
    st.download_button('⬇ Download my profile (JSON)',json.dumps(export_profile,indent=2),
        file_name='my_pathwise_profile.json',mime='application/json',use_container_width=True)
    upload=st.file_uploader('Restore a profile backup',type=['json'],key='pw_upload')
    if upload and st.button('Load backup into editor'):
        try:
            incoming=json.load(upload)
            if not isinstance(incoming,dict) or any(k not in incoming for k in ('name','career_goal','interests','skills','completed_prerequisites','readiness')):
                raise ValueError('Invalid profile')
            if incoming['career_goal'] not in careers or not 0<=float(incoming['readiness'])<=1:
                raise ValueError('Invalid career or readiness')
            if any(not isinstance(incoming[k],list) for k in ('interests','skills','completed_prerequisites')):
                raise ValueError('Invalid profile lists')
            st.session_state['pw_saved_profile']=incoming
            st.session_state['pw_pending_restore']=incoming
            st.rerun()
        except (ValueError,TypeError,KeyError,json.JSONDecodeError):
            st.error('Could not load backup. Please select a valid PathWise profile JSON.')
    st.caption('The course catalogue is illustrative. Do not enter confidential academic records.')

student={'student_id':'CUSTOM','name':name.strip() or 'Student',
    'career_goal':career,'interests':interests,'completed_prerequisites':completed,
    'skills':skills,'readiness':readiness/100}

if not name.strip() or not interests:
    st.markdown('### ✨ Create your personal academic profile')
    st.info('Enter your name and select at least one interest in the sidebar to unlock your personalized dashboard.')
    st.stop()

# Always reflect the current form; the button is an explicit affordance, not a requirement.
try:
    result = recommend(student, courses, careers, top_n=top_n)
except (ValueError, KeyError) as exc:
    st.error(f"Please correct the profile: {exc}")
    st.stop()
if run:
    st.toast("Your personalized pathway is ready!", icon=":material/check_circle:")

rec = result["ranked_recommendations"]
blocked = result["ineligible_courses"]
all_skills = set(tokens(careers[career]["required_skills"]))
known = all_skills.intersection(set(skills))
missing = result["career_skill_gaps"]
st.markdown("#### Your academic snapshot")
st.caption("👤 " + html.escape(student["name"]) + " · Personalized academic intelligence")
m1,m2,m3,m4=st.columns(4)
m1.metric("Eligible electives",result["eligible_count"])
m2.metric("Courses needing prerequisites",len(blocked))
m3.metric("Top suitability",f'{rec[0]["score"]*100:.1f}%' if rec else "—")
m4.metric("Career skills covered",f"{len(known)}/{len(all_skills)}")

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9=st.tabs(["✨ Recommendations","🔐 Eligibility","📊 Skill gaps","⚖️ Compare","🧪 Evaluation","🗺️ Roadmap","🔮 What-if Lab","💬 AI Assistant","🧠 How the AI works"])

with tab1:
    st.markdown("### Recommended electives")
    st.caption("Only eligible courses are ranked. A score is a weighted suitability measure—not a success probability.")
    if not rec:
        st.warning("No courses meet the selected prerequisite tags. Check the Eligibility tab to see what's missing.")
    for i,c in enumerate(rec,1):
        left,right=st.columns([5,1])
        with left:
            st.markdown(f'<div class="pw-card"><div class="pw-rank">RECOMMENDATION {i:02d} · {c["course_id"]}</div>'
                        f'<div class="pw-name">{c["title"]}</div>'
                        f'<div class="pw-muted">{c["explanation"]}</div></div>',unsafe_allow_html=True)
        with right:
            st.metric("Suitability",f'{c["score"]*100:.1f}%')
            st.progress(float(c["score"]))
        with st.expander(f'Why {c["title"]}? · Score breakdown'):
            breakdown=pd.DataFrame([{"Factor":k.title(),"Match":round(c["factors"][k]*100,1),
                                     "Weight":round(result["weights"][k]*100,0),
                                     "Contribution":round(c["weighted_contributions"][k]*100,2)}
                                    for k in result["weights"]])
            st.dataframe(breakdown,hide_index=True,use_container_width=True)
            st.bar_chart(breakdown.set_index("Factor")["Contribution"],horizontal=True)
            st.write("Skills you could develop in this course:",", ".join(c["course_skill_gaps"]) or "No listed gaps")
    st.download_button("⬇ Download complete recommendation report (JSON)",
                       data=json.dumps(result,indent=2),file_name="pathwise_report.json",
                       mime="application/json",use_container_width=True)

with tab2:
    st.markdown("### Prerequisite eligibility")
    st.success(f"{result['eligible_count']} electives meet the sample catalogue's prerequisite rules.")
    if blocked:
        rows=[{"Course":c["title"],"Course ID":c["course_id"],
               "Missing prerequisite tags":", ".join(c["missing_prerequisites"])} for c in blocked]
        st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
        st.info("An ineligible course is excluded from recommendations even if its interests and career match strongly.")
    else:
        st.success("No blocked courses for this profile.")
    with st.expander("See prerequisite rules for all courses"):
        st.dataframe(pd.DataFrame([{"Course":c["title"],"Required tags":c["prerequisites"] or "None"}
                                  for c in courses]),hide_index=True,use_container_width=True)

with tab3:
    st.markdown(f'### Career skill map · {careers[career]["label"]}')
    if all_skills:
        ratio=len(known)/len(all_skills)
        st.progress(ratio,text=f"{len(known)} of {len(all_skills)} required skills already listed")
    left,right=st.columns(2)
    with left:
        st.markdown("#### ✓ Skills already held")
        if known:
            for skill in sorted(known): st.markdown(f'<span class="pw-chip">✓ {skill.replace("_"," ").title()}</span>',unsafe_allow_html=True)
        else: st.caption("No required career skills matched yet.")
    with right:
        st.markdown("#### ↗ Skills to develop")
        if missing:
            for skill in missing: st.markdown(f'<span class="pw-chip" style="background:#402b49;color:#ffc0d7">+ {skill.replace("_"," ").title()}</span>',unsafe_allow_html=True)
        else: st.success("All listed career skills are covered.")
    st.markdown("#### Skills overview")
    chart=pd.DataFrame({"Status":["Already held","To develop"],"Count":[len(known),len(missing)]}).set_index("Status")
    st.bar_chart(chart,horizontal=True)
    st.caption("These are catalogue-based skill differences, not verified assessments of student ability.")

with tab4:
    st.markdown("### Compare eligible electives")
    st.caption("Compare the same profile across courses; scores are heuristic suitability, not probabilities.")
    if rec:
        names = {r['course_id']: f"{r['course_id']} · {r['title']}" for r in rec}
        choices = st.multiselect("Choose up to 4 eligible courses", list(names),
                                 default=list(names)[:min(3, len(names))], format_func=lambda k:names[k], max_selections=4)
        selected_recs = [r for r in rec if r['course_id'] in choices]
        if selected_recs:
            comparison = pd.DataFrame([{'Course':r['title'], 'Suitability (%)':round(100*r['score'],1),
                                        'Interest':round(100*r['factors']['interest'],1),
                                        'Career':round(100*r['factors']['career'],1),
                                        'Readiness':round(100*r['factors']['readiness'],1),
                                        'Skill':round(100*r['factors']['skill'],1),
                                        'Skill gaps':', '.join(r['course_skill_gaps']) or 'None'}
                                       for r in selected_recs])
            st.bar_chart(comparison.set_index('Course')['Suitability (%)'], horizontal=True)
            st.dataframe(comparison, hide_index=True, use_container_width=True)
            st.download_button('⬇ Download comparison (CSV)', comparison.to_csv(index=False).encode('utf-8'),
                               file_name='pathwise_course_comparison.csv', mime='text/csv')
        else:
            st.info('Select at least one course to compare.')
    else:
        st.info('No eligible courses to compare.')

with tab5:
    st.markdown("### Synthetic-profile evaluation")
    st.caption("This measures rule compliance, sorting and reproducibility—not real-world recommendation accuracy.")
    evaluation = evaluate_profiles([student], courses, careers)
    a,b,c = st.columns(3)
    a.metric('Profiles evaluated', evaluation['profiles_evaluated'])
    b.metric('Eligibility decisions', evaluation['total_eligible_decisions'] + evaluation['total_blocked_decisions'])
    c.metric('Checks', 'Passed' if all(evaluation[k] for k in ('prerequisite_rules_pass','ranking_order_pass','determinism_pass')) else 'Review needed')
    st.dataframe(pd.DataFrame(evaluation['profile_results']), hide_index=True, use_container_width=True)
    st.download_button('⬇ Download evaluation evidence (JSON)', json.dumps(evaluation, indent=2),
                       file_name='pathwise_evaluation.json', mime='application/json')
    st.warning('The synthetic dataset has no expert-labelled ideal recommendations, so precision, recall and relevance accuracy cannot be calculated meaningfully.')


with tab6:
    st.markdown("### 🗺️ Personalized academic roadmap")
    st.caption("Choose a destination course. The planner identifies a hypothetical sequence of courses that teach missing prerequisite tags, where possible.")
    target = st.selectbox("Target elective", [c['course_id'] for c in courses],
                          format_func=lambda cid: next(c['title'] + ' · ' + cid for c in courses if c['course_id']==cid),
                          key='roadmap_target')
    roadmap = plan_roadmap(student,courses,careers,target)
    for i,step in enumerate(roadmap['steps'],1):
        with st.container(border=True):
            a,b=st.columns([4,1])
            a.markdown(f"**{i:02d} · {step['title']}**  · `{step['course_id']}`")
            b.markdown({'eligible now':'🟢 Eligible now',
                        'ready after earlier steps':'🔵 After earlier steps',
                        'requires external prerequisites':'🟠 Check first'}[step['status']])
            st.caption('Teaches: '+(', '.join(step['skills_from_course']) or 'no mapped target skills'))
            if step['missing_before_step']:
                st.warning('Prerequisite tags still needed before this step: '+', '.join(step['missing_before_step']))
    if roadmap['external_prerequisites']:
        st.error('Not resolved within this sample course catalogue: '+', '.join(roadmap['external_prerequisites']))
    else:
        st.success('All prerequisite tags are mapped or already present for this hypothetical sequence. Later courses are not necessarily eligible now.')
    st.caption(roadmap['disclaimer'])
    st.download_button('⬇ Export roadmap (JSON)',json.dumps(roadmap,indent=2),file_name='pathwise_roadmap.json',mime='application/json')

with tab7:
    st.markdown('### 🔮 What-if recommendation simulator')
    st.caption('Your original sidebar profile is the baseline. Change the hypothetical inputs below without modifying the baseline.')
    what_interests=st.multiselect('Hypothetical interests',interest_options,default=interests,key='what_interests_'+key_suffix)
    what_prereqs=st.multiselect('Hypothetical completed prerequisite tags',prereq_options,default=completed,key='what_prereqs_'+key_suffix)
    what_skills=st.multiselect('Hypothetical skills',skill_options,default=skills,key='what_skills_'+key_suffix)
    what_readiness=st.slider('Hypothetical academic readiness',0,100,readiness,key='what_readiness_'+key_suffix)
    what_career=st.selectbox('Hypothetical career goal',career_keys,index=career_keys.index(career),
                             format_func=lambda k:careers[k]['label'],key='what_career_'+key_suffix)
    simulation=simulate_change(student,courses,careers,interests=what_interests,
        completed_prerequisites=what_prereqs,skills=what_skills,readiness=what_readiness/100,career_goal=what_career)
    before,after=simulation['before'],simulation['after']
    x,y=st.columns(2)
    x.metric('Baseline eligible courses',before['eligible_count'])
    y.metric('What-if eligible courses',after['eligible_count'],delta=after['eligible_count']-before['eligible_count'])
    rows=pd.DataFrame(simulation['comparison'])
    if not rows.empty:
        st.dataframe(rows.rename(columns={'title':'Course','before_score':'Before','after_score':'After',
            'score_change':'Change','status':'Eligibility'}).drop(columns=['course_id']),
            hide_index=True,use_container_width=True)
        st.bar_chart(rows[rows['score_change'].notna()].set_index('title')['score_change'],horizontal=True)
    st.caption(simulation['disclaimer'])
    st.download_button('⬇ Export simulation (JSON)',json.dumps(simulation,indent=2),
                       file_name='pathwise_what_if.json',mime='application/json')

with tab8:
    st.markdown('### 💬 Grounded academic assistant')
    st.caption('Offline, rule-based Q&A using only the local PathWise catalogue and your current profile. No LLM or external API.')
    prompts=['What are my top recommendations?','Why is CS309 blocked?',
             'What skills am I missing for my career?','How are scores calculated?']
    example=st.selectbox('Example question',prompts,index=0,key='assistant_example')
    question=st.text_input('Ask PathWise',value=example,key='assistant_question')
    if st.button('Ask assistant',type='primary',key='assistant_submit'):
        st.session_state['assistant_last_question']=question
    active_question=st.session_state.get('assistant_last_question',example)
    st.markdown('**Assistant response**')
    st.info(answer_question(active_question,student,courses,careers))
    st.caption('This is a constrained retrieval/rule-based assistant; it does not generate novel academic advice.')

with tab9:
    st.markdown("### Transparent hybrid decision process")
    st.markdown("**1. Symbolic prerequisite rules** → **2. Weighted content matching** → **3. Ranking and explanations**")
    st.latex(r"S(s,c)=0.40I+0.30C+0.20R+0.10K")
    st.dataframe(pd.DataFrame([
        {"Factor":"Interest (I)","Weight":"40%","Method":"Share of course topics present in student interests"},
        {"Factor":"Career (C)","Weight":"30%","Method":"1 if course maps to chosen career; otherwise 0"},
        {"Factor":"Readiness (R)","Weight":"20%","Method":"Self-rated readiness × (6 − difficulty)/5"},
        {"Factor":"Skill (K)","Weight":"10%","Method":"Share of foundation skills already held"},
    ]),hide_index=True,use_container_width=True)
    st.info("Weights are provisional. No machine-learning model has been trained, and the sample dataset is synthetic.")
    st.markdown("#### Current profile (for reproducibility)")
    st.json(student)
    st.markdown("#### Data limitations")
    st.caption("The catalogue, prerequisites and career mappings are illustrative and must be checked against your university curriculum before real-world use.")

st.divider()
st.caption("PathWise 2.0 · Hybrid knowledge-based + content-based recommendations · Synthetic academic catalogue · Account profiles stored only when cloud saving is configured")

