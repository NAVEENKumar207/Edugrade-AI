"""
API permission and role-based authorization tests for EduGrade AI.
Uses DRF APIClient to verify anonymous and student security boundaries.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord

class ApiPermissionsTests(TestCase):
    """Test RBAC and access boundaries."""

    def setUp(self):
        self.client = APIClient()

        # Create student 1
        self.student_user = User.objects.create_user(username='student1', password='password123')
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role='student',
            roll_number='71762104001',
            current_cgpa=8.50
        )
        SemesterRecord.objects.create(student=self.student_profile, semester_number=1, sgpa=8.50)

        # Create student 2
        self.student2_user = User.objects.create_user(username='student2', password='password123')
        self.student2_profile = UserProfile.objects.create(
            user=self.student2_user,
            role='student',
            roll_number='71762104002',
            current_cgpa=6.20
        )
        SemesterRecord.objects.create(student=self.student2_profile, semester_number=1, sgpa=6.20)

        # Create faculty/admin user
        self.admin_user = User.objects.create_user(username='admin1', password='password123', is_staff=True)
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            roll_number='FAC-001'
        )

    def test_anonymous_access_denied_on_protected_endpoints(self):
        """Anonymous requests to protected endpoints must return 401 or 403."""
        protected_endpoints = [
            '/api/students/dashboard/',
            '/api/student/arrears/',
            '/api/academics/results/',
            '/api/placements/eligibility/',
            '/api/advisor/chat/',
            '/api/faculty/overview/',
            '/api/faculty/students/',
            '/api/admin/grades/sample-csv/',
            '/api/admin/analytics/',
            '/api/transcript/pdf/',
        ]
        for url in protected_endpoints:
            res = self.client.get(url)
            self.assertIn(
                res.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                f"Expected 401/403 for anonymous on {url}, got {res.status_code}"
            )

    def test_student_forbidden_from_admin_faculty_endpoints(self):
        """Student requests to faculty/admin endpoints must return 403."""
        self.client.force_authenticate(user=self.student_user)

        admin_endpoints = [
            ('/api/faculty/overview/', 'GET'),
            ('/api/faculty/students/', 'GET'),
            ('/api/faculty/results/upload/', 'POST'),
            ('/api/admin/grades/sample-csv/', 'GET'),
            ('/api/admin/grades/bulk-upload/', 'POST'),
            ('/api/admin/analytics/', 'GET'),
        ]
        for url, method in admin_endpoints:
            if method == 'GET':
                res = self.client.get(url)
            else:
                res = self.client.post(url, {})
            self.assertEqual(
                res.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Student should receive 403 on {url}, got {res.status_code}"
            )

    def test_admin_can_access_admin_faculty_endpoints(self):
        """Faculty/admin requests to admin endpoints succeed with 200 OK."""
        self.client.force_authenticate(user=self.admin_user)

        admin_get_endpoints = [
            '/api/faculty/overview/',
            '/api/faculty/students/',
            '/api/admin/grades/sample-csv/',
            '/api/admin/analytics/',
        ]
        for url in admin_get_endpoints:
            res = self.client.get(url)
            self.assertEqual(
                res.status_code,
                status.HTTP_200_OK,
                f"Admin should receive 200 on {url}, got {res.status_code}"
            )

    def test_student_cannot_read_another_student_data(self):
        """A student accessing /api/students/dashboard/ only receives their own data."""
        self.client.force_authenticate(user=self.student_user)
        res = self.client.get('/api/students/dashboard/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data['student']['roll_number'], '71762104001')
        self.assertEqual(data['student']['current_cgpa'], 8.50)

        # Switch to student 2
        self.client.force_authenticate(user=self.student2_user)
        res2 = self.client.get('/api/students/dashboard/')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        data2 = res2.json()
        self.assertEqual(data2['student']['roll_number'], '71762104002')
        self.assertEqual(data2['student']['current_cgpa'], 6.20)
