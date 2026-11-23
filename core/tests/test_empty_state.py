"""
Automated Integration Tests for Empty Database State Handling.
Verifies that all student endpoints return HTTP 200 without
500 crashes, division by zero, or NaN errors when no results/students exist.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CompanyPlacementCriteria
from core.services.academic_service import placement_readiness


class EmptyStateEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create fresh student user with 0 records
        self.student_user = User.objects.create_user(
            username="empty_student",
            password="password123",
            first_name="New",
            last_name="Enrollee"
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            roll_number="NEW2026001",
            department="Computer Science & Engineering",
            current_semester=1,
            current_cgpa=0.0,
            target_cgpa=8.5,
            credits_earned=0,
            backlogs_count=0
        )

        # Create fresh staff user
        self.admin_user = User.objects.create_user(
            username="empty_admin",
            password="password123",
            first_name="Dean",
            last_name="Office",
            is_staff=True
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            roll_number="FAC-ADMIN-01",
            department="Dean Office"
        )

    def test_student_dashboard_empty_state(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/students/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['student']['current_cgpa'], 0.0)
        self.assertEqual(len(data['semesters']), 0)
        self.assertIn('placement_readiness', data)

    def test_student_results_empty_state(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/academics/results/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['semesters']), 0)

    def test_student_arrears_empty_state(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/student/arrears/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data.get('active', [])), 0)
        self.assertEqual(len(data.get('cleared', [])), 0)

    def test_placement_eligibility_empty_state(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/placements/eligibility/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('placement_readiness', data)

    def test_advisor_chat_empty_state_rule_based(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post('/api/advisor/chat/', {'message': 'What is my CGPA?'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('not been published yet', data['reply'])
        self.assertEqual(data['source'], 'rule_based')

    def test_advisor_chat_empty_state_tamil(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post('/api/advisor/chat/', {'message': 'எனது CGPA என்ன?'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('வெளியிடப்படவில்லை', data['reply'])

    def test_pdf_transcript_empty_state(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/transcript/pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 100)

    def test_cgpa_planner_zero_completed_credits(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(
            '/api/planner/cgpa/',
            data={
                'current_cgpa': 0.0,
                'completed_credits': 0,
                'target_cgpa': 8.5,
                'remaining_semesters': 8,
                'total_credits': 160
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertTrue(data['is_achievable'])
        self.assertEqual(data['required_average_sgpa'], 8.5)

    def test_deleted_faculty_admin_endpoints_return_404(self):
        self.client.force_authenticate(user=self.student_user)
        for ep in ['/api/faculty/overview/', '/api/admin/analytics/', '/api/faculty/students/']:
            response = self.client.get(ep)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_placement_readiness_service_zero_companies(self):
        CompanyPlacementCriteria.objects.all().delete()
        res = placement_readiness(self.student_profile)
        self.assertEqual(res['company_part'], 0.0)
        self.assertEqual(res['tip'], "No companies have been added yet.")
