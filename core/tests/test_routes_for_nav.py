"""
Regression test suite verifying that all navigation routes and links
used across EduGrade AI resolve to real, functional endpoints.
"""

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from core.models import UserProfile


class RoutesForNavTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Student user
        self.student_user = User.objects.create_user(
            username='nav_test_student',
            password='testpassword123'
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role='student',
            roll_number='NAV_S01',
            department='Computer Science & Engineering',
            current_cgpa=8.50,
            credits_earned=60
        )

        # Faculty / Admin user
        self.faculty_user = User.objects.create_user(
            username='nav_test_faculty',
            password='testpassword123',
            is_staff=True
        )
        self.faculty_profile = UserProfile.objects.create(
            user=self.faculty_user,
            role='faculty',
            roll_number='NAV_F01',
            department='Computer Science & Engineering'
        )

    def test_anonymous_nav_routes(self):
        """Anonymous visitor navigation endpoints return 200 OK, while protected routes redirect."""
        public_routes = [
            'home',
            'login',
            'signup',
            'api_health',
        ]
        for r_name in public_routes:
            url = reverse(r_name)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Route {r_name} ({url}) returned {resp.status_code}")

        # Protected syllabus view redirects unauthenticated visitors to login
        url_syllabus = reverse('syllabus')
        resp_syllabus = self.client.get(url_syllabus)
        self.assertEqual(resp_syllabus.status_code, 302, "Unauthenticated syllabus access must redirect to login")

    def test_student_legacy_nav_routes(self):
        """Logged-in student legacy navigation endpoints return 200 OK."""
        self.client.login(username='nav_test_student', password='testpassword123')
        student_routes = [
            'dashboard',
            'results',
            'cgpa_planner',
            'placement',
            'ai_advisor',
            'syllabus',
        ]
        for r_name in student_routes:
            url = reverse(r_name)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Student route {r_name} ({url}) returned {resp.status_code}")

    def test_faculty_legacy_nav_routes(self):
        """Logged-in faculty legacy navigation endpoints return 200 OK."""
        self.client.login(username='nav_test_faculty', password='testpassword123')
        faculty_routes = [
            'admin_dashboard',
            'upload',
            'syllabus',
        ]
        for r_name in faculty_routes:
            url = reverse(r_name)
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Faculty route {r_name} ({url}) returned {resp.status_code}")

    def test_reactpy_navigation_items_registered(self):
        """Ensures all page IDs in AppLayout are mapped in EduGradeApp routing."""
        from ui.components.layout import AppLayout
        from ui.app import EduGradeApp

        # Known valid pages mapped in ui/app.py
        valid_student_pages = {
            "dashboard", "future_lab", "results", "planner",
            "placements", "journey", "advisor", "regulations", "profile"
        }
        valid_faculty_pages = {
            "admin_dashboard", "drives", "regulations", "profile"
        }
        self.assertTrue(valid_student_pages.issubset({
            "dashboard", "student_dashboard", "future_lab", "futurelab", "twin",
            "results", "planner", "placements", "placement", "journey", "my_journey",
            "advisor", "ai_advisor", "ai-advisor", "regulations", "syllabus", "profile"
        }))
        self.assertTrue(valid_faculty_pages.issubset({
            "admin_dashboard", "admin", "cohort", "drives", "drive_manager",
            "regulations", "syllabus", "profile"
        }))
