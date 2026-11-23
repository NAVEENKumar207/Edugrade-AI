"""
Data Service for EduGrade AI ReactPy Frontend.
Interfaces ReactPy components with Django ORM, authentication, and
the deterministic academic calculation engine.
"""

import os
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

import hmac
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from core.models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog
)
from core.services.academic_service import (
    calculate_cgpa, check_placement_eligibility,
    record_course_result, placement_readiness, GRADE_ORDER
)
from core.services.ai_service import generate_ai_advice
from core.services.security_service import (
    is_account_locked, record_failed_login, reset_login_attempts, get_lockout_message
)

def is_debug_mode():
    """Returns True if Django DEBUG is active (used by UI for demo shortcuts)."""
    return getattr(settings, 'DEBUG', False)

def quick_demo_login(role='student'):
    """
    1-Click Demo Access for development / DEBUG mode.
    Auto-provisions the demo student account (with realistic semester results and telemetry)
    if it does not yet exist, and logs in immediately without manual credential entry.
    """
    user = User.objects.filter(username__in=['demo_student', 'student01']).first()
    password = 'student123'

    if not user:
        try:
            from django.core.management import call_command
            call_command('seed_demo_student')
            user = User.objects.filter(username='demo_student').first()
        except Exception:
            pass

    if not user:
        username = 'student01'
        with transaction.atomic():
            user = User.objects.create_user(
                username='student01',
                password='student123',
                email='student01@edugrade.ai',
                first_name='Kavitha',
                last_name='Ramesh',
                is_staff=False
            )
            profile = UserProfile.objects.create(
                user=user,
                roll_number='717622CS041',
                department='Computer Science & Engineering',
                current_semester=6,
                current_cgpa=8.42,
                target_cgpa=9.00,
                credits_earned=88,
                total_credits=160,
                backlogs_count=0,
                is_placement_eligible=True
            )
            sample_courses = [
                (1, "CS101", "Problem Solving & Python Programming", 4, "A+", 9.0),
                (1, "MA101", "Matrices and Calculus", 4, "A", 8.0),
                (1, "PH101", "Engineering Physics", 3, "A", 8.0),
                (1, "CY101", "Engineering Chemistry", 3, "B+", 7.0),
                (1, "GE101", "Engineering Graphics", 4, "A", 8.0),
                (1, "GE102", "Python Programming Lab", 2, "O", 10.0),
                (1, "BS101", "Physics & Chemistry Lab", 2, "O", 10.0),

                (2, "CS201", "Data Structures", 4, "A+", 9.0),
                (2, "MA201", "Statistics and Linear Algebra", 4, "A", 8.0),
                (2, "CS202", "Digital Principles & System Design", 3, "A", 8.0),
                (2, "CS203", "Programming in C", 3, "A+", 9.0),
                (2, "GE201", "Environmental Science", 3, "B+", 7.0),
                (2, "CS204", "Data Structures Lab", 2, "O", 10.0),
                (2, "CS205", "C Programming Lab", 2, "O", 10.0),

                (3, "CS301", "Design and Analysis of Algorithms", 4, "A+", 9.0),
                (3, "CS302", "Database Management Systems", 4, "O", 10.0),
                (3, "CS303", "Operating Systems", 3, "A", 8.0),
                (3, "MA301", "Discrete Mathematics", 4, "B+", 7.0),
                (3, "CS304", "Software Engineering", 3, "A", 8.0),
                (3, "CS305", "DBMS Laboratory", 2, "O", 10.0),
                (3, "CS306", "Operating Systems Lab", 2, "A+", 9.0),

                (4, "CS401", "Computer Networks", 4, "A", 8.0),
                (4, "CS402", "Object Oriented Analysis & Design", 3, "A", 8.0),
                (4, "CS403", "Theory of Computation", 4, "B+", 7.0),
                (4, "CS404", "Artificial Intelligence & ML", 4, "O", 10.0),
                (4, "CS405", "Web Technology", 3, "A+", 9.0),
                (4, "CS406", "Networks & Web Lab", 2, "O", 10.0),
                (4, "CS407", "AI & ML Laboratory", 2, "O", 10.0),
            ]
            sem_totals = {}
            for s_num, code, name, cr, gr, gp in sample_courses:
                if s_num not in sem_totals:
                    sem_totals[s_num] = {'points': 0.0, 'credits': 0}
                sem_totals[s_num]['points'] += float(gp) * cr
                sem_totals[s_num]['credits'] += cr

            for s_num, totals in sem_totals.items():
                sgpa = round(totals['points'] / totals['credits'], 2) if totals['credits'] > 0 else 8.0
                sem_rec, _ = SemesterRecord.objects.get_or_create(
                    student=profile,
                    semester_number=s_num,
                    defaults={'sgpa': sgpa, 'credits_earned': totals['credits']}
                )
                for sem_n, code, name, cr, gp_grade, gp in sample_courses:
                    if sem_n == s_num:
                        CourseResult.objects.create(
                            student=profile,
                            semester_record=sem_rec,
                            semester_number=s_num,
                            course_code=code,
                            course_name=name,
                            credits=cr,
                            grade=gp_grade,
                            grade_point=gp
                        )
            SubjectInsight.objects.get_or_create(
                student=profile,
                subject_name="Database Management Systems",
                defaults={'grade_point': 10.0, 'status_label': 'Strong'}
            )
            SubjectInsight.objects.get_or_create(
                student=profile,
                subject_name="Artificial Intelligence & ML",
                defaults={'grade_point': 10.0, 'status_label': 'Strong'}
            )
            SubjectInsight.objects.get_or_create(
                student=profile,
                subject_name="Data Structures",
                defaults={'grade_point': 9.0, 'status_label': 'Strong'}
            )
            SubjectInsight.objects.get_or_create(
                student=profile,
                subject_name="Theory of Computation",
                defaults={'grade_point': 7.0, 'status_label': 'Good'}
            )
    else:
        username = user.username
        if not user.check_password(password):
            user.set_password(password)
            user.save()

    reset_login_attempts(username)
    auth_user = authenticate(username=username, password=password)
    return (auth_user or user), None

