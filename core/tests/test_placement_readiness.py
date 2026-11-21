from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CompanyPlacementCriteria
from core.services.academic_service import placement_readiness


class PlacementReadinessTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Seed companies
        CompanyPlacementCriteria.objects.create(
            company_name="TechCorp",
            role_title="Software Engineer",
            package_lpa=12.0,
            min_cgpa=8.0,
            max_backlogs=0,
            is_active=True
        )
        CompanyPlacementCriteria.objects.create(
            company_name="InnovateLabs",
            role_title="Systems Engineer",
            package_lpa=7.5,
            min_cgpa=7.0,
            max_backlogs=1,
            is_active=True
        )

        self.student_user = User.objects.create_user(username="placement_student", password="password123")
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role="student",
            roll_number="CS2026555",
            department="CSE",
            current_semester=6,
            current_cgpa=8.0,
            backlogs_count=1,
            credits_earned=100
        )

    def test_placement_readiness_standard_formula(self):
        # CGPA 8.0, 1 backlog, 3 eligible out of 6 companies -> 70
        res = placement_readiness(
            profile_or_cgpa=8.0,
            backlogs=1,
            eligible_count=3,
            total_companies=6
        )
        self.assertEqual(res['score'], 70)
        self.assertEqual(res['cgpa_part'], 40.0)
        self.assertEqual(res['backlog_part'], 20.0)
        self.assertEqual(res['company_part'], 10.0)
        self.assertEqual(int(res), 70)
        self.assertIn("Clear 1 active arrear", res['tip'])

    def test_placement_readiness_perfect_score(self):
        res = placement_readiness(
            profile_or_cgpa=10.0,
            backlogs=0,
            eligible_count=10,
            total_companies=10
        )
        self.assertEqual(res['score'], 100)
        self.assertEqual(res['cgpa_part'], 50.0)
        self.assertEqual(res['backlog_part'], 30.0)
        self.assertEqual(res['company_part'], 20.0)
        self.assertIn("100%", res['tip'])

    def test_placement_readiness_zero_companies(self):
        # Must not throw ZeroDivisionError
        res = placement_readiness(
            profile_or_cgpa=8.0,
            backlogs=0,
            eligible_count=0,
            total_companies=0
        )
        self.assertEqual(res['company_part'], 0.0)
        self.assertEqual(res['score'], 70)
        self.assertEqual(res['tip'], "No companies have been added yet.")

    def test_placement_readiness_many_backlogs_floor_zero(self):
        # 5 backlogs -> backlog_part max(0, 30 - 50) = 0
        res = placement_readiness(
            profile_or_cgpa=6.0,
            backlogs=5,
            eligible_count=0,
            total_companies=4
        )
        self.assertEqual(res['backlog_part'], 0.0)
        self.assertEqual(res['cgpa_part'], 30.0)
        self.assertEqual(res['score'], 30)

    def test_placement_readiness_with_profile_object(self):
        res = placement_readiness(self.student_profile)
        self.assertIsInstance(res['score'], int)
        self.assertGreaterEqual(res['score'], 0)
        self.assertLessEqual(res['score'], 100)

    def test_api_endpoints_return_placement_readiness(self):
        self.client.force_authenticate(user=self.student_user)

        # 1. Student Dashboard
        dash_res = self.client.get('/api/students/dashboard/')
        self.assertEqual(dash_res.status_code, status.HTTP_200_OK)
        self.assertIn('placement_readiness', dash_res.data)
        self.assertIn('score', dash_res.data['placement_readiness'])
        self.assertIn('tip', dash_res.data['placement_readiness'])

        # 2. Placement Eligibility
        place_res = self.client.get('/api/placements/eligibility/')
        self.assertEqual(place_res.status_code, status.HTTP_200_OK)
        self.assertIn('placement_readiness', place_res.data)
        self.assertIn('score', place_res.data['placement_readiness'])
