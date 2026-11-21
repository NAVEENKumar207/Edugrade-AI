"""
Tests for Arrear (Backlog) Tracking and Clearance Engine.
Verifies failure recording, passing remediation, backlog decrement,
audit logging, and arrear listing API.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult, AcademicAuditLog
from core.services.academic_service import record_course_result
from ui.services.data_service import get_arrears

class ArrearTrackerTests(TestCase):
    """Test arrear clearing and recalculation flow."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='arrear_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='student',
            roll_number='71762104099',
            current_cgpa=0.00,
            backlogs_count=0
        )
        self.admin_user = User.objects.create_user(username='prof_smith', password='password123', is_staff=True)

    def test_fail_then_pass_course_clears_arrear(self):
        """
        1. Record failing grade U for course CS8451:
           -> backlog count becomes 1.
        2. Record passing grade B+ for course CS8451:
           -> previous_grade is set to U.
           -> arrear_cleared becomes True.
           -> cleared_on is set.
           -> backlog count reduces from 1 to 0.
           -> SGPA and CGPA recalculate.
           -> AcademicAuditLog contains 'Arrear cleared: CS8451 (U -> B+)'.
        """
        # Step 1: Fail course
        cr, cleared = record_course_result(
            action_user=self.admin_user,
            student_profile=self.profile,
            semester_number=4,
            course_code='CS8451',
            course_name='Operating Systems',
            credits=3,
            grade='U',
            grade_point=0.0,
            recalculate=True
        )
        self.profile.refresh_from_db()
        self.assertFalse(cleared)
        self.assertFalse(cr.arrear_cleared)
        self.assertEqual(self.profile.backlogs_count, 1)
        self.assertEqual(float(self.profile.current_cgpa), 0.0)

        # Check get_arrears reflects 1 active arrear
        arrears_before = get_arrears(self.profile)
        self.assertEqual(len(arrears_before['active']), 1)
        self.assertEqual(arrears_before['active'][0]['course_code'], 'CS8451')
        self.assertEqual(len(arrears_before['cleared']), 0)

        # Step 2: Pass course
        cr2, cleared2 = record_course_result(
            action_user=self.admin_user,
            student_profile=self.profile,
            semester_number=4,
            course_code='CS8451',
            course_name='Operating Systems',
            credits=3,
            grade='B+',
            grade_point=7.0,
            recalculate=True
        )
        self.profile.refresh_from_db()
        self.assertTrue(cleared2)
        self.assertTrue(cr2.arrear_cleared)
        self.assertEqual(cr2.previous_grade, 'U')
        self.assertIsNotNone(cr2.cleared_on)
        self.assertEqual(self.profile.backlogs_count, 0)
        self.assertEqual(float(self.profile.current_cgpa), 7.00)

        # Check audit log written
        audit = AcademicAuditLog.objects.filter(action_type="Arrear cleared").first()
        self.assertIsNotNone(audit)
        self.assertIn("Arrear cleared: CS8451 (U -> B+)", audit.description)

        # Check get_arrears reflects 0 active and 1 cleared
        arrears_after = get_arrears(self.profile)
        self.assertEqual(len(arrears_after['active']), 0)
        self.assertEqual(len(arrears_after['cleared']), 1)
        self.assertEqual(arrears_after['cleared'][0]['course_code'], 'CS8451')
        self.assertEqual(arrears_after['cleared'][0]['previous_grade'], 'U')
        self.assertEqual(arrears_after['cleared'][0]['current_grade'], 'B+')

    def test_arrears_api_endpoint(self):
        """GET /api/student/arrears/ returns student's active and cleared arrears."""
        self.client.force_authenticate(user=self.user)

        # Record active arrear
        record_course_result(
            action_user=self.admin_user,
            student_profile=self.profile,
            semester_number=4,
            course_code='CS8492',
            course_name='DBMS',
            credits=3,
            grade='RA',
            grade_point=0.0
        )

        res = self.client.get('/api/student/arrears/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIn('active', data)
        self.assertIn('cleared', data)
        self.assertEqual(len(data['active']), 1)
        self.assertEqual(data['active'][0]['course_code'], 'CS8492')