def authenticate_user(username, password):
    """Authenticates username and password with attempt limiting. Returns (user, error_message)."""
    clean_username = (username or '').strip()
    locked, mins = is_account_locked(clean_username)
    if locked:
        return None, get_lockout_message(mins)
    user = authenticate(username=clean_username, password=password)
    if user:
        reset_login_attempts(clean_username)
        return user, None
    else:
        is_locked, mins = record_failed_login(clean_username)
        if is_locked:
            return None, get_lockout_message(mins)
        return None, "Invalid credentials. Please verify your username and password."

def change_user_password(user, old_password, new_password, confirm_password):
    """Validates and updates user password with audit logging."""
    if not old_password:
        return False, "Current password is required."
    if not user.check_password(old_password):
        return False, "Current password is incorrect."
    if not new_password:
        return False, "New password is required."
    if old_password == new_password:
        return False, "New password must differ from current password."
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters long."
    if new_password != confirm_password:
        return False, "New password and confirmation do not match."

    try:
        validate_password(new_password, user=user)
    except ValidationError as err:
        return False, " ".join(err.messages)
    
    user.set_password(new_password)
    user.save()

    AcademicAuditLog.objects.create(
        action_by=user,
        action_type="Password changed",
        description="Password changed successfully"
    )
    return True, "Password changed successfully."

def register_user(username, password, fullname='', department='Computer Science & Engineering', roll_number='', semester=1, **kwargs):
    """Registers a new student user and student profile."""
    if not username or not password:
        return False, "Username and password are required."
    
    if User.objects.filter(username=username).exists():
        return False, "An account with this username already exists."

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            password=password,
            email=username if '@' in username else f"{username}@edugrade.ai",
            is_staff=False
        )
        if fullname:
            parts = fullname.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save()

        UserProfile.objects.create(
            user=user,
            roll_number=roll_number or ('7176' + username),
            department=department,
            current_semester=int(semester) if str(semester).isdigit() else 1,
            current_cgpa=0.00,
            target_cgpa=8.50,
            credits_earned=0,
            total_credits=160
        )

    return True, user

