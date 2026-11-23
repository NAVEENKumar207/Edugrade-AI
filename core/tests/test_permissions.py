"""
API permission and student isolation tests for EduGrade AI.
Uses DRF APIClient to verify anonymous and student security boundaries in a student-only portal.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult


class ApiPermissionsTests(TestCase):
    """Test student isolation and access boundaries."""

    def setUp(self):
        self.client = APIClient()

        # Create student 1
        self.student_user = User.objects.create_user(username='student1', password='password123')
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            roll_number='71762104001',
            current_cgpa=8.50
        )
        self.sem1 = SemesterRecord.objects.create(student=self.student_profile, semester_number=1, sgpa=8.50)
        self.course1 = CourseResult.objects.create(
            student=self.student_profile,
            semester_record=self.sem1,
            semester_number=1,
            course_code="CS101",
            course_name="Intro to Programming",
            credits=4,
            grade="A",
            grade_point=8.0
        )

        # Create student 2
        self.student2_user = User.objects.create_user(username='student2', password='password123')
        self.student2_profile = UserProfile.objects.create(
            user=self.student2_user,
            roll_number='71762104002',
            current_cgpa=6.20
        )
        self.sem2 = SemesterRecord.objects.create(student=self.student2_profile, semester_number=1, sgpa=6.20)
        self.course2 = CourseResult.objects.create(
            student=self.student2_profile,
            semester_record=self.sem2,
            semester_number=1,
            course_code="CS102",
            course_name="Data Structures",
            credits=4,
            grade="C",
            grade_point=5.0
        )

    def test_anonymous_access_denied_on_protected_endpoints(self):
        """Anonymous requests to protected endpoints must return 401 or 403."""
        protected_endpoints = [
            '/api/students/dashboard/',
            '/api/student/arrears/',
            '/api/academics/results/',
            '/api/placements/eligibility/',
            '/api/advisor/chat/',
            '/api/transcript/pdf/',
        ]
        for url in protected_endpoints:
            res = self.client.get(url)
            self.assertIn(
                res.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                f"Expected 401/403 for anonymous on {url}, got {res.status_code}"
            )

    def test_deleted_faculty_admin_endpoints_return_404(self):
        """Deleted faculty and admin endpoints must return 404 Not Found."""
        self.client.force_authenticate(user=self.student_user)

        deleted_endpoints = [
            ('/api/faculty/overview/', 'GET'),
            ('/api/faculty/students/', 'GET'),
            ('/api/faculty/results/upload/', 'POST'),
            ('/api/admin/drives/', 'GET'),
            ('/api/admin/drives/1/', 'GET'),
            ('/api/admin/drives/1/export/', 'GET'),
            ('/api/admin/grades/sample-csv/', 'GET'),
            ('/api/admin/grades/bulk-upload/', 'POST'),
            ('/api/admin/analytics/', 'GET'),
        ]
        for url, method in deleted_endpoints:
            if method == 'GET':
                res = self.client.get(url)
            else:
                res = self.client.post(url, {})
            self.assertEqual(
                res.status_code,
                status.HTTP_404_NOT_FOUND,
                f"Deleted endpoint {url} should return 404, got {res.status_code}"
            )

    def test_student_cannot_read_another_student_dashboard(self):
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

    def test_student_cannot_fetch_another_student_transcript_pdf(self):
        """Passing another student's ID to /api/transcript/pdf/?student_id=X returns 403 Forbidden."""
        self.client.force_authenticate(user=self.student_user)
        res = self.client.get(f'/api/transcript/pdf/?student_id={self.student2_profile.id}')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_modify_or_delete_another_student_course(self):
        """Student 1 cannot PUT or DELETE Student 2's course result."""
        self.client.force_authenticate(user=self.student_user)

        # Attempt to modify student 2's course
        res_put = self.client.put(
            f'/api/academics/results/{self.course2.id}/',
            {'grade': 'O'},
            format='json'
        )
        self.assertIn(res_put.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Attempt to delete student 2's course
        res_del = self.client.delete(f'/api/academics/results/{self.course2.id}/')
        self.assertIn(res_del.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Ensure course 2 was not altered or deleted
        self.course2.refresh_from_db()
        self.assertEqual(self.course2.grade, 'C')

    def test_signup_always_creates_student(self):
        """Signup always creates a student account, role parameter is ignored."""
        res = self.client.post('/api/auth/signup/', {
            'username': 'newstudent',
            'password': 'strongpassword123',
            'confirm_password': 'strongpassword123',
            'fullname': 'New Student',
            'department': 'CSE',
            'roll_number': '717622CS999',
            'role': 'admin'  # Should be ignored
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username='newstudent')
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
