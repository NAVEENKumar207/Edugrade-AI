"""
Unit tests for the Academic Calculation Engine (core.services.academic_service).
Covers grade mapping, SGPA, CGPA, target planner, what-if scenarios, and placement eligibility.
"""

from django.test import SimpleTestCase, TestCase
from core.models import UserProfile, CompanyPlacementCriteria
from django.contrib.auth.models import User
from core.services.academic_service import (
    grade_to_point, calculate_sgpa, calculate_cgpa,
    plan_target_cgpa, check_placement_eligibility
)

class AcademicServiceUnitTests(SimpleTestCase):
    """Test pure deterministic calculation functions."""

    def test_grade_to_point_mapping(self):
        """Verify 10-point scale mapping for all standard letter grades."""
        self.assertEqual(grade_to_point('O'), 10.0)
        self.assertEqual(grade_to_point('A+'), 9.0)
        self.assertEqual(grade_to_point('A'), 8.0)
        self.assertEqual(grade_to_point('B+'), 7.0)
        self.assertEqual(grade_to_point('B'), 6.0)
        self.assertEqual(grade_to_point('C'), 5.0)
        self.assertEqual(grade_to_point('U'), 0.0)
        self.assertEqual(grade_to_point('RA'), 0.0)
        self.assertEqual(grade_to_point('SA'), 0.0)
        self.assertEqual(grade_to_point('W'), 0.0)

        # Existing code strips whitespace and converts to uppercase:
        self.assertEqual(grade_to_point(' a+ '), 9.0)
        self.assertEqual(grade_to_point('o'), 10.0)
        self.assertEqual(grade_to_point('  b+  '), 7.0)
        self.assertEqual(grade_to_point('u'), 0.0)
        self.assertEqual(grade_to_point('UNKNOWN'), 0.0)

    def test_sgpa_basic(self):
        """
        Courses: (4 cr O), (3 cr A), (3 cr B+), (2 cr C)
        Points = (4*10 + 3*8 + 3*7 + 2*5) = 40 + 24 + 21 + 10 = 95
        Credits = 4 + 3 + 3 + 2 = 12
        Expected SGPA = 95 / 12 = 7.9166... -> 7.92. Backlogs = 0.
        """
        courses = [
            {'credits': 4, 'grade': 'O'},
            {'credits': 3, 'grade': 'A'},
            {'credits': 3, 'grade': 'B+'},
            {'credits': 2, 'grade': 'C'},
        ]
        res = calculate_sgpa(courses)
        self.assertEqual(res['sgpa'], 7.92)
        self.assertEqual(res['total_credits'], 12.0)
        self.assertEqual(res['backlogs'], 0)

    def test_sgpa_with_failure(self):
        """
        Courses: (4 cr A+), (3 cr U), (3 cr A)
        Points = 4*9 + 3*0 + 3*8 = 36 + 0 + 24 = 60
        Credits = 4 + 3 + 3 = 10
        Expected SGPA = 60 / 10 = 6.00. Backlogs = 1.
        """
        courses = [
            {'credits': 4, 'grade': 'A+'},
            {'credits': 3, 'grade': 'U'},
            {'credits': 3, 'grade': 'A'},
        ]
        res = calculate_sgpa(courses)
        self.assertEqual(res['sgpa'], 6.00)
        self.assertEqual(res['total_credits'], 10.0)
        self.assertEqual(res['backlogs'], 1)

    def test_sgpa_empty_course_list(self):
        """Empty course list must return zeroed result without crashing."""
        res = calculate_sgpa([])
        self.assertEqual(res['sgpa'], 0.0)
        self.assertEqual(res['total_credits'], 0.0)
        self.assertEqual(res['backlogs'], 0)

    def test_cgpa_calculation(self):
        """
        Semester 1: SGPA 8.0 with 20 credits
        Semester 2: SGPA 9.0 with 20 credits
        Points = (8.0 * 20) + (9.0 * 20) = 160 + 180 = 340
        Credits = 40
        Expected CGPA = 340 / 40 = 8.50.
        """
        semesters = [
            {'sgpa': 8.0, 'credits_earned': 20},
            {'sgpa': 9.0, 'credits_earned': 20},
        ]
        res = calculate_cgpa(semesters)
        self.assertEqual(res['cgpa'], 8.50)
        self.assertEqual(res['total_credits'], 40.0)

    def test_planner_feasible(self):
        """
        Target: 8.5, total: 160, current: 8.0, completed: 80
        Required SGPA = (8.5*160 - 8.0*80) / 80 = (1360 - 640) / 80 = 720 / 80 = 9.0
        Status: 'feasible'
        """
        res = plan_target_cgpa(
            current_cgpa=8.0,
            completed_credits=80,
            target_cgpa=8.5,
            degree_total_credits=160
        )
        self.assertEqual(res['status'], 'feasible')
        self.assertTrue(res['is_achievable'])
        self.assertEqual(res['required_average_sgpa'], 9.0)

    def test_planner_impossible(self):
        """
        Target: 9.5, total: 160, current: 7.0, completed: 120
        Required SGPA = (9.5*160 - 7.0*120) / 40 = (1520 - 840) / 40 = 680 / 40 = 17.0
        Status: 'impossible'
        """
        res = plan_target_cgpa(
            current_cgpa=7.0,
            completed_credits=120,
            target_cgpa=9.5,
            degree_total_credits=160
        )
        self.assertEqual(res['status'], 'impossible')
        self.assertFalse(res['is_achievable'])
        self.assertIsNone(res['required_average_sgpa'])

    def test_planner_already_achieved(self):
        """Current CGPA >= target CGPA -> status 'already_achieved'."""
        res = plan_target_cgpa(
            current_cgpa=9.0,
            completed_credits=100,
            target_cgpa=8.5,
            degree_total_credits=160
        )
        self.assertEqual(res['status'], 'already_achieved')
        self.assertTrue(res['is_achievable'])

    def test_planner_easily_achievable(self):
        """
        Target: 4.8, total: 160, current: 4.5, completed: 40
        Required SGPA = (4.8*160 - 4.5*40) / 120 = (768 - 180) / 120 = 588 / 120 = 4.90
        Status: 'easily_achievable' (<= 5.0)
        """
        res = plan_target_cgpa(
            current_cgpa=4.5,
            completed_credits=40,
            target_cgpa=4.8,
            degree_total_credits=160
        )
        self.assertEqual(res['status'], 'easily_achievable')
        self.assertTrue(res['is_achievable'])
        self.assertEqual(res['required_average_sgpa'], 4.90)

    def test_planner_invalid_inputs(self):
        """Negative credits and CGPA above 10 must return status 'invalid'."""
        res_neg = plan_target_cgpa(
            current_cgpa=8.0,
            completed_credits=-10,
            target_cgpa=8.5,
            degree_total_credits=160
        )
        self.assertEqual(res_neg['status'], 'invalid')
        self.assertFalse(res_neg['is_achievable'])

        res_over = plan_target_cgpa(
            current_cgpa=11.0,
            completed_credits=80,
            target_cgpa=8.5,
            degree_total_credits=160
        )
        self.assertEqual(res_over['status'], 'invalid')
        self.assertFalse(res_over['is_achievable'])

    def test_what_if_scenarios(self):
        """
        Verify exactly 7 what-if scenarios are generated for
        SGPA 10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0 with correct calculations.
        """
        res = plan_target_cgpa(
            current_cgpa=8.0,
            completed_credits=80,
            target_cgpa=8.5,
            degree_total_credits=160
        )
        scenarios = res['scenarios']
        self.assertEqual(len(scenarios), 7)
        expected_sgpas = [10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0]
        actual_sgpas = [s['future_average_sgpa'] for s in scenarios]
        self.assertEqual(actual_sgpas, expected_sgpas)

        # For future SGPA 10.0:
        # Current points = 8.0 * 80 = 640
        # Future points = 10.0 * 80 = 800
        # Total points = 1440 / 160 = 9.00
        self.assertEqual(scenarios[0]['projected_final_cgpa'], 9.00)
        self.assertTrue(scenarios[0]['meets_target'])

        # For future SGPA 7.0:
        # Future points = 7.0 * 80 = 560
        # Total points = 1200 / 160 = 7.50
        self.assertEqual(scenarios[6]['projected_final_cgpa'], 7.50)
        self.assertFalse(scenarios[6]['meets_target'])


