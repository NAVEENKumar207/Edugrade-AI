from django.test import SimpleTestCase
from core.regulation import (
    INTERNAL_MAX,
    EXTERNAL_PAPER_MAX,
    EXTERNAL_WEIGHT,
    MIN_EXTERNAL_PERCENT,
    MIN_TOTAL_TO_PASS,
    GRADE_BOUNDARIES,
    marks_to_grade,
)
from core.services.academic_service import (
    required_marks,
    evaluate_expected_marks,
)

class RegulationConfigTests(SimpleTestCase):
    def test_regulation_constants(self):
        self.assertEqual(INTERNAL_MAX, 40)
        self.assertEqual(EXTERNAL_PAPER_MAX, 100)
        self.assertEqual(EXTERNAL_WEIGHT, 0.6)
        self.assertEqual(MIN_EXTERNAL_PERCENT, 45)
        self.assertEqual(MIN_TOTAL_TO_PASS, 50)
        self.assertEqual(GRADE_BOUNDARIES["O"], 91)
        self.assertEqual(GRADE_BOUNDARIES["A+"], 81)
        self.assertEqual(GRADE_BOUNDARIES["A"], 71)
        self.assertEqual(GRADE_BOUNDARIES["B+"], 61)
        self.assertEqual(GRADE_BOUNDARIES["B"], 56)
        self.assertEqual(GRADE_BOUNDARIES["C"], 50)

    def test_marks_to_grade_exact_specified_checks(self):
        """
        Exact checks specified in FIX 2:
        100 -> O, 91 -> O, 90.99 -> A+, 90.5 -> A+, 81 -> A+, 80.5 -> A,
        71 -> A, 70.5 -> B+, 61 -> B+, 60.5 -> B, 56 -> B, 55.5 -> C,
        50 -> C, 49.99 -> U, 0 -> U, 100.5 -> error, -1 -> error.
        """
        exact_mappings = [
            (100, "O"),
            (91, "O"),
            (90.99, "A+"),
            (90.5, "A+"),
            (81, "A+"),
            (80.5, "A"),
            (71, "A"),
            (70.5, "B+"),
            (61, "B+"),
            (60.5, "B"),
            (56, "B"),
            (55.5, "C"),
            (50, "C"),
            (49.99, "U"),
            (0, "U"),
        ]
        for total_val, expected_grade in exact_mappings:
            with self.subTest(total=total_val):
                self.assertEqual(marks_to_grade(total_val), expected_grade)

        # Totals below 0 or above 100 must raise ValueError
        with self.assertRaises(ValueError):
            marks_to_grade(100.5)

        with self.assertRaises(ValueError):
            marks_to_grade(-1)

        with self.assertRaises(ValueError):
            marks_to_grade(-5)

        with self.assertRaises(ValueError):
            marks_to_grade(None)

    def test_all_boundaries_loop_no_gaps(self):
        """Loop over all boundary values (min, min+0.01, min-0.01) to verify no gaps exist."""
        sorted_bounds = sorted(GRADE_BOUNDARIES.items(), key=lambda x: x[1], reverse=True)
        for i, (grade, lower_bound) in enumerate(sorted_bounds):
            with self.subTest(grade=grade, bound=lower_bound):
                # Exactly at lower bound
                self.assertEqual(marks_to_grade(lower_bound), grade)
                # Slightly above lower bound
                if lower_bound + 0.1 <= 100:
                    self.assertEqual(marks_to_grade(lower_bound + 0.1), grade)
                # Slightly below lower bound (should fall to next lower grade or U)
                just_below = lower_bound - 0.01
                if i + 1 < len(sorted_bounds):
                    next_grade = sorted_bounds[i + 1][0]
                    self.assertEqual(marks_to_grade(just_below), next_grade)
                else:
                    self.assertEqual(marks_to_grade(just_below), "U")

    def test_required_and_expected_marks_agree_with_marks_to_grade_at_every_boundary(self):
        """
        Verify required_marks and evaluate_expected_marks agree with marks_to_grade
        at every boundary (e.g. internal 36 + paper marks that give total 81 must give A+).
        """
        # Specific requirement: internal 36 + paper marks giving total 81 (paper=75, 36+75*0.6=81)
        exp_res = evaluate_expected_marks(internal=36.0, paper_marks=75.0)
        self.assertEqual(exp_res["total"], 81.0)
        self.assertEqual(exp_res["grade"], "A+")
        self.assertEqual(marks_to_grade(81.0), exp_res["grade"])

        req_res = required_marks(internal=36.0, target_grade="A+")
        self.assertEqual(req_res["required_paper"], 75)
        self.assertEqual(req_res["resulting_total"], 81.0)
        self.assertEqual(req_res["grade"], "A+")
        self.assertEqual(marks_to_grade(req_res["resulting_total"]), req_res["grade"])

        # Test each grade boundary with an internal score that achieves the exact grade
        boundary_test_cases = [
            ("O", 91, 40.0, 85),    # 40 + 85*0.6 = 40 + 51 = 91.0 -> O
            ("A+", 81, 36.0, 75),   # 36 + 75*0.6 = 36 + 45 = 81.0 -> A+
            ("A", 71, 35.0, 60),    # 35 + 60*0.6 = 35 + 36 = 71.0 -> A
            ("B+", 61, 25.0, 60),   # 25 + 60*0.6 = 25 + 36 = 61.0 -> B+
            ("B", 56, 20.0, 60),    # 20 + 60*0.6 = 20 + 36 = 56.0 -> B
            ("C", 50, 20.0, 50),    # 20 + 50*0.6 = 20 + 30 = 50.0 -> C
        ]

        for grade, min_score, internal_val, paper_val in boundary_test_cases:
            total_at_boundary = round(internal_val + (paper_val * EXTERNAL_WEIGHT), 1)
            eval_out = evaluate_expected_marks(internal_val, paper_val)
            expected_from_m2g = marks_to_grade(total_at_boundary)

            with self.subTest(grade=grade, boundary=min_score):
                self.assertEqual(total_at_boundary, min_score)
                self.assertEqual(eval_out["grade"], expected_from_m2g)
                self.assertEqual(eval_out["grade"], grade)
                req_out = required_marks(internal_val, grade)
                self.assertEqual(req_out["status"], "possible")
                self.assertEqual(req_out["grade"], grade)
                self.assertEqual(req_out["required_paper"], paper_val)

    def test_external_paper_below_minimum_always_results_in_fail(self):
        """Even if internal is 40 and paper is 44 (total 40 + 44*0.6 = 66.4 >= 61), grade must be U."""
        exp_res = evaluate_expected_marks(internal=40.0, paper_marks=44.0)
        self.assertEqual(exp_res["grade"], "U")
        self.assertFalse(exp_res["passed_external"])
