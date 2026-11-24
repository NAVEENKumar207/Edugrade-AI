from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult, CompanyPlacementCriteria
from core.services.journey_service import (
    get_journey, get_badges, predict_next_sgpa, evaluate_student_risk
)

class JourneyBadgesAndEarlyWarningTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='journey_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
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

    def test_student_with_no_data_all_seven_locked_no_crash(self):
        sparse_user = User.objects.create_user(username='empty_student', password='password123')
        sparse_profile = UserProfile.objects.create(user=sparse_user, current_cgpa=0.0, backlogs_count=0)
        res = get_badges(sparse_profile)
        self.assertEqual(len(res["all_badges"]), 7)
        self.assertEqual(len(res["earned_badges"]), 0)
        self.assertEqual(len(res["locked_badges"]), 7)
        self.assertTrue(all(b["earned"] is False for b in res["all_badges"]))

    def test_badge_1_zero_arrears_earned_and_locked(self):
        # Earned: backlogs == 0 and at least 1 semester has results
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "zero_arrears" and b["earned"] for b in b_dict["all_badges"]))

        # Locked if backlogs > 0
        self.profile.backlogs_count = 1
        self.profile.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "zero_arrears" and not b["earned"] for b in b_dict["all_badges"]))

    def test_badge_2_comeback_earned_and_locked(self):
        # Locked: no cleared arrears
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "comeback" and not b["earned"] for b in b_dict["all_badges"]))

        # Earned: at least 1 arrear has been cleared
        CourseResult.objects.create(
            student=self.profile, semester_number=1, course_code="CS99",
            course_name="C Prog", credits=3, grade="B", grade_point=6.0, arrear_cleared=True
        )
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "comeback" and b["earned"] for b in b_dict["all_badges"]))

    def test_badge_3_rising_star_earned_and_locked(self):
        # Earned: 8.0 -> 8.5 -> 8.8 (increased across 2 consecutive semesters, 3 semesters)
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "rising_star" and b["earned"] for b in b_dict["all_badges"]))

        # Locked: if not increasing consecutively (e.g. 8.0 -> 8.5 -> 8.2)
        self.sem3.sgpa = 8.20
        self.sem3.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "rising_star" and not b["earned"] for b in b_dict["all_badges"]))

    def test_badge_4_steady_earned_and_locked(self):
        # Set 3 SGPAs within 0.5 of each other: 8.0, 8.2, 8.3 (max-min = 0.3 <= 0.5)
        self.sem1.sgpa = 8.00
        self.sem1.save()
        self.sem2.sgpa = 8.20
        self.sem2.save()
        self.sem3.sgpa = 8.30
        self.sem3.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "steady" and b["earned"] for b in b_dict["all_badges"]))

        # Locked: if last 3 SGPAs exceed 0.5 difference (e.g. 7.0, 8.0, 8.5 -> max-min = 1.5)
        self.sem1.sgpa = 7.00
        self.sem1.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "steady" and not b["earned"] for b in b_dict["all_badges"]))

    def test_badge_5_distinction_earned_and_locked(self):
        # Earned: CGPA 8.80 >= 8.5
        self.profile.current_cgpa = 8.80
        self.profile.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "distinction" and b["earned"] for b in b_dict["all_badges"]))

        # Locked: CGPA < 8.5 (e.g. 8.49)
        self.profile.current_cgpa = 8.49
        self.profile.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "distinction" and not b["earned"] for b in b_dict["all_badges"]))

    def test_badge_6_full_credit_semester_earned_and_locked(self):
        # Earned: sem1 and sem2 courses have no failing grades
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "full_credit" and b["earned"] for b in b_dict["all_badges"]))

        # Locked: if every semester has a failing grade
        self.c1.grade = "U"
        self.c1.save()
        self.c2.grade = "RA"
        self.c2.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "full_credit" and not b["earned"] for b in b_dict["all_badges"]))

    def test_badge_7_placement_ready_earned_and_locked(self):
        # With no companies, it is NOT earned
        CompanyPlacementCriteria.objects.all().delete()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "placement_ready" and not b["earned"] for b in b_dict["all_badges"]))

        # Create company criteria so readiness can be computed
        CompanyPlacementCriteria.objects.create(
            company_name="TechCorp", role_title="SE", min_cgpa=7.0, max_backlogs=0, package_lpa=8.0, is_active=True
        )
        # High CGPA (9.0) + 0 backlogs -> readiness: 45 (cgpa) + 30 (backlogs) + 20 (companies) = 95 >= 70
        self.profile.current_cgpa = 9.00
        self.profile.backlogs_count = 0
        self.profile.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "placement_ready" and b["earned"] for b in b_dict["all_badges"]))

        # Locked: low CGPA + backlogs -> readiness < 70
        self.profile.current_cgpa = 5.00
        self.profile.backlogs_count = 3
        self.profile.save()
        b_dict = get_badges(self.profile)
        self.assertTrue(any(b["id"] == "placement_ready" and not b["earned"] for b in b_dict["all_badges"]))

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
        self.profile.current_cgpa = 8.50
        self.profile.backlogs_count = 0
        self.profile.save()
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

    def test_deleted_admin_analytics_endpoint_returns_404(self):
        admin_user = User.objects.create_user(username='admin_at_risk', password='password123', is_staff=True)
        UserProfile.objects.create(user=admin_user)

        self.client.force_authenticate(user=admin_user)
        resp = self.client.get('/api/admin/analytics/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_students_cannot_read_other_students_journeys(self):
        other_user = User.objects.create_user(username='other_journey_user', password='password123')
        UserProfile.objects.create(user=other_user, current_cgpa=6.0)

        self.client.force_authenticate(user=other_user)
        resp = self.client.get('/api/journey/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Should only see their own journey (empty for other_user)
        self.assertEqual(len(resp.data['journey']), 0)
