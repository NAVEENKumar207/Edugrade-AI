from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult, CompanyPlacementCriteria
from core.services.twin_service import simulate_future, rank_next_moves

class DigitalTwinSimulatorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(username='student_twin', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.student_user,
            role='student',
            roll_number='71762104101',
            current_semester=5,
            current_cgpa=7.50,
            target_cgpa=8.50,
            credits_earned=60,
            total_credits=160,
            backlogs_count=0
        )
        self.sem1 = SemesterRecord.objects.create(student=self.profile, semester_number=1, sgpa=7.50, credits_earned=20)
        self.sem2 = SemesterRecord.objects.create(student=self.profile, semester_number=2, sgpa=7.50, credits_earned=20)

        # Create 5 course results for simulator
        self.c1 = CourseResult.objects.create(student=self.profile, semester_number=1, course_code="CS101", course_name="Intro to CS", credits=4, grade="A", grade_point=8.0)
        self.c2 = CourseResult.objects.create(student=self.profile, semester_number=1, course_code="CS102", course_name="Data Structures", credits=4, grade="B+", grade_point=7.0)
        self.c3 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS201", course_name="DBMS", credits=4, grade="B", grade_point=6.0)
        self.c4 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS202", course_name="Algorithms", credits=4, grade="A+", grade_point=9.0)
        self.c5 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS203", course_name="Networks", credits=4, grade="B+", grade_point=7.0)

        CompanyPlacementCriteria.objects.create(company_name="AlphaCorp", role_title="Dev", min_cgpa=8.00, max_backlogs=0, package_lpa=10.0)
        CompanyPlacementCriteria.objects.create(company_name="BetaSoft", role_title="Analyst", min_cgpa=7.00, max_backlogs=1, package_lpa=6.0)

    def test_repeatable_with_fixed_seed(self):
        res1 = simulate_future(self.profile, target_cgpa=8.0, effort="same", runs=500, seed=42)
        res2 = simulate_future(self.profile, target_cgpa=8.0, effort="same", runs=500, seed=42)
        self.assertEqual(res1["probability"], res2["probability"])
        self.assertEqual(res1["expected_cgpa"], res2["expected_cgpa"])
        self.assertEqual(res1["p10_cgpa"], res2["p10_cgpa"])
        self.assertEqual(res1["p90_cgpa"], res2["p90_cgpa"])

    def test_probabilities_within_bounds(self):
        res = simulate_future(self.profile, target_cgpa=8.0, effort="same", runs=500, seed=123)
        self.assertTrue(0.0 <= res["probability"] <= 100.0)
        self.assertTrue(0.0 <= res["zero_backlogs_probability"] <= 100.0)
        for comp in res["companies"]:
            self.assertTrue(0.0 <= comp["probability"] <= 100.0)

    def test_effort_monotonicity(self):
        res_low = simulate_future(self.profile, target_cgpa=8.0, effort="lower", runs=1000, seed=99)
        res_same = simulate_future(self.profile, target_cgpa=8.0, effort="same", runs=1000, seed=99)
        res_high = simulate_future(self.profile, target_cgpa=8.0, effort="higher", runs=1000, seed=99)
        self.assertTrue(res_high["probability"] >= res_same["probability"] >= res_low["probability"])
        self.assertTrue(res_high["expected_cgpa"] >= res_same["expected_cgpa"] >= res_low["expected_cgpa"])

    def test_fewer_than_five_results_returns_enough_data_false(self):
        new_user = User.objects.create_user(username='sparse_user', password='password123')
        sparse_profile = UserProfile.objects.create(user=new_user, role='student', current_cgpa=8.0)
        # Create only 3 courses
        for i in range(3):
            CourseResult.objects.create(student=sparse_profile, course_code=f"C{i}", course_name=f"Sub {i}", credits=3, grade="A", grade_point=8.0)

        res = simulate_future(sparse_profile, target_cgpa=8.5)
        self.assertFalse(res["enough_data"])
        self.assertIn("Add at least 5 course results", res["message"])

    def test_target_below_cgpa_with_no_remaining_credits(self):
        self.profile.credits_earned = 160
        self.profile.total_credits = 160
        self.profile.current_cgpa = 8.50
        self.profile.save()

        res = simulate_future(self.profile, target_cgpa=7.0, seed=42)
        self.assertTrue(res["enough_data"])
        self.assertEqual(res["probability"], 100.0)
        self.assertEqual(res["expected_cgpa"], 8.50)

    def test_company_list_is_sorted_by_probability_desc(self):
        res = simulate_future(self.profile, target_cgpa=8.0, runs=500, seed=42)
        probs = [c["probability"] for c in res["companies"]]
        self.assertEqual(probs, sorted(probs, reverse=True))

    def test_student_cannot_call_for_another_student(self):
        other_user = User.objects.create_user(username='other_student', password='password123')
        other_profile = UserProfile.objects.create(user=other_user, role='student', current_cgpa=6.0)

        self.client.force_authenticate(user=self.student_user)
        resp = self.client.post('/api/twin/simulate/', {'target_cgpa': 8.5, 'effort': 'same', 'student_id': other_profile.id})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class NextBestMoveTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_user = User.objects.create_user(username='arrear_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.student_user,
            role='student',
            current_cgpa=5.50,
            credits_earned=60,
            backlogs_count=2,
            total_credits=160
        )
        CompanyPlacementCriteria.objects.create(company_name="Zoho", role_title="SE", min_cgpa=7.20, max_backlogs=0, package_lpa=8.5)
        CompanyPlacementCriteria.objects.create(company_name="TCS", role_title="Ninja", min_cgpa=6.50, max_backlogs=0, package_lpa=4.0)

        # 2 active arrears
        self.arr1 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS2001", course_name="DBMS", credits=4, grade="U", grade_point=0.0, arrear_cleared=False)
        self.arr2 = CourseResult.objects.create(student=self.profile, semester_number=2, course_code="CS2002", course_name="OS", credits=3, grade="RA", grade_point=0.0, arrear_cleared=False)

    def test_ranking_order_correct_on_two_arrears(self):
        moves = rank_next_moves(self.profile, assumed_grade="B")
        self.assertEqual(len(moves), 2)
        # Higher credit course (4 credits vs 3) yields higher CGPA gain
        self.assertEqual(moves[0]["course_code"], "CS2001")
        self.assertTrue(moves[0]["cgpa_gain"] >= moves[1]["cgpa_gain"])
        self.assertIn("Clearing DBMS", moves[0]["sentence"])

    def test_simulated_clearing_does_not_mutate_db(self):
        pre_results_count = CourseResult.objects.count()
        pre_backlogs = self.profile.backlogs_count
        pre_cgpa = self.profile.current_cgpa

        rank_next_moves(self.profile, assumed_grade="B")

        self.profile.refresh_from_db()
        self.assertEqual(CourseResult.objects.count(), pre_results_count)
        self.assertEqual(self.profile.backlogs_count, pre_backlogs)
        self.assertEqual(float(self.profile.current_cgpa), float(pre_cgpa))

    def test_no_arrears_returns_single_suggestion(self):
        # Clear all arrears
        self.arr1.grade = "B"
        self.arr1.arrear_cleared = True
        self.arr1.save()
        self.arr2.grade = "A"
        self.arr2.arrear_cleared = True
        self.arr2.save()
        self.profile.backlogs_count = 0
        self.profile.save()

        moves = rank_next_moves(self.profile, assumed_grade="B")
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["type"], "no_arrears")
        self.assertIn("All arrears clear", moves[0]["sentence"])

    def test_assumed_grade_validation(self):
        with self.assertRaises(ValueError):
            rank_next_moves(self.profile, assumed_grade="F")

        self.client.force_authenticate(user=self.student_user)
        resp = self.client.get('/api/twin/next-moves/?grade=INVALID')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
