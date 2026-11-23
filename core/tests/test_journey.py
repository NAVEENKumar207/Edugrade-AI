from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult
from core.services.journey_service import (
    get_journey, get_badges, predict_next_sgpa, evaluate_student_risk
)

class JourneyBadgesAndEarlyWarningTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='journey_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='student',
            current_cgpa=8.80,
            credits_earned=60,
            backlogs_count=0
        )
        self.sem1 = SemesterRecord.objects.create(student=self.profile, semester_number=1, sgpa=8.00, credits_earned=20)
        self.sem2 = SemesterRecord.objects.create(student=self.profile, semester_number=2, sgpa=8.50, credits_earned=20)
        self.sem3 = SemesterRecord.objects.create(student=self.profile, semester_number=3, sgpa=8.80, credits_earned=20)

        # Courses
        self.c1 = CourseResult.objects.create(student=self.profile, semester_number=1, course_code="CS101", course_name="Maths", credits=4, grade="A", grade_point=8.0)
        self.c2 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS201", course_name="Data Structures", credits=4, grade="O", grade_point=10.0)

    def test_journey_order_and_highlights(self):
        journey = get_journey(self.profile)
        self.assertEqual(len(journey), 3)
        self.assertEqual([s["semester_number"] for s in journey], [1, 2, 3])
        # Sem 2 was an increase (+0.50) from Sem 1
        self.assertEqual(journey[1]["change"], "up")
        self.assertIn("surged", journey[1]["highlight"].lower())

    def test_each_badge_earned_and_locked_cases(self):
        badges_dict = get_badges(self.profile)
        earned_ids = [b["id"] for b in badges_dict["earned_badges"]]
        locked_ids = [b["id"] for b in badges_dict["locked_badges"]]

        # Zero arrears should be earned (0 backlogs, 3 semesters)
        self.assertIn("zero_arrears", earned_ids)
        # Distinction should be earned (CGPA 8.80 >= 8.5)
        self.assertIn("distinction", earned_ids)
        # Rising star earned (8.0 -> 8.5 -> 8.8)
        self.assertIn("rising_star", earned_ids)
        # Comeback locked (no arrear cleared)
        self.assertIn("comeback", locked_ids)

        # Now simulate clearing an arrear
        CourseResult.objects.create(student=self.profile, semester_number=1, course_code="CS99", course_name="C Prog", credits=3, grade="B", grade_point=6.0, arrear_cleared=True)
        updated_badges = get_badges(self.profile)
        updated_earned_ids = [b["id"] for b in updated_badges["earned_badges"]]
        self.assertIn("comeback", updated_earned_ids)

    def test_least_squares_prediction_on_known_series(self):
        # Specific requirement: [8.0, 7.0, 6.0] predicts 5.0
        predicted = predict_next_sgpa([8.0, 7.0, 6.0])
        self.assertEqual(predicted, 5.00)

        # Clamping to 0.00 - 10.00
        self.assertEqual(predict_next_sgpa([3.0, 2.0, 1.0]), 0.00)
        self.assertEqual(predict_next_sgpa([8.0, 9.0, 10.0]), 10.00)
        # Fewer than 2 data points returns None
        self.assertIsNone(predict_next_sgpa([8.5]))

    def test_risk_levels_and_reasons(self):
        # Normal profile -> low risk
        r_low = evaluate_student_risk(self.profile)
        self.assertEqual(r_low["risk_level"], "low")

        # High risk: CGPA < 6.0
        self.profile.current_cgpa = 5.80
        r_high = evaluate_student_risk(self.profile)
        self.assertEqual(r_high["risk_level"], "high")
        self.assertTrue(any("below 6.0" in r for r in r_high["reasons"]))

        # Medium risk: dropped by >= 1.0 (e.g. sem 2 = 8.5, sem 3 = 7.0)
        self.profile.current_cgpa = 7.50
        self.sem3.sgpa = 7.00
        self.sem3.save()
        r_med = evaluate_student_risk(self.profile)
        self.assertEqual(r_med["risk_level"], "medium")
        self.assertTrue(any("fell" in r.lower() for r in r_med["reasons"]))

    def test_old_at_risk_outputs_are_unchanged_in_api(self):
        admin_user = User.objects.create_user(username='admin_at_risk', password='password123', is_staff=True)
        UserProfile.objects.create(user=admin_user, role='admin')

        self.client.force_authenticate(user=admin_user)
        resp = self.client.get('/api/admin/analytics/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', resp.data)
        self.assertIn('grade_distribution', resp.data)
        self.assertIn('at_risk_students', resp.data)

    def test_students_cannot_read_other_students_journeys(self):
        other_user = User.objects.create_user(username='other_journey_user', password='password123')
        UserProfile.objects.create(user=other_user, role='student', current_cgpa=6.0)

        self.client.force_authenticate(user=other_user)
        resp = self.client.get('/api/journey/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should only see their own journey (empty for other_user)
        self.assertEqual(len(resp.data['journey']), 0)
