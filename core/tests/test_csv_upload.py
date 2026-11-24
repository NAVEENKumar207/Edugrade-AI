"""Tests for student-owned CSV grade import, format validation, and atomic commits."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult


class StudentCSVGradeImportTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Student user
        self.student_user = User.objects.create_user(username="student_user", password="studentpassword123")
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
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

    def test_sample_csv_download_student_allowed(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get('/api/academics/results/sample-csv/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('sample_grades_template.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('semester,course_code,course_name,credits,grade', content)

    def test_sample_csv_download_anonymous_unauthorized(self):
        response = self.client.get('/api/academics/results/sample-csv/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_student_import_valid_csv_file(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = (
            "semester,course_code,course_name,credits,grade\n"
            "4,CS8451,Operating Systems,3,A+\n"
            "4,CS8491,Computer Networks,3,O\n"
        )
        uploaded = SimpleUploadedFile("grades.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported_count'], 2)
        self.assertEqual(response.data['errors'], [])

        # Verify courses saved under authenticated student
        courses = CourseResult.objects.filter(student=self.student_profile, semester_number=4)
        self.assertEqual(courses.count(), 2)

    def test_student_import_csv_raw_text(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = (
            "semester,course_code,course_name,credits,grade\n"
            "4,CS8451,Operating Systems,3,A\n"
        )
        response = self.client.post('/api/academics/results/import/', {'csv_text': csv_data}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported_count'], 1)

    def test_student_import_utf8_bom(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = (
            "semester,course_code,course_name,credits,grade\n"
            "4,CS8451,Operating Systems,3,B+\n"
        )
        uploaded = SimpleUploadedFile("grades_bom.csv", csv_data.encode("utf-8-sig"), content_type="text/csv")
        response = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported_count'], 1)

    def test_student_import_skips_invalid_rows(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = (
            "semester,course_code,course_name,credits,grade\n"
            "99,CS8451,Operating Systems,3,A+\n"  # Invalid semester
            "4,,Operating Systems,3,A+\n"           # Missing course code
            "4,CS8451,,3,A+\n"                    # Missing course title
            "4,CS8451,Operating Systems,-1,A+\n"   # Invalid credits
            "4,CS8451,Operating Systems,3,XYZ\n"  # Invalid grade
            "4,CS8401,Valid Subject,3,A\n"        # Valid row
        )
        uploaded = SimpleUploadedFile("grades_mixed.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported_count'], 1)
        self.assertEqual(len(response.data['errors']), 5)

    def test_student_import_clears_arrear(self):
        self.client.force_authenticate(user=self.arrear_user)
        self.arrear_profile.refresh_from_db()
        self.assertEqual(self.arrear_profile.backlogs_count, 1)

        csv_data = (
            "semester,course_code,course_name,credits,grade\n"
            "3,CS8391,Data Structures,3,B+\n"
        )
        uploaded = SimpleUploadedFile("clear_arrear.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported_count'], 1)
        self.assertEqual(response.data['cleared_arrears_count'], 1)

        cr = CourseResult.objects.get(student=self.arrear_profile, semester_number=3, course_code="CS8391")
        self.assertTrue(cr.arrear_cleared)
        self.assertEqual(cr.previous_grade, "U")
        self.assertEqual(cr.grade, "B+")

        self.arrear_profile.refresh_from_db()
        self.assertEqual(self.arrear_profile.backlogs_count, 0)

    def test_student_import_missing_required_column(self):
        self.client.force_authenticate(user=self.student_user)
        csv_data = (
            "semester,course_code,credits,grade\n"  # Missing course_name
            "4,CS8451,3,A+\n"
        )
        uploaded = SimpleUploadedFile("bad_header.csv", csv_data.encode("utf-8"), content_type="text/csv")
        response = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course_name", response.data['error'])

    def test_deleted_admin_bulk_endpoints_return_404(self):
        self.client.force_authenticate(user=self.student_user)
        r1 = self.client.get('/api/admin/grades/sample-csv/')
        self.assertEqual(r1.status_code, status.HTTP_404_NOT_FOUND)

        r2 = self.client.post('/api/admin/grades/bulk-upload/', {})
        self.assertEqual(r2.status_code, status.HTTP_404_NOT_FOUND)
