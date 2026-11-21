"""Tests for bulk CSV grades upload, CSV format validation, and atomic commits."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult, AcademicAuditLog


class BulkCSVGradeUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin_user = User.objects.create_user(username="admin_user", password="adminpassword123")
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role="admin",
            department="CSE"
        )

        # Faculty user
        self.faculty_user = User.objects.create_user(username="faculty_user", password="facultypassword123")
        self.faculty_profile = UserProfile.objects.create(
            user=self.faculty_user,
            role="faculty",
            department="ECE"
        )

        # Student user
        self.student_user = User.objects.create_user(username="student_user", password="studentpassword123")
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role="student",
            roll_number="CS2026999",
            department="CSE",
            current_semester=4,
            current_cgpa=8.0,
            credits_earned=60,
            backlogs_count=0,
            is_placement_eligible=True
        )

        # Student with arrear
        self.arrear_user = User.objects.create_user(username="arrear_user", password="arrearpassword123")
        self.arrear_profile = UserProfile.objects.create(
            user=self.arrear_user,
            role="student",
            roll_number="CS2026888",
            department="CSE",
            current_semester=4,
            current_cgpa=6.5,
            credits_earned=45,
            backlogs_count=1,
            is_placement_eligible=False
        )
        CourseResult.objects.create(
            student=self.arrear_profile,
            semester_number=3,
            course_code="CS8391",
            course_name="Data Structures",
            credits=3,
            grade="U",
            grade_point=0.0
        )

    def test_sample_csv_download_faculty_allowed(self):
        self.client.force_authenticate(user=self.faculty_user)
        response = self.client.get('/api/admin/grades/sample-csv/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="sample_grades.csv"', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('roll_number,semester,course_code,course_title,credits,grade', content)

    def test_sample_csv_download_student_forbidden(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/admin/grades/sample-csv/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sample_csv_download_anonymous_unauthorized(self):
        response = self.client.get('/api/admin/grades/sample-csv/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_bulk_upload_valid_csv(self):
        self.client.force_authenticate(user=self.admin_user)
        csv_data = (
            "roll_number,semester,course_code,course_title,credits,grade\n"
            "CS2026999,4,CS8451,Operating Systems,3,A+\n"
            "CS2026999,4,CS8491,Computer Networks,3,O\n"
        )
        uploaded = SimpleUploadedFile("grades.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['saved'], 2)
        self.assertEqual(response.data['skipped'], 0)
        self.assertEqual(response.data['errors'], [])

        # Verify courses saved
        courses = CourseResult.objects.filter(student=self.student_profile, semester_number=4)
        self.assertEqual(courses.count(), 2)

    def test_bulk_upload_utf8_bom(self):
        self.client.force_authenticate(user=self.admin_user)
        csv_data = (
            "roll_number,semester,course_code,course_title,credits,grade\n"
            "CS2026999,4,CS8451,Operating Systems,3,B+\n"
        )
        # Encode with utf-8-sig (adds BOM)
        uploaded = SimpleUploadedFile("grades_bom.csv", csv_data.encode("utf-8-sig"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['saved'], 1)

    def test_bulk_upload_skips_invalid_rows(self):
        self.client.force_authenticate(user=self.faculty_user)
        csv_data = (
            "roll_number,semester,course_code,course_title,credits,grade\n"
            "NONEXISTENT,4,CS8451,Operating Systems,3,A+\n"  # Invalid student
            "CS2026999,99,CS8451,Operating Systems,3,A+\n"  # Invalid semester
            "CS2026999,4,,Operating Systems,3,A+\n"           # Missing course code
            "CS2026999,4,CS8451,,3,A+\n"                    # Missing course title
            "CS2026999,4,CS8451,Operating Systems,-1,A+\n"   # Invalid credits
            "CS2026999,4,CS8451,Operating Systems,3,XYZ\n"  # Invalid grade
            "CS2026999,4,CS8401,Valid Subject,3,A\n"        # Valid row
        )
        uploaded = SimpleUploadedFile("grades_mixed.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['saved'], 1)
        self.assertEqual(response.data['skipped'], 6)
        self.assertEqual(len(response.data['errors']), 6)

    def test_bulk_upload_clears_arrear(self):
        self.client.force_authenticate(user=self.admin_user)
        # Pre-check arrear state
        self.arrear_profile.refresh_from_db()
        self.assertEqual(self.arrear_profile.backlogs_count, 1)

        # Upload passing grade for failed subject CS8391
        csv_data = (
            "roll_number,semester,course_code,course_title,credits,grade\n"
            "CS2026888,3,CS8391,Data Structures,3,B+\n"
        )
        uploaded = SimpleUploadedFile("clear_arrear.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['saved'], 1)

        # Check arrear marked cleared and backlogs count decremented
        cr = CourseResult.objects.get(student=self.arrear_profile, semester_number=3, course_code="CS8391")
        self.assertTrue(cr.arrear_cleared)
        self.assertEqual(cr.previous_grade, "U")
        self.assertEqual(cr.grade, "B+")

        self.arrear_profile.refresh_from_db()
        self.assertEqual(self.arrear_profile.backlogs_count, 0)

        # Check audit log
        audit = AcademicAuditLog.objects.filter(description__contains="Arrear cleared: CS8391").first()
        self.assertIsNotNone(audit)

    def test_bulk_upload_missing_required_column(self):
        self.client.force_authenticate(user=self.admin_user)
        csv_data = (
            "roll_number,semester,course_code,credits,grade\n"  # Missing course_title
            "CS2026999,4,CS8451,3,A+\n"
        )
        uploaded = SimpleUploadedFile("bad_header.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Missing required column(s): course_title", response.data['error'])

    def test_bulk_upload_non_csv_extension_rejected(self):
        self.client.force_authenticate(user=self.admin_user)
        uploaded = SimpleUploadedFile("grades.xlsx", b"some binary data", content_type="application/vnd.ms-excel")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(".csv", response.data['error'])

    def test_bulk_upload_file_too_large_rejected(self):
        self.client.force_authenticate(user=self.admin_user)
        # Create a file just over 2MB
        large_bytes = b"x" * (2 * 1024 * 1024 + 10)
        uploaded = SimpleUploadedFile("large.csv", large_bytes, content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exceeds maximum limit of 2MB", response.data['error'])

    def test_bulk_upload_student_forbidden(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = "roll_number,semester,course_code,course_title,credits,grade\nCS2026999,4,CS8451,OS,3,A+\n"
        uploaded = SimpleUploadedFile("grades.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/admin/grades/bulk-upload/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
