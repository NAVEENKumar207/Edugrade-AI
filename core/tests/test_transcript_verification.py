from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, TranscriptIssue
from core.services.transcript_service import issue_or_reuse_transcript, verify_transcript_token
from core.services.pdf_service import generate_transcript_pdf

class TranscriptVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='verified_student',
            email='secret_student@example.com',
            first_name='Kavitha',
            last_name='',
            password='password123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='student',
            roll_number='71762104042',
            department='Computer Science & Engineering',
            current_cgpa=8.75,
            credits_earned=84,
            backlogs_count=0
        )
        SemesterRecord.objects.create(student=self.profile, semester_number=1, sgpa=8.75, credits_earned=20)

    def test_valid_transcript_verifies_successfully(self):
        issue = issue_or_reuse_transcript(self.profile)
        res = verify_transcript_token(issue.token)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["status"], "VALID")
        self.assertEqual(res["masked_name"], "K******")
        self.assertEqual(res["masked_roll"], "********042")
        self.assertEqual(res["cgpa"], 8.75)

    def test_altering_stored_snapshot_makes_it_invalid(self):
        issue = issue_or_reuse_transcript(self.profile)
        # Tamper with snapshot in DB
        issue.snapshot["cgpa"] = 9.99
        issue.save()

        res = verify_transcript_token(issue.token)
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "NOT VALID")
        self.assertIn("altered", res["reason"].lower())

    def test_revoked_transcript_is_invalid(self):
        issue = issue_or_reuse_transcript(self.profile)
        issue.is_revoked = True
        issue.save()

        res = verify_transcript_token(issue.token)
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "NOT VALID")
        self.assertIn("revoked", res["reason"].lower())

    def test_unknown_token_returns_not_valid_page_without_crashing(self):
        resp_html = self.client.get('/verify/non-existent-token-12345/')
        self.assertEqual(resp_html.status_code, 404)
        self.assertIn("NOT VALID", resp_html.content.decode('utf-8'))

        resp_json = self.client.get('/api/verify/non-existent-token-12345/')
        self.assertEqual(resp_json.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(resp_json.data["is_valid"])

    def test_page_and_json_contain_no_email_and_no_full_roll_number(self):
        issue = issue_or_reuse_transcript(self.profile)

        resp_html = self.client.get(f'/verify/{issue.token}/')
        html_str = resp_html.content.decode('utf-8')
        self.assertNotIn("secret_student@example.com", html_str)
        self.assertNotIn("71762104042", html_str)
        self.assertIn("********042", html_str)

        resp_json = self.client.get(f'/api/verify/{issue.token}/')
        json_str = str(resp_json.data)
        self.assertNotIn("secret_student@example.com", json_str)
        self.assertNotIn("71762104042", json_str)
        self.assertNotIn("student_id", resp_json.data)

    def test_downloading_twice_without_changes_reuses_one_transcript_issue(self):
        self.assertEqual(TranscriptIssue.objects.count(), 0)
        issue1 = issue_or_reuse_transcript(self.profile)
        self.assertEqual(TranscriptIssue.objects.count(), 1)

        issue2 = issue_or_reuse_transcript(self.profile)
        self.assertEqual(TranscriptIssue.objects.count(), 1)
        self.assertEqual(issue1.token, issue2.token)

    def test_pdf_transcript_contains_pdf_header_and_token_text(self):
        pdf_bytes = generate_transcript_pdf(self.profile)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

        # Token text must be present in the generated PDF bytes
        issue = TranscriptIssue.objects.filter(student=self.profile).first()
        self.assertIsNotNone(issue)
        self.assertIn(issue.token.encode('ascii'), pdf_bytes)
