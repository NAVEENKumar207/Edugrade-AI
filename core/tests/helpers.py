"""
Reusable test factory helpers for student, admin, and course records in EduGrade AI.
Provides create_student, create_admin, and add_result factory functions.
"""

from django.contrib.auth.models import User
from core.models import UserProfile, CourseResult, SemesterRecord


def create_student(username='student1', roll_number='71762104001', password='password123', cgpa=8.0, department='CSE', semester=6, **kwargs):
    """Factory helper to create a student User and UserProfile."""
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': kwargs.get('first_name', 'Student'), 'last_name': kwargs.get('last_name', 'User')}
    )
    user.set_password(password)
    user.save()

    profile, _ = UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'role': 'student',
            'roll_number': roll_number,
            'department': department,
            'current_semester': semester,
            'current_cgpa': cgpa,
            'credits_earned': kwargs.get('credits_earned', 0),
            'backlogs_count': kwargs.get('backlogs_count', 0),
            'target_cgpa': kwargs.get('target_cgpa', 8.5),
            'is_placement_eligible': kwargs.get('is_placement_eligible', True),
        }
    )
    return profile


def create_admin(username='admin1', roll_number='FAC-001', password='password123', department='CSE', **kwargs):
    """Factory helper to create a faculty/admin User and UserProfile."""
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': kwargs.get('first_name', 'Admin'), 'last_name': kwargs.get('last_name', 'Faculty'), 'is_staff': True}
    )
    user.is_staff = True
    user.set_password(password)
    user.save()

    profile, _ = UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'role': 'admin',
            'roll_number': roll_number,
            'department': department,
        }
    )
    return profile


def add_result(student, sem_num, code, name, credits, grade, grade_point=None):
    """Factory helper to add a CourseResult (and optional SemesterRecord) for a student."""
    if grade_point is None:
        from core.services.academic_service import GRADE_POINTS
        grade_point = GRADE_POINTS.get(grade.upper(), 0.0)

    sem_rec, _ = SemesterRecord.objects.get_or_create(
        student=student,
        semester_number=sem_num,
        defaults={'sgpa': grade_point}
    )

    return CourseResult.objects.create(
        student=student,
        semester=sem_rec,
        semester_number=sem_num,
        course_code=code,
        course_name=name,
        credits=credits,
        grade=grade,
        grade_point=grade_point
    )
