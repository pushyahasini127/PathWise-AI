"""CLI: python main.py --student STU001 --top 5"""
import argparse
import json
from pathlib import Path
from pathwise import load_knowledge_base, recommend

def main():
    parser = argparse.ArgumentParser(description="PathWise hybrid recommendation engine")
    parser.add_argument("--student", default="STU001", help="ID from sample_students.json")
    parser.add_argument("--profile", type=Path, help="Path to custom student JSON object")
    parser.add_argument("--top", type=int, default=5, help="Number of ranked recommendations")
    parser.add_argument("--output", type=Path, help="Optional JSON report destination")
    args = parser.parse_args()
    courses, careers = load_knowledge_base()
    if args.profile:
        student = json.loads(args.profile.read_text(encoding="utf-8"))
    else:
        students = json.loads((Path(__file__).parent / "data/sample_students.json").read_text(encoding="utf-8"))
        student = next((s for s in students if s["student_id"] == args.student), None)
        if student is None:
            parser.error("Unknown student ID; use STU001–STU005 or --profile")
    try:
        report = recommend(student, courses, careers, args.top)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Saved report to {args.output}")
    else:
        print(rendered)

if __name__ == "__main__":
    main()
