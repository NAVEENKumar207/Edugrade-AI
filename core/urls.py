from django.urls import path
from django.views.generic import RedirectView
from . import views
from . import api_views

urlpatterns = [
    # ==========================================
    # MODERN REST API ENDPOINTS
    # ==========================================
    path('api/auth/me/', api_views.api_me, name='api_me'),
    path('api/auth/login/', api_views.api_login, name='api_login'),
    path('api/auth/signup/', api_views.api_signup, name='api_signup'),
    path('api/auth/logout/', api_views.api_logout, name='api_logout'),
    path('api/auth/change-password/', api_views.api_change_password, name='api_change_password'),
    path('api/students/dashboard/', api_views.api_student_dashboard, name='api_student_dashboard'),
    path('api/student/arrears/', api_views.api_student_arrears, name='api_student_arrears'),
    path('api/academics/results/', api_views.api_results, name='api_results'),
    path('api/academics/results/<int:course_id>/', api_views.api_results, name='api_results_detail'),
    path('api/academics/results/import/', api_views.api_results_import, name='api_results_import'),
    path('api/academics/results/sample-csv/', api_views.api_results_sample_csv, name='api_results_sample_csv'),
    path('api/academics/results/export-csv/', api_views.api_results_export_csv, name='api_results_export_csv'),
    path('api/planner/cgpa/', api_views.api_plan_cgpa, name='api_plan_cgpa'),
    path('api/placements/eligibility/', api_views.api_placement_eligibility, name='api_placement_eligibility'),
    path('api/advisor/chat/', api_views.api_advisor_chat, name='api_advisor_chat'),
    path('api/advisor/history/', api_views.api_advisor_clear_history, name='api_advisor_clear_history'),
    path('api/transcript/pdf/', api_views.api_transcript_pdf, name='api_transcript_pdf'),
    path('api/health/', api_views.api_health, name='api_health'),
    path('api/demo/prepare/', api_views.api_demo_prepare, name='api_demo_prepare'),
    path('api/demo/cleanup/', api_views.api_demo_cleanup, name='api_demo_cleanup'),

    # Digital Twin, Career Readiness, Skills, Verification & Analytics
    path('api/twin/simulate/', api_views.api_twin_simulate, name='api_twin_simulate'),
    path('api/twin/next-moves/', api_views.api_twin_next_moves, name='api_twin_next_moves'),
    path('api/tools/marks-target/', api_views.api_marks_target, name='api_marks_target'),
    path('api/skills/', api_views.api_skills, name='api_skills'),
    path('verify/<str:token>/', views.verify_transcript_view, name='verify_transcript_view'),
    path('api/verify/<str:token>/', api_views.api_verify_transcript, name='api_verify_transcript'),
    path('api/journey/', api_views.api_journey, name='api_journey'),

    # Backward-compatible endpoints
    path('api/chat-ai/', views.chat_ai, name='chat_ai'),
    path('api/calculate-cgpa/', views.api_calculate_cgpa, name='api_calculate_cgpa'),
    path('api/save-results/', views.api_save_results, name='api_save_results'),

    # ==========================================
    # LEGACY / COMPATIBILITY DJANGO VIEW ROUTES
    # ==========================================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_view, name='upload'),
    path('syllabus/', views.syllabus_view, name='syllabus'),
    path('results/', views.results_view, name='results'),
    path('cgpa-planner/', views.cgpa_planner_view, name='cgpa_planner'),
    path('placement/', views.placement_view, name='placement'),
    path('ai-advisor/', views.ai_advisor_view, name='ai_advisor'),

    # Direct .html compatibility URLs
    path('index.html', views.home),
    path('login.html', views.login_view),
    path('signup.html', views.signup_view),
    path('dashboard.html', views.dashboard_view),
    path('upload.html', views.upload_view),
    path('syllabus.html', views.syllabus_view),
    path('results.html', views.results_view),
    path('cgpa_planner.html', views.cgpa_planner_view),
    path('placement.html', views.placement_view),
    path('ai_advisor.html', views.ai_advisor_view),

    # Nested redirects
    path('login/dashboard.html', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('signup/dashboard.html', RedirectView.as_view(url='/dashboard/', permanent=False)),
]
