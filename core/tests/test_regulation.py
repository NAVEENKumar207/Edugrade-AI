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
from core.services.academic_service import marks_to_grade as service_marks_to_grade

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

    def test_marks_to_grade_exact_boundaries(self):
        self.assertEqual(marks_to_grade(100), "O")
        self.assertEqual(marks_to_grade(91), "O")
        self.assertEqual(marks_to_grade(90.9), "A+")
        self.assertEqual(marks_to_grade(81), "A+")
        self.assertEqual(marks_to_grade(80.5), "A")
        self.assertEqual(marks_to_grade(71), "A")
        self.assertEqual(marks_to_grade(70), "B+")
        self.assertEqual(marks_to_grade(61), "B+")
        self.assertEqual(marks_to_grade(60.9), "B")
        self.assertEqual(marks_to_grade(56), "B")
        self.assertEqual(marks_to_grade(55.9), "C")
        self.assertEqual(marks_to_grade(50), "C")
        self.assertEqual(marks_to_grade(49.9), "U")
        self.assertEqual(marks_to_grade(0), "U")
        self.assertEqual(marks_to_grade(-5), "U")
        self.assertEqual(marks_to_grade(None), "U")

    def test_academic_service_export(self):
        self.assertEqual(service_marks_to_grade(95), "O")
        self.assertEqual(service_marks_to_grade(40), "U")
