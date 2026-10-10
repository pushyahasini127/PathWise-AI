import json
import unittest
from pathlib import Path
from pathwise.engine import load_knowledge_base
from pathwise.evaluation import evaluate_profiles

ROOT = Path(__file__).resolve().parents[1]

class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses, cls.careers = load_knowledge_base()
        cls.profiles = json.loads((ROOT / 'data' / 'sample_students.json').read_text(encoding='utf-8'))

    def test_all_sample_profiles_pass_rule_checks(self):
        result = evaluate_profiles(self.profiles, self.courses, self.careers)
        self.assertTrue(result['prerequisite_rules_pass'])
        self.assertTrue(result['ranking_order_pass'])
        self.assertTrue(result['determinism_pass'])

    def test_every_course_is_classified_per_profile(self):
        result = evaluate_profiles(self.profiles, self.courses, self.careers)
        self.assertEqual(result['total_eligible_decisions'] + result['total_blocked_decisions'],
                         len(self.profiles) * len(self.courses))

    def test_empty_profile_set(self):
        result = evaluate_profiles([], self.courses, self.careers)
        self.assertEqual(result['profiles_evaluated'], 0)
        self.assertEqual(result['profile_results'], [])

if __name__ == '__main__':
    unittest.main()
