import hmac
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile, SemesterRecord, SubjectInsight
from .services.security_service import (
    is_account_locked, record_failed_login, reset_login_attempts, get_lockout_message
)
import json

def home(request):
    """Render the EduGrade AI ReactPy application."""
    return render(request, 'reactpy_index.html')

def login_view(request):
    """Handle Student sign in."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Check for account lockout after 5 consecutive failed attempts
        locked, mins = is_account_locked(username)
        if locked:
            messages.error(request, get_lockout_message(mins))
            return render(request, 'login.html', {'debug': settings.DEBUG})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            reset_login_attempts(username)
            login(request, user)
            
            # Check profile or create default profile if missing
            UserProfile.objects.get_or_create(user=user)
            return redirect('dashboard')
        else:
            is_locked, mins = record_failed_login(username)
            if is_locked:
                messages.error(request, get_lockout_message(mins))
            else:
                messages.error(request, 'Invalid credentials. Please check your username/email and password.')
            return render(request, 'login.html', {'debug': settings.DEBUG})

    return render(request, 'login.html', {'debug': settings.DEBUG})

def signup_view(request):
    """Handle Student account registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        institution_name = request.POST.get('institution_name', 'K.S. Rangasamy College of Technology (Autonomous)').strip()
        department = request.POST.get('department', 'Computer Science & Business Systems')
        syllabus_regulation = request.POST.get('syllabus_regulation', request.POST.get('syllabus', 'Regulation 2021 (R2021 CBCS)')).strip() or 'Regulation 2021 (R2021 CBCS)'
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        roll_number = request.POST.get('roll_number', '').strip()
        semester = request.POST.get('semester', '1')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'An account with this email/username already exists.')
            return render(request, 'signup.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=username,
            is_staff=False
        )

        if fullname:
            parts = fullname.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save()

        # Create UserProfile
        UserProfile.objects.create(
            user=user,
            roll_number=roll_number or ('7176' + username),
            institution_name=institution_name or 'Anna University / Affiliated Institution',
            department=department,
            syllabus_regulation=syllabus_regulation,
            current_semester=int(semester) if semester.isdigit() else 1
        )

        login(request, user)
        messages.success(request, 'Welcome! Your student account was created successfully.')
        return redirect('dashboard')

    return render(request, 'signup.html')

def logout_view(request):
    """Log out the current user."""
    logout(request)
    return redirect('home')

def dashboard_view(request):
    """Render the student performance dashboard."""
    if not request.user.is_authenticated:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)
    semesters = SemesterRecord.objects.filter(student=profile)
    insights = SubjectInsight.objects.filter(student=profile)
    from ui.services.data_service import get_arrears
    arrears = get_arrears(profile)

    context = {
        'profile': profile,
        'semesters': semesters,
        'insights': insights,
        'arrears': arrears,
    }
    return render(request, 'dashboard.html', context)


# =======================================================
# NEW WORKFLOW & FEATURE PAGES
# =======================================================

def upload_view(request):
    """Render the multi-step Academic Data & Document Upload Flow."""
    return render(request, 'upload.html')

def syllabus_view(request):
    """Render the Curriculum & Syllabus Explorer page."""
    if not request.user.is_authenticated:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'syllabus.html', context)


def results_view(request):
    """Render the Semester Transcripts & Results page."""
    if not request.user.is_authenticated:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)
    semesters = SemesterRecord.objects.filter(student=profile).order_by('-semester_number')

    context = {
        'profile': profile,
        'semesters': semesters,
    }
    return render(request, 'results.html', context)


def cgpa_planner_view(request):
    """Render the Target CGPA Simulator & Planner page."""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'cgpa_planner.html')

def placement_view(request):
    """Render the Placement Eligibility & Company Matrix page."""
    if not request.user.is_authenticated:
        return redirect('login')

    profile = UserProfile.objects.get(user=request.user)

    context = {
        'profile': profile,
    }
    return render(request, 'placement.html', context)


def ai_advisor_view(request):
    """Render the Interactive AI Academic Advisor Chatbot."""
    return render(request, 'ai_advisor.html')

# =======================================================
# DJANGO REST / API ENDPOINTS
# =======================================================

def chat_ai(request):
    """API endpoint for the AI Academic Advisor chatbot."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
            from core.services.ai_service import generate_ai_advice
            advice = generate_ai_advice(profile, user_message)
            return JsonResponse({
                'status': 'success',
                'reply': advice.get('response', ''),
                'response': advice.get('response', ''),
                'source': advice.get('source', 'rule_based')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_calculate_cgpa(request):

    """API endpoint for live SGPA and weighted CGPA calculation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            subjects = data.get('subjects', [])
            total_credits = 0
            total_points = 0
            for sub in subjects:
                c = float(sub.get('credits', 3))
                gp = float(sub.get('grade_point', 9))
                total_credits += c
                total_points += (c * gp)

            sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 8.61
            prev_cgpa = float(data.get('prev_cgpa', 8.38))
            prev_credits = float(data.get('prev_credits', 80))
            updated_cgpa = round(((prev_cgpa * prev_credits) + total_points) / (prev_credits + total_credits), 2)

            return JsonResponse({
                'status': 'success',
                'sgpa': sgpa,
                'cgpa': updated_cgpa,
                'total_credits': total_credits
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def api_save_results(request):
    """API endpoint to save semester results and update CGPA."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            semester_num = int(data.get('semester', 5))
            subjects = data.get('subjects', [])

            profile = UserProfile.objects.get(user=request.user)

            # 1. Calculate SGPA for the new data
            total_credits = 0
            total_points = 0
            for sub in subjects:
                c = float(sub.get('credits', 3))
                gp = float(sub.get('grade_point', 9))
                total_credits += c
                total_points += (c * gp)

            sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0

            # 2. Save SemesterRecord
            SemesterRecord.objects.update_or_create(
                student=profile,
                semester_number=semester_num,
                defaults={'sgpa': sgpa, 'credits_earned': total_credits}
            )

            # 3. Save SubjectInsights
            for sub in subjects:
                SubjectInsight.objects.update_or_create(
                    student=profile,
                    subject_name=sub.get('name'),
                    defaults={
                        'grade_point': float(sub.get('grade_point', 9)),
                        'status_label': 'Strong' if float(sub.get('grade_point', 9)) >= 8.5 else 'Good' if float(sub.get('grade_point', 9)) >= 7.5 else 'Needs attention'
                    }
                )

            # 4. Recalculate Cumulative CGPA
            all_semesters = SemesterRecord.objects.filter(student=profile)
            cum_points = sum(sem.sgpa * sem.credits_earned for sem in all_semesters)
            cum_credits = sum(sem.credits_earned for sem in all_semesters)

            if cum_credits > 0:
                profile.current_cgpa = round(cum_points / cum_credits, 2)
                profile.credits_earned = cum_credits
                profile.save()

            return JsonResponse({'status': 'success', 'cgpa': profile.current_cgpa})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def verify_transcript_view(request, token):
    """Public verification page displaying cryptographically validated transcript snapshot."""
    from core.services.transcript_service import verify_transcript_token
    ctx = verify_transcript_token(token)
    stat = 200 if ctx.get('is_valid') else 404
    return render(request, 'verify.html', ctx, status=stat)


