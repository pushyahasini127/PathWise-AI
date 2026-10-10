import json
import unittest
from pathlib import Path
from pathwise.engine import load_knowledge_base
from pathwise.advanced import plan_roadmap, simulate_change

ROOT = Path(__file__).resolve().parents[1]

class FinalReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses, cls.careers = load_knowledge_base()
        cls.profiles = json.loads((ROOT / "data" / "sample_students.json").read_text(encoding="utf-8"))

    def test_roadmap_distinguishes_current_from_future(self):
        student = self.profiles[3]
        plan = plan_roadmap(student, self.courses, self.careers, "CS310")
        statuses = [step["status"] for step in plan["steps"]]
        self.assertIn("ready after earlier steps", statuses)
        self.assertTrue(all(s in {"eligible now", "ready after earlier steps", "requires external prerequisites"} for s in statuses))

    def test_roadmap_preserves_actual_profile(self):
        student = self.profiles[3]
        before = json.dumps(student, sort_keys=True)
        plan_roadmap(student, self.courses, self.careers, "CS310")
        self.assertEqual(before, json.dumps(student, sort_keys=True))

    def test_simulator_changes_prerequisite_eligibility(self):
        student = self.profiles[3]
        updated = student["completed_prerequisites"] + ["statistics"]
        result = simulate_change(student, self.courses, self.careers, completed_prerequisites=updated)
        self.assertEqual(next(r for r in result["comparison"] if r["course_id"]=="CS309")["status"], "newly eligible")

    def test_dataset_has_expected_scope(self):
        self.assertEqual(len(self.courses), 20)
        self.assertEqual(len(self.profiles), 5)

if __name__ == "__main__":
    unittest.main()
