# PathWise Step 5 — Technical Guide

## New modules

- `pathwise/advanced.py`: deterministic roadmap planner, counterfactual simulator, constrained catalogue Q&A assistant.
- `app.py`: three new Streamlit tabs: Roadmap, What-if Lab, AI Assistant. All six Step 4 tabs are retained.
- `tests/test_advanced.py`: tests for new features.

## Roadmap algorithm

For a selected destination course, inspect its prerequisite tags. For a missing tag, search sample catalogue courses whose `target_skills` contains that tag. Recursively visit a matching course (chosen by current profile score), then add it to the proposed learning sequence. Missing tags with no feasible course path are explicitly marked as external/unresolved. Tags learned from a course are treated as provisionally available only if that course's own prerequisite tags are already available. This is **not** an official course equivalence or guaranteed graduation plan.

## What-if simulator

Re-run the original deterministic `recommend()` function on the baseline profile and a modified copy. Show eligible-course count, changes in suitability, newly blocked courses, and newly eligible courses. Unavailable scores remain `null`, not zero. This is a counterfactual **heuristic comparison**, not a causal or predictive model.

## Grounded assistant

A constrained, offline rule-based FAQ that recognizes catalogue course IDs/titles and a few question intents (recommendation, eligibility, skills, scoring). It retrieves all facts from the course catalogue and existing recommendation engine. Unrecognized questions receive a limitation message. **No LLM has been trained or integrated.**

## Scope and limitations

The 20-course catalogue and 5 sample students are synthetic. Scores are advisory, weights are provisional, prerequisites are illustrative, readiness is self-assessed, and skill labels are not verified competencies. Test success demonstrates internal correctness against these rules, not educational effectiveness.

## Suggested demonstration

1. Select sample STU001 and show the top eligible course.
2. Open Roadmap and choose Deep Learning (CS310); examine Machine Learning as a potential preparatory step.
3. Open What-if Lab, add `machine_learning` to hypothetical completed prerequisite tags, and observe changes in eligibility.
4. Ask the assistant "Can I take CS310?" and show the grounded response.
5. Run `python -m unittest discover -s tests -v` and `python evaluate.py`.