class PlacementEligibilityTests(TestCase):
    """Test company placement eligibility evaluation against criteria."""

    def setUp(self):
        self.user = User.objects.create_user(username='test_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            current_cgpa=8.20,
            backlogs_count=0,
            role='student'
        )
        self.company = CompanyPlacementCriteria.objects.create(
            company_name='Apex Corp',
            role_title='Software Engineer',
            min_cgpa=7.50,
            max_backlogs=0,
            package_lpa=12.0
        )

    def test_placement_eligible(self):
        """CGPA 8.2, 0 backlogs vs min 7.5 / max 0 backlogs -> eligible."""
        res = check_placement_eligibility(self.profile, [self.company])
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]['is_eligible'])
        self.assertEqual(res[0]['status'], 'eligible')

    def test_placement_ineligible_by_cgpa(self):
        """
        CGPA 6.8 vs min 7.5 -> ineligible.
        Message mentions CGPA 6.80, 7.50 and deficit of 0.70.
        """
        self.profile.current_cgpa = 6.80
        self.profile.save()
        res = check_placement_eligibility(self.profile, [self.company])
        self.assertFalse(res[0]['is_eligible'])
        reasons_text = " ".join(res[0]['reasons'])
        self.assertIn("6.80", reasons_text)
        self.assertIn("7.50", reasons_text)
        self.assertIn("0.70", reasons_text)

    def test_placement_ineligible_by_backlogs(self):
        """
        1 backlog vs max 0 -> ineligible.
        Message mentions active backlogs.
        """
        self.profile.current_cgpa = 8.20
        self.profile.backlogs_count = 1
        self.profile.save()
        res = check_placement_eligibility(self.profile, [self.company])
        self.assertFalse(res[0]['is_eligible'])
        reasons_text = " ".join(res[0]['reasons'])
        self.assertIn("backlogs", reasons_text.lower())
        self.assertIn("1", reasons_text)
