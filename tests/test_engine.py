import unittest
from pathwise import load_knowledge_base, recommend
from pathwise.engine import coverage, score_course

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses, cls.careers = load_knowledge_base()
        cls.student = {
            "student_id":"TEST","name":"Test Student",
            "interests":["ai","data"],"completed_prerequisites":["programming","mathematics"],
            "skills":["programming","python"],"career_goal":"ml_engineer","readiness":0.8
        }

    def test_catalogue(self):
        self.assertEqual(len(self.courses),20)
        self.assertEqual(len(self.careers),8)

    def test_missing_prerequisite_blocks_course(self):
        report=recommend(self.student,self.courses,self.careers)
        ml=next(c for c in report["ineligible_courses"] if c["course_id"]=="CS309")
        self.assertIn("statistics",ml["missing_prerequisites"])
        self.assertFalse(any(c["course_id"]=="CS309" for c in report["ranked_recommendations"]))

    def test_ranking_descending_and_bounded(self):
        report=recommend(self.student,self.courses,self.careers,top_n=100)
        scores=[c["score"] for c in report["ranked_recommendations"]]
        self.assertEqual(scores,sorted(scores,reverse=True))
        self.assertTrue(all(0<=s<=1 for s in scores))

    def test_contributions_sum_to_score_with_rounding(self):
        report=recommend(self.student,self.courses,self.careers)
        for c in report["ranked_recommendations"]:
            self.assertAlmostEqual(sum(c["weighted_contributions"].values()),c["score"],places=3)

    def test_skill_gaps(self):
        report=recommend(self.student,self.courses,self.careers)
        self.assertIn("machine_learning",report["career_skill_gaps"])
        self.assertNotIn("python",report["career_skill_gaps"])

    def test_explanations(self):
        report=recommend(self.student,self.courses,self.careers)
        self.assertIn("Eligible",report["ranked_recommendations"][0]["explanation"])
        self.assertIn("missing prerequisite",report["ineligible_courses"][0]["explanation"])

    def test_validation(self):
        for bad in (-.1,1.1,"high",True):
            profile={**self.student,"readiness":bad}
            with self.assertRaises(ValueError):
                recommend(profile,self.courses,self.careers)
        with self.assertRaises(ValueError):
            recommend({**self.student,"career_goal":"not_a_career"},self.courses,self.careers)

    def test_empty_requirements(self):
        self.assertEqual(coverage([],[]),1)
        self.assertEqual(coverage(["ai","data"],["ai"]),.5)

    def test_deterministic(self):
        self.assertEqual(recommend(self.student,self.courses,self.careers),
                         recommend(self.student,self.courses,self.careers))

if __name__=="__main__":
    unittest.main()
