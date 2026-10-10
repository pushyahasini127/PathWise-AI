"""Deterministic hybrid rule-based + content-based academic decision engine."""
from __future__ import annotations
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WEIGHTS = {"interest": 0.40, "career": 0.30, "readiness": 0.20, "skill": 0.10}

def tokens(value):
    """Return normalized distinct tokens from a semicolon-separated field or list."""
    if isinstance(value, str):
        values = value.split(";")
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        raise ValueError("Expected a list or semicolon-separated string")
    return sorted({str(x).strip().lower() for x in values if str(x).strip()})

def load_knowledge_base(data_dir=DATA_DIR):
    folder = Path(data_dir)
    with (folder / "courses.csv").open(encoding="utf-8", newline="") as handle:
        courses = list(csv.DictReader(handle))
    with (folder / "careers.json").open(encoding="utf-8") as handle:
        careers = json.load(handle)
    if not courses or not careers:
        raise ValueError("Course catalogue and careers cannot be empty")
    required = {"course_id","title","prerequisites","topics","careers",
                "foundation_skills","target_skills","difficulty"}
    if not required.issubset(courses[0]):
        raise ValueError("Missing required course columns")
    ids = [row["course_id"] for row in courses]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate course IDs")
    for row in courses:
        difficulty = int(row["difficulty"])
        if not 1 <= difficulty <= 5:
            raise ValueError("Difficulty must be 1–5")
        if set(tokens(row["careers"])) - set(careers):
            raise ValueError(f"Unknown career in {row['course_id']}")
    return courses, careers

def validate_student(student, careers):
    if not isinstance(student, dict):
        raise ValueError("Student profile must be an object")
    for key in ("interests","completed_prerequisites","skills","career_goal","readiness"):
        if key not in student:
            raise ValueError(f"Missing student field: {key}")
    for key in ("interests","completed_prerequisites","skills"):
        if not isinstance(student[key], list):
            raise ValueError(f"{key} must be a list")
    if student["career_goal"] not in careers:
        raise ValueError("Unknown career_goal; see data/careers.json")
    if isinstance(student["readiness"], bool) or not isinstance(student["readiness"], (float,int)):
        raise ValueError("readiness must be a number from 0 to 1")
    if not 0 <= student["readiness"] <= 1:
        raise ValueError("readiness must be between 0 and 1")
    return {
        "student_id": student.get("student_id", "unknown"),
        "name": student.get("name", "Student"),
        "interests": tokens(student["interests"]),
        "completed_prerequisites": tokens(student["completed_prerequisites"]),
        "skills": tokens(student["skills"]),
        "career_goal": student["career_goal"],
        "readiness": float(student["readiness"]),
    }

def coverage(need, have):
    """Share of required/matching attributes present; empty requirement scores 1."""
    required = set(need)
    return len(required & set(have)) / len(required) if required else 1.0

def score_course(course, student):
    interests = tokens(course["topics"])
    course_careers = tokens(course["careers"])
    foundations = tokens(course["foundation_skills"])
    target_skills = tokens(course["target_skills"])
    # Explicit, transparent heuristic; not a trained predictor.
    factors = {
        "interest": coverage(interests, student["interests"]),
        "career": 1.0 if student["career_goal"] in course_careers else 0.0,
        "readiness": round(student["readiness"] * (6 - int(course["difficulty"])) / 5, 6),
        "skill": coverage(foundations, student["skills"]),
    }
    score = sum(WEIGHTS[k] * factors[k] for k in WEIGHTS)
    contributions = {k: round(WEIGHTS[k] * factors[k], 4) for k in WEIGHTS}
    return round(score, 4), {k: round(v, 4) for k,v in factors.items()}, contributions, target_skills

def recommend(student, courses=None, careers=None, top_n=5):
    if courses is None or careers is None:
        default_courses, default_careers = load_knowledge_base()
        courses = default_courses if courses is None else courses
        careers = default_careers if careers is None else careers
    profile = validate_student(student, careers)
    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 1:
        raise ValueError("top_n must be a positive integer")
    eligible, ineligible = [], []
    completed = set(profile["completed_prerequisites"])
    for course in courses:
        missing = sorted(set(tokens(course["prerequisites"])) - completed)
        if missing:
            ineligible.append({
                "course_id": course["course_id"], "title": course["title"],
                "missing_prerequisites": missing,
                "explanation": "Not eligible: missing prerequisite(s): " + ", ".join(missing) + ".",
            })
            continue
        score, factors, contributions, targets = score_course(course, profile)
        leading = sorted(contributions, key=lambda k: (-contributions[k], k))[:2]
        rationale = (
            f"Eligible: all listed prerequisites satisfied. Suitability {score:.0%}. "
            f"Top score contributors: {', '.join(f'{k} ({contributions[k]:.2f})' for k in leading)}."
        )
        eligible.append({
            "course_id": course["course_id"], "title": course["title"],
            "score": score, "factors": factors, "weighted_contributions": contributions,
            "course_skill_gaps": sorted(set(targets) - set(profile["skills"])),
            "explanation": rationale,
        })
    eligible.sort(key=lambda r: (-r["score"], r["course_id"]))
    career = careers[profile["career_goal"]]
    career_gaps = sorted(set(tokens(career["required_skills"])) - set(profile["skills"]))
    return {
        "student": {"student_id": profile["student_id"], "name": profile["name"],
                    "career_goal": profile["career_goal"], "career_label": career["label"]},
        "weights": WEIGHTS.copy(),
        "ranked_recommendations": eligible[:top_n],
        "eligible_count": len(eligible),
        "ineligible_courses": sorted(ineligible, key=lambda r: r["course_id"]),
        "career_skill_gaps": career_gaps,
        "disclaimer": "Advisory heuristic based on synthetic sample data; verify institutional prerequisites. Scores are not success probabilities.",
    }
