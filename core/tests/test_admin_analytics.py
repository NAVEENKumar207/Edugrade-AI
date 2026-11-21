"""Tests for the faculty/admin analytics API and student risk metrics."""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult
from core.api_views import AT_RISK_CGPA_THRESHOLD, AT_RISK_BACKLOG_THRESHOLD


class AdminAnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Threshold verification
        self.assertEqual(AT_RISK_CGPA_THRESHOLD, 6.0)
        self.assertEqual(AT_RISK_BACKLOG_THRESHOLD, 2)

        # Faculty user
        self.faculty_user = User.objects.create_user(username="faculty_analytics", password="password123")
        self.faculty_profile = UserProfile.objects.create(
            user=self.faculty_user,
            role="faculty",
            department="CSE"
        )

        # Student user (normal standing)
        self.good_student_user = User.objects.create_user(username="good_student", password="password123")
        self.good_student = UserProfile.objects.create(
            user=self.good_student_user,
            role="student",
            roll_number="CS2026001",
            department="CSE",
            current_semester=4,
            current_cgpa=8.5,
            backlogs_count=0,
            is_placement_eligible=True
        )

        # At-risk student by CGPA (< 6.0)
        self.cgpa_risk_user = User.objects.create_user(username="cgpa_risk", password="password123")
        self.cgpa_risk = UserProfile.objects.create(
            user=self.cgpa_risk_user,
            role="student",
            roll_number="CS2026002",
            department="ECE",
            current_semester=4,
            current_cgpa=5.8,
            backlogs_count=0,
            is_placement_eligible=False
        )

        # At-risk student by backlogs (>= 2)
        self.backlog_risk_user = User.objects.create_user(username="backlog_risk", password="password123")
        self.backlog_risk = UserProfile.objects.create(
            user=self.backlog_risk_user,
            role="student",
            roll_number="CS2026003",
            department="MECH",
            current_semester=4,
            current_cgpa=6.8,
            backlogs_count=2,
            is_placement_eligible=False
        )

        # Seed sample course grades
        CourseResult.objects.create(
            student=self.good_student,
            semester_number=1,
            course_code="CS101",
            course_name="Intro to CS",
            credits=3,
            grade="O",
            grade_point=10.0
        )
        CourseResult.objects.create(
            student=self.good_student,
            semester_number=1,
            course_code="CS102",
            course_name="Data Structures",
            credits=3,
            grade="A+",
            grade_point=9.0
        )
        CourseResult.objects.create(
            student=self.backlog_risk,
            semester_number=1,
            course_code="ME101",
            course_name="Thermodynamics",
            credits=3,
            grade="U",
            grade_point=0.0
        )

    def test_analytics_faculty_allowed(self):
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn('metrics', data)
        self.assertIn('grade_distribution', data)
        self.assertIn('department_stats', data)
        self.assertIn('at_risk_students', data)

    def test_analytics_student_forbidden(self):
        self.client.force_authenticate(user=self.good_student_user)
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analytics_anonymous_unauthorized(self):
        response = self.client.get('/api/admin/analytics/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_grade_distribution_counts(self):
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dist = response.data['grade_distribution']
        self.assertEqual(dist['O'], 1)
        self.assertEqual(dist['A+'], 1)
        self.assertEqual(dist['U'], 1)
        self.assertEqual(dist['B'], 0)

    def test_at_risk_students_identification(self):
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        at_risk = response.data['at_risk_students']
        at_risk_rolls = [s['roll_number'] for s in at_risk]

        # Both at-risk students must be present
        self.assertIn("CS2026002", at_risk_rolls)
        self.assertIn("CS2026003", at_risk_rolls)
        # Normal standing student must NOT be present
        self.assertNotIn("CS2026001", at_risk_rolls)

    def test_department_stats(self):
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.get('/api/admin/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dept_names = [d['department'] for d in response.data['department_stats']]
        self.assertIn("CSE", dept_names)
        self.assertIn("ECE", dept_names)
        self.assertIn("MECH", dept_names)
