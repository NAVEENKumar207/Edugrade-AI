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
            default='717622CB041',
            help='Roll number for demo student (default: 717622CB041)'
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
        profile.department = "Computer Science and Business Systems"
        profile.institution_name = "K.S. Rangasamy College of Technology (Autonomous)"
        profile.current_semester = 6
        profile.target_cgpa = 8.75
        profile.total_credits = 164
        profile.save()

        # Wipe old demo records for this student before reseeding cleanly
        CourseResult.objects.filter(student=profile).delete()
        SemesterRecord.objects.filter(student=profile).delete()
        SubjectInsight.objects.filter(student=profile).delete()

        # 5 Semesters of realistic CBCS Courses from R2022 B.Tech CSBS (2024-2028 batch)
        semesters_data = [
            (1, [
                ("60 EN 003", "Business Communication and Value Science I", 2, "A+", False, ""),
                ("60 MA 002", "Statistics and Probability", 4, "A", False, ""),
                ("61 PH 008", "Fundamentals of Physics", 3, "A", False, ""),
                ("61 CB 101", "Computer Programming (Python)", 3, "A+", False, ""),
                ("60 EE 003", "Principles of Electrical Engineering and Lab", 4, "B+", False, ""),
                ("60 CB 1P1", "Computer Programming Lab (Python)", 2, "O", False, ""),
                ("60 PH 0P3", "Fundamentals of Physics Lab", 2, "O", False, ""),
            ]),
            (2, [
                ("60 EN 004", "Business Communication and Value Science II", 2, "A", False, ""),
                ("60 HS 001", "Fundamentals of Economics", 3, "A", False, ""),
                ("60 MA 005", "Statistical Modeling", 5, "B+", True, "U"),  # Cleared Arrear!
                ("60 CB 201", "Computer Organization and Architecture", 3, "A+", False, ""),
                ("61 CB 202", "Object Oriented Programming", 3, "A+", False, ""),
                ("60 ME 0P1", "Fabrication and Reverse Engineering Laboratory", 2, "O", False, ""),
                ("61 CB 2P1", "Object Oriented Programming Lab", 2, "O", False, ""),
            ]),
            (3, [
                ("60 HS 004", "Introduction to Innovation, IP Management & Entrepreneurship", 3, "A+", False, ""),
                ("60 MA 013", "Computational Statistics", 4, "A", False, ""),
                ("61 CB 301", "Automata and Compiler Design", 4, "A", False, ""),
                ("60 CB 302", "Database Management Systems", 3, "O", False, ""),
                ("60 CB 303", "Data Structures", 3, "A+", False, ""),
                ("60 CB 304", "Software Engineering", 3, "A", False, ""),
                ("60 CB 3P1", "Database Management Systems Lab", 2, "O", False, ""),
                ("60 CB 3P2", "Data Structures Lab", 2, "O", False, ""),
            ]),
            (4, [
                ("60 MA 018", "Optimization Techniques", 4, "A", False, ""),
                ("60 CB 401", "Operating Systems", 3, "A+", False, ""),
                ("60 CB 402", "Design and Analysis of Algorithms", 3, "A+", False, ""),
                ("60 CB 403", "Software Design with UML", 3, "A", False, ""),
                ("60 CB 404", "MERN Stack", 3, "O", False, ""),
                ("60 OE L01", "Open Elective-I", 3, "A", False, ""),
                ("60 CB 4P1", "Operating Systems Lab", 2, "O", False, ""),
                ("60 CB 4P2", "Design and Analysis of Algorithms Lab", 2, "O", False, ""),
            ]),
            (5, [
                ("60 CB 501", "Computer Networks", 3, "A", False, ""),
                ("60 CB 502", "C# and .NET Programming", 3, "A+", False, ""),
                ("60 CB 503", "Artificial Intelligence", 3, "O", False, ""),
                ("60 IT 003", "Design Thinking", 3, "A+", False, ""),
                ("60 CB E11", "Modern Software Engineering & DevOps", 3, "O", False, ""),
                ("60 OE L02", "Open Elective-II", 3, "A", False, ""),
                ("60 CB 5P1", "Computer Networks Laboratory", 2, "O", False, ""),
                ("60 CB 5P2", "C# and .NET Programming Laboratory", 2, "O", False, ""),
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
        SubjectInsight.objects.create(student=profile, subject_name="Artificial Intelligence", grade_point=10.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="MERN Stack", grade_point=10.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="Data Structures", grade_point=9.0, status_label="Strong")
        SubjectInsight.objects.create(student=profile, subject_name="Optimization Techniques", grade_point=8.0, status_label="Good")

        # Recalculate all metrics atomically
        recalculate_student_metrics(profile)
        profile.refresh_from_db()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded demo student '{username}' ({roll_number}): "
            f"5 Semesters, CGPA={profile.current_cgpa:.2f}, Credits={profile.credits_earned}, Active Arrears={profile.backlogs_count}."
        ))
