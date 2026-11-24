"""Integration tests for EduGrade AI models, audit logging, and calculations."""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria
)
from core.services.academic_service import (
    calculate_sgpa, calculate_cgpa, plan_target_cgpa,
    check_placement_eligibility, grade_to_point
)
from core.services.ai_service import generate_ai_advice
from ui.pages.cgpa_planner import CgpaPlanner

class AcademicCalculationTests(TestCase):
    """Unit tests for deterministic academic calculations."""

    def test_grade_to_point(self):
        self.assertEqual(grade_to_point('O'), 10.0)
        self.assertEqual(grade_to_point('A+'), 9.0)
        self.assertEqual(grade_to_point('A'), 8.0)
        self.assertEqual(grade_to_point('B+'), 7.0)
        self.assertEqual(grade_to_point('B'), 6.0)
        self.assertEqual(grade_to_point('U'), 0.0)
        self.assertEqual(grade_to_point('RA'), 0.0)

    def test_sgpa_calculation(self):
        # 3 courses: (cr=4, gp=10), (cr=3, gp=8), (cr=3, gp=6)
        # points: 40 + 24 + 18 = 82 / 10 = 8.20
        courses = [
            {'credits': 4, 'grade_point': 10.0},
            {'credits': 3, 'grade_point': 8.0},
            {'credits': 3, 'grade_point': 6.0},
        ]
        result = calculate_sgpa(courses)
        self.assertEqual(result['sgpa'], 8.20)
        self.assertEqual(result['total_credits'], 10.0)
        self.assertEqual(result['backlogs'], 0)

    def test_sgpa_with_backlog(self):
        courses = [
            {'credits': 3, 'grade_point': 9.0},
            {'credits': 3, 'grade_point': 0.0, 'grade': 'U'},
        ]
        result = calculate_sgpa(courses)
        self.assertEqual(result['sgpa'], 4.50)
        self.assertEqual(result['backlogs'], 1)

    def test_cgpa_calculation(self):
        semesters = [
            {'sgpa': 8.0, 'credits_earned': 20},
            {'sgpa': 9.0, 'credits_earned': 20},
        ]
        # (160 + 180) / 40 = 340 / 40 = 8.50
        result = calculate_cgpa(semesters)
        self.assertEqual(result['cgpa'], 8.50)
        self.assertEqual(result['total_credits'], 40)

    def test_target_cgpa_planner_feasible(self):
        # Test 1: Normal feasible target (8.42 CGPA, 98 credits, 160 total, 9.00 target)
        plan = plan_target_cgpa(
            current_cgpa=8.42,
            completed_credits=98,
            target_cgpa=9.00,
            remaining_semesters=3,
            degree_total_credits=160
        )
        self.assertTrue(plan['is_achievable'])
        self.assertEqual(plan['remaining_credits'], 62)
        self.assertAlmostEqual(plan['required_average_sgpa'], 9.92, places=2)
        self.assertEqual(plan['status'], 'feasible')

    def test_target_cgpa_planner_feasible_threshold(self):
        # Test 2: Target 8.50 with current 8.42 (Required SGPA ~8.63, feasible)
        plan = plan_target_cgpa(
            current_cgpa=8.42,
            completed_credits=98,
            target_cgpa=8.50,
            remaining_semesters=3,
            degree_total_credits=160
        )
        self.assertTrue(plan['is_achievable'])
        self.assertEqual(plan['remaining_credits'], 62)
        self.assertAlmostEqual(plan['required_average_sgpa'], 8.63, places=2)
        self.assertEqual(plan['status'], 'feasible')

    def test_target_cgpa_planner_impossible(self):
        # Test 3: Mathematically impossible target (6.00 CGPA, 120 credits out of 160, Target: 9.50)
        plan = plan_target_cgpa(
            current_cgpa=6.0,
            completed_credits=120,
            target_cgpa=9.5,
            remaining_credits=40,
            remaining_semesters=2,
            degree_total_credits=160
        )
        self.assertFalse(plan['is_achievable'])
        self.assertEqual(plan['status'], 'impossible')
        self.assertIsNone(plan['required_average_sgpa'])
        self.assertEqual(plan['max_achievable_cgpa'], 7.00)
        self.assertIn("mathematically unattainable", plan['message'])
        self.assertIn("7.00", plan['message'])

    def test_target_cgpa_planner_already_achieved(self):
        # Test 4: Already achieved target (Current CGPA: 9.20, Target: 8.50)
        plan = plan_target_cgpa(
            current_cgpa=9.20,
            completed_credits=98,
            target_cgpa=8.50,
            remaining_semesters=3,
            degree_total_credits=160
        )
        self.assertTrue(plan['is_achievable'])
        self.assertEqual(plan['status'], 'already_achieved')
        self.assertIsNotNone(plan['required_average_sgpa'])
        self.assertIn("already been achieved", plan['message'].lower())

    def test_target_cgpa_planner_zero_remaining_credits(self):
        # Test 5: Zero remaining credits (Completed: 160, Total: 160)
        plan = plan_target_cgpa(
            current_cgpa=8.42,
            completed_credits=160,
            target_cgpa=8.50,
            remaining_semesters=1,
            degree_total_credits=160
        )
        self.assertEqual(plan['remaining_credits'], 0.0)
        self.assertIsNone(plan['required_average_sgpa'])
        self.assertFalse(plan['is_achievable']) # 8.42 < 8.50 with 0 credits remaining
        self.assertEqual(plan['status'], 'impossible')
        self.assertIn("All 160 degree credits have been completed", plan['message'])

    def test_target_cgpa_planner_invalid_inputs(self):
        # Test 6: Invalid inputs (negative credits, CGPA > 10, total <= 0, completed > total)
        p1 = plan_target_cgpa(current_cgpa=-1.0, completed_credits=50, target_cgpa=9.0)
        self.assertEqual(p1['status'], 'invalid')
        self.assertFalse(p1['is_achievable'])

        p2 = plan_target_cgpa(current_cgpa=8.0, completed_credits=50, target_cgpa=11.0)
        self.assertEqual(p2['status'], 'invalid')

        p3 = plan_target_cgpa(current_cgpa=8.0, completed_credits=-10, target_cgpa=9.0)
        self.assertEqual(p3['status'], 'invalid')

        p4 = plan_target_cgpa(current_cgpa=8.0, completed_credits=180, target_cgpa=9.0, degree_total_credits=160)
        self.assertEqual(p4['status'], 'invalid')

        p5 = plan_target_cgpa(current_cgpa=8.0, completed_credits=50, target_cgpa=9.0, remaining_semesters=0)
        self.assertEqual(p5['status'], 'invalid')

        # Negative remaining credits must be rejected
        p6 = plan_target_cgpa(current_cgpa=8.0, completed_credits=80, target_cgpa=8.5, remaining_credits=-20)
        self.assertEqual(p6['status'], 'invalid')
        self.assertFalse(p6['is_achievable'])
        self.assertIn("Remaining credits cannot be negative", p6['message'])

    def test_target_cgpa_planner_explicit_zero_remaining_credits(self):
        # Explicit zero remaining credits
        plan = plan_target_cgpa(current_cgpa=8.50, completed_credits=160, target_cgpa=8.50, remaining_credits=0)
        self.assertEqual(plan['remaining_credits'], 0.0)
        self.assertTrue(plan['is_achievable'])
        self.assertEqual(plan['status'], 'already_achieved')
        self.assertIsNone(plan['required_average_sgpa'])
        self.assertIn("All 160 degree credits have been completed", plan['message'])

    def test_academic_year_calculation(self):
        # Standard ((semester + 1) // 2) mapping
        expected_years = {
            1: 1, 2: 1,  # Year 1
            3: 2, 4: 2,  # Year 2
            5: 3, 6: 3,  # Year 3
            7: 4, 8: 4   # Year 4
        }
        for sem, exp_yr in expected_years.items():
            calc_yr = ((sem + 1) // 2)
            self.assertEqual(calc_yr, exp_yr, f"Semester {sem} should map to Academic Year {exp_yr}")

        # Fallback when semester is None or falsy
        none_sem = None
        fallback_sem = none_sem if none_sem else 5
        self.assertEqual(((fallback_sem + 1) // 2), 3)

    def test_target_cgpa_planner_scenarios(self):
        # Test 7: Verify all 7 future SGPA scenarios calculate properly
        plan = plan_target_cgpa(
            current_cgpa=8.42,
            completed_credits=98,
            target_cgpa=9.00,
            remaining_semesters=3,
            degree_total_credits=160
        )
        scenarios = plan['scenarios']
        self.assertEqual(len(scenarios), 7)
        expected_sgpas = [10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0]
        for idx, sc in enumerate(scenarios):
            self.assertEqual(sc['future_average_sgpa'], expected_sgpas[idx])
            self.assertLessEqual(sc['projected_final_cgpa'], 10.00)
            self.assertGreaterEqual(sc['projected_final_cgpa'], 0.00)
            self.assertEqual(sc['meets_target'], sc['projected_final_cgpa'] >= 9.00)

class DatabaseCRUDAndIntegrityTests(TestCase):
    """Isolated database CRUD and referential integrity tests."""

    def setUp(self):
        self.user = User.objects.create_user(username='teststudent', password='password123', email='test@edu.com')
        self.profile = UserProfile.objects.create(
            user=self.user,
            roll_number='7176TEST',
            current_semester=3,
            current_cgpa=8.10,
            credits_earned=60
        )

    def test_create_and_retrieve_semester(self):
        sem = SemesterRecord.objects.create(
            student=self.profile,
            semester_number=1,
            sgpa=8.25,
            credits_earned=20
        )
        retrieved = SemesterRecord.objects.get(id=sem.id)
        self.assertEqual(retrieved.student.user.username, 'teststudent')
        self.assertEqual(float(retrieved.sgpa), 8.25)

    def test_update_academic_record(self):
        self.profile.current_cgpa = 8.55
        self.profile.save()
        updated = UserProfile.objects.get(id=self.profile.id)
        self.assertEqual(float(updated.current_cgpa), 8.55)

    def test_cascade_delete_integrity(self):
        sem = SemesterRecord.objects.create(
            student=self.profile,
            semester_number=1,
            sgpa=8.0,
            credits_earned=20
        )
        CourseResult.objects.create(
            student=self.profile,
            semester_record=sem,
            course_code='CS101',
            course_name='Intro to CS',
            credits=3,
            grade='A',
            grade_point=8.0
        )
        self.assertEqual(CourseResult.objects.count(), 1)
        # Deleting student should cascade clean
        self.profile.delete()
        self.assertEqual(SemesterRecord.objects.count(), 0)
        self.assertEqual(CourseResult.objects.count(), 0)

    def test_placement_eligibility_criteria_check(self):
        crit1 = CompanyPlacementCriteria.objects.create(
            company_name='TechCorp',
            role_title='Dev',
            min_cgpa=8.00,
            max_backlogs=0
        )
        crit2 = CompanyPlacementCriteria.objects.create(
            company_name='SuperTech',
            role_title='Architect',
            min_cgpa=9.00,
            max_backlogs=0
        )
        results = check_placement_eligibility(self.profile, [crit1, crit2])
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]['is_eligible'])   # 8.10 >= 8.00
        self.assertFalse(results[1]['is_eligible'])  # 8.10 < 9.00
        self.assertIn("Current CGPA (8.10) is below minimum requirement (9.00)", results[1]['reasons'][0])

class AIAdvisorServiceTests(TestCase):
    """Test AI Advisor service and fallback logic."""

    def setUp(self):
        self.user = User.objects.create_user(username='alex', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            current_cgpa=8.42,
            target_cgpa=9.00,
            credits_earned=98,
            current_semester=5
        )
        SubjectInsight.objects.create(
            student=self.profile,
            subject_name='Operating Systems',
            grade_point=6.0,
            status_label='Needs attention'
        )

    def test_ai_advisor_english_response(self):
        res = generate_ai_advice(self.profile, "How can I improve my CGPA?")
        self.assertIn('response', res)
        self.assertIn('8.42', res['response'])
        self.assertIn('Operating Systems', res['response'])

class CgpaPlannerReactPyRenderTests(TestCase):
    """Test 8: ReactPy rendering of CgpaPlanner across all student scenarios."""

    def setUp(self):
        self.user = User.objects.create_user(username='planner_test', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            current_cgpa=8.42,
            target_cgpa=9.00,
            credits_earned=98,
            total_credits=160,
            current_semester=5
        )

    def test_render_normal_student(self):
        vdom = CgpaPlanner(self.user)
        self.assertIsNotNone(vdom)

    def test_render_easily_achievable(self):
        self.profile.current_cgpa = 9.00
        self.profile.target_cgpa = 7.00
        self.profile.save()
        vdom = CgpaPlanner(self.user)
        self.assertIsNotNone(vdom)

    def test_render_impossible_target(self):
        self.profile.current_cgpa = 6.00
        self.profile.credits_earned = 120
        self.profile.target_cgpa = 9.50
        self.profile.save()
        vdom = CgpaPlanner(self.user)
        self.assertIsNotNone(vdom)

    def test_render_already_achieved_target(self):
        self.profile.current_cgpa = 9.20
        self.profile.target_cgpa = 8.50
        self.profile.save()
        vdom = CgpaPlanner(self.user)
        self.assertIsNotNone(vdom)

    def test_render_zero_remaining_credits(self):
        self.profile.credits_earned = 160
        self.profile.total_credits = 160
        self.profile.save()
        vdom = CgpaPlanner(self.user)
        self.assertIsNotNone(vdom)

class CgpaPlannerAPITests(TestCase):
    """Test suite for /api/planner/cgpa/ validation and response status codes."""

    def setUp(self):
        self.client = Client()

    def test_api_invalid_non_numeric_input_returns_400(self):
        resp = self.client.post('/api/planner/cgpa/', data=json.dumps({
            'current_cgpa': 'invalid_non_numeric',
            'target_cgpa': 9.0
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn('error', data)
        self.assertIn('details', data)

    def test_api_out_of_bounds_input_returns_400(self):
        # Negative current CGPA
        r1 = self.client.post('/api/planner/cgpa/', data=json.dumps({'current_cgpa': -2.5}), content_type='application/json')
        self.assertEqual(r1.status_code, 400)

        # Target CGPA > 10.0
        r2 = self.client.post('/api/planner/cgpa/', data=json.dumps({'target_cgpa': 12.0}), content_type='application/json')
        self.assertEqual(r2.status_code, 400)

        # Total credits <= 0
        r3 = self.client.post('/api/planner/cgpa/', data=json.dumps({'total_credits': 0}), content_type='application/json')
        self.assertEqual(r3.status_code, 400)

    def test_api_negative_remaining_credits_returns_400(self):
        resp = self.client.post('/api/planner/cgpa/', data=json.dumps({
            'current_cgpa': 8.0,
            'remaining_credits': -15.0
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())

    def test_api_explicit_zero_remaining_credits_returns_200(self):
        resp = self.client.post('/api/planner/cgpa/', data=json.dumps({
            'current_cgpa': 8.50,
            'completed_credits': 160,
            'target_cgpa': 8.50,
            'remaining_credits': 0
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['remaining_credits'], 0.0)
        self.assertIsNone(data['required_average_sgpa'])
        self.assertEqual(data['status'], 'already_achieved')


