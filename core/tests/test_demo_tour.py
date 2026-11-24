"""
Unit and integration tests for EduGrade AI Auto-Play Demo Mode.
Validates demo environment preparation, cleanup, authentication,
data-demo attributes, and static script registration.
"""

import os
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import UserProfile, CourseResult, SemesterRecord
from ui.services.data_service import (
    is_demo_mode_enabled,
    prepare_demo_environment,
    cleanup_demo_environment,
    authenticate_user,
)


class DemoTourModeTests(TestCase):
    def setUp(self):
        # Ensure fresh state
        User.objects.filter(username='demo_student').delete()

    def tearDown(self):
        cleanup_demo_environment(delete_demo_courses=True)

    def test_demo_mode_setting_and_service_function(self):
        """DEMO_MODE_ENABLED setting is recognized and returns boolean."""
        self.assertTrue(is_demo_mode_enabled())

    def test_prepare_demo_environment_creates_demo_student(self):
        """prepare_demo_environment seeds demo_student and academic records."""
        success, msg = prepare_demo_environment()
        self.assertTrue(success)

        demo_user = User.objects.filter(username='demo_student').first()
        self.assertIsNotNone(demo_user)
        self.assertTrue(hasattr(demo_user, 'profile'))

        profile = demo_user.profile
        self.assertEqual(profile.roll_number, '717622CS101')
        self.assertGreater(profile.current_cgpa, 8.0)
        self.assertGreater(profile.credits_earned, 100)

        # Confirm semester records and course results exist
        sem_records = SemesterRecord.objects.filter(student=profile)
        self.assertGreater(sem_records.count(), 0)
        courses = CourseResult.objects.filter(student=profile)
        self.assertGreater(courses.count(), 0)

    def test_demo_student_authentication(self):
        """demo_student authenticates reliably with demo passwords."""
        prepare_demo_environment()

        # Valid passwords
        user1, err1 = authenticate_user('demo_student', 'student123')
        self.assertIsNotNone(user1)
        self.assertIsNone(err1)
        self.assertEqual(user1.username, 'demo_student')

        user2, err2 = authenticate_user('demo_student', 'student01')
        self.assertIsNotNone(user2)
        self.assertIsNone(err2)
        self.assertEqual(user2.username, 'demo_student')

        # Invalid password
        user_invalid, err_invalid = authenticate_user('demo_student', 'wrong_pass')
        self.assertIsNone(user_invalid)
        self.assertIsNotNone(err_invalid)

    def test_cleanup_demo_environment_persists_modifications_in_db(self):
        """cleanup_demo_environment preserves demo modifications in the database and recalculates metrics."""
        prepare_demo_environment()
        demo_user = User.objects.get(username='demo_student')
        sem1 = SemesterRecord.objects.filter(student=demo_user.profile).first()

        # Simulate user adding DEMO101 during the tour
        CourseResult.objects.create(
            student=demo_user.profile,
            semester_record=sem1,
            semester_number=sem1.semester_number,
            course_code='DEMO101',
            course_name='Advanced Cloud Computing',
            credits=3,
            grade='O',
            grade_point=10.0
        )
        self.assertTrue(CourseResult.objects.filter(course_code='DEMO101').exists())

        # Cleanup preserves modifications by default
        cleanup_demo_environment()
        self.assertTrue(CourseResult.objects.filter(course_code='DEMO101').exists())

        # When explicitly requested with delete_demo_courses=True, removes demo courses
        cleanup_demo_environment(delete_demo_courses=True)
        self.assertFalse(CourseResult.objects.filter(course_code='DEMO101').exists())

    def test_demo_api_endpoints(self):
        """REST endpoints /api/demo/prepare/ and /api/demo/cleanup/ return 200 OK."""
        res_prep = self.client.post(reverse('api_demo_prepare'))
        self.assertEqual(res_prep.status_code, 200)
        data_prep = res_prep.json()
        self.assertTrue(data_prep.get('success'))

        res_clean = self.client.post(reverse('api_demo_cleanup'))
        self.assertEqual(res_clean.status_code, 200)
        data_clean = res_clean.json()
        self.assertTrue(data_clean.get('success'))

    def test_demo_script_file_exists_and_contains_expected_tokens(self):
        """static/js/demo_tour.js exists, is loaded in HTML, and defines engine primitives."""
        js_path = os.path.join('static', 'js', 'demo_tour.js')
        self.assertTrue(os.path.exists(js_path))

        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('window.startEduGradeDemo', content)
        self.assertIn('TOUR_STEPS', content)
        self.assertIn('setNativeValue', content)
        self.assertIn('edugrade-fake-cursor', content)
        self.assertIn('edugrade-tour-caption-bar', content)
        self.assertIn('edugrade-tour-controls', content)

        # Check reactpy_index.html loads demo_tour.js
        html_path = os.path.join('templates', 'reactpy_index.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        self.assertIn('/static/js/demo_tour.js', html_content)
