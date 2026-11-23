"""
Measured Query Count Tests for EduGrade AI Endpoints.
Uses Django's CaptureQueriesContext with logged-in APIClient to measure real SQL queries
including authentication, session, and business logic execution.
Enforces constant-query O(1) complexity across student cohorts for faculty/admin endpoints.
"""

from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    UserProfile, SemesterRecord, CourseResult,
    CompanyPlacementCriteria, CourseSkillMap
)

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
        role='student',
        roll_number=roll_num,
        department='Computer Science & Engineering',
        current_semester=semesters_count,
        current_cgpa=cgpa,
        credits_earned=semesters_count * courses_per_sem * 4,
        backlogs_count=backlogs,
        is_placement_eligible=(cgpa >= 7.0 and backlogs == 0)
    )

    for sem_num in range(1, semesters_count + 1):
        SemesterRecord.objects.create(
            student=profile,
            semester_number=sem_num,
            sgpa=cgpa,
            credits_earned=courses_per_sem * 4,
            is_published=True
        )
        for c_idx in range(1, courses_per_sem + 1):
            CourseResult.objects.create(
                student=profile,
                semester_number=sem_num,
                course_code=f"CS{sem_num}0{c_idx}",
                course_name=f"Course {sem_num}0{c_idx} Programming",
                credits=4,
                grade="A" if backlogs == 0 or sem_num != semesters_count or c_idx != 1 else "U",
                grade_point=8.0 if backlogs == 0 or sem_num != semesters_count or c_idx != 1 else 0.0,
                is_published=True
            )

    return user, profile

def create_faculty_user(username='admin_faculty'):
    """Helper to create a faculty/admin user."""
    user = User.objects.create_user(
        username=username,
        password='password123',
        is_staff=True
    )
    profile = UserProfile.objects.create(
        user=user,
        role='admin',
        department='Computer Science & Engineering'
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
        print(f"\n[QUERY COUNT] 1. GET /api/students/dashboard/: {measured} queries")

        # Upper limit assertion (measured + 2) and exact measured count
        self.assertLessEqual(measured, 4 + 2)
        self.assertEqual(measured, 4)

    def test_2_admin_analytics_query_count_constant(self):
        """2. GET /api/admin/analytics/ with 5 students and again with 40 students (IDENTICAL query count)"""
        faculty_user, _ = create_faculty_user('faculty_analytics')

        # Population 1: 5 students (some at risk)
        for i in range(1, 6):
            cgpa = 5.50 if i <= 2 else 8.00  # at-risk students
            backlogs = 2 if i <= 2 else 0
            create_student_with_academics(f'stud_5_{i}', f'717650{i}', semesters_count=3, courses_per_sem=4, cgpa=cgpa, backlogs=backlogs)

        self.client.force_authenticate(user=faculty_user)
        with CaptureQueriesContext(connection) as ctx_5:
            resp_5 = self.client.get('/api/admin/analytics/')
        self.assertEqual(resp_5.status_code, status.HTTP_200_OK)
        count_5 = len(ctx_5.captured_queries)

        # Population 2: Add 35 more students (total 40 students)
        for i in range(6, 41):
            cgpa = 5.20 if i <= 15 else 8.20  # more at-risk students
            backlogs = 2 if i <= 15 else 0
            create_student_with_academics(f'stud_40_{i}', f'717640{i:02d}', semesters_count=3, courses_per_sem=4, cgpa=cgpa, backlogs=backlogs)

        with CaptureQueriesContext(connection) as ctx_40:
            resp_40 = self.client.get('/api/admin/analytics/')
        self.assertEqual(resp_40.status_code, status.HTTP_200_OK)
        count_40 = len(ctx_40.captured_queries)

        print(f"\n[QUERY COUNT] 2. GET /api/admin/analytics/: 5 students = {count_5} queries, 40 students = {count_40} queries")
        # Query count must be identical regardless of student population size
        self.assertEqual(count_5, count_40)
        self.assertEqual(count_5, 6)

    def test_3_admin_drives_detail_query_count_constant(self):
        """3. GET /api/admin/drives/<id>/ with 5 students and again with 40 students (IDENTICAL query count)"""
        faculty_user, _ = create_faculty_user('faculty_drives')
        company = CompanyPlacementCriteria.objects.create(
            company_name='Zoho', role_title='Software Engineer',
            min_cgpa=7.0, max_backlogs=0, package_lpa=8.5, required_skills='DSA, DBMS, Python'
        )

        # Population 1: 5 students
        for i in range(1, 6):
            create_student_with_academics(f'drive_stud_5_{i}', f'7176D5{i}', semesters_count=3, courses_per_sem=4)

        self.client.force_authenticate(user=faculty_user)
        with CaptureQueriesContext(connection) as ctx_5:
            resp_5 = self.client.get(f'/api/admin/drives/{company.id}/')
        self.assertEqual(resp_5.status_code, status.HTTP_200_OK)
        count_5 = len(ctx_5.captured_queries)

        # Population 2: Add 35 more students (total 40 students)
        for i in range(6, 41):
            create_student_with_academics(f'drive_stud_40_{i}', f'7176D40{i:02d}', semesters_count=3, courses_per_sem=4)

        with CaptureQueriesContext(connection) as ctx_40:
            resp_40 = self.client.get(f'/api/admin/drives/{company.id}/')
        self.assertEqual(resp_40.status_code, status.HTTP_200_OK)
        count_40 = len(ctx_40.captured_queries)

        print(f"\n[QUERY COUNT] 3. GET /api/admin/drives/<id>/: 5 students = {count_5} queries, 40 students = {count_40} queries")
        # Query count must be identical regardless of student population size
        self.assertEqual(count_5, count_40)
        self.assertEqual(count_5, 4)

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
        print(f"\n[QUERY COUNT] 4. GET /api/journey/: {measured} queries")

        self.assertLessEqual(measured, 4 + 2)
        self.assertEqual(measured, 4)

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
        print(f"\n[QUERY COUNT] 5. GET /api/skills/: {measured} queries")

        self.assertLessEqual(measured, 3 + 2)
        self.assertEqual(measured, 3)

    def test_6_faculty_students_query_count_constant(self):
        """6. GET /api/faculty/students/ with 5 and with 40 students (IDENTICAL query count)"""
        faculty_user, _ = create_faculty_user('faculty_studlist')

        # Population 1: 5 students
        for i in range(1, 6):
            create_student_with_academics(f'flist_5_{i}', f'7176L5{i}', semesters_count=3, courses_per_sem=4)

        self.client.force_authenticate(user=faculty_user)
        with CaptureQueriesContext(connection) as ctx_5:
            resp_5 = self.client.get('/api/faculty/students/')
        self.assertEqual(resp_5.status_code, status.HTTP_200_OK)
        count_5 = len(ctx_5.captured_queries)

        # Population 2: Add 35 more students (total 40 students)
        for i in range(6, 41):
            create_student_with_academics(f'flist_40_{i}', f'7176L40{i:02d}', semesters_count=3, courses_per_sem=4)

        with CaptureQueriesContext(connection) as ctx_40:
            resp_40 = self.client.get('/api/faculty/students/')
        self.assertEqual(resp_40.status_code, status.HTTP_200_OK)
        count_40 = len(ctx_40.captured_queries)

        print(f"\n[QUERY COUNT] 6. GET /api/faculty/students/: 5 students = {count_5} queries, 40 students = {count_40} queries")
        # Query count must be identical regardless of student population size
        self.assertEqual(count_5, count_40)
        self.assertEqual(count_5, 1)
