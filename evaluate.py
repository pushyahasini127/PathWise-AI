"""Run evaluation against synthetic student profiles and save JSON/CSV evidence."""
import csv
import json
from pathlib import Path
from pathwise.engine import load_knowledge_base
from pathwise.evaluation import evaluate_profiles

ROOT = Path(__file__).resolve().parent

def main():
    courses, careers = load_knowledge_base()
    students = json.loads((ROOT/'data'/'sample_students.json').read_text(encoding='utf-8'))
    results = evaluate_profiles(students, courses, careers)
    out = ROOT/'reports'
    out.mkdir(exist_ok=True)
    (out/'evaluation_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    with (out/'evaluation_profiles.csv').open('w', newline='', encoding='utf-8') as f:
        rows = results['profile_results']
        if rows:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(results, indent=2))
    print('\nSaved evaluation files in reports/')

if __name__ == '__main__':
    main()
