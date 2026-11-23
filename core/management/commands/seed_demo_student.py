"""
Management command to seed a realistic student account with CBCS semester records,
cleared arrears, subject insights, and academic metrics.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import UserProfile, SemesterRecord, CourseResult, SubjectInsight
from core.services.academic_service import recalculate_student_metrics, grade_to_point


class Command(BaseCommand):
    help = "Seeds a realistic student account (demo_student / 717622CS101) with CBCS coursework and cleared arrears."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='demo_student',
            help='Username for demo student (default: demo_student)'
        )
        parser.add_argument(
            '--password',
            default='student123',
            help='Password for demo student (default: student123)'
        )
        parser.add_argument(
            '--roll-number',
            default='717622CS101',
            help='Roll number for demo student (default: 717622CS101)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        roll_number = options['roll_number']

        user, created = User.objects.get_or_create(username=username)
        user.first_name = "Naveenkumar"
        user.last_name = "S"
        user.email = f"{username}@edugrade.ai"
        user.set_password(password)
        user.is_staff = False
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.roll_number = roll_number
        profile.department = "Computer Science and Engineering"
        profile.current_semester = 6
        profile.target_cgpa = 8.75
        profile.save()

        # Wipe old demo records for this student before reseeding cleanly
        CourseResult.objects.filter(student=profile).delete()
        SemesterRecord.objects.filter(student=profile).delete()
        SubjectInsight.objects.filter(student=profile).delete()

        # 5 Semesters of realistic CBCS Courses
        semesters_data = [
            (1, [
                ("CS101", "Programming in Python", 4, "A+", False, ""),
                ("MA101", "Matrices and Calculus", 4, "A", False, ""),
                ("PH101", "Engineering Physics", 3, "A", False, ""),
                ("CY101", "Engineering Chemistry", 3, "B+", False, ""),
                ("GE101", "Engineering Graphics", 4, "B+", False, ""),
                ("GE102", "Python Programming Lab", 2, "O", False, ""),
                ("BS101", "Physics & Chemistry Lab", 2, "O", False, ""),
            ]),
            (2, [
                ("CS201", "Data Structures", 4, "A+", False, ""),
                ("MA201", "Statistics & Linear Algebra", 4, "B+", True, "U"),  # Cleared Arrear!
                ("CS202", "Digital Principles & System Design", 3, "A", False, ""),
                ("CS203", "Programming in C", 3, "A+", False, ""),
                ("GE201", "Environmental Science", 3, "B", False, ""),
                ("CS204", "Data Structures Lab", 2, "O", False, ""),
                ("CS205", "C Programming Lab", 2, "A+", False, ""),
            ]),
            (3, [
                ("CS301", "Design and Analysis of Algorithms", 4, "A+", False, ""),
                ("CS302", "Database Management Systems", 4, "O", False, ""),
                ("CS303", "Operating Systems", 3, "A", False, ""),
                ("MA301", "Discrete Mathematics", 4, "B+", False, ""),
                ("CS304", "Software Engineering", 3, "A", False, ""),
                ("CS305", "DBMS Laboratory", 2, "O", False, ""),
                ("CS306", "Operating Systems Lab", 2, "A+", False, ""),
            ]),
            (4, [
                ("CS401", "Computer Networks", 4, "A", False, ""),
                ("CS402", "Object Oriented Analysis & Design", 3, "A", False, ""),
                ("CS403", "Theory of Computation", 4, "B+", False, ""),
                ("CS404", "Artificial Intelligence & ML", 4, "O", False, ""),
                ("CS405", "Web Technology", 3, "A+", False, ""),
                ("CS406", "Networks & Web Lab", 2, "O", False, ""),
                ("CS407", "AI & ML Laboratory", 2, "O", False, ""),
            ]),
            (5, [
                ("CS501", "Compiler Design", 4, "A", False, ""),
                ("CS502", "Cryptography & Network Security", 3, "A+", False, ""),
                ("CS503", "Cloud Computing & DevOps", 4, "O", False, ""),
                ("CS504", "Mobile Application Development", 3, "A+", False, ""),
                ("CS505", "Cyber Forensics & Ethics", 3, "A", False, ""),
                ("CS506", "Cloud & Security Lab", 2, "O", False, ""),
                ("CS507", "Creative Innovation Project", 2, "O", False, ""),
            ]),
        ]

        now = timezone.now()
        for s_num, courses in semesters_data:
            sem_rec = SemesterRecord.objects.create(
                student=profile,
                semester_number=s_num,
                sgpa=0.0,
                credits_earned=0
            )
            for code, name, cr, grade, arrear_cleared, prev_grade in courses:
                gp = grade_to_point(grade)
                CourseResult.objects.create(
                    student=profile,
                    semester_record=sem_rec,
                    semester_number=s_num,
                    course_code=code,
                    course_name=name,
                    credits=cr,
                    grade=grade,
                    grade_point=gp,
                    arrear_cleared=arrear_cleared,
                    previous_grade=prev_grade,
                    cleared_on=now if arrear_cleared else None
                )

        SubjectInsight.objects.create(student=profile, subject_name="Database Management Systems", grade_point=10.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="Cloud Computing & DevOps", grade_point=10.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="Data Structures", grade_point=9.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="Theory of Computation", grade_point=7.0, status_label="Good")

        # Recalculate all metrics atomically
        recalculate_student_metrics(profile)
        profile.refresh_from_db()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded demo student '{username}' ({roll_number}): "
            f"5 Semesters, CGPA={profile.current_cgpa:.2f}, Credits={profile.credits_earned}, Active Arrears={profile.backlogs_count}."
        ))
