from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.services.academic_service import required_marks, evaluate_expected_marks

class MarksTargetCalculatorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='marks_user', password='password123')

    def test_example_1_internal_36_target_A_plus(self):
        # internal 36, target A+ -> needed total 81 -> paper 75
        res = required_marks(internal=36, target_grade="A+")
        self.assertEqual(res["status"], "possible")
        self.assertEqual(res["required_paper"], 75)
        self.assertEqual(res["resulting_total"], 81.0)
        self.assertEqual(res["grade"], "A+")

    def test_example_2_internal_36_target_pass(self):
        # internal 36, target "pass" -> raw 23.3 but minimum 45 applies -> paper 45, total 63
        res = required_marks(internal=36, target_grade="pass")
        self.assertEqual(res["status"], "possible")
        self.assertEqual(res["required_paper"], 45)
        self.assertEqual(res["resulting_total"], 63.0)
        self.assertEqual(res["grade"], "B+")

    def test_example_3_internal_30_target_O_impossible(self):
        # internal 30, target O -> (91-30)/0.6 = 101.7 -> impossible, best reachable grade A+ (total 90)
        res = required_marks(internal=30, target_grade="O")
        self.assertEqual(res["status"], "impossible")
        self.assertIsNone(res["required_paper"])
        self.assertEqual(res["resulting_total"], 90.0)
        self.assertEqual(res["grade"], "A+")
        self.assertEqual(res["best_grade"], "A+")

    def test_example_4_internal_41_validation_error(self):
        with self.assertRaises(ValueError):
            required_marks(internal=41, target_grade="A")

    def test_what_grade_will_i_get_passing(self):
        # internal 36, expected paper 75 -> total 81.0 -> A+
        res = evaluate_expected_marks(internal=36, paper_marks=75)
        self.assertEqual(res["total"], 81.0)
        self.assertEqual(res["grade"], "A+")
        self.assertTrue(res["passed_external"])

    def test_what_grade_will_i_get_below_external_minimum_fails_even_with_high_total(self):
        # internal 40, paper 40 -> total = 40 + 24 = 64 (would be B+), but paper 40 < 45 -> U
        res = evaluate_expected_marks(internal=40, paper_marks=40)
        self.assertEqual(res["total"], 64.0)
        self.assertEqual(res["grade"], "U")
        self.assertFalse(res["passed_external"])
        self.assertIn("minimum passing threshold", res["message"])

    def test_api_marks_target_endpoint_both_modes(self):
        self.client.force_authenticate(user=self.user)

        # Mode A: Target Grade
        resp_a = self.client.post('/api/tools/marks-target/', {'internal': 36, 'target_grade': 'A+'})
        self.assertEqual(resp_a.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_a.data["required_paper"], 75)

        # Mode B: Expected Marks
        resp_b = self.client.post('/api/tools/marks-target/', {'internal': 36, 'paper_marks': 75, 'mode': 'expected'})
        self.assertEqual(resp_b.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_b.data["grade"], "A+")
