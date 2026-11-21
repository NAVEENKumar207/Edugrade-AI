"""Tests for the AI academic advisor API, prompt generation, and chat persistence."""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult, AdvisorChatMessage, AcademicAuditLog
from core.services.ai_service import generate_ai_advice


class AIAdvisorImprovementsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Student 1
        self.student1_user = User.objects.create_user(username="advisor_student1", password="password123")
        self.student1_profile = UserProfile.objects.create(
            user=self.student1_user,
            role="student",
            roll_number="CS2026771",
            department="CSE",
            current_semester=5,
            current_cgpa=7.5,
            backlogs_count=0
        )

        # Student 2
        self.student2_user = User.objects.create_user(username="advisor_student2", password="password123")
        self.student2_profile = UserProfile.objects.create(
            user=self.student2_user,
            role="student",
            roll_number="CS2026772",
            department="ECE",
            current_semester=5,
            current_cgpa=8.0,
            backlogs_count=0
        )

        # Create sample courses for student 1 with a known weakest course
        CourseResult.objects.create(
            student=self.student1_profile,
            semester_number=4,
            course_code="CS8491",
            course_name="Computer Networks",
            credits=3,
            grade="O",
            grade_point=10.0
        )
        CourseResult.objects.create(
            student=self.student1_profile,
            semester_number=4,
            course_code="CS8451",
            course_name="Operating Systems",
            credits=3,
            grade="C",
            grade_point=5.0
        )

        # Seed chat messages for student 1 and student 2
        for i in range(8):
            AdvisorChatMessage.objects.create(
                user=self.student1_user,
                sender="user" if i % 2 == 0 else "ai",
                message=f"Student 1 message {i+1}"
            )

        AdvisorChatMessage.objects.create(
            user=self.student2_user,
            sender="user",
            message="Student 2 important message"
        )

    def test_clear_chat_history_deletes_only_calling_user(self):
        self.client.force_authenticate(user=self.student1_user)
        response = self.client.delete('/api/advisor/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Student 1's messages must be gone
        self.assertEqual(AdvisorChatMessage.objects.filter(user=self.student1_user).count(), 0)

        # Student 2's messages must remain untouched
        self.assertEqual(AdvisorChatMessage.objects.filter(user=self.student2_user).count(), 1)

        # Audit log must be created
        audit = AcademicAuditLog.objects.filter(
            action_by=self.student1_user,
            action_type="CLEAR_CHAT_HISTORY"
        ).first()
        self.assertIsNotNone(audit)

    def test_clear_chat_anonymous_unauthorized(self):
        response = self.client.delete('/api/advisor/history/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_weakest_subject_study_plan_english(self):
        result = generate_ai_advice(self.student1_profile, "Make a study plan for my weakest subject")
        reply = result['response']

        # Must identify Operating Systems (grade C) as weakest
        self.assertIn("Operating Systems", reply)
        self.assertIn("Week 1", reply)
        self.assertIn("Week 2", reply)
        self.assertIn("Week 3", reply)
        self.assertIn("Week 4", reply)
        self.assertEqual(result.get('language'), 'en')

    def test_weakest_subject_study_plan_tamil(self):
        result = generate_ai_advice(self.student1_profile, "எனது பலவீனமான பாடத்திற்கு ஒரு படிப்புத் திட்டம் உருவாக்கவும்")
        reply = result['response']

        self.assertIn("Operating Systems", reply)
        self.assertIn("வாரம் 1", reply)
        self.assertIn("வாரம் 2", reply)
        self.assertIn("வாரம் 3", reply)
        self.assertIn("வாரம் 4", reply)
        self.assertEqual(result.get('language'), 'ta')
