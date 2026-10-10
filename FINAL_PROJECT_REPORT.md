# PATHWISE | AI Academic Decision Assistant
## Final Mini-Capstone Project Report - Step 6

**Course:** AI Mini-Capstone (25CS301)  
**Release:** Step 6, October 2026  
**Status:** Working offline prototype using synthetic catalogue and fictional students

### 1. Abstract
PathWise supports exploratory academic elective decisions. It checks prerequisite tags, ranks eligible electives, explains score contributions, highlights career skill gaps, compares courses, evaluates deterministic rule consistency, simulates hypothetical profile changes, and builds a provisional course-to-skill roadmap. A constrained assistant answers grounded questions using the same local knowledge base. No trained machine-learning model or external LLM is used.

### 2. Problem and objectives
Students may find it difficult to compare elective relevance, prerequisites, interests, skills and career aspirations in one place. PathWise aims to: (1) exclude courses with unmet listed prerequisites, (2) produce explainable suitability rankings, (3) identify catalogue-based skill gaps, (4) support counterfactual exploration and hypothetical roadmaps, and (5) make decision logic auditable.

### 3. Architecture and data
Streamlit UI -> validated student profile -> local catalogue and career knowledge base -> prerequisite rule filter -> weighted scoring and explanations -> recommendations, comparison, evaluation, roadmap, what-if and grounded FAQ.

The bundled dataset contains 20 synthetic courses, eight illustrative career pathways and five fictional student profiles. These are not verified university requirements.

### 4. Proposed AI technique
A hybrid **symbolic rule-based + content-based heuristic** approach. For a course to be ranked, every listed prerequisite tag must be present in the student's completed-prerequisite set. For eligible courses:

**Suitability = 0.40 x Interest + 0.30 x Career + 0.20 x Readiness + 0.10 x Skill**

Interest measures overlap between course topics and student interests; Career is a binary match to mapped career goals; Readiness uses self-rated readiness adjusted for course difficulty; Skill measures coverage of foundation skills. All factors are bounded from 0 to 1. Weights are provisional and not learned from student outcomes. Scores are NOT probabilities of success.

### 5. Implemented functionality
- Student profile selection and editing; ranked recommendations with factor-level explanations.
- Prerequisite eligibility and missing tags; career skill-gap display.
- Side-by-side course comparison; synthetic-profile consistency evaluation.
- Academic roadmap showing eligible-now versus conditionally ready after earlier steps, and unresolved external prerequisite tags.
- What-if Lab comparing baseline and hypothetical profiles without mutating baseline data.
- Offline constrained question-answering about catalogue courses, rankings, prerequisites and skill gaps; unsupported questions receive a bounded fallback.
- JSON exports for reproducible results.

### 6. Testing and evaluation
The final release passed **26/26 automated unit tests** in the build environment. They cover the original engine, internal evaluation, roadmap planning, simulator behavior, assistant grounding, and release-specific behavior. The evaluation script examines 5 sample profiles x 20 courses = 100 classification decisions: **51 eligible** and **49 blocked**. Prerequisite rule consistency, ranking order, and determinism checks passed for these samples.

These tests verify specified software behavior and internal consistency. They do NOT establish educational recommendation relevance, fairness, institutional eligibility, or predictive accuracy. No labelled ground truth is supplied, so relevance precision/recall cannot be validly reported.

### 7. Roadmap status semantics
**Eligible now**: prerequisites for that step are present in the original profile. **Ready after earlier steps**: prerequisites are accounted for by earlier hypothetical steps, not necessarily completed in real life. **Check first**: one or more requirements remain unresolved in the proposed sequence. A course-to-skill mapping is not an official prerequisite equivalence.

### 8. Deployment and reproducibility
Windows + VS Code + uv + Python 3.13. From the folder containing `app.py`, run:

`uv run --python 3.13 --with streamlit --with pandas streamlit run app.py`

Run tests with `uv run --python 3.13 python -m unittest discover -s tests -v` and evaluate with `uv run --python 3.13 python evaluate.py`. A local browser URL (typically localhost:8501) opens the app. Public deployment requires separate hosting and security review; no public deployment has been performed or verified.

### 9. Limitations and future work
The catalogue, prerequisites, skill mappings, students and career associations are illustrative. Inputs are self-reported; scoring weights are arbitrary; the roadmap is not a semester timetable; the assistant is not a generative LLM. Future work should include institution-verified curricula, expert-labelled relevance judgements, student consent/privacy controls, fairness audits, user studies, and potentially supervised learning if real labelled data becomes available.

### 10. Conclusion
PathWise demonstrates an end-to-end, explainable academic decision-support prototype with rule enforcement, transparent ranking, interactive exploration and reproducible tests. It is advisory and should not replace official academic counselling or degree regulations.
