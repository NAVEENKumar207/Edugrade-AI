from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile
from core.services.academic_service import required_marks, evaluate_expected_marks

class MarksTargetCalculatorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(username='student_marks', password='password123')
        self.student_profile = UserProfile.objects.create(user=self.student_user)

        self.faculty_user = User.objects.create_user(username='faculty_marks', password='password123', is_staff=True)
        self.faculty_profile = UserProfile.objects.create(user=self.faculty_user)

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

    def test_anonymous_request_rejected_on_both_modes(self):
        # Anonymous client (not authenticated)
        anon_client = APIClient()

        # Mode A: Target mode
        resp_a = anon_client.post('/api/tools/marks-target/', {'internal': 36, 'target_grade': 'A+'})
        self.assertIn(resp_a.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        # Mode B: Expected mode
        resp_b = anon_client.post('/api/tools/marks-target/', {'internal': 36, 'paper_marks': 75, 'mode': 'expected'})
        self.assertIn(resp_b.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_student_and_faculty_both_succeed_with_valid_input(self):
        # Student user
        self.client.force_authenticate(user=self.student_user)
        resp_s_target = self.client.post('/api/tools/marks-target/', {'internal': 36, 'target_grade': 'A+'})
        self.assertEqual(resp_s_target.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_s_target.data["required_paper"], 75)

        resp_s_exp = self.client.post('/api/tools/marks-target/', {'internal': 36, 'paper_marks': 75, 'mode': 'expected'})
        self.assertEqual(resp_s_exp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_s_exp.data["grade"], "A+")

        # Faculty user
        self.client.force_authenticate(user=self.faculty_user)
        resp_f_target = self.client.post('/api/tools/marks-target/', {'internal': 36, 'target_grade': 'A+'})
        self.assertEqual(resp_f_target.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_f_target.data["required_paper"], 75)

        resp_f_exp = self.client.post('/api/tools/marks-target/', {'internal': 36, 'paper_marks': 75, 'mode': 'expected'})
        self.assertEqual(resp_f_exp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_f_exp.data["grade"], "A+")

    def test_invalid_input_returns_400(self):
        self.client.force_authenticate(user=self.student_user)

        # Missing internal
        resp_missing = self.client.post('/api/tools/marks-target/', {'target_grade': 'A+'})
        self.assertEqual(resp_missing.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid target grade
        resp_inv_grade = self.client.post('/api/tools/marks-target/', {'internal': 36, 'target_grade': 'INVALID'})
        self.assertEqual(resp_inv_grade.status_code, status.HTTP_400_BAD_REQUEST)

        # Internal out of range (>40)
        resp_out_range = self.client.post('/api/tools/marks-target/', {'internal': 45, 'target_grade': 'A+'})
        self.assertEqual(resp_out_range.status_code, status.HTTP_400_BAD_REQUEST)

        # Expected mode with missing paper_marks
        resp_no_paper = self.client.post('/api/tools/marks-target/', {'internal': 36, 'mode': 'expected'})
        self.assertEqual(resp_no_paper.status_code, status.HTTP_400_BAD_REQUEST)
