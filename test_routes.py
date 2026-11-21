import os
import django
import json
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edugrade.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import UserProfile, SemesterRecord, CourseResult, AdvisorChatMessage, AcademicAuditLog

def run_all_tests():
    uid = uuid.uuid4().hex[:8]
    student_user = f"test_student_{uid}"
    student_pass = f"Pass_{uid}_123!"
    admin_user = f"test_admin_{uid}"
    admin_pass = f"Admin_{uid}_123!"

    # Create temporary isolated test users
    s_user = User.objects.create_user(username=student_user, password=student_pass, first_name="Test", last_name="Student")
    s_profile = UserProfile.objects.create(
        user=s_user,
        role="student",
        roll_number=f"ROLL{uid[:6].upper()}",
        department="Computer Science & Engineering",
        current_semester=5,
        current_cgpa=8.20,
        target_cgpa=9.00,
        credits_earned=90,
        total_credits=160,
        backlogs_count=0,
        is_placement_eligible=True
    )
    s_sem = SemesterRecord.objects.create(student=s_profile, semester_number=4, sgpa=8.20, credits_earned=20, is_published=True)
    CourseResult.objects.create(
        student=s_profile,
        semester_record=s_sem,
        semester_number=4,
        course_code="CS8401",
        course_name="Operating Systems",
        credits=3,
        grade="A",
        grade_point=8.0,
        is_published=True
    )

    a_user = User.objects.create_user(username=admin_user, password=admin_pass, first_name="Test", last_name="Admin", is_staff=True, is_superuser=True)
    a_profile = UserProfile.objects.create(
        user=a_user,
        role="admin",
        roll_number=f"FAC{uid[:6].upper()}",
        department="Computer Science & Engineering"
    )

    client = Client()

    try:
        # 1. Test Student Login (Form post)
        print(f"Testing Student Session Login ({student_user})...")
        resp = client.post('/login/', {'username': student_user, 'password': student_pass, 'role': 'student'})
        assert resp.status_code == 302, f"Expected 302 on login, got {resp.status_code}"
        assert resp.headers.get('Location') in ['/dashboard/', 'dashboard/']

        resp_dash = client.get('/dashboard/')
        assert resp_dash.status_code == 200
        print("[PASS] Student session login and dashboard verified.")

        # 2. Test Modern REST API Endpoints with Authenticated Student Session
        print("\nTesting Modern REST API endpoints (Student)...")
        me_resp = client.get('/api/auth/me/')
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data['authenticated'] is True
        assert me_data['profile']['role'] == 'student'
        print("[PASS] /api/auth/me/ returned student profile.")

        dash_resp = client.get('/api/students/dashboard/')
        assert dash_resp.status_code == 200
        dash_data = dash_resp.json()
        assert 'student' in dash_data
        assert float(dash_data['student']['current_cgpa']) > 0
        print(f"[PASS] /api/students/dashboard/ verified (CGPA={dash_data['student']['current_cgpa']}, Semesters={len(dash_data['semesters'])}).")

        results_resp = client.get('/api/academics/results/')
        assert results_resp.status_code == 200
        results_data = results_resp.json()
        assert len(results_data['semesters']) >= 1
        print(f"[PASS] /api/academics/results/ verified ({len(results_data['semesters'])} semesters).")

        # CGPA Planner API
        plan_resp = client.post('/api/planner/cgpa/', data=json.dumps({
            'current_cgpa': 8.20,
            'completed_credits': 90,
            'target_cgpa': 8.60,
            'remaining_semesters': 3,
            'total_credits': 160
        }), content_type='application/json')
        assert plan_resp.status_code == 200
        plan_data = plan_resp.json()
        assert plan_data['is_achievable'] is True
        assert plan_data['required_average_sgpa'] is not None
        print(f"[PASS] /api/planner/cgpa/ verified (Required SGPA={plan_data['required_average_sgpa']}).")

        # Placement Eligibility API
        place_resp = client.get('/api/placements/eligibility/')
        assert place_resp.status_code == 200
        place_data = place_resp.json()
        print(f"[PASS] /api/placements/eligibility/ verified ({place_data['summary']['eligible_companies']}/{place_data['summary']['total_companies']} eligible).")

        # AI Advisor API
        ai_resp = client.post('/api/advisor/chat/', data=json.dumps({
            'message': 'What is my plan for reaching 9.0 CGPA?'
        }), content_type='application/json')
        assert ai_resp.status_code == 200
        ai_data = ai_resp.json()
        assert 'reply' in ai_data and len(ai_data['reply']) > 10
        print(f"[PASS] /api/advisor/chat/ verified (AI reply received, source={ai_data.get('source')}).")

        # Arrears API
        arrears_resp = client.get('/api/student/arrears/')
        assert arrears_resp.status_code == 200
        assert 'active' in arrears_resp.json()
        print("[PASS] /api/student/arrears/ verified.")

        # PDF Transcript API
        pdf_resp = client.get('/api/transcript/pdf/')
        assert pdf_resp.status_code == 200
        assert pdf_resp['Content-Type'] == 'application/pdf'
        assert pdf_resp.content.startswith(b'%PDF')
        print("[PASS] /api/transcript/pdf/ verified (PDF generated).")

        # Clear Advisor Chat History API (DELETE)
        del_chat_resp = client.delete('/api/advisor/history/')
        assert del_chat_resp.status_code == 200
        print("[PASS] DELETE /api/advisor/history/ verified.")

        # Role Protection Check: Student should NOT access faculty endpoint
        fac_forbidden = client.get('/api/faculty/overview/')
        assert fac_forbidden.status_code == 403
        print("[PASS] Security Check: Student forbidden from /api/faculty/overview/ (HTTP 403).")

        fac_analytics_forbidden = client.get('/api/admin/analytics/')
        assert fac_analytics_forbidden.status_code == 403
        print("[PASS] Security Check: Student forbidden from /api/admin/analytics/ (HTTP 403).")

        client.logout()

        # 3. Test Admin REST APIs
        print(f"\nTesting Faculty / Admin Login & APIs ({admin_user})...")
        admin_login_resp = client.post('/api/auth/login/', data=json.dumps({
            'username': admin_user,
            'password': admin_pass,
            'role': 'admin'
        }), content_type='application/json')
        assert admin_login_resp.status_code == 200
        assert admin_login_resp.json()['is_admin'] is True

        fac_overview = client.get('/api/faculty/overview/')
        assert fac_overview.status_code == 200
        fac_data = fac_overview.json()
        assert fac_data['metrics']['total_students'] >= 1
        print(f"[PASS] /api/faculty/overview/ verified (Total Students={fac_data['metrics']['total_students']}).")

        fac_students = client.get('/api/faculty/students/')
        assert fac_students.status_code == 200
        assert len(fac_students.json()['students']) >= 1
        print(f"[PASS] /api/faculty/students/ verified ({len(fac_students.json()['students'])} students retrieved).")

        # Sample CSV Template API
        sample_csv_resp = client.get('/api/admin/grades/sample-csv/')
        assert sample_csv_resp.status_code == 200
        assert sample_csv_resp['Content-Type'] == 'text/csv'
        print("[PASS] /api/admin/grades/sample-csv/ verified.")

        # Admin Analytics API
        analytics_resp = client.get('/api/admin/analytics/')
        assert analytics_resp.status_code == 200
        analytics_data = analytics_resp.json()
        assert 'grade_distribution' in analytics_data
        assert 'at_risk_students' in analytics_data
        print(f"[PASS] /api/admin/analytics/ verified ({len(analytics_data['at_risk_students'])} at-risk students flagged).")

        # Health API
        health_resp = client.get('/api/health/')
        assert health_resp.status_code == 200
        assert health_resp.json()['status'] == 'healthy'
        print("[PASS] /api/health/ verified.")

        # 4. Test .html legacy alias routes
        print("\nTesting .html legacy alias routes...")
        assert client.get('/dashboard.html').status_code == 200
        assert client.get('/admin_dashboard.html').status_code == 200
        assert client.get('/upload.html').status_code == 200
        assert client.get('/cgpa_planner.html').status_code == 200
        assert client.get('/placement.html').status_code == 200
        assert client.get('/ai_advisor.html').status_code == 200
        print("[PASS] All legacy .html routes verified.")

        print("\n===========================================================")
        print("ALL ROUTE, AUTH, API, AND PERMISSION TESTS PASSED (100% OK)")
        print("===========================================================")

    finally:
        # Clean up temporary users and records
        CourseResult.objects.filter(student=s_profile).delete()
        SemesterRecord.objects.filter(student=s_profile).delete()
        AdvisorChatMessage.objects.filter(user__in=[s_user, a_user]).delete()
        AcademicAuditLog.objects.filter(action_by__in=[s_user, a_user]).delete()
        s_profile.delete()
        a_profile.delete()
        s_user.delete()
        a_user.delete()

if __name__ == '__main__':
    run_all_tests()
