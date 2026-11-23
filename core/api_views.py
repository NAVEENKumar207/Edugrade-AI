"""
REST API Views for EduGrade AI Platform.
Serves modern React frontend and API clients with strict authentication,
role-based permissions, database transactions, and deterministic calculations.
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

def require_admin(request, message="Faculty or admin access required."):
    """Helper returning HTTP 403 Response if user is not faculty/admin, else None."""
    profile = getattr(request.user, 'profile', None)
    if not profile or not profile.is_admin():
        return Response({'error': message}, status=status.HTTP_403_FORBIDDEN)
    return None


# ==========================================
# AUTHENTICATION APIs
# ==========================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_me(request):
    """Returns the currently authenticated user's profile and role."""
    if not request.user.is_authenticated:
        return Response({'authenticated': False}, status=status.HTTP_200_OK)

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'admin' if request.user.is_staff else 'student'}
    )
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
        },
        'profile': {
            'role': profile.role,
            'roll_number': profile.roll_number,
            'department': profile.department,
            'current_semester': profile.current_semester,
            'current_cgpa': float(profile.current_cgpa),
            'target_cgpa': float(profile.target_cgpa),
            'credits_earned': profile.credits_earned,
            'total_credits': profile.total_credits,
            'backlogs_count': profile.backlogs_count,
            'is_placement_eligible': profile.is_placement_eligible,
            'is_admin': profile.is_admin(),
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Authenticates student or faculty/admin with attempt rate limiting."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    selected_role = request.data.get('role', 'student')

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
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': selected_role}
    )

    return Response({
        'message': 'Login successful',
        'role': profile.role,
        'is_admin': profile.is_admin(),
        'redirect_url': '/admin-dashboard' if profile.is_admin() else '/dashboard'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    """Registers a new student or faculty/admin account."""
    data = request.data
    role = data.get('role', 'student')
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    fullname = data.get('fullname', '').strip()
    department = data.get('department', 'Computer Science & Engineering')
    roll_number = data.get('roll_number', '').strip()
    semester = data.get('semester', 1)
    admin_key = data.get('admin_key', '').strip()

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'An account with this username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    is_staff = False
    admin_signup_key = getattr(settings, 'ADMIN_SIGNUP_KEY', '')
    if role in ['admin', 'faculty']:
        if not admin_signup_key:
            return Response({'error': 'Admin signup is disabled'}, status=status.HTTP_403_FORBIDDEN)
        if not admin_key or not hmac.compare_digest(admin_key, admin_signup_key):
            return Response({'error': 'Invalid Faculty/Admin Authorization Key.'}, status=status.HTTP_403_FORBIDDEN)
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

        profile = UserProfile.objects.create(
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

    login(request, user)
    return Response({
        'message': 'Account created successfully',
        'role': profile.role,
        'is_admin': profile.is_admin(),
        'redirect_url': '/admin-dashboard' if profile.is_admin() else '/dashboard'
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
    """Updates password for authenticated student or faculty."""
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
        'id', 'semester_number', 'sgpa', 'credits_earned', 'is_published'
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_results(request):
    """Returns detailed semester results and course grades."""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    semesters = SemesterRecord.objects.filter(student=profile).order_by('-semester_number')
    semester_data = []

    for sem in semesters:
        courses = CourseResult.objects.filter(student=profile, semester_number=sem.semester_number).values(
            'id', 'course_code', 'course_name', 'credits', 'grade', 'grade_point', 'is_published'
        )
        semester_data.append({
            'semester_number': sem.semester_number,
            'sgpa': float(sem.sgpa),
            'credits_earned': sem.credits_earned,
            'is_published': sem.is_published,
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


# ==========================================
# FACULTY / ADMIN WORKFLOWS
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_faculty_overview(request):
    """Returns department and institution-wide metrics for faculty/admin."""
    err = require_admin(request, 'Unauthorized: Faculty access required')
    if err:
        return err

    from django.db.models import Avg, Count, Q

    students = UserProfile.objects.filter(role='student')
    agg = students.aggregate(
        total_students=Count('id'),
        avg_cgpa=Avg('current_cgpa', filter=Q(current_cgpa__gt=0)),
        eligible_count=Count('id', filter=Q(is_placement_eligible=True))
    )
    total_students = agg['total_students']
    avg_cgpa = round(float(agg['avg_cgpa'] or 0.0), 2)
    eligible_count = agg['eligible_count']
    eligibility_rate = round((eligible_count / total_students * 100), 1) if total_students > 0 else 0.0

    dept_qs = students.values('department').annotate(
        count=Count('id'),
        avg_cgpa=Avg('current_cgpa', filter=Q(current_cgpa__gt=0))
    ).order_by('department')

    dept_stats = [
        {
            'department': d['department'],
            'student_count': d['count'],
            'avg_cgpa': round(float(d['avg_cgpa'] or 0.0), 2)
        }
        for d in dept_qs
    ]

    recent_audits = AcademicAuditLog.objects.all()[:5].values(
        'action_type', 'description', 'timestamp'
    )

    return Response({
        'metrics': {
            'total_students': total_students,
            'average_cgpa': avg_cgpa,
            'eligible_count': eligible_count,
            'eligibility_rate': eligibility_rate,
            'active_regulations': '2026 Choice Based Credit System (CBCS)',
        },
        'department_stats': dept_stats,
        'recent_audits': list(recent_audits)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_faculty_students(request):
    """Lists student records with search and placement status filter."""
    err = require_admin(request, 'Unauthorized: Faculty access required')
    if err:
        return err

    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    dept_filter = request.GET.get('department', 'all')

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

    if status_filter == 'eligible':
        qs = qs.filter(is_placement_eligible=True)
    elif status_filter == 'ineligible':
        qs = qs.filter(is_placement_eligible=False)

    if dept_filter != 'all':
        qs = qs.filter(department__icontains=dept_filter)

    results = []
    for s in qs:
        results.append({
            'id': s.id,
            'user_id': s.user.id,
            'name': f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username,
            'roll_number': s.roll_number,
            'department': s.department,
            'current_semester': s.current_semester,
            'current_cgpa': float(s.current_cgpa),
            'credits_earned': s.credits_earned,
            'backlogs_count': s.backlogs_count,
            'is_placement_eligible': s.is_placement_eligible,
        })

    return Response({'students': results})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_faculty_upload_results(request):
    """
    Validates and imports student semester results in bulk.
    Guarantees atomic transaction and creates audit record.
    """
    err = require_admin(request, 'Unauthorized: Faculty access required')
    if err:
        return err

    data = request.data
    records = data.get('records', [])
    if not records:
        return Response({'error': 'No academic records provided for upload'}, status=status.HTTP_400_BAD_REQUEST)

    success_count = 0
    errors = []

    try:
        with transaction.atomic():
            for idx, item in enumerate(records):
                roll = item.get('roll_number', '').strip()
                sem_num = item.get('semester_number')
                courses = item.get('courses', [])

                if not roll or not sem_num:
                    errors.append(f"Row {idx+1}: Missing roll number or semester number.")
                    continue

                student_prof = UserProfile.objects.filter(roll_number=roll, role='student').first()
                if not student_prof:
                    errors.append(f"Row {idx+1}: Student with roll number '{roll}' does not exist.")
                    continue

                for c in courses:
                    record_course_result(
                        action_user=request.user,
                        student_profile=student_prof,
                        semester_number=int(sem_num),
                        course_code=c.get('code', 'GEN01'),
                        course_name=c.get('name', 'Course Subject'),
                        credits=int(c.get('credits', 3)),
                        grade=c.get('grade', 'A'),
                        grade_point=float(c.get('grade_point', 8.0)),
                        recalculate=False
                    )

                recalculate_student_metrics(student_prof)
                success_count += 1

            # Log audit
            AcademicAuditLog.objects.create(
                action_by=request.user,
                action_type='BULK_RESULT_IMPORT',
                description=f"Imported results for {success_count} student(s) by faculty {request.user.username}."
            )

    except Exception as e:
        return Response({'error': f"Import transaction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'message': f"Successfully processed results for {success_count} student(s).",
        'success_count': success_count,
        'errors': errors
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_grades_sample_csv(request):
    """Returns downloadable sample CSV template for bulk grade upload."""
    err = require_admin(request, 'Faculty or admin access required.')
    if err:
        return err

    from django.http import HttpResponse
    csv_content = (
        "roll_number,semester,course_code,course_title,credits,grade\r\n"
        "EXAMPLE001,4,CS8451,Operating Systems,3,A+\r\n"
        "EXAMPLE002,4,CS8491,Computer Networks,3,O\r\n"
        "EXAMPLE003,3,MA8351,Discrete Mathematics,4,B+\r\n"
    )
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_grades.csv"'
    response['X-Description'] = 'Example template rows for faculty bulk grade upload'
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_admin_grades_bulk_upload(request):
    """
    Bulk uploads grades from a CSV file.
    Validates CSV extension, size <= 2MB, header columns, rows <= 1000,
    and individual field constraints.
    """
    err = require_admin(request, 'Faculty or admin access required.')
    if err:
        return err

    uploaded_file = request.FILES.get('file') or request.FILES.get('csv_file')
    if not uploaded_file:
        return Response({'error': 'No CSV file provided.'}, status=status.HTTP_400_BAD_REQUEST)

    if not uploaded_file.name.lower().endswith('.csv'):
        return Response({'error': 'Invalid file type. Please upload a .csv file.'}, status=status.HTTP_400_BAD_REQUEST)

    if uploaded_file.size > 2 * 1024 * 1024:
        return Response({'error': 'File size exceeds maximum limit of 2MB.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        raw_bytes = uploaded_file.read()
        csv_text = raw_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        return Response({'error': 'File must be UTF-8 encoded.'}, status=status.HTTP_400_BAD_REQUEST)

    from .services.academic_service import process_bulk_grades_csv
    result = process_bulk_grades_csv(action_user=request.user, csv_text=csv_text)

    if result.get("status_code") == 400:
        return Response({'error': result.get("error", "CSV validation failed.")}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'saved': result['saved'],
        'skipped': result['skipped'],
        'errors': result['errors']
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_transcript_pdf(request):
    """
    Generates and downloads an official academic transcript in PDF format.
    Students can only download their own transcript; faculty/admin can view any student.
    """
    from django.http import HttpResponse
    from .services.pdf_service import generate_transcript_pdf

    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    student_id = request.GET.get('student_id')
    target_profile = None

    if user_profile.role == 'student':
        if student_id and str(student_id) not in [str(user_profile.id), str(request.user.id), user_profile.roll_number]:
            return Response({'error': 'Students can only access their own transcript.'}, status=status.HTTP_403_FORBIDDEN)
        target_profile = user_profile
    else:
        # Faculty or admin
        if student_id:
            target_profile = (
                UserProfile.objects.filter(id=student_id).first()
                or UserProfile.objects.filter(user__id=student_id).first()
                or UserProfile.objects.filter(roll_number=student_id).first()
            )
            if not target_profile:
                return Response({'error': f"Student with ID '{student_id}' not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            if user_profile.role == 'student':
                target_profile = user_profile
            else:
                first_student = UserProfile.objects.filter(role='student').first()
                if first_student:
                    target_profile = first_student
                else:
                    return Response({'error': 'Please specify a student_id parameter.'}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_analytics(request):
    """
    Returns high-level institution analytics for faculty and admins:
      - Grade distribution across all published course results
      - Department-wise average CGPA
      - At-risk students cohort (CGPA < 6.0 or backlogs >= 2)
      - Aggregate metrics
    Optimized with aggregates and select_related.
    """
    err = require_admin(request, 'Faculty or admin access required.')
    if err:
        return err

    from django.db.models import Avg, Count, Q

    students_qs = UserProfile.objects.filter(role='student')
    total_students = students_qs.count()

    # Aggregate student stats
    agg_stats = students_qs.aggregate(
        avg_cgpa=Avg('current_cgpa'),
        eligible_count=Count('id', filter=Q(is_placement_eligible=True))
    )
    avg_cgpa = round(float(agg_stats['avg_cgpa'] or 0.0), 2)
    eligible_count = agg_stats['eligible_count'] or 0
    eligibility_rate = round((eligible_count / total_students * 100), 1) if total_students > 0 else 0.0

    # 1. Grade Distribution
    grade_counts = {g: 0 for g in GRADE_ORDER}
    grade_data = CourseResult.objects.values('grade').annotate(count=Count('id'))
    for item in grade_data:
        g = str(item['grade']).strip().upper()
        if g in grade_counts:
            grade_counts[g] += item['count']
        elif g in ['RA', 'SA', 'W', 'U']:
            grade_counts[g] = grade_counts.get(g, 0) + item['count']

    # 2. Department-wise breakdown
    dept_stats = []
    departments = students_qs.values('department').annotate(
        student_count=Count('id'),
        avg_cgpa=Avg('current_cgpa')
    ).order_by('-student_count')

    for d in departments:
        dept_name = d['department'] or 'General'
        dept_stats.append({
            'department': dept_name,
            'student_count': d['student_count'],
            'avg_cgpa': round(float(d['avg_cgpa'] or 0.0), 2)
        })

    # 3. At-risk students
    from core.services.journey_service import evaluate_student_risk
    at_risk_qs = students_qs.filter(
        Q(current_cgpa__lt=AT_RISK_CGPA_THRESHOLD) | Q(backlogs_count__gte=AT_RISK_BACKLOG_THRESHOLD)
    ).select_related('user').order_by('current_cgpa')

    at_risk_list = list(at_risk_qs)
    all_semesters = list(SemesterRecord.objects.filter(
        student__in=at_risk_list, is_published=True
    ).order_by('semester_number'))
    semesters_by_student = {}
    for sem in all_semesters:
        semesters_by_student.setdefault(sem.student_id, []).append(sem)

    at_risk_students = []
    for s in at_risk_list:
        reasons = []
        if float(s.current_cgpa) < AT_RISK_CGPA_THRESHOLD:
            reasons.append(f"CGPA {float(s.current_cgpa):.2f} < {AT_RISK_CGPA_THRESHOLD}")
        if s.backlogs_count >= AT_RISK_BACKLOG_THRESHOLD:
            reasons.append(f"{s.backlogs_count} Active Arrears (>= {AT_RISK_BACKLOG_THRESHOLD})")

        risk_data = evaluate_student_risk(s, prefetched_semesters=semesters_by_student.get(s.id, []))

        at_risk_students.append({
            'id': s.id,
            'name': f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username,
            'roll_number': s.roll_number,
            'department': s.department,
            'current_semester': s.current_semester,
            'current_cgpa': float(s.current_cgpa),
            'backlogs_count': s.backlogs_count,
            'reason': " & ".join(reasons) if reasons else "Academic review needed",
            'predicted_next_sgpa': risk_data['predicted_next_sgpa'],
            'trend': risk_data['trend'],
            'risk_level': risk_data['risk_level'],
            'reasons': risk_data['reasons'],
        })

    return Response({
        'metrics': {
            'total_students': total_students,
            'average_cgpa': avg_cgpa,
            'eligible_count': eligible_count,
            'eligibility_rate': eligibility_rate,
            'at_risk_count': len(at_risk_students),
            'thresholds': {
                'cgpa': AT_RISK_CGPA_THRESHOLD,
                'backlogs': AT_RISK_BACKLOG_THRESHOLD
            }
        },
        'grade_distribution': grade_counts,
        'department_stats': dept_stats,
        'at_risk_students': at_risk_students
    })

# ==========================================
# DIGITAL TWIN & CAREER READINESS APIS
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_twin_simulate(request):
    """
    Monte Carlo academic future trajectory simulation.
    Requires student role and validates target CGPA (0.00-10.00) and effort ('lower', 'same', 'higher').
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'student':
        return Response({'error': 'Student access required.'}, status=status.HTTP_403_FORBIDDEN)

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
    if not profile or profile.role != 'student':
        return Response({'error': 'Student access required.'}, status=status.HTTP_403_FORBIDDEN)

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
    if not profile or profile.role != 'student':
        return Response({'error': 'Student access required.'}, status=status.HTTP_403_FORBIDDEN)

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
@permission_classes([IsAuthenticated])
def api_admin_drives_list(request):
    """Lists all corporate recruitment drives with criteria (faculty/admin only)."""
    err = require_admin(request)
    if err:
        return err

    from core.models import CompanyPlacementCriteria
    companies = list(CompanyPlacementCriteria.objects.all().order_by('-package_lpa').values(
        'id', 'company_name', 'role_title', 'min_cgpa', 'max_backlogs', 'package_lpa', 'required_skills', 'is_active'
    ))
    return Response({
        'companies': companies,
        'drives': companies
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_drive_detail(request, company_id):
    """
    Returns eligible and almost-eligible candidate cohorts for a specific placement drive.
    Uses batch queries to maintain constant query count regardless of student population.
    """
    err = require_admin(request)
    if err:
        return err

    from core.models import CompanyPlacementCriteria, UserProfile, CourseResult, CourseSkillMap
    company = CompanyPlacementCriteria.objects.filter(id=company_id).first()
    if not company:
        return Response({'error': 'Company placement drive not found.'}, status=status.HTTP_404_NOT_FOUND)

    dept_filter = request.query_params.get('department')
    students_qs = UserProfile.objects.filter(role='student').select_related('user').order_by('-current_cgpa')
    if dept_filter:
        students_qs = students_qs.filter(department=dept_filter)

    students = list(students_qs)
    min_cgpa = float(company.min_cgpa)
    max_backlogs = company.max_backlogs

    # Query count optimization: prefetch all student courses and skill maps in 2 queries
    all_courses = list(CourseResult.objects.filter(student__in=students, is_published=True).order_by('semester_number', 'id'))
    courses_by_student = {}
    for c in all_courses:
        courses_by_student.setdefault(c.student_id, []).append(c)

    db_mappings = list(CourseSkillMap.objects.all())
    mappings_by_code = {}
    for m in db_mappings:
        mappings_by_code.setdefault(m.course_code.upper(), []).append(m.skill)

    raw_req = company.required_skills or ""
    req_list = [s.strip() for s in raw_req.replace(';', ',').split(',') if s.strip()]

    eligible_list = []
    almost_list = []

    aliases = {
        "sql": "dbms", "database": "dbms", "algorithms": "dsa", "data structures": "dsa",
        "operating systems": "os", "networking": "networks", "machine learning": "ai/ml",
        "mathematics": "maths"
    }

    from core.services.skill_service import _match_keywords_for_title

    for s in students:
        cgpa = float(s.current_cgpa or 0.0)
        backlogs = int(s.backlogs_count or 0)
        name = f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username

        # In-memory skill calculation per student
        c_list = courses_by_student.get(s.id, [])
        latest_c = {}
        for c in c_list:
            latest_c[c.course_code.upper()] = c

        skill_buckets = {}
        for c in latest_c.values():
            skills = mappings_by_code.get(c.course_code.upper())
            if not skills:
                skills = _match_keywords_for_title(c.course_name)
            for sk in skills:
                skill_buckets.setdefault(sk, []).append(c)

        s_scores = {}
        for sk, clist in skill_buckets.items():
            tot_cr = sum(float(c.credits) for c in clist)
            tot_pt = sum(float(c.credits) * float(c.grade_point) for c in clist)
            s_scores[sk.lower()] = round(((tot_pt / tot_cr) / 10.0) * 100.0, 1) if tot_cr > 0 else 0.0

        cov = []
        for req in req_list:
            k = aliases.get(req.lower(), req.lower())
            if k in s_scores:
                cov.append(s_scores[k])
        skill_match = round(sum(cov) / len(cov), 1) if cov else 0.0

        student_info = {
            'id': s.id,
            'name': name,
            'roll_number': s.roll_number,
            'department': s.department,
            'current_cgpa': cgpa,
            'backlogs_count': backlogs,
            'skill_match': skill_match,
        }

        cgpa_short = round(min_cgpa - cgpa, 2)
        backlogs_over = backlogs - max_backlogs

        if cgpa >= min_cgpa and backlogs <= max_backlogs:
            student_info['status'] = 'Eligible'
            eligible_list.append(student_info)
        elif cgpa_short <= 0.50 and backlogs_over <= 1:
            gaps = []
            if cgpa_short > 0:
                gaps.append(f"needs +{cgpa_short:.2f} CGPA")
            if backlogs_over > 0:
                gaps.append(f"clear {backlogs_over} arrear")
            student_info['status'] = 'Almost Eligible'
            student_info['gap_text'] = ", ".join(gaps) if gaps else "Near eligibility threshold"
            almost_list.append(student_info)

    return Response({
        'company': {
            'id': company.id,
            'company_name': company.company_name,
            'role_title': company.role_title,
            'min_cgpa': min_cgpa,
            'max_backlogs': max_backlogs,
            'package_lpa': float(company.package_lpa),
            'required_skills': company.required_skills
        },
        'counts': {
            'eligible': len(eligible_list),
            'almost_eligible': len(almost_list),
            'total_reviewed': len(students)
        },
        'eligible_students': eligible_list,
        'almost_eligible_students': almost_list
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_drive_export(request, company_id):
    """Exports eligible and almost-eligible drive candidates to CSV format."""
    err = require_admin(request)
    if err:
        return err

    from core.models import CompanyPlacementCriteria
    import csv
    from django.http import HttpResponse

    company = CompanyPlacementCriteria.objects.filter(id=company_id).first()
    if not company:
        return Response({'error': 'Company placement drive not found.'}, status=status.HTTP_404_NOT_FOUND)

    detail_res = api_admin_drive_detail(request._request, company_id)
    if detail_res.status_code != 200:
        return detail_res
    res_data = detail_res.data
    eligible = res_data.get('eligible_students', [])
    almost = res_data.get('almost_eligible_students', [])

    http_resp = HttpResponse(content_type='text/csv')
    clean_name = "".join(c for c in company.company_name if c.isalnum() or c in (' ', '_', '-')).strip()
    http_resp['Content-Disposition'] = f'attachment; filename="{clean_name}_drive_candidates.csv"'

    writer = csv.writer(http_resp)
    writer.writerow(['Status', 'Roll Number', 'Name', 'Department', 'CGPA', 'Backlogs', 'Skill Match (%)', 'Gap / Notes'])

    for s in eligible:
        writer.writerow(['Eligible', s.get('roll_number', ''), s.get('name', ''), s.get('department', ''), s.get('current_cgpa', ''), s.get('backlogs_count', ''), s.get('skill_match', ''), 'Meets all criteria'])

    for s in almost:
        writer.writerow(['Almost Eligible', s.get('roll_number', ''), s.get('name', ''), s.get('department', ''), s.get('current_cgpa', ''), s.get('backlogs_count', ''), s.get('skill_match', ''), s.get('gap_text', '')])

    return http_resp


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
    if not profile or profile.role != 'student':
        return Response({'error': 'Student access required.'}, status=status.HTTP_403_FORBIDDEN)

    from core.services.journey_service import get_journey, get_badges
    from core.models import SemesterRecord, CourseResult
    sem_records = list(SemesterRecord.objects.filter(student=profile, is_published=True).order_by('semester_number'))
    courses = list(CourseResult.objects.filter(student=profile, is_published=True))
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
