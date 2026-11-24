from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, TranscriptIssue
from core.services.transcript_service import (
    issue_or_reuse_transcript,
    verify_transcript_token,
    mask_name,
    mask_roll,
    compute_snapshot_hash,
    compute_signature,
)
from core.services.pdf_service import generate_transcript_pdf

class TranscriptVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='verified_student',
            email='secret_student@example.com',
            first_name='Naveenkumar',
            last_name='S',
            password='password123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
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
        self.assertEqual(res["masked_name"], "N****")
        self.assertEqual(res["masked_roll"], "******042")
        self.assertEqual(res["cgpa"], 8.75)

    def test_name_mask_length_identical_for_different_lengths(self):
        """A 3-letter name and a 20-letter name give the exact same mask length."""
        short_name = "Bob"
        long_name = "Bartholomew-Alexande"  # 20 chars
        mask_short = mask_name(short_name)
        mask_long = mask_name(long_name)
        self.assertEqual(mask_short, "B****")
        self.assertEqual(mask_long, "B****")
        self.assertEqual(len(mask_short), len(mask_long))
        self.assertEqual(len(mask_short), 5)

        # Empty name gives ****
        self.assertEqual(mask_name(""), "****")
        self.assertEqual(mask_name(None), "****")

    def test_roll_mask_length_identical_for_different_lengths(self):
        """The roll number mask length is the same (9 chars) for different lengths."""
        roll_11 = mask_roll("71762104042")  # 11 chars
        roll_5 = mask_roll("CS101")         # 5 chars
        roll_3 = mask_roll("101")           # 3 chars
        roll_2 = mask_roll("12")            # 2 chars
        roll_empty = mask_roll("")          # 0 chars

        self.assertEqual(roll_11, "******042")
        self.assertEqual(roll_5, "******101")
        self.assertEqual(roll_3, "******101")
        self.assertEqual(roll_2, "*********")
        self.assertEqual(roll_empty, "*********")

        self.assertEqual(len(roll_11), 9)
        self.assertEqual(len(roll_5), 9)
        self.assertEqual(len(roll_3), 9)
        self.assertEqual(len(roll_2), 9)
        self.assertEqual(len(roll_empty), 9)

    def test_old_style_snapshot_with_long_mask_verifies_and_displays_fixed_mask(self):
        """
        An old-style snapshot stored with the old long mask and valid signature
        still verifies as VALID and displays the new fixed-length mask.
        """
        # Create an old-style snapshot with old-style masks
        old_snapshot = {
            "student_id": self.profile.id,
            "masked_name": "K******",       # old 7-char mask
            "masked_roll": "********042",   # old 11-char mask
            "department": self.profile.department,
            "cgpa": 8.75,
            "credits_earned": 84,
            "backlogs": 0,
            "semester_count": 1,
            "issue_date": "2026-01-01",
        }
        old_hash = compute_snapshot_hash(old_snapshot)
        old_sig = compute_signature(old_hash)

        old_issue = TranscriptIssue.objects.create(
            student=self.profile,
            snapshot=old_snapshot,
            snapshot_hash=old_hash,
            signature=old_sig,
            is_revoked=False
        )

        res = verify_transcript_token(old_issue.token)
        self.assertTrue(res["is_valid"])
        self.assertEqual(res["status"], "VALID")
        # Display-time masking normalizes to fixed length
        self.assertEqual(res["masked_name"], "K****")
        self.assertEqual(res["masked_roll"], "******042")

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
        self.assertIn("******042", html_str)
        self.assertNotIn("student_id", html_str)

        resp_json = self.client.get(f'/api/verify/{issue.token}/')
        json_str = str(resp_json.data)
        self.assertNotIn("secret_student@example.com", json_str)
        self.assertNotIn("71762104042", json_str)
        self.assertIn("******042", json_str)
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
