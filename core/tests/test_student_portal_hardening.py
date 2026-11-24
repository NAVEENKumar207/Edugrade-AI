"""
Student-Only Portal Hardening & Audit Verification Tests.
Verifies:
1. PUT/DELETE on another student's course result returns 404 or 403.
2. Signup with a legacy 'role' payload field still creates a normal student.
3. SGPA, CGPA, credits, backlogs, and eligibility recalculate correctly after Add, Edit, Delete, and CSV Import.
4. Trend Alert early warning thresholds (CGPA, backlogs, predicted SGPA, SGPA drop).
5. AcademicAuditLog rows are created for every student-initiated action.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    UserProfile, SemesterRecord, CourseResult,
    CompanyPlacementCriteria, AcademicAuditLog, AdvisorChatMessage
)
from core.services.journey_service import (
    evaluate_student_risk, predict_next_sgpa,
    RISK_HIGH_CGPA, RISK_HIGH_BACKLOGS, RISK_HIGH_PREDICTED_SGPA,
    RISK_MEDIUM_SGPA_DROP, RISK_MEDIUM_BACKLOGS
)


class StudentPortalHardeningTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Student 1
        self.u1 = User.objects.create_user(username='student_alpha', password='password123')
        self.p1 = UserProfile.objects.create(
            user=self.u1,
            roll_number='717622CS001',
            department='Computer Science & Engineering',
            current_semester=4,
            current_cgpa=8.00,
            target_cgpa=9.00,
            credits_earned=60,
            total_credits=160,
            backlogs_count=0,
            is_placement_eligible=True
        )
        self.s1_sem1 = SemesterRecord.objects.create(student=self.p1, semester_number=1, sgpa=8.00, credits_earned=20)
        self.c1 = CourseResult.objects.create(
            student=self.p1,
            semester_record=self.s1_sem1,
            semester_number=1,
            course_code='CS101',
            course_name='Programming Fundamentals',
            credits=4,
            grade='A',
            grade_point=8.0
        )

        # Student 2
        self.u2 = User.objects.create_user(username='student_beta', password='password123')
        self.p2 = UserProfile.objects.create(
            user=self.u2,
            roll_number='717622CS002',
            department='Computer Science & Engineering',
            current_semester=4,
            current_cgpa=7.50,
            target_cgpa=8.50,
            credits_earned=60,
            total_credits=160,
            backlogs_count=0,
            is_placement_eligible=True
        )
        self.s2_sem1 = SemesterRecord.objects.create(student=self.p2, semester_number=1, sgpa=7.50, credits_earned=20)
        self.c2 = CourseResult.objects.create(
            student=self.p2,
            semester_record=self.s2_sem1,
            semester_number=1,
            course_code='CS102',
            course_name='Discrete Mathematics',
            credits=4,
            grade='B+',
            grade_point=7.0
        )

        # Company criterion for placement eligibility checks
        CompanyPlacementCriteria.objects.create(
            company_name='Target Placement Corp',
            role_title='Software Engineer',
            min_cgpa=7.00,
            max_backlogs=0,
            package_lpa=8.00,
            is_active=True
        )

    # -------------------------------------------------------------
    # 1. Isolation Tests: PUT / DELETE on foreign student's result
    # -------------------------------------------------------------
    def test_put_on_another_student_result_forbidden_or_not_found(self):
        """Student 1 attempting to PUT student 2's course result returns 404/403."""
        self.client.force_authenticate(user=self.u1)
        resp = self.client.put(
            f'/api/academics/results/{self.c2.id}/',
            {'grade': 'O'},
            format='json'
        )
        self.assertIn(resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

        # Assert no change in student 2's course
        self.c2.refresh_from_db()
        self.assertEqual(self.c2.grade, 'B+')

    def test_delete_on_another_student_result_forbidden_or_not_found(self):
        """Student 1 attempting to DELETE student 2's course result returns 404/403."""
        self.client.force_authenticate(user=self.u1)
        resp = self.client.delete(f'/api/academics/results/{self.c2.id}/')
        self.assertIn(resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])

        # Assert student 2's course is NOT deleted
        self.assertTrue(CourseResult.objects.filter(id=self.c2.id).exists())

    # -------------------------------------------------------------
    # 2. Signup with a "role" field still creates a normal student
    # -------------------------------------------------------------
    def test_signup_with_role_payload_creates_normal_student(self):
        """Passing 'role': 'admin' or 'faculty' in signup payload creates a student without staff privileges."""
        resp = self.client.post('/api/auth/signup/', {
            'username': 'attempted_admin_signup',
            'password': 'SafePassword123!',
            'confirm_password': 'SafePassword123!',
            'fullname': 'Attempted Admin',
            'department': 'Computer Science & Engineering',
            'roll_number': '717622CS991',
            'semester': 1,
            'role': 'admin'  # Should be ignored completely
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created_user = User.objects.get(username='attempted_admin_signup')
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)
        self.assertTrue(hasattr(created_user, 'profile'))
        self.assertEqual(created_user.profile.roll_number, '717622CS991')

    def test_signup_stores_syllabus_regulation_and_exposes_in_me_api(self):
        """Student registration accepts syllabus regulation and exposes it in profile and /api/auth/me/."""
        resp = self.client.post('/api/auth/signup/', {
            'username': 'student_syllabus_test',
            'password': 'SyllabusPass123!',
            'confirm_password': 'SyllabusPass123!',
            'fullname': 'Syllabus Test Student',
            'department': 'Computer Science and Business Systems',
            'roll_number': '717624CB088',
            'syllabus_regulation': 'Regulation 2022 (R2022 Autonomous CBCS)',
            'semester': 3
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='student_syllabus_test')
        self.assertEqual(user.profile.syllabus_regulation, 'Regulation 2022 (R2022 Autonomous CBCS)')
        self.assertEqual(user.profile.current_semester, 3)

        # Call /api/auth/me/ to verify syllabus_regulation is returned
        self.client.force_authenticate(user=user)
        me_resp = self.client.get('/api/auth/me/')
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        me_data = me_resp.json()
        self.assertEqual(me_data['profile']['syllabus_regulation'], 'Regulation 2022 (R2022 Autonomous CBCS)')

    # -------------------------------------------------------------
    # 3. Recalculation across Add, Edit, Delete, and CSV Import
    # -------------------------------------------------------------
    def test_recalculation_after_add_edit_delete_and_csv_import(self):
        """Verifies SGPA, CGPA, credits, backlogs, and eligibility recalculate correctly across all operations."""
        self.client.force_authenticate(user=self.u1)

        # A. ADD Course
        add_resp = self.client.post('/api/academics/results/', {
            'semester_number': 1,
            'course_code': 'CS103',
            'course_name': 'Data Structures',
            'credits': 4,
            'grade': 'U'  # Arrear introduced
        }, format='json')
        self.assertEqual(add_resp.status_code, status.HTTP_201_CREATED)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.backlogs_count, 1)
        self.assertFalse(self.p1.is_placement_eligible)  # Backlogs > 0 violates criteria
        added_id = add_resp.data['course']['id']

        # B. EDIT Course (Clear arrear by updating grade to A)
        edit_resp = self.client.put(f'/api/academics/results/{added_id}/', {
            'grade': 'A'
        }, format='json')
        self.assertEqual(edit_resp.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.backlogs_count, 0)
        self.assertTrue(self.p1.is_placement_eligible)

        # C. DELETE Course
        del_resp = self.client.delete(f'/api/academics/results/{added_id}/')
        self.assertEqual(del_resp.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.backlogs_count, 0)

        # D. CSV IMPORT
        csv_payload = (
            "semester,course_code,course_name,credits,grade\n"
            "2,CS201,Database Management Systems,4,O\n"
            "2,CS202,Operating Systems,4,A+\n"
        )
        import_resp = self.client.post('/api/academics/results/import/', {
            'csv_text': csv_payload
        }, format='json')
        self.assertEqual(import_resp.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        # Initial course CS101: 4 cred * 8.0 = 32.
        # Imported CS201: 4 cred * 10.0 = 40.
        # Imported CS202: 4 cred * 9.0 = 36.
        # Total points = 108. Total credits = 12. CGPA = 108 / 12 = 9.00.
        self.assertAlmostEqual(float(self.p1.current_cgpa), 9.00, places=2)
        self.assertEqual(self.p1.credits_earned, 12)
        self.assertEqual(self.p1.backlogs_count, 0)
        self.assertTrue(self.p1.is_placement_eligible)

    # -------------------------------------------------------------
    # 4. Trend Alert Thresholds Tests
    # -------------------------------------------------------------
    def test_trend_alert_high_risk_thresholds(self):
        """Verifies high risk triggers on CGPA < 6.0, backlogs >= 2, or predicted SGPA < 5.5."""
        # High Risk via CGPA < 6.0
        self.p1.current_cgpa = 5.80
        self.p1.backlogs_count = 0
        risk_res = evaluate_student_risk(self.p1, prefetched_semesters=[])
        self.assertEqual(risk_res['risk_level'], 'high')
        self.assertTrue(any('CGPA' in r for r in risk_res['reasons']))

        # High Risk via backlogs >= 2
        self.p1.current_cgpa = 8.00
        self.p1.backlogs_count = RISK_HIGH_BACKLOGS
        risk_res = evaluate_student_risk(self.p1, prefetched_semesters=[])
        self.assertEqual(risk_res['risk_level'], 'high')
        self.assertTrue(any('arrear' in r for r in risk_res['reasons']))

    def test_trend_alert_medium_risk_thresholds(self):
        """Verifies medium risk triggers on 1 backlog or last semester SGPA drop >= 1.0."""
        # Medium Risk via 1 backlog
        self.p1.current_cgpa = 8.00
        self.p1.backlogs_count = RISK_MEDIUM_BACKLOGS
        risk_res = evaluate_student_risk(self.p1, prefetched_semesters=[])
        self.assertEqual(risk_res['risk_level'], 'medium')

        # Medium Risk via SGPA drop >= 1.0
        self.p1.current_cgpa = 8.00
        self.p1.backlogs_count = 0
        sem1 = SemesterRecord(student=self.p1, semester_number=1, sgpa=8.50, credits_earned=20)
        sem2 = SemesterRecord(student=self.p1, semester_number=2, sgpa=7.30, credits_earned=20)  # drop of 1.20 >= 1.0
        risk_res = evaluate_student_risk(self.p1, prefetched_semesters=[sem1, sem2])
        self.assertEqual(risk_res['risk_level'], 'medium')
        self.assertTrue(any('fell' in r for r in risk_res['reasons']))

    def test_trend_alert_low_risk_standing(self):
        """Verifies low risk standing with steady or improving SGPA and no backlogs."""
        self.p1.current_cgpa = 8.50
        self.p1.backlogs_count = 0
        sem1 = SemesterRecord(student=self.p1, semester_number=1, sgpa=8.00, credits_earned=20)
        sem2 = SemesterRecord(student=self.p1, semester_number=2, sgpa=8.50, credits_earned=20)
        risk_res = evaluate_student_risk(self.p1, prefetched_semesters=[sem1, sem2])
        self.assertEqual(risk_res['risk_level'], 'low')
        self.assertEqual(risk_res['trend'], 'improving')

    # -------------------------------------------------------------
    # 5. AcademicAuditLog rows created for every student action
    # -------------------------------------------------------------
    def test_audit_logs_created_for_all_student_actions(self):
        """Verifies that AcademicAuditLog records are created on Add, Edit, Delete, CSV, Chat Clear, and Password Change."""
        self.client.force_authenticate(user=self.u1)
        initial_log_count = AcademicAuditLog.objects.count()

        # Action A: Add Course Result
        add_res = self.client.post('/api/academics/results/', {
            'semester_number': 1,
            'course_code': 'AUD101',
            'course_name': 'Audit Subject',
            'credits': 3,
            'grade': 'A'
        }, format='json')
        self.assertEqual(add_res.status_code, status.HTTP_201_CREATED)
        c_id = add_res.data['course']['id']
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='SINGLE_RESULT_ENTRY', action_by=self.u1).exists())

        # Action B: Edit Course Result
        edit_res = self.client.put(f'/api/academics/results/{c_id}/', {'grade': 'A+'}, format='json')
        self.assertEqual(edit_res.status_code, status.HTTP_200_OK)
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='COURSE_RESULT_UPDATED', action_by=self.u1).exists())

        # Action C: Delete Course Result
        del_res = self.client.delete(f'/api/academics/results/{c_id}/')
        self.assertEqual(del_res.status_code, status.HTTP_200_OK)
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='COURSE_RESULT_DELETED', action_by=self.u1).exists())

        # Action D: CSV Import
        csv_text = "semester,course_code,course_name,credits,grade\n3,AUD201,Audit CSV,3,O\n"
        imp_res = self.client.post('/api/academics/results/import/', {'csv_text': csv_text}, format='json')
        self.assertEqual(imp_res.status_code, status.HTTP_200_OK)
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='STUDENT_CSV_IMPORT', action_by=self.u1).exists())

        # Action E: Clear AI Advisor Chat History
        AdvisorChatMessage.objects.create(user=self.u1, sender='user', message='Hello Advisor')
        clear_res = self.client.delete('/api/advisor/history/')
        self.assertEqual(clear_res.status_code, status.HTTP_200_OK)
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='CLEAR_CHAT_HISTORY', action_by=self.u1).exists())

        # Action F: Change Password
        pwd_res = self.client.post('/api/auth/change-password/', {
            'old_password': 'password123',
            'new_password': 'NewPassword789!',
            'confirm_password': 'NewPassword789!'
        }, format='json')
        self.assertEqual(pwd_res.status_code, status.HTTP_200_OK)
        self.assertTrue(AcademicAuditLog.objects.filter(action_type='Password changed', action_by=self.u1).exists())

        # Total new audit logs created should be at least 6
        final_log_count = AcademicAuditLog.objects.count()
        self.assertGreaterEqual(final_log_count - initial_log_count, 6)

    # -------------------------------------------------------------
    # 6. CSV Import & Export Hardening (Max 1MB, Max 500 rows, UTF-8, Formula Injection)
    # -------------------------------------------------------------
    def test_csv_import_exceeds_1mb_rejected(self):
        """CSV file upload or text exceeding 1 MB is rejected with HTTP 400."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.u1)

        large_payload = "semester,course_code,course_name,credits,grade\n" + ("1,CS101,Subject,3,A\n" * 60000)
        large_bytes = large_payload.encode('utf-8')
        self.assertGreater(len(large_bytes), 1024 * 1024)

        uploaded = SimpleUploadedFile("oversized.csv", large_bytes, content_type="text/csv")
        resp = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("1MB", resp.data.get('error', ''))

    def test_csv_import_exceeds_500_rows_rejected(self):
        """CSV containing more than 500 data rows is rejected with HTTP 400."""
        self.client.force_authenticate(user=self.u1)

        rows = ["semester,course_code,course_name,credits,grade"]
        for i in range(1, 502):
            rows.append(f"1,CS{i:04d},Course Name {i},3,A")
        csv_text = "\n".join(rows)

        resp = self.client.post('/api/academics/results/import/', {'csv_text': csv_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("500 rows", resp.data.get('error', ''))

    def test_csv_import_non_utf8_rejected(self):
        """Non-UTF-8 encoded CSV file upload is rejected with HTTP 400."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.force_authenticate(user=self.u1)

        # Latin-1 bytes that are invalid in UTF-8
        bad_bytes = b"semester,course_code,course_name,credits,grade\n1,CS101,Caf\xe9 Math,3,A\n\xff\xfe"
        uploaded = SimpleUploadedFile("invalid_encoding.csv", bad_bytes, content_type="text/csv")
        resp = self.client.post('/api/academics/results/import/', {'file': uploaded}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("UTF-8", resp.data.get('error', ''))

    def test_csv_import_rejects_invalid_grades_and_credits(self):
        """Invalid grades and non-integer/out-of-bounds credits are skipped with descriptive errors."""
        self.client.force_authenticate(user=self.u1)
        csv_text = (
            "semester,course_code,course_name,credits,grade\n"
            "1,CS111,Invalid Grade Subject,3,INVALID_GRADE\n"
            "1,CS112,Fractional Credits,3.5,A\n"
            "1,CS113,Zero Credits,0,A\n"
            "1,CS114,Excessive Credits,15,A\n"
            "1,CS115,Negative Credits,-4,A\n"
            "1,CS116,Valid Course,3,O\n"
        )
        resp = self.client.post('/api/academics/results/import/', {'csv_text': csv_text}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['saved'], 1)
        self.assertEqual(len(resp.data['errors']), 5)
        # Check reasons
        reasons = " ".join([e['reason'] for e in resp.data['errors']])
        self.assertIn("Invalid grade", reasons)
        self.assertIn("Credits must be an integer between 1 and 10", reasons)

    def test_csv_export_sanitizes_formula_injection(self):
        """Exported CSV cells starting with '=', '+', '-', or '@' are prefixed with a quote."""
        from core.services.academic_service import export_student_grades_csv, sanitize_csv_cell
        self.assertEqual(sanitize_csv_cell("=CMD('calc')"), "'=CMD('calc')")
        self.assertEqual(sanitize_csv_cell("+12345"), "'+12345")
        self.assertEqual(sanitize_csv_cell("-SOMETHING"), "'-SOMETHING")
        self.assertEqual(sanitize_csv_cell("@SUM(A1:A5)"), "'@SUM(A1:A5)")
        self.assertEqual(sanitize_csv_cell("Normal Text"), "Normal Text")

        # Create a course with potential formula characters
        CourseResult.objects.create(
            student=self.p1,
            semester_record=self.s1_sem1,
            semester_number=1,
            course_code="=INJ101",
            course_name="@ExcelFormula Course",
            credits=3,
            grade="A+",
            grade_point=9.0
        )
        csv_out = export_student_grades_csv(self.p1)
        self.assertIn("'=INJ101", csv_out)
        self.assertIn("'@ExcelFormula Course", csv_out)

        # Test endpoint
        self.client.force_authenticate(user=self.u1)
        resp = self.client.get('/api/academics/results/export-csv/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("'=INJ101", resp.content.decode('utf-8'))

    # -------------------------------------------------------------
    # 7. quick_demo_login Gated Behind settings.DEBUG
    # -------------------------------------------------------------
    def test_quick_demo_login_gated_by_debug(self):
        """quick_demo_login returns (None, err) when DEBUG=False, and succeeds when DEBUG=True."""
        from django.test import override_settings
        from ui.services.data_service import quick_demo_login

        with override_settings(DEBUG=False):
            demo_user, demo_err = quick_demo_login()
            self.assertIsNone(demo_user)
            self.assertIn("DEBUG=True", demo_err)

        with override_settings(DEBUG=True):
            demo_user, demo_err = quick_demo_login()
            self.assertIsNotNone(demo_user)
            self.assertIsNone(demo_err)
            self.assertIn(demo_user.username, ['demo_student', 'student01'])

    # -------------------------------------------------------------
    # 8. Prominent "SELF-REPORTED - NOT INSTITUTION VERIFIED" in Header
    # -------------------------------------------------------------
    def test_pdf_and_verify_page_header_displays_self_reported_notice(self):
        """Verifies that 'SELF-REPORTED - NOT INSTITUTION VERIFIED' is visible in PDF and verify page header."""
        from core.services.pdf_service import generate_transcript_pdf
        from core.services.transcript_service import issue_or_reuse_transcript

        # A. Check PDF header
        pdf_bytes = generate_transcript_pdf(self.p1)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
        self.assertIn(b"SELF-REPORTED - NOT INSTITUTION VERIFIED", pdf_bytes)

        # B. Check Verify HTML Page header
        issue = issue_or_reuse_transcript(self.p1)
        resp = self.client.get(f'/verify/{issue.token}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        html_content = resp.content.decode('utf-8')
        self.assertIn("SELF-REPORTED - NOT INSTITUTION VERIFIED", html_content)
