"""
Automated Unit Tests for Groq Cloud AI Academic Advisor Integration.
Verifies Groq request payload, privacy redactions, fallback mechanisms,
error resilience, and offline execution via unittest.mock.
"""

import os
import json
import io
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import UserProfile, CourseResult, AdvisorChatMessage
from core.services.ai_service import generate_ai_advice


class GroqAdvisorIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="groq_student",
            password="secretpassword",
            first_name="Ananya",
            last_name="Rajan",
            email="ananya.rajan@university.edu"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            roll_number="REG2026888",
            department="Computer Science & Engineering",
            current_semester=6,
            current_cgpa=8.25,
            target_cgpa=9.00,
            credits_earned=110,
            backlogs_count=0
        )
        # Create course results
        CourseResult.objects.create(
            student=self.profile,
            semester_number=5,
            course_code="CS8501",
            course_name="Theory of Computation",
            credits=3,
            grade="C",
            grade_point=5.0
        )
        CourseResult.objects.create(
            student=self.profile,
            semester_number=5,
            course_code="CS8591",
            course_name="Computer Networks",
            credits=3,
            grade="A+",
            grade_point=9.0
        )
        # Seed 8 chat messages to verify max-6 history truncation
        for i in range(8):
            AdvisorChatMessage.objects.create(
                user=self.user,
                sender="user" if i % 2 == 0 else "ai",
                message=f"History message {i+1}"
            )

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345', 'GROQ_MODEL': 'llama-3.3-70b-versatile'})
    def test_groq_success_calls_correct_endpoint_and_headers(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [
                {
                    "message": {
                        "content": "Focus on Theory of Computation fundamentals to lift your CGPA."
                    }
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = generate_ai_advice(self.profile, "How can I improve my CGPA?")

        self.assertEqual(result['source'], 'groq')
        self.assertIn("Theory of Computation", result['response'])

        # Verify request details
        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.full_url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(req.headers.get("Authorization"), "Bearer gsk_mock_test_key_12345")
        self.assertEqual(req.headers.get("Content-type"), "application/json")

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345', 'GROQ_MODEL': 'llama-3.3-70b-versatile'})
    def test_payload_system_role_and_privacy_guarantees(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "Tailored guidance."}}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        generate_ai_advice(self.profile, "Tell me about my grades")

        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode('utf-8'))

        messages = payload.get('messages', [])
        self.assertGreaterEqual(len(messages), 2)

        # First message must be system role
        self.assertEqual(messages[0]['role'], 'system')
        system_content = messages[0]['content']

        # Privacy checks: Must NOT contain student PII
        self.assertNotIn("Ananya", system_content)
        self.assertNotIn("Rajan", system_content)
        self.assertNotIn("REG2026888", system_content)
        self.assertNotIn("ananya.rajan@university.edu", system_content)
        self.assertNotIn("groq_student", system_content)
        self.assertNotIn("secretpassword", system_content)

        # Academic context MUST be present
        self.assertIn("Computer Science & Engineering", system_content)
        self.assertIn("8.25", system_content)
        self.assertIn("CS8501", system_content)

        # History: max 6 messages + 1 system + 1 new user message = 8 messages
        self.assertEqual(len(messages), 8)
        # History messages must alternate roles
        self.assertEqual(messages[1]['role'], 'user')
        self.assertEqual(messages[1]['content'], 'History message 3')  # Oldest of the last 6
        self.assertEqual(messages[6]['content'], 'History message 8')
        self.assertEqual(messages[7]['role'], 'user')
        self.assertEqual(messages[7]['content'], 'Tell me about my grades')

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345'})
    def test_groq_http_401_falls_back_cleanly(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=401,
            msg="Unauthorized: Invalid API Key",
            hdrs={},
            fp=io.BytesIO(b'{"error": "invalid_api_key"}')
        )

        result = generate_ai_advice(self.profile, "How can I prepare for placements?")
        self.assertEqual(result['source'], 'rule_based')
        self.assertTrue(len(result['response']) > 10)

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345'})
    def test_groq_http_429_rate_limit_falls_back(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=429,
            msg="Rate limit exceeded",
            hdrs={},
            fp=io.BytesIO(b'{"error": "rate_limit"}')
        )

        result = generate_ai_advice(self.profile, "How can I raise my CGPA?")
        self.assertEqual(result['source'], 'rule_based')
        self.assertIn("CGPA", result['response'])

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345'})
    def test_groq_http_500_server_error_falls_back(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=io.BytesIO(b'{"error": "server_down"}')
        )

        result = generate_ai_advice(self.profile, "Study plan for semester")
        self.assertEqual(result['source'], 'rule_based')

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345'})
    def test_groq_timeout_falls_back_cleanly(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError(reason="timed out")

        result = generate_ai_advice(self.profile, "What is my placement status?")
        self.assertEqual(result['source'], 'rule_based')

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_test_key_12345'})
    def test_groq_invalid_json_falls_back(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html>Bad Gateway</html>'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = generate_ai_advice(self.profile, "Hello")
        self.assertEqual(result['source'], 'rule_based')

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': ''})
    def test_no_keys_configured_makes_zero_http_calls(self, mock_urlopen):
        result = generate_ai_advice(self.profile, "Hello")
        self.assertEqual(result['source'], 'rule_based')
        mock_urlopen.assert_not_called()

    @patch('urllib.request.urlopen')
    @patch.dict(os.environ, {'GROQ_API_KEY': 'gsk_mock_super_secret_key_999'})
    def test_api_key_never_logged_or_exposed_in_response(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://api.groq.com/openai/v1/chat/completions",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=io.BytesIO(b'forbidden')
        )

        with self.assertLogs('core.services.ai_service', level='WARNING') as cm:
            result = generate_ai_advice(self.profile, "Help me plan")

        # Response must not contain key
        self.assertNotIn("gsk_mock_super_secret_key_999", result['response'])

        # Logs must not contain key
        combined_logs = " ".join(cm.output)
        self.assertNotIn("gsk_mock_super_secret_key_999", combined_logs)
        self.assertIn("HTTP 403", combined_logs)
