from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from core.models import UserProfile, CourseResult, CompanyPlacementCriteria, CourseSkillMap
from core.services.skill_service import skill_scores, company_skill_match, evaluate_placement_fit

class SkillMapAndPlacementMatchTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='skill_student', password='password123')
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='student',
            current_cgpa=8.00,
            backlogs_count=0
        )
        self.company = CompanyPlacementCriteria.objects.create(
            company_name="TechCorp",
            role_title="Backend Engineer",
            min_cgpa=7.50,
            max_backlogs=0,
            required_skills="DSA, DBMS, Cloud"
        )

    def test_weighted_skill_score_on_seeded_student(self):
        # 2 courses mapped to DSA: CS101 (4 cr, grade point 8.0) and CS102 (2 cr, grade point 10.0)
        # Weighted avg gp = (4*8 + 2*10) / 6 = (32 + 20) / 6 = 52 / 6 = 8.67
        # Score scaled 0-100 = 86.7
        CourseSkillMap.objects.create(course_code="CS101", skill="DSA")
        CourseSkillMap.objects.create(course_code="CS102", skill="DSA")

        CourseResult.objects.create(student=self.profile, course_code="CS101", course_name="Data Structures", credits=4, grade="A", grade_point=8.0)
        CourseResult.objects.create(student=self.profile, course_code="CS102", course_name="Advanced Algorithms", credits=2, grade="O", grade_point=10.0)

        scores = skill_scores(self.profile)
        self.assertIn("DSA", scores)
        self.assertEqual(scores["DSA"]["score"], 86.7)
        self.assertEqual(scores["DSA"]["total_credits"], 6)

    def test_uncovered_skills_are_listed_and_not_scored(self):
        CourseSkillMap.objects.create(course_code="CS101", skill="DSA")
        CourseResult.objects.create(student=self.profile, course_code="CS101", course_name="Data Structures", credits=4, grade="A", grade_point=8.0)

        match_res = company_skill_match(self.profile, self.company)
        # Required: DSA, DBMS, Cloud. Only DSA has course evidence
        self.assertIn("Cloud", match_res["uncovered_skills"])
        self.assertIn("DBMS", match_res["uncovered_skills"])
        self.assertEqual(match_res["match_percent"], 80.0) # only DSA's score (80.0) is averaged

    def test_fit_labels_for_each_case(self):
        CourseSkillMap.objects.create(course_code="CS101", skill="DSA")
        CourseResult.objects.create(student=self.profile, course_code="CS101", course_name="Data Structures", credits=4, grade="A", grade_point=8.0)

        # Case 1: Ready -> eligible (cgpa 8.0 >= 7.5, 0 backlogs) and match >= 70 (80.0)
        m1 = company_skill_match(self.profile, self.company)
        fit1 = evaluate_placement_fit(self.profile, self.company, m1)
        self.assertEqual(fit1["fit_label"], "Ready")

        # Case 2: Almost -> eligible but match < 70
        CourseResult.objects.filter(course_code="CS101").update(grade="C", grade_point=5.0)
        m2 = company_skill_match(self.profile, self.company)
        fit2 = evaluate_placement_fit(self.profile, self.company, m2)
        self.assertEqual(fit2["fit_label"], "Almost")

        # Case 3: Almost -> not eligible but within 0.5 CGPA (e.g. min 7.50, student 7.20)
        self.profile.current_cgpa = 7.20
        self.profile.save()
        m3 = company_skill_match(self.profile, self.company)
        fit3 = evaluate_placement_fit(self.profile, self.company, m3)
        self.assertEqual(fit3["fit_label"], "Almost")

        # Case 4: Not yet -> CGPA 6.0 (gap > 0.5)
        self.profile.current_cgpa = 6.00
        self.profile.save()
        m4 = company_skill_match(self.profile, self.company)
        fit4 = evaluate_placement_fit(self.profile, self.company, m4)
        self.assertEqual(fit4["fit_label"], "Not yet")

    def test_fallback_keyword_mapping_works_without_db_rows(self):
        CourseSkillMap.objects.all().delete()
        CourseResult.objects.create(student=self.profile, course_code="CS999", course_name="Python Programming and Data Structures", credits=3, grade="O", grade_point=10.0)

        scores = skill_scores(self.profile)
        self.assertIn("Python", scores)
        self.assertIn("DSA", scores)
        self.assertEqual(scores["Python"]["score"], 100.0)

    def test_empty_data_works_without_crashes(self):
        new_user = User.objects.create_user(username='empty_student', password='password123')
        empty_prof = UserProfile.objects.create(user=new_user, role='student', current_cgpa=0.0)

        scores = skill_scores(empty_prof)
        self.assertEqual(scores, {})

        match_res = company_skill_match(empty_prof, self.company)
        self.assertEqual(match_res["match_percent"], 0.0)
        self.assertEqual(len(match_res["uncovered_skills"]), 3)
