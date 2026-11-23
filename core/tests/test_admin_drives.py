from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult, CompanyPlacementCriteria

class AdminDriveManagerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username='admin_drive', password='password123', is_staff=True)
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role='admin')

        self.student_user = User.objects.create_user(username='student_drive', password='password123')
        self.student_profile = UserProfile.objects.create(user=self.student_user, role='student', current_cgpa=8.00)

        # Company requiring 8.00 CGPA and 0 backlogs
        self.company = CompanyPlacementCriteria.objects.create(
            company_name="ApexGlobal",
            role_title="Software Architect",
            min_cgpa=8.00,
            max_backlogs=0,
            package_lpa=12.0
        )

    def test_student_gets_403_forbidden(self):
        self.client.force_authenticate(user=self.student_user)
        resp1 = self.client.get('/api/admin/drives/')
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)

        resp2 = self.client.get(f'/api/admin/drives/{self.company.id}/')
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)

        resp3 = self.client.get(f'/api/admin/drives/{self.company.id}/export/')
        self.assertEqual(resp3.status_code, status.HTTP_403_FORBIDDEN)

    def test_boundary_cases_eligible_almost_neither(self):
        # Student 1: exactly at min CGPA (8.00, 0 backlogs) -> eligible
        u1 = User.objects.create_user(username='s_exact', password='password123')
        UserProfile.objects.create(user=u1, role='student', current_cgpa=8.00, backlogs_count=0)

        # Student 2: 0.50 short (7.50, 0 backlogs) -> almost eligible
        u2 = User.objects.create_user(username='s_almost', password='password123')
        UserProfile.objects.create(user=u2, role='student', current_cgpa=7.50, backlogs_count=0)

        # Student 3: 0.51 short (7.49, 0 backlogs) -> neither
        u3 = User.objects.create_user(username='s_neither', password='password123')
        UserProfile.objects.create(user=u3, role='student', current_cgpa=7.49, backlogs_count=0)

        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(f'/api/admin/drives/{self.company.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        eligible_rolls = [s['name'] for s in resp.data['eligible_students']]
        almost_rolls = [s['name'] for s in resp.data['almost_eligible_students']]

        self.assertIn("s_exact", eligible_rolls)
        self.assertIn("s_almost", almost_rolls)
        self.assertNotIn("s_neither", eligible_rolls)
        self.assertNotIn("s_neither", almost_rolls)

    def test_csv_export_content(self):
        u1 = User.objects.create_user(username='csv_stud', first_name='John', last_name='Doe', password='password123')
        UserProfile.objects.create(user=u1, role='student', roll_number='ROLL999', current_cgpa=8.50, backlogs_count=0)

        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(f'/api/admin/drives/{self.company.id}/export/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp['Content-Type'], 'text/csv')

        content = resp.content.decode('utf-8')
        self.assertIn("Status,Roll Number,Name", content)
        self.assertIn("ROLL999", content)
        self.assertIn("John Doe", content)

    def test_constant_query_count_regardless_of_data_size(self):
        # Test with 2 students
        for i in range(2):
            u = User.objects.create_user(username=f'pop_small_{i}', password='password123')
            UserProfile.objects.create(user=u, role='student', current_cgpa=8.0)

        self.client.force_authenticate(user=self.admin_user)
        with CaptureQueriesContext(connection) as ctx_small:
            self.client.get(f'/api/admin/drives/{self.company.id}/')
        query_count_small = len(ctx_small)

        # Add 10 more students (larger size)
        for i in range(10):
            u = User.objects.create_user(username=f'pop_large_{i}', password='password123')
            UserProfile.objects.create(user=u, role='student', current_cgpa=7.5)

        with CaptureQueriesContext(connection) as ctx_large:
            self.client.get(f'/api/admin/drives/{self.company.id}/')
        query_count_large = len(ctx_large)

        # Query count must remain constant (independent of student count)
        self.assertEqual(query_count_small, query_count_large)
        self.assertTrue(query_count_large <= 10)
