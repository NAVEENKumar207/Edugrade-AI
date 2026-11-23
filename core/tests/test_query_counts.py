"""
Performance regression test suite asserting measured query counts for student-only portal endpoints.
Enforces that queries are bounded and that no N+1 query patterns exist.
"""

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, SemesterRecord, CourseResult, CompanyPlacementCriteria


def create_student_with_academics(username, roll_num, semesters_count=3, courses_per_sem=4, cgpa=8.0, backlogs=0):
    """Helper to create a student with populated semesters and course results."""
    user = User.objects.create_user(
        username=username,
        password='password123',
        first_name=username.capitalize(),
        last_name='Student'
    )
    profile = UserProfile.objects.create(
        user=user,
        roll_number=roll_num,
        department='Computer Science & Engineering',
        current_semester=semesters_count,
        current_cgpa=cgpa,
        credits_earned=semesters_count * courses_per_sem * 4,
        backlogs_count=backlogs,
        is_placement_eligible=(cgpa >= 7.0 and backlogs == 0)
    )

    for sem_num in range(1, semesters_count + 1):
        sem_rec = SemesterRecord.objects.create(
            student=profile,
            semester_number=sem_num,
            sgpa=cgpa,
            credits_earned=courses_per_sem * 4
        )
        for c_idx in range(1, courses_per_sem + 1):
            CourseResult.objects.create(
                student=profile,
                semester_record=sem_rec,
                semester_number=sem_num,
                course_code=f"CS{sem_num}0{c_idx}",
                course_name=f"Course {sem_num}0{c_idx} Programming",
                credits=4,
                grade="A" if backlogs == 0 or sem_num != semesters_count or c_idx != 1 else "U",
                grade_point=8.0 if backlogs == 0 or sem_num != semesters_count or c_idx != 1 else 0.0
            )

    return user, profile


class MeasuredQueryCountsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_1_student_dashboard_query_count(self):
        """1. GET /api/students/dashboard/ (student with 3 semesters, 12 results)"""
        user, profile = create_student_with_academics('dash_stud', '7176001', semesters_count=3, courses_per_sem=4)
        CompanyPlacementCriteria.objects.create(
            company_name='TestCorp', role_title='SE', min_cgpa=7.0, max_backlogs=0, package_lpa=8.0, is_active=True
        )
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get('/api/students/dashboard/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)

    def test_2_results_query_count(self):
        """2. GET /api/academics/results/ (student with 3 semesters, 12 results)"""
        user, profile = create_student_with_academics('res_stud', '7176002', semesters_count=3, courses_per_sem=4)
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get('/api/academics/results/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)

    def test_3_placements_query_count(self):
        """3. GET /api/placements/eligibility/ with multiple active placement criteria"""
        user, profile = create_student_with_academics('place_stud', '7176003', semesters_count=3, courses_per_sem=4)
        for i in range(5):
            CompanyPlacementCriteria.objects.create(
                company_name=f'PlaceCorp{i}', role_title='Engineer',
                min_cgpa=7.0, max_backlogs=0, package_lpa=8.0 + i, is_active=True
            )
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get('/api/placements/eligibility/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)

    def test_4_journey_query_count(self):
        """4. GET /api/journey/ (student with 3 semesters)"""
        user, profile = create_student_with_academics('journey_q_stud', '7176J01', semesters_count=3, courses_per_sem=4)
        CompanyPlacementCriteria.objects.create(
            company_name='AlphaCorp', role_title='Analyst', min_cgpa=6.5, max_backlogs=1, package_lpa=6.0, is_active=True
        )
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get('/api/journey/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)

    def test_5_skills_query_count(self):
        """5. GET /api/skills/ (student with 3 semesters)"""
        user, profile = create_student_with_academics('skills_q_stud', '7176S01', semesters_count=3, courses_per_sem=4)
        for i in range(6):
            CompanyPlacementCriteria.objects.create(
                company_name=f'Corp{i}', role_title='Dev', min_cgpa=7.0, max_backlogs=0, package_lpa=7.0 + i, is_active=True
            )
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get('/api/skills/')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)

    def test_6_twin_simulate_query_count(self):
        """6. POST /api/twin/simulate/ (Monte Carlo digital twin)"""
        user, profile = create_student_with_academics('twin_q_stud', '7176T01', semesters_count=4, courses_per_sem=4)
        self.client.force_authenticate(user=user)

        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.post('/api/twin/simulate/', {'target_cgpa': 8.5, 'effort': 'same', 'seed': 42}, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        measured = len(ctx.captured_queries)
        self.assertLessEqual(measured, 8)
