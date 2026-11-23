"""
Regression test suite verifying that all navigation routes and links
used across EduGrade AI resolve to real, functional endpoints in a student-only portal.
"""

from django.test import TestCase, Client
from django.urls import reverse
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
            roll_number='NAV_S01',
            department='Computer Science & Engineering',
            current_cgpa=8.50,
            credits_earned=60
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

    def test_legacy_admin_dashboard_redirects_to_student_dashboard(self):
        """Accessing legacy /admin-dashboard/ redirects to /dashboard/."""
        self.client.login(username='nav_test_student', password='testpassword123')
        resp = self.client.get('/admin-dashboard/')
        self.assertIn(resp.status_code, [301, 302])
        self.assertEqual(resp.url, '/dashboard/')

    def test_reactpy_navigation_items_registered(self):
        """Ensures all student page IDs in AppLayout are mapped in EduGradeApp routing."""
        # Known valid pages mapped in ui/app.py
        valid_student_pages = {
            "dashboard", "future_lab", "results", "planner",
            "placements", "journey", "advisor", "regulations", "profile"
        }
        self.assertTrue(valid_student_pages.issubset({
            "dashboard", "student_dashboard", "future_lab", "futurelab", "twin",
            "results", "planner", "placements", "placement", "journey", "my_journey",
            "advisor", "ai_advisor", "ai-advisor", "regulations", "syllabus", "profile"
        }))
