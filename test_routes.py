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

    # Create temporary isolated test student
    s_user = User.objects.create_user(username=student_user, password=student_pass, first_name="Test", last_name="Student")
    s_profile = UserProfile.objects.create(
        user=s_user,
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
    s_sem = SemesterRecord.objects.create(student=s_profile, semester_number=4, sgpa=8.20, credits_earned=20)
    cr = CourseResult.objects.create(
        student=s_profile,
        semester_record=s_sem,
        semester_number=4,
        course_code="CS8401",
        course_name="Operating Systems",
        credits=3,
        grade="A",
        grade_point=8.0
    )

    client = Client()

    try:
        # 1. Test Student Login (Form post)
        print(f"Testing Student Session Login ({student_user})...")
        resp = client.post('/login/', {'username': student_user, 'password': student_pass})
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
        assert me_data['profile']['roll_number'] == s_profile.roll_number
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

        # PDF Transcript API (Student isolation & PDF output)
        pdf_resp = client.get('/api/transcript/pdf/')
        assert pdf_resp.status_code == 200
        assert pdf_resp['Content-Type'] == 'application/pdf'
        assert pdf_resp.content.startswith(b'%PDF')
        print("[PASS] /api/transcript/pdf/ verified (PDF generated).")

        # Digital Twin & Tools APIs
        sim_resp = client.post('/api/twin/simulate/', data=json.dumps({
            'target_cgpa': 9.0,
            'effort': 'same'
        }), content_type='application/json')
        assert sim_resp.status_code == 200
        print("[PASS] /api/twin/simulate/ verified.")

        moves_resp = client.get('/api/twin/next-moves/')
        assert moves_resp.status_code == 200
        print("[PASS] /api/twin/next-moves/ verified.")

        skills_resp = client.get('/api/skills/')
        assert skills_resp.status_code == 200
        print("[PASS] /api/skills/ verified.")

        journey_resp = client.get('/api/journey/')
        assert journey_resp.status_code == 200
        assert len(journey_resp.json()['badges']['all_badges']) == 7
        print("[PASS] /api/journey/ verified (7 badges).")

        # Clear Advisor Chat History API (DELETE)
        del_chat_resp = client.delete('/api/advisor/history/')
        assert del_chat_resp.status_code == 200
        print("[PASS] DELETE /api/advisor/history/ verified.")

        # 3. Test Student Academic Results CRUD & CSV
        print("\nTesting Student-Owned Results CRUD & CSV APIs...")

        # Sample CSV template download
        sample_csv_resp = client.get('/api/academics/results/sample-csv/')
        assert sample_csv_resp.status_code == 200
        assert 'text/csv' in sample_csv_resp['Content-Type']
        assert 'semester,course_code,course_name,credits,grade' in sample_csv_resp.content.decode()
        print("[PASS] /api/academics/results/sample-csv/ verified.")

        # POST single course result
        create_res = client.post('/api/academics/results/', data=json.dumps({
            'semester_number': 4,
            'course_code': 'CS8402',
            'course_name': 'Database Management Systems',
            'credits': 3,
            'grade': 'B+'
        }), content_type='application/json')
        assert create_res.status_code in [200, 201]
        created_id = create_res.json()['course']['id']
        print(f"[PASS] POST /api/academics/results/ verified (Created id={created_id}).")

        # PUT single course result
        update_res = client.put(f'/api/academics/results/{created_id}/', data=json.dumps({
            'grade': 'A+'
        }), content_type='application/json')
        assert update_res.status_code == 200
        assert update_res.json()['course']['grade'] == 'A+'
        print(f"[PASS] PUT /api/academics/results/{created_id}/ verified.")

        # DELETE single course result
        delete_res = client.delete(f'/api/academics/results/{created_id}/')
        assert delete_res.status_code == 200
        print(f"[PASS] DELETE /api/academics/results/{created_id}/ verified.")

        # 4. Verify Deleted Faculty/Admin Endpoints return 404
        print("\nVerifying Deleted Faculty/Admin Endpoints return HTTP 404...")
        assert client.get('/api/faculty/overview/').status_code == 404
        assert client.get('/api/faculty/students/').status_code == 404
        assert client.post('/api/faculty/results/upload/').status_code == 404
        assert client.get('/api/admin/drives/').status_code == 404
        assert client.get('/api/admin/analytics/').status_code == 404
        assert client.get('/api/admin/grades/sample-csv/').status_code == 404
        assert client.post('/api/admin/grades/bulk-upload/').status_code == 404
        print("[PASS] All removed faculty/admin REST endpoints return HTTP 404.")

        # 5. Health API
        health_resp = client.get('/api/health/')
        assert health_resp.status_code == 200
        assert health_resp.json()['status'] == 'healthy'
        print("[PASS] /api/health/ verified.")

        # 6. Test .html legacy alias routes
        print("\nTesting .html legacy alias routes...")
        assert client.get('/dashboard.html').status_code == 200
        assert client.get('/admin_dashboard.html').status_code in [200, 302]
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
        AdvisorChatMessage.objects.filter(user=s_user).delete()
        AcademicAuditLog.objects.filter(action_by=s_user).delete()
        s_profile.delete()
        s_user.delete()

if __name__ == '__main__':
    run_all_tests()
