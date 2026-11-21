from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult, SemesterRecord


class PDFTranscriptTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin_user = User.objects.create_user(username="admin_pdf", password="password123")
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role="admin",
            department="CSE"
        )

        # Student 1
        self.student1_user = User.objects.create_user(username="student1", password="password123")
        self.student1_profile = UserProfile.objects.create(
            user=self.student1_user,
            role="student",
            roll_number="CS2026111",
            department="Computer Science",
            current_semester=4,
            current_cgpa=8.5,
            credits_earned=60,
            backlogs_count=0,
            is_placement_eligible=True
        )
        # Add a semester and courses
        self.sem1 = SemesterRecord.objects.create(
            student=self.student1_profile,
            semester_number=1,
            sgpa=8.5,
            credits_earned=20,
            is_published=True
        )
        CourseResult.objects.create(
            student=self.student1_profile,
            semester_record=self.sem1,
            semester_number=1,
            course_code="CS8101",
            course_name="Programming in C",
            credits=3,
            grade="A+",
            grade_point=9.0
        )

        # Student 2
        self.student2_user = User.objects.create_user(username="student2", password="password123")
        self.student2_profile = UserProfile.objects.create(
            user=self.student2_user,
            role="student",
            roll_number="CS2026222",
            department="Information Tech",
            current_semester=2,
            current_cgpa=7.2,
            credits_earned=20,
            backlogs_count=0,
            is_placement_eligible=True
        )

    def test_student_can_download_own_transcript(self):
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get('/api/transcript/pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.assertIn('attachment; filename="transcript_CS2026111.pdf"', response['Content-Disposition'])

    def test_student_download_filtered_semester(self):
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.get('/api/transcript/pdf/?semester=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_student_forbidden_from_other_student_transcript(self):
        self.client.force_authenticate(user=self.student1_user)
        # Attempt to access student2's transcript
        response = self.client.get(f'/api/transcript/pdf/?student_id={self.student2_profile.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("own transcript", response.data['error'])

    def test_anonymous_unauthorized(self):
        response = self.client.get('/api/transcript/pdf/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_faculty_admin_can_access_any_student_transcript(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/transcript/pdf/?student_id={self.student1_profile.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.assertIn('attachment; filename="transcript_CS2026111.pdf"', response['Content-Disposition'])

    def test_empty_student_transcript(self):
        self.client.force_authenticate(user=self.student2_user)
        # Student 2 has no CourseResult objects
        response = self.client.get('/api/transcript/pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
