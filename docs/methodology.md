# Methodology and technical decisions

## Alignment with Review 1
Topic: PathWise, an AI Academic Decision Assistant.
Problem: Students need personalized, eligibility-aware, explainable elective guidance.
Motivation: personalization, feasibility, skill awareness, transparency, access.
Objectives: profile validation; knowledge base; eligibility; ranking; skill-gap explanations; evaluation.
Technique: symbolic IF–THEN rules plus content-based weighted ranking.

## Formal eligibility rule
For each course c, let P(c) be the set of mandatory prerequisite tags.
Let P(s) be the student's completed prerequisite tags.
Course c is eligible iff P(c) is a subset of P(s).
Missing tags are reported explicitly. No course with missing tags appears in eligible rankings.

## Scoring
All factors lie in [0,1].
InterestMatch = |course topics ∩ student interests| / |course topics|.
CareerMatch = 1 if student's target career is in course career mappings, else 0.
ReadinessMatch = student readiness × (6 − difficulty)/5.
SkillMatch = |course foundation skills ∩ student skills| / |course foundation skills|.
Empty requirement lists return 1 for coverage.
Score = 0.40 I + 0.30 C + 0.20 R + 0.10 K.
Ties are broken deterministically by course ID.

This simple heuristic is chosen for interpretability. Career match is binary, and readiness is a self-reported proxy; both are limitations to evaluate. The score is **not** a success probability.

## Skill gaps
Career gap = career required skills minus current student skills.
Course learning opportunity = course target skills minus current student skills.
A learning opportunity is **not** the same as a missing mandatory prerequisite.

## Explanations
The output reports actual missing prerequisite tags for blocked courses.
For eligible courses it includes the full score breakdown and top weighted contributions.
These are faithful rule/score explanations, not post-hoc generative claims.

## Suggested evaluation (future work)
- Rule accuracy: test prerequisite sets against hand-reviewed cases.
- Ranking quality: construct expert-reviewed relevant course labels for test profiles, then compute Precision@3.
- Runtime: benchmark recommendation latency.
- Sensitivity: vary weights and compare ranking stability.
No such evaluation measurements are claimed by this starter project.