def get_student_dashboard_data(user):
    """Retrieves live metrics, semesters, subject insights, and recent courses for student."""
    profile = getattr(user, 'profile', None)
    if not profile:
        profile, _ = UserProfile.objects.get_or_create(user=user)

    semesters = list(SemesterRecord.objects.filter(student=profile).order_by('semester_number'))
    
    # Recalculate CGPA
    if semesters:
        cgpa_calc = calculate_cgpa([{'sgpa': s.sgpa, 'credits_earned': s.credits_earned} for s in semesters])
        profile.current_cgpa = cgpa_calc['cgpa']
        profile.credits_earned = int(cgpa_calc['total_credits'])
        profile.save(update_fields=['current_cgpa', 'credits_earned'])

    insights = list(SubjectInsight.objects.filter(student=profile))
    recent_courses = list(CourseResult.objects.filter(student=profile).order_by('-semester_number', 'course_code')[:8])

    latest_sgpa = semesters[-1].sgpa if semesters else 0.0
    readiness = placement_readiness(profile)

    return {
        'student': {
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'roll_number': profile.roll_number,
            'department': profile.department,
            'current_semester': profile.current_semester,
            'current_cgpa': float(profile.current_cgpa),
            'latest_sgpa': float(latest_sgpa),
            'target_cgpa': float(profile.target_cgpa),
            'credits_earned': profile.credits_earned,
            'total_credits': profile.total_credits,
            'backlogs_count': profile.backlogs_count,
            'is_placement_eligible': profile.is_placement_eligible,
        },
        'placement_readiness': readiness,
        'semesters': semesters,
        'subject_insights': insights,
        'recent_courses': recent_courses,
    }

def get_semester_results_data(user):
    """Retrieves detailed semester records and course breakdown."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return {'semesters': []}

    semesters = SemesterRecord.objects.filter(student=profile).order_by('-semester_number')
    semester_data = []

    for sem in semesters:
        courses = CourseResult.objects.filter(student=profile, semester_number=sem.semester_number)
        semester_data.append({
            'semester_number': sem.semester_number,
            'sgpa': float(sem.sgpa),
            'credits_earned': sem.credits_earned,
            'courses': list(courses)
        })

    return {
        'student_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'roll_number': profile.roll_number,
        'department': profile.department,
        'current_cgpa': float(profile.current_cgpa),
        'credits_earned': profile.credits_earned,
        'total_credits': profile.total_credits,
        'semesters': semester_data
    }

def get_placement_matrix_data(user):
    """Evaluates authenticated student against company criteria."""
    profile = getattr(user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.first()

    companies = CompanyPlacementCriteria.objects.filter(is_active=True).order_by('-package_lpa')
    evaluated = check_placement_eligibility(profile, companies) if profile else []
    eligible_count = sum(1 for c in evaluated if c['is_eligible'])

    student_name = f"{user.first_name} {user.last_name}".strip() or getattr(user, 'username', 'Student') if user else 'Student'
    readiness = placement_readiness(profile, eligible_count=eligible_count, total_companies=len(evaluated)) if profile else None

    return {
        'student': {
            'name': student_name,
            'current_cgpa': float(profile.current_cgpa) if profile else 0.0,
            'backlogs_count': profile.backlogs_count if profile else 0,
            'is_placement_eligible': profile.is_placement_eligible if profile else True,
        },
        'placement_readiness': readiness,
        'summary': {
            'total_companies': len(evaluated),
            'eligible_companies': eligible_count,
            'eligible_count': eligible_count,
            'ineligible_count': len(evaluated) - eligible_count,
            'eligibility_rate': round((eligible_count / len(evaluated) * 100), 1) if evaluated else 0,
        },
        'companies': evaluated
    }

def get_advisor_messages(user):
    """Retrieves chat history."""
    return list(AdvisorChatMessage.objects.filter(user=user).order_by('timestamp'))

def send_advisor_chat_message(user, text):
    """Saves user message, generates intelligent advice, saves AI response."""
    AdvisorChatMessage.objects.create(user=user, sender='user', message=text)
    profile = getattr(user, 'profile', None)
    advice_res = generate_ai_advice(profile, text)
    reply_text = advice_res.get('response', 'I am here to assist your academic journey.')
    source = advice_res.get('source', 'rule_based')
    AdvisorChatMessage.objects.create(user=user, sender='ai', message=reply_text)
    return {'reply': reply_text, 'source': source}

def clear_advisor_chat_history(user):
    """Clears all conversation messages for user and logs audit."""
    count, _ = AdvisorChatMessage.objects.filter(user=user).delete()
    AcademicAuditLog.objects.create(
        action_by=user if getattr(user, 'is_authenticated', False) else None,
        action_type="CLEAR_CHAT_HISTORY",
        description=f"Cleared {count} chat messages."
    )
    return True

def get_arrears(student):
    """
    Returns active and cleared arrears for student (User or UserProfile).
    active: list of dicts with course_code, course_name, semester, grade.
    cleared: list of dicts with course_code, course_name, semester, previous_grade, current_grade, cleared_on.
    """
    if hasattr(student, 'profile'):
        profile = student.profile
    elif isinstance(student, UserProfile):
        profile = student
    else:
        profile = UserProfile.objects.filter(user=student).first()

    if not profile:
        return {'active': [], 'cleared': []}

    failing_grades = ['U', 'RA', 'SA', 'W', 'u', 'ra', 'sa', 'w']
    active_qs = CourseResult.objects.filter(student=profile, grade__in=failing_grades).order_by('semester_number', 'course_code')
    cleared_qs = CourseResult.objects.filter(student=profile, arrear_cleared=True).order_by('-cleared_on', 'semester_number')

    active = []
    for c in active_qs:
        active.append({
            'id': c.id,
            'course_code': c.course_code,
            'course_name': c.course_name,
            'semester': c.semester_number,
            'grade': c.grade,
        })

    cleared = []
    for c in cleared_qs:
        cleared.append({
            'id': c.id,
            'course_code': c.course_code,
            'course_name': c.course_name,
            'semester': c.semester_number,
            'previous_grade': c.previous_grade,
            'current_grade': c.grade,
            'cleared_on': c.cleared_on.strftime('%Y-%m-%d') if c.cleared_on else '',
        })

    return {'active': active, 'cleared': cleared}

def save_student_course_result(user, semester_number, course_code, course_name, credits, grade):
    """Validates and persists a student-owned course result atomically."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return False, "Student profile not found."
    from core.services.academic_service import grade_to_point
    g_clean = str(grade).strip().upper()
    gp = grade_to_point(g_clean)
    try:
        with transaction.atomic():
            cr, arrear_cleared = record_course_result(
                action_user=user,
                student_profile=profile,
                semester_number=int(semester_number),
                course_code=str(course_code).strip().upper(),
                course_name=str(course_name).strip(),
                credits=int(credits),
                grade=g_clean,
                grade_point=gp,
                recalculate=True
            )
        msg = f"Course result saved successfully. {'(Arrear marked as cleared)' if arrear_cleared else ''}"
        return True, msg.strip()
    except Exception as e:
        return False, str(e)

