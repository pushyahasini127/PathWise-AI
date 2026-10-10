# PathWise — Review 2: Prototype Implementation and Evaluation

> Presentation-ready technical notes. Confirm the exact Review 2 rubric and submission format with your course guidelines before submitting.

## 1. Project and problem
**PathWise – AI Academic Decision Assistant** helps students explore suitable electives based on their interests, career aspirations, readiness and existing skills, while checking prerequisite eligibility.

## 2. Implementation completed
- Synthetic knowledge base: 20 elective records, 8 career mappings and 5 example student profiles.
- Python recommendation engine with mandatory prerequisite filtering.
- Interpretable weighted suitability ranking: interest 40%, career match 30%, readiness 20%, skill match 10%.
- Student profile editing, course cards, eligibility diagnostics and skill-gap charts in Streamlit.
- Step 4: side-by-side eligible course comparison, CSV export, reproducible synthetic-profile evaluation and JSON report.

## 3. System architecture
Student input → profile validation → course/career knowledge base → prerequisite rules → eligible course ranking → explanations and career skill-gap analysis → Streamlit dashboard / exports.

See `docs/architecture.mmd` for the editable Mermaid flowchart.

## 4. Algorithm explanation
For student s and eligible course c:

`Score(s,c) = 0.40 × Interest + 0.30 × Career + 0.20 × Readiness + 0.10 × Skill`

- Interest: fraction of course topic tags matching selected interests.
- Career: binary membership in course career mappings.
- Readiness: self-rated readiness scaled by course difficulty.
- Skill: fraction of listed foundation skill tags held by student.
- Prerequisites: hard gate. Courses missing required tags are not ranked.

This is a knowledge-based + content-based **heuristic recommender**; it is not a trained ML model.

## 5. Testing and evaluation methodology
1. Run `python -m unittest discover -s tests -v` to test validation, prerequisite enforcement, ranking, determinism, explanations and skill gaps.
2. Run `python evaluate.py` to evaluate all five synthetic student profiles across the catalogue.
3. Check whether every course is classified as eligible or blocked for every student, whether ranked scores are nonincreasing, and whether repeated runs match.
4. Inspect `reports/evaluation_results.json` and `reports/evaluation_profiles.csv` for evidence.
5. Demonstrate changing the sidebar profile and the four main student-facing views.

**Do not report classification accuracy, precision or recall** as a measure of recommendation quality without independently labelled ground-truth recommendations. Rule-compliance checks are internal correctness checks, not proof of educational effectiveness.

## 6. Limitations
- All records are illustrative, not actual university curriculum data.
- Skill tags and readiness are self-reported; no verification of transcript or grades.
- Fixed weights have not been optimized or validated with user studies.
- No accounts, persistent student database, or personalized learning from feedback.
- A prerequisite tag is not the same as official course eligibility.

## 7. Next steps
- Replace synthetic courses with an approved university catalogue.
- Interview students or faculty and collect consented feedback.
- Obtain expert-labelled recommendation sets and evaluate relevance, fairness and usefulness.
- Add optional authentication and privacy-preserving persistence only if required.

## 8. Suggested demonstration sequence (3–5 minutes)
1. Show profile input and choose sample student Asha.
2. Show top eligible recommendations and factor contributions.
3. Show a blocked elective and missing prerequisite tags.
4. Show career skill gaps and comparison tab.
5. Show evaluation tab, explain synthetic tests vs real-world validation.
