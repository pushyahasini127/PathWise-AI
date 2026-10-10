import json
import unittest
from pathlib import Path
from pathwise.engine import load_knowledge_base
from pathwise.advanced import plan_roadmap, simulate_change, answer_question

ROOT = Path(__file__).resolve().parents[1]

class AdvancedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses, cls.careers = load_knowledge_base()
        cls.students = json.loads((ROOT/'data'/'sample_students.json').read_text(encoding='utf-8'))
        cls.student = cls.students[0]

    def test_roadmap_existing_eligible(self):
        roadmap=plan_roadmap(self.student,self.courses,self.careers,'CS309')
        self.assertEqual(roadmap['steps'][-1]['course_id'],'CS309')
        self.assertTrue(roadmap['target_ready_after_plan'])

    def test_roadmap_unknown_target(self):
        with self.assertRaises(ValueError):
            plan_roadmap(self.student,self.courses,self.careers,'CS999')

    def test_roadmap_missing_external(self):
        student=dict(self.student,completed_prerequisites=[])
        plan=plan_roadmap(student,self.courses,self.careers,'CS309')
        self.assertIn('mathematics',plan['external_prerequisites'])
        self.assertFalse(plan['target_ready_after_plan'])

    def test_simulator_unchanged(self):
        s=simulate_change(self.student,self.courses,self.careers)
        self.assertEqual(s['before'],s['after'])
        self.assertTrue(all(row['score_change']==0 for row in s['comparison']))

    def test_simulator_unlocks_ml(self):
        student=self.students[3]
        s=simulate_change(student,self.courses,self.careers,
                          completed_prerequisites=student['completed_prerequisites']+['statistics'])
        ml=next(row for row in s['comparison'] if row['course_id']=='CS309')
        self.assertEqual(ml['status'],'newly eligible')

    def test_simulator_does_not_mutate_profile(self):
        original=json.dumps(self.student,sort_keys=True)
        simulate_change(self.student,self.courses,self.careers,readiness=0.2)
        self.assertEqual(json.dumps(self.student,sort_keys=True),original)

    def test_assistant_grounded_eligibility(self):
        ans=answer_question('Can I take CS310?',self.student,self.courses,self.careers)
        self.assertIn('machine_learning',ans)
        self.assertIn('Not eligible',ans)

    def test_assistant_scores(self):
        ans=answer_question('How are scores calculated?',self.student,self.courses,self.careers)
        self.assertIn('40%',ans)
        self.assertIn('30%',ans)

    def test_assistant_fallback(self):
        ans=answer_question('What will my salary be?',self.student,self.courses,self.careers)
        self.assertIn('only answer grounded',ans)

    def test_assistant_top_recommendation(self):
        ans=answer_question('What are my top recommendations?',self.student,self.courses,self.careers)
        self.assertIn('Machine Learning',ans)

if __name__ == '__main__': unittest.main()