def update_student_course_result(user, course_id, semester_number, course_code, course_name, credits, grade):
    """Updates an existing student-owned course result atomically with recalculation."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return False, "Student profile not found."
    cr = CourseResult.objects.filter(id=course_id, student=profile).first()
    if not cr:
        return False, "Course result record not found or not owned by student."
    from core.services.academic_service import grade_to_point
    g_clean = str(grade).strip().upper()
    gp = grade_to_point(g_clean)
    try:
        with transaction.atomic():
            failing = ['U', 'RA', 'SA', 'W']
            passing = ['O', 'A+', 'A', 'B+', 'B', 'C']
            if cr.grade in failing and g_clean in passing:
                cr.arrear_cleared = True
                cr.previous_grade = cr.grade
                from django.utils import timezone
                cr.cleared_on = timezone.now()
            cr.semester_number = int(semester_number)
            cr.course_code = str(course_code).strip().upper()
            cr.course_name = str(course_name).strip()
            cr.credits = int(credits)
            cr.grade = g_clean
            cr.grade_point = gp
            cr.save()
            from core.services.academic_service import recalculate_student_metrics
            recalculate_student_metrics(profile)
        return True, "Course result updated successfully."
    except Exception as e:
        return False, str(e)

def delete_student_course_result(user, course_id):
    """Deletes a student-owned course result atomically with recalculation."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return False, "Student profile not found."
    cr = CourseResult.objects.filter(id=course_id, student=profile).first()
    if not cr:
        return False, "Course result record not found or not owned by student."
    try:
        with transaction.atomic():
            cr.delete()
            from core.services.academic_service import recalculate_student_metrics
            recalculate_student_metrics(profile)
        return True, "Course result deleted successfully."
    except Exception as e:
        return False, str(e)

