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
    record_course_result, placement_readiness
)
from core.services.ai_service import generate_ai_advice
from core.services.security_service import (
    is_account_locked, record_failed_login, reset_login_attempts, get_lockout_message
)

def is_debug_mode():
    """Returns True if Django DEBUG is active (used by UI for demo shortcuts)."""
    return getattr(settings, 'DEBUG', False)

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

def register_user(role, fullname, username, department, password, roll_number='', semester=1, admin_key=''):
    """Registers a new user and user profile."""
    if not username or not password:
        return False, "Username and password are required."
    
    if User.objects.filter(username=username).exists():
        return False, "An account with this username already exists."

    is_staff = False
    admin_signup_key = getattr(settings, 'ADMIN_SIGNUP_KEY', '')
    if role in ['admin', 'faculty']:
        if not admin_signup_key:
            return False, "Admin signup is disabled"
        if not admin_key or not hmac.compare_digest(admin_key, admin_signup_key):
            return False, "Invalid Faculty/Admin Authorization Key."
        is_staff = True

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            password=password,
            email=username if '@' in username else f"{username}@edugrade.ai",
            is_staff=is_staff
        )
        if fullname:
            parts = fullname.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save()

        UserProfile.objects.create(
            user=user,
            role=role,
            roll_number=roll_number or ('FAC-' + username.upper() if is_staff else '7176' + username),
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

def get_faculty_overview_data():
    """Aggregates institution metrics, department stats, and audit logs."""
    students = UserProfile.objects.filter(role='student')
    total_students = students.count()

    cgpas = [float(s.current_cgpa) for s in students if s.current_cgpa > 0]
    avg_cgpa = round(sum(cgpas) / len(cgpas), 2) if cgpas else 0.0

    eligible_count = students.filter(is_placement_eligible=True).count()
    eligibility_rate = round((eligible_count / total_students * 100), 1) if total_students > 0 else 0.0

    # Department breakdown
    dept_stats = []
    departments = students.values_list('department', flat=True).distinct()
    for dept in departments:
        dept_students = students.filter(department=dept)
        count = dept_students.count()
        d_cgpas = [float(s.current_cgpa) for s in dept_students if s.current_cgpa > 0]
        dept_avg = round(sum(d_cgpas) / len(d_cgpas), 2) if d_cgpas else 0.0
        dept_stats.append({
            'department': dept,
            'student_count': count,
            'avg_cgpa': dept_avg
        })

    recent_audits = AcademicAuditLog.objects.all()[:5]

    return {
        'metrics': {
            'total_students': total_students,
            'average_cgpa': avg_cgpa,
            'eligible_count': eligible_count,
            'eligibility_rate': eligibility_rate,
            'active_regulations': '2026 Choice Based Credit System (CBCS)',
        },
        'department_stats': dept_stats,
        'recent_audits': recent_audits,
    }

def get_faculty_students_list(search='', status='all', department='all'):
    """Queries and filters student records."""
    qs = UserProfile.objects.filter(role='student').select_related('user').order_by('-current_cgpa')

    if search:
        qs = qs.filter(
            user__first_name__icontains=search
        ) | qs.filter(
            user__last_name__icontains=search
        ) | qs.filter(
            roll_number__icontains=search
        ) | qs.filter(
            user__username__icontains=search
        )

    if status == 'eligible':
        qs = qs.filter(is_placement_eligible=True)
    elif status == 'ineligible':
        qs = qs.filter(is_placement_eligible=False)

    if department != 'all':
        qs = qs.filter(department__icontains=department)

    return list(qs)

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

def save_single_course_result(action_user, roll_number, semester_number, course_code, course_name, credits, grade, grade_point):
    """Validates and persists a single student course result atomically using shared helper."""
    student_prof = UserProfile.objects.filter(roll_number=roll_number, role='student').first()
    if not student_prof:
        return False, f"Student with roll number '{roll_number}' not found."

    with transaction.atomic():
        cr, arrear_cleared = record_course_result(
            action_user=action_user,
            student_profile=student_prof,
            semester_number=int(semester_number),
            course_code=course_code,
            course_name=course_name,
            credits=int(credits),
            grade=grade,
            grade_point=grade_point,
            recalculate=True
        )

    msg = f"Course result published successfully. {'(Arrear marked as cleared)' if arrear_cleared else ''}"
    return True, msg.strip()

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

def bulk_upload_grades_csv(user, csv_text: str):
    """Processes bulk CSV text input for faculty/admin."""
    from core.services.academic_service import process_bulk_grades_csv
    return process_bulk_grades_csv(user, csv_text)

def get_admin_analytics_data():
    """Aggregates institution analytics: grade distribution, dept CGPA, at-risk students."""
    from django.db.models import Avg, Count, Q
    from core.api_views import AT_RISK_CGPA_THRESHOLD, AT_RISK_BACKLOG_THRESHOLD

    students_qs = UserProfile.objects.filter(role='student')

    # 1. Grade distribution
    grade_order = ['O', 'A+', 'A', 'B+', 'B', 'C', 'U', 'RA', 'SA', 'W']
    grade_counts = {g: 0 for g in grade_order}
    for item in CourseResult.objects.values('grade').annotate(count=Count('id')):
        g = str(item['grade']).strip().upper()
        if g in grade_counts:
            grade_counts[g] += item['count']
        elif g in ['RA', 'SA', 'W', 'U']:
            grade_counts[g] = grade_counts.get(g, 0) + item['count']

    # 2. Dept stats
    dept_stats = []
    departments = students_qs.values('department').annotate(
        student_count=Count('id'),
        avg_cgpa=Avg('current_cgpa')
    ).order_by('-student_count')

    for d in departments:
        dept_stats.append({
            'department': d['department'] or 'General',
            'student_count': d['student_count'],
            'avg_cgpa': round(float(d['avg_cgpa'] or 0.0), 2)
        })

    # 3. At-risk students
    at_risk_qs = students_qs.filter(
        Q(current_cgpa__lt=AT_RISK_CGPA_THRESHOLD) | Q(backlogs_count__gte=AT_RISK_BACKLOG_THRESHOLD)
    ).select_related('user').order_by('current_cgpa')

    at_risk_students = []
    for s in at_risk_qs:
        reasons = []
        if float(s.current_cgpa) < AT_RISK_CGPA_THRESHOLD:
            reasons.append(f"CGPA {float(s.current_cgpa):.2f} < {AT_RISK_CGPA_THRESHOLD}")
        if s.backlogs_count >= AT_RISK_BACKLOG_THRESHOLD:
            reasons.append(f"{s.backlogs_count} Active Arrears (>= {AT_RISK_BACKLOG_THRESHOLD})")

        at_risk_students.append({
            'id': s.id,
            'name': f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username,
            'roll_number': s.roll_number,
            'department': s.department,
            'current_semester': s.current_semester,
            'current_cgpa': float(s.current_cgpa),
            'backlogs_count': s.backlogs_count,
            'reason': " & ".join(reasons) if reasons else "Academic review needed"
        })

    return {
        'grade_distribution': grade_counts,
        'department_stats': dept_stats,
        'at_risk_students': at_risk_students,
        'thresholds': {
            'cgpa': AT_RISK_CGPA_THRESHOLD,
            'backlogs': AT_RISK_BACKLOG_THRESHOLD
        }
    }

def get_landing_stats():
    """Returns real counts from the database for landing page highlights without hardcoded figures."""
    students_count = UserProfile.objects.filter(role='student').count()
    grades_count = CourseResult.objects.count()
    recruiters_count = CompanyPlacementCriteria.objects.filter(is_active=True).count()
    return {
        'students_count': students_count,
        'grades_count': grades_count,
        'recruiters_count': recruiters_count,
    }




