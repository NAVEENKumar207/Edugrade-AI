"""
REST API Views for EduGrade AI Platform.
Serves modern React frontend and API clients with strict authentication,
Database transactions and deterministic calculations.
"""

import hmac
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from .models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog
)
from .services.academic_service import (
    calculate_cgpa, plan_target_cgpa, check_placement_eligibility,
    placement_readiness, record_course_result, recalculate_student_metrics,
    AT_RISK_CGPA_THRESHOLD, AT_RISK_BACKLOG_THRESHOLD, GRADE_ORDER
)
from .services.ai_service import generate_ai_advice
from .services.security_service import (
    is_account_locked, record_failed_login, reset_login_attempts, get_lockout_message
)

# ==========================================
# AUTHENTICATION APIs
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_me(request):
    """Returns the currently authenticated student's profile."""
    if not request.user.is_authenticated:
        return Response({'authenticated': False}, status=status.HTTP_200_OK)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        },
        'profile': {
            'roll_number': profile.roll_number,
            'institution_name': profile.institution_name,
            'department': profile.department,
            'syllabus_regulation': getattr(profile, 'syllabus_regulation', 'Regulation 2021 (R2021 CBCS)'),
            'current_semester': profile.current_semester,
            'current_cgpa': float(profile.current_cgpa),
            'target_cgpa': float(profile.target_cgpa),
            'credits_earned': profile.credits_earned,
            'total_credits': profile.total_credits,
            'backlogs_count': profile.backlogs_count,
            'is_placement_eligible': profile.is_placement_eligible,
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Authenticates student with attempt rate limiting."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    locked, mins = is_account_locked(username)
    if locked:
        return Response(
            {'error': get_lockout_message(mins)},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    user = authenticate(request, username=username, password=password)
    if not user:
        is_locked, mins = record_failed_login(username)
        if is_locked:
            return Response(
                {'error': get_lockout_message(mins)},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return Response(
            {'error': 'Invalid credentials. Please verify your username and password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    reset_login_attempts(username)
    login(request, user)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    return Response({
        'message': 'Login successful',
        'redirect_url': '/dashboard'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    """Registers a new student account (student-only portal)."""
    data = request.data
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    fullname = data.get('fullname', '').strip()
    department = data.get('department', 'Computer Science & Engineering')
    institution_name = data.get('institution_name', 'Anna University / Affiliated Institution').strip() or 'Anna University / Affiliated Institution'
    syllabus_regulation = data.get('syllabus_regulation', data.get('syllabus', 'Regulation 2021 (R2021 CBCS)')).strip() or 'Regulation 2021 (R2021 CBCS)'
    roll_number = data.get('roll_number', '').strip()
    semester = data.get('semester', 1)

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'An account with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

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

        profile = UserProfile.objects.create(
            user=user,
            roll_number=roll_number or ('7176' + username),
            institution_name=institution_name,
            department=department,
            syllabus_regulation=syllabus_regulation,
            current_semester=int(semester) if str(semester).isdigit() else 1,
            current_cgpa=0.00,
            target_cgpa=8.50,
            credits_earned=0,
            total_credits=160
        )

    login(request, user)
    return Response({
        'message': 'Account created successfully',
        'redirect_url': '/dashboard'
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_logout(request):
    """Logs out the active session."""
    logout(request)
    return Response({'message': 'Logged out successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """Updates password for authenticated student."""
    old_password = request.data.get('old_password', '')
    new_password = request.data.get('new_password', '')
    confirm_password = request.data.get('confirm_password', '')

    errors = {}
    if not old_password:
        errors['old_password'] = ['Old password is required.']
    elif not request.user.check_password(old_password):
        errors['old_password'] = ['Old password is incorrect.']

    if not new_password:
        errors['new_password'] = ['New password is required.']
    elif old_password and new_password == old_password:
        errors['new_password'] = ['New password must differ from old password.']
    elif len(new_password) < 8:
        errors['new_password'] = ['New password must be at least 8 characters long.']
    else:
        try:
            validate_password(new_password, user=request.user)
        except ValidationError as val_err:
            errors['new_password'] = list(val_err.messages)

    if not confirm_password:
        errors['confirm_password'] = ['Password confirmation is required.']
    elif new_password and confirm_password != new_password:
        errors['confirm_password'] = ['Passwords do not match.']

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(new_password)
    request.user.save()

    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, request.user)

    AcademicAuditLog.objects.create(
        action_by=request.user,
        action_type="Password changed",
        description="Password changed successfully"
    )

    return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)

# ==========================================
# STUDENT DASHBOARD & ACADEMICS
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_student_dashboard(request):
    """Returns complete real-time dashboard data for the authenticated student."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    semesters = list(SemesterRecord.objects.filter(student=profile).order_by('semester_number').values(
        'id', 'semester_number', 'sgpa', 'credits_earned'
    ))

    # Recalculate true cumulative CGPA only if values changed
    if semesters:
        cgpa_calc = calculate_cgpa(semesters)
        new_cgpa = cgpa_calc['cgpa']
        new_credits = int(cgpa_calc['total_credits'])
        if float(profile.current_cgpa) != float(new_cgpa) or profile.credits_earned != new_credits:
            profile.current_cgpa = new_cgpa
            profile.credits_earned = new_credits
            profile.save(update_fields=['current_cgpa', 'credits_earned'])

    insights = list(SubjectInsight.objects.filter(student=profile).values(
        'id', 'subject_name', 'grade_point', 'status_label'
    ))

    recent_courses = list(CourseResult.objects.filter(student=profile).order_by('-semester_number', 'course_code')[:8].values(
        'id', 'semester_number', 'course_code', 'course_name', 'credits', 'grade', 'grade_point'
    ))

    latest_sgpa = semesters[-1]['sgpa'] if semesters else 0.0
    readiness = placement_readiness(profile)

    return Response({
        'student': {
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
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
        'placement_readiness': dict(readiness),
        'semesters': semesters,
        'subject_insights': insights,
        'recent_courses': recent_courses,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_student_arrears(request):
    """Returns active and cleared arrears for the authenticated student."""
    from ui.services.data_service import get_arrears
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'active': [], 'cleared': []})
    data = get_arrears(profile)
    return Response(data)

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_results(request, course_id=None):
    """
    CRUD for student course results:
    GET: Returns semester results and course grades for authenticated student.
    POST: Adds single course result and recalculates metrics atomically.
    PUT: Updates existing course result.
    DELETE: Deletes course result and recalculates metrics atomically.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        semesters = SemesterRecord.objects.filter(student=profile).order_by('-semester_number')
        semester_data = []

        for sem in semesters:
            courses = CourseResult.objects.filter(student=profile, semester_number=sem.semester_number).values(
                'id', 'course_code', 'course_name', 'credits', 'grade', 'grade_point',
                'previous_grade', 'arrear_cleared', 'cleared_on'
            )
            semester_data.append({
                'semester_number': sem.semester_number,
                'sgpa': float(sem.sgpa),
                'credits_earned': sem.credits_earned,
                'courses': list(courses)
            })

        return Response({
            'student_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'roll_number': profile.roll_number,
            'department': profile.department,
            'current_cgpa': float(profile.current_cgpa),
            'credits_earned': profile.credits_earned,
            'total_credits': profile.total_credits,
            'semesters': semester_data
        })

    elif request.method == 'POST':
        data = request.data
        sem_num = data.get('semester_number') or data.get('semester')
        code = str(data.get('course_code', '')).strip().upper()
        name = str(data.get('course_name', '')).strip()
        credits_raw = data.get('credits', 3)
        grade_raw = str(data.get('grade', '')).strip().upper()

        if not sem_num or not code or not name or not grade_raw:
            return Response({'error': 'semester_number, course_code, course_name, credits, and grade are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sem_int = int(sem_num)
            if not (1 <= sem_int <= 8):
                return Response({'error': 'Semester must be between 1 and 8.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid semester number.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            credits_int = int(float(credits_raw))
            if not (1 <= credits_int <= 10):
                return Response({'error': 'Credits must be between 1 and 10.'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid credits value.'}, status=status.HTTP_400_BAD_REQUEST)

        from .services.academic_service import VALID_GRADES, GRADE_ORDER
        if grade_raw not in VALID_GRADES:
            return Response({'error': f"Invalid grade '{grade_raw}'. Allowed: {', '.join(GRADE_ORDER)}"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            cr, arrear_cleared = record_course_result(
                action_user=request.user,
                student_profile=profile,
                semester_number=sem_int,
                course_code=code,
                course_name=name,
                credits=credits_int,
                grade=grade_raw,
                recalculate=True
            )

        return Response({
            'message': 'Course result saved successfully.',
            'arrear_cleared': arrear_cleared,
            'course': {
                'id': cr.id,
                'course_code': cr.course_code,
                'course_name': cr.course_name,
                'credits': cr.credits,
                'grade': cr.grade,
                'grade_point': float(cr.grade_point),
                'arrear_cleared': cr.arrear_cleared,
                'previous_grade': cr.previous_grade
            },
            'metrics': {
                'current_cgpa': float(profile.current_cgpa),
                'credits_earned': profile.credits_earned,
                'backlogs_count': profile.backlogs_count,
                'is_placement_eligible': profile.is_placement_eligible
            }
        }, status=status.HTTP_201_CREATED)

    elif request.method == 'PUT':
        target_id = course_id or request.data.get('id') or request.data.get('course_id')
        if not target_id:
            return Response({'error': 'course_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        cr = CourseResult.objects.filter(id=target_id, student=profile).first()
        if not cr:
            return Response({'error': 'Course result not found for this student.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'course_name' in data:
            cr.course_name = str(data['course_name']).strip() or cr.course_name
        if 'course_code' in data:
            cr.course_code = str(data['course_code']).strip().upper() or cr.course_code
        if 'credits' in data:
            try:
                c_val = int(float(data['credits']))
                if 1 <= c_val <= 10:
                    cr.credits = c_val
            except (ValueError, TypeError):
                pass
        if 'grade' in data:
            new_grade = str(data['grade']).strip().upper()
            from .services.academic_service import VALID_GRADES, grade_to_point, is_failing_grade
            if new_grade in VALID_GRADES:
                from django.utils import timezone
                old_grade = cr.grade
                if is_failing_grade(old_grade) and not is_failing_grade(new_grade):
                    cr.previous_grade = old_grade[:3]
                    cr.arrear_cleared = True
                    cr.cleared_on = timezone.now()
                elif is_failing_grade(new_grade):
                    cr.arrear_cleared = False
                    cr.cleared_on = None
                cr.grade = new_grade
                cr.grade_point = grade_to_point(new_grade)

        with transaction.atomic():
            cr.save()
            recalculate_student_metrics(profile)
            AcademicAuditLog.objects.create(
                action_by=request.user,
                action_type="COURSE_RESULT_UPDATED",
                description=f"Course result {cr.course_code} updated by student {request.user.username}."
            )

        return Response({
            'message': 'Course result updated successfully.',
            'course': {
                'id': cr.id,
                'course_code': cr.course_code,
                'course_name': cr.course_name,
                'credits': cr.credits,
                'grade': cr.grade,
                'grade_point': float(cr.grade_point),
                'arrear_cleared': cr.arrear_cleared,
                'previous_grade': cr.previous_grade
            },
            'metrics': {
                'current_cgpa': float(profile.current_cgpa),
                'credits_earned': profile.credits_earned,
                'backlogs_count': profile.backlogs_count,
                'is_placement_eligible': profile.is_placement_eligible
            }
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        sem_param = request.query_params.get('semester_number') or request.query_params.get('semester') or (request.data.get('semester_number') if isinstance(request.data, dict) else None)
        target_id = course_id or request.query_params.get('id') or request.query_params.get('course_id') or (request.data.get('id') if isinstance(request.data, dict) else None)

        if sem_param and not target_id:
            from ui.services.data_service import delete_student_semester_result
            ok, msg = delete_student_semester_result(request.user, sem_param)
            if ok:
                return Response({'message': msg}, status=status.HTTP_200_OK)
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        if not target_id:
            return Response({'error': 'course_id or semester_number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        cr = CourseResult.objects.filter(id=target_id, student=profile).first()
        if not cr:
            return Response({'error': 'Course result not found for this student.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            code = cr.course_code
            cr.delete()
            recalculate_student_metrics(profile)
            AcademicAuditLog.objects.create(
                action_by=request.user,
                action_type="COURSE_RESULT_DELETED",
                description=f"Course result {code} deleted by student {request.user.username}."
            )

        return Response({'message': 'Course result deleted successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_results_sample_csv(request):
    """Returns downloadable sample CSV template for student results upload with injection hardening."""
    from django.http import HttpResponse
    from .services.academic_service import sanitize_csv_cell
    sample_rows = [
        ["semester", "course_code", "course_name", "credits", "grade"],
        [1, "HS8151", "Communicative English", 3, "A"],
        [1, "MA8151", "Engineering Mathematics - I", 4, "A+"],
        [1, "PH8151", "Engineering Physics", 3, "A"],
        [1, "CY8151", "Engineering Chemistry", 3, "B+"],
        [1, "GE8151", "Problem Solving & Python Programming", 3, "O"],
    ]
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    for r in sample_rows:
        writer.writerow([sanitize_csv_cell(c) for c in r])
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_grades_template.csv"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_results_export_csv(request):
    """Exports the authenticated student's results as a CSV file with formula injection protection."""
    from django.http import HttpResponse
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    from .services.academic_service import export_student_grades_csv
    csv_content = export_student_grades_csv(profile)
    roll = profile.roll_number or 'student'
    response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="student_grades_{roll}.csv"'
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_results_import(request):
    """
    Imports academic results from CSV for the authenticated student.
    Enforces hardening: max 1 MB, max 500 rows, UTF-8 only, and strict grade/credit validation.
    Accepts file upload (file/csv_file) or raw text (csv_text).
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    uploaded_file = request.FILES.get('file') or request.FILES.get('csv_file')
    if uploaded_file:
        if not uploaded_file.name.lower().endswith('.csv'):
            return Response({'error': 'Invalid file type. Please upload a .csv file.'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded_file.size > 1024 * 1024:
            return Response({'error': 'File size exceeds maximum limit of 1MB.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            raw_bytes = uploaded_file.read()
            if len(raw_bytes) > 1024 * 1024:
                return Response({'error': 'File size exceeds maximum limit of 1MB.'}, status=status.HTTP_400_BAD_REQUEST)
            csv_text = raw_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            return Response({'error': 'File must be UTF-8 encoded.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        csv_text = request.data.get('csv_text', '')
        if not isinstance(csv_text, str):
            csv_text = str(csv_text or '')
        try:
            raw_bytes = csv_text.encode('utf-8')
            if len(raw_bytes) > 1024 * 1024:
                return Response({'error': 'File size exceeds maximum limit of 1MB.'}, status=status.HTTP_400_BAD_REQUEST)
        except UnicodeEncodeError:
            return Response({'error': 'File must be UTF-8 encoded.'}, status=status.HTTP_400_BAD_REQUEST)

    from .services.academic_service import process_student_grades_csv
    result = process_student_grades_csv(student_profile=profile, action_user=request.user, csv_text=csv_text)
    if result.get("status_code") == 400:
        return Response({'error': result.get("error", "CSV validation failed.")}, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)

# ==========================================
# CGPA PLANNER & SIMULATOR
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_plan_cgpa(request):
    """Evaluates target CGPA feasibility and returns what-if scenario simulations."""
    data = request.data if isinstance(request.data, dict) else {}
    validation_errors = []

    def parse_numeric(val, field_name, num_type=float, default=None, min_val=None, max_val=None):
        if val is None or val == "":
            return default
        try:
            parsed = num_type(val)
            if min_val is not None and parsed < min_val:
                validation_errors.append(f"{field_name} cannot be less than {min_val}.")
            if max_val is not None and parsed > max_val:
                validation_errors.append(f"{field_name} cannot exceed {max_val}.")
            return parsed
        except (ValueError, TypeError):
            validation_errors.append(f"{field_name} must be a valid number.")
            return default

    current_cgpa = parse_numeric(data.get('current_cgpa', 8.42), 'Current CGPA', float, 8.42, 0.0, 10.0)
    completed_credits = parse_numeric(data.get('completed_credits', 98), 'Completed credits', float, 98.0, 0.0)
    target_cgpa = parse_numeric(data.get('target_cgpa', 9.00), 'Target CGPA', float, 9.00, 0.0, 10.0)

    # Explicitly check whether remaining_credits is None (supports explicitly supplied 0)
    remaining_credits = None
    if 'remaining_credits' in data and data['remaining_credits'] is not None:
        raw_rem = data['remaining_credits']
        if str(raw_rem).strip() != "":
            remaining_credits = parse_numeric(raw_rem, 'Remaining credits', float, None, 0.0)

    remaining_semesters = parse_numeric(data.get('remaining_semesters', 3), 'Remaining semesters', int, 3, 1)
    degree_total_credits = parse_numeric(data.get('total_credits', 160), 'Total degree credits', float, 160.0, 1.0)

    if validation_errors:
        return Response({
            'error': 'Invalid calculation parameters',
            'details': validation_errors
        }, status=status.HTTP_400_BAD_REQUEST)

    plan = plan_target_cgpa(
        current_cgpa=current_cgpa,
        completed_credits=completed_credits,
        target_cgpa=target_cgpa,
        remaining_credits=remaining_credits,
        remaining_semesters=remaining_semesters,
        degree_total_credits=degree_total_credits
    )

    if plan.get('status') == 'invalid':
        return Response({
            'error': 'Invalid calculation parameters',
            'details': [plan.get('message')]
        }, status=status.HTTP_400_BAD_REQUEST)

    # If authenticated, optionally persist target_cgpa update
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        request.user.profile.target_cgpa = target_cgpa
        request.user.profile.save(update_fields=['target_cgpa'])

    return Response(plan)

# ==========================================
# PLACEMENT ELIGIBILITY MATRIX
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_placement_eligibility(request):
    """Evaluates authenticated student against company placement criteria."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    companies = CompanyPlacementCriteria.objects.filter(is_active=True).order_by('-package_lpa')
    evaluated = check_placement_eligibility(profile, companies)

    eligible_count = sum(1 for c in evaluated if c['is_eligible'])
    readiness = placement_readiness(profile, eligible_count=eligible_count, total_companies=len(evaluated))

    return Response({
        'student': {
            'current_cgpa': float(profile.current_cgpa),
            'backlogs_count': profile.backlogs_count,
            'is_placement_eligible': profile.is_placement_eligible,
        },
        'placement_readiness': dict(readiness),
        'summary': {
            'total_companies': len(evaluated),
            'eligible_companies': eligible_count,
            'eligibility_rate': round((eligible_count / len(evaluated) * 100), 1) if evaluated else 0,
        },
        'companies': evaluated
    })

# ==========================================
# AI ACADEMIC ADVISOR
# ==========================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_advisor_chat(request):
    """
    GET: Retrieves conversation history for the student.
    POST: Processes prompt and returns AI advice grounded in student records.
    """
    if request.method == 'GET':
        history = AdvisorChatMessage.objects.filter(user=request.user).order_by('timestamp').values(
            'id', 'sender', 'message', 'timestamp'
        )
        return Response({'history': list(history)})

    profile = getattr(request.user, 'profile', None)
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Message cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

    # Save user message to history
    AdvisorChatMessage.objects.create(
        user=request.user,
        sender='user',
        message=message
    )

    # Generate grounded advice
    advice_res = generate_ai_advice(profile, message)
    reply_text = advice_res.get('response', 'I am here to guide your academic journey.')

    # Save AI response to history
    AdvisorChatMessage.objects.create(
        user=request.user,
        sender='ai',
        message=reply_text
    )

    return Response({
        'reply': reply_text,
        'source': advice_res.get('source'),
        'context_used': advice_res.get('context_used', False)
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_advisor_clear_history(request):
    """Deletes conversation chat history only for the calling user."""
    count, _ = AdvisorChatMessage.objects.filter(user=request.user).delete()
    AcademicAuditLog.objects.create(
        action_by=request.user,
        action_type="CLEAR_CHAT_HISTORY",
        description=f"Cleared {count} advisor messages for {request.user.username}."
    )
    return Response({'message': f'Cleared {count} chat messages successfully.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_transcript_pdf(request):
    """
    Generates and downloads an academic transcript in PDF format for the authenticated student.
    Strict data isolation: students can only access their own transcript.
    """
    from django.http import HttpResponse
    from .services.pdf_service import generate_transcript_pdf

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    student_id = request.GET.get('student_id')
    if student_id and str(student_id) not in [str(user_profile.id), str(request.user.id), user_profile.roll_number]:
        return Response({'error': 'Students can only access their own transcript.'}, status=status.HTTP_403_FORBIDDEN)

    target_profile = user_profile

    semester_filter = None
    sem_param = request.GET.get('semester')
    if sem_param:
        try:
            s_val = int(sem_param)
            if 1 <= s_val <= 8:
                semester_filter = s_val
        except (ValueError, TypeError):
            pass

    pdf_bytes = generate_transcript_pdf(target_profile, semester_filter=semester_filter)
    filename = f"transcript_{target_profile.roll_number or 'student'}.pdf"

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# ==========================================
# DIGITAL TWIN & CAREER READINESS APIS
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_twin_simulate(request):
    """
    Monte Carlo academic future trajectory simulation.
    Validates target CGPA (0.00-10.00) and effort ('lower', 'same', 'higher').
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    req_student_id = request.data.get('student_id')
    if req_student_id is not None and int(req_student_id) != profile.id:
        return Response({'error': 'You can only simulate your own academic profile.'}, status=status.HTTP_403_FORBIDDEN)

    target_cgpa = request.data.get('target_cgpa')
    effort = str(request.data.get('effort', 'same')).strip().lower()

    if target_cgpa is None:
        return Response({'error': 'target_cgpa is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_val = float(target_cgpa)
        if target_val < 0.0 or target_val > 10.0:
            return Response({'error': 'Target CGPA must be between 0.00 and 10.00.'}, status=status.HTTP_400_BAD_REQUEST)
    except (TypeError, ValueError):
        return Response({'error': 'Target CGPA must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)

    if effort not in ['lower', 'same', 'higher']:
        return Response({'error': 'Effort must be one of: lower, same, higher.'}, status=status.HTTP_400_BAD_REQUEST)

    seed = request.data.get('seed')
    if seed is not None:
        try:
            seed = int(seed)
        except (ValueError, TypeError):
            seed = None

    from core.services.twin_service import simulate_future
    result = simulate_future(profile, target_cgpa=target_val, effort=effort, seed=seed)
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_twin_next_moves(request):
    """
    Ranks arrear clearing impact on CGPA and placement company eligibility without altering stored records.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    grade = request.query_params.get('grade', 'B').strip().upper()
    if grade not in ['C', 'B', 'A']:
        return Response({'error': 'Assumed grade must be one of: C, B, A.'}, status=status.HTTP_400_BAD_REQUEST)

    from core.services.twin_service import rank_next_moves
    try:
        moves = rank_next_moves(profile, assumed_grade=grade)
        return Response({'moves': moves, 'assumed_grade': grade}, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_marks_target(request):
    """
    Calculates marks target paper requirements or evaluates expected grade based on institutional regulation.
    Available to any authenticated user.
    """
    from core.services.academic_service import required_marks, evaluate_expected_marks

    internal = request.data.get('internal')
    if internal is None:
        internal = request.data.get('internal_marks')
    if internal is None:
        return Response({'error': 'internal marks is required.'}, status=status.HTTP_400_BAD_REQUEST)

    paper_marks = request.data.get('paper_marks')
    target_grade = request.data.get('target_grade')
    mode = request.data.get('mode')

    try:
        if paper_marks is not None or mode == 'expected':
            if paper_marks is None:
                return Response({'error': 'paper_marks is required in expected mode.'}, status=status.HTTP_400_BAD_REQUEST)
            res = evaluate_expected_marks(internal, paper_marks)
            return Response(res, status=status.HTTP_200_OK)
        else:
            if not target_grade:
                return Response({'error': 'target_grade is required in target mode.'}, status=status.HTTP_400_BAD_REQUEST)
            res = required_marks(internal, target_grade)
            return Response(res, status=status.HTTP_200_OK)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_skills(request):
    """
    Returns the student's credit-weighted skill scores and company fit assessment.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    from core.services.skill_service import skill_scores, company_skill_match, evaluate_placement_fit
    from core.models import CompanyPlacementCriteria

    scores = skill_scores(profile)
    companies = list(CompanyPlacementCriteria.objects.filter(is_active=True).order_by('-package_lpa'))

    evaluations = []
    for comp in companies:
        match_res = company_skill_match(profile, comp, scores=scores)
        fit_res = evaluate_placement_fit(profile, comp, match_res)
        evaluations.append(fit_res)

    return Response({
        'skills': scores,
        'companies': evaluations
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_verify_transcript(request, token):
    """Public verification endpoint returning cryptographically validated transcript snapshot."""
    from core.services.transcript_service import verify_transcript_token
    ctx = verify_transcript_token(token)
    stat = status.HTTP_200_OK if ctx.get('is_valid') else status.HTTP_404_NOT_FOUND
    return Response(ctx, status=stat)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_journey(request):
    """Returns chronological academic journey timeline and earned/locked badges."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Student profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    from core.services.journey_service import get_journey, get_badges
    from core.models import SemesterRecord, CourseResult
    sem_records = list(SemesterRecord.objects.filter(student=profile).order_by('semester_number'))
    courses = list(CourseResult.objects.filter(student=profile))
    journey = get_journey(profile, sem_records=sem_records, courses=courses)
    badges = get_badges(profile, sem_records=sem_records, courses=courses)

    return Response({
        'journey': journey,
        'badges': badges
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """Database and service health endpoint."""
    return Response({
        'status': 'healthy',
        'platform': 'EduGrade AI - Academic Intelligence Platform',
        'version': '2.0.0',
        'database': 'sqlite3'
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_demo_prepare(request):
    """Prepares clean demo student state before presentation tour starts."""
    from ui.services.data_service import prepare_demo_environment, is_demo_mode_enabled
    if not is_demo_mode_enabled():
        return Response({'success': False, 'error': 'Demo mode is disabled in settings.'}, status=status.HTTP_403_FORBIDDEN)
    success, msg = prepare_demo_environment()
    return Response({'status': 'ok' if success else 'error', 'success': success, 'message': msg})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_demo_cleanup(request):
    """Cleans up test records created during automated demo presentation."""
    from ui.services.data_service import cleanup_demo_environment
    success, msg = cleanup_demo_environment()
    return Response({'status': 'ok' if success else 'error', 'success': success, 'message': msg})