def import_student_grades_csv(user, csv_text: str):
    """Processes student-owned CSV grade import."""
    from core.services.academic_service import process_student_grades_csv
    return process_student_grades_csv(user, csv_text)

def update_user_profile(user, first_name=None, last_name=None, email=None, target_cgpa=None, department=None):
    """Updates user and user profile details."""
    try:
        profile = getattr(user, 'profile', None)
        if not profile:
            return False, "Profile not found."

        if first_name is not None:
            user.first_name = first_name.strip()
        if last_name is not None:
            user.last_name = last_name.strip()
        if email is not None and email.strip():
            user.email = email.strip()
        user.save()

        if target_cgpa is not None:
            try:
                tg = float(target_cgpa)
                if 0.0 <= tg <= 10.0:
                    profile.target_cgpa = tg
            except (ValueError, TypeError):
                pass

        if department is not None and department.strip():
            profile.department = department.strip()

        profile.save()
        return True, "Profile details updated successfully."
    except Exception as e:
        return False, str(e)

def get_landing_stats():
    """Returns real counts from the database for landing page highlights without hardcoded figures."""
    students_count = UserProfile.objects.count()
    grades_count = CourseResult.objects.count()
    recruiters_count = CompanyPlacementCriteria.objects.filter(is_active=True).count()
    return {
        'students_count': students_count,
        'grades_count': grades_count,
        'recruiters_count': recruiters_count,
    }


# ==========================================
# DIGITAL TWIN & CAREER READINESS BRIDGES
# ==========================================

def get_student_profile(user):
    """Retrieves student UserProfile instance for authenticated user."""
    if not user or not user.is_authenticated:
        return None
    return getattr(user, 'profile', None)

def run_digital_twin_simulation(user, target_cgpa, effort="same", seed=None):
    """Executes Monte Carlo academic simulation for current student."""
    profile = get_student_profile(user)
    if not profile:
        return {"enough_data": False, "message": "Student profile not found."}
    from core.services.twin_service import simulate_future
    return simulate_future(profile, target_cgpa=float(target_cgpa), effort=effort, seed=seed)

def get_next_moves(user, assumed_grade="B"):
    """Fetches ranked Next Best Move list for active arrears."""
    profile = get_student_profile(user)
    if not profile:
        return []
    from core.services.twin_service import rank_next_moves
    try:
        return rank_next_moves(profile, assumed_grade=assumed_grade)
    except Exception:
        return []

def calculate_marks_target_bridge(internal, target_grade=None, paper_marks=None, mode="target"):
    """Calculates marks target required paper score or evaluates expected grade."""
    from core.services.academic_service import required_marks, evaluate_expected_marks
    if paper_marks is not None or mode == 'expected':
        return evaluate_expected_marks(internal, paper_marks)
    return required_marks(internal, target_grade)

def get_skills_and_fit(user):
    """Returns acquired skill scores and corporate fit analysis for student."""
    profile = get_student_profile(user)
    if not profile:
        return {'skills': {}, 'companies': []}
    from core.services.skill_service import skill_scores, company_skill_match, evaluate_placement_fit
    scores = skill_scores(profile)
    companies = list(CompanyPlacementCriteria.objects.filter(is_active=True).order_by('-package_lpa'))
    evaluations = []
    for comp in companies:
        m = company_skill_match(profile, comp)
        fit = evaluate_placement_fit(profile, comp, m)
        evaluations.append(fit)
    return {'skills': scores, 'companies': evaluations}

def get_journey_and_badges(user):
    """Returns chronological journey timeline and earned milestone badges."""
    profile = get_student_profile(user)
    if not profile:
        return {'journey': [], 'badges': {'earned_badges': [], 'locked_badges': [], 'all_badges': []}}
    from core.services.journey_service import get_journey, get_badges
    return {
        'journey': get_journey(profile),
        'badges': get_badges(profile)
    }

def get_student_trend_alert(user):
    """Evaluates student academic trajectory risk & predicted SGPA for personal dashboard alert card."""
    profile = get_student_profile(user)
    if not profile:
        return {
            'predicted_next_sgpa': None,
            'trend': 'steady',
            'risk_level': 'low',
            'reasons': ['Consistent academic standing']
        }
    from core.services.journey_service import evaluate_student_risk
    return evaluate_student_risk(profile)






