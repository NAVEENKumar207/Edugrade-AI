from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog,
    CourseSkillMap, TranscriptIssue
)


class SuperuserOnlyAdminSite(admin.AdminSite):
    """
    Custom Django AdminSite restricted strictly to active superusers.
    Prevents unauthorized access from regular students or non-superuser staff.
    """
    site_header = "EduGrade AI Superuser Administration"
    site_title = "EduGrade AI Admin"
    index_title = "Platform Superuser Control"

    def has_permission(self, request):
        return bool(request.user and request.user.is_active and request.user.is_superuser)


superuser_admin_site = SuperuserOnlyAdminSite(name='superuser_admin')

# Register auth models for superuser management
superuser_admin_site.register(User, UserAdmin)
superuser_admin_site.register(Group, GroupAdmin)


@admin.register(UserProfile, site=superuser_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'department', 'current_semester', 'current_cgpa', 'is_placement_eligible')
    list_filter = ('department', 'is_placement_eligible')
    search_fields = ('user__username', 'roll_number', 'user__first_name', 'user__last_name')


@admin.register(SemesterRecord, site=superuser_admin_site)
class SemesterRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester_number', 'sgpa', 'credits_earned')
    list_filter = ('semester_number',)
    search_fields = ('student__user__username', 'student__roll_number')


@admin.register(SubjectInsight, site=superuser_admin_site)
class SubjectInsightAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_name', 'grade_point', 'status_label')
    list_filter = ('status_label',)
    search_fields = ('student__user__username', 'subject_name')


@admin.register(CourseResult, site=superuser_admin_site)
class CourseResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester_number', 'course_code', 'course_name', 'grade', 'grade_point', 'credits')
    list_filter = ('semester_number', 'grade')
    search_fields = ('course_code', 'course_name', 'student__user__username')


@admin.register(CompanyPlacementCriteria, site=superuser_admin_site)
class CompanyPlacementCriteriaAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'role_title', 'min_cgpa', 'max_backlogs', 'package_lpa', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('company_name', 'role_title')


@admin.register(AdvisorChatMessage, site=superuser_admin_site)
class AdvisorChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'timestamp', 'short_message')
    list_filter = ('sender', 'timestamp')
    search_fields = ('user__username', 'message')

    def short_message(self, obj):
        return obj.message[:50]


@admin.register(AcademicAuditLog, site=superuser_admin_site)
class AcademicAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'action_by', 'timestamp', 'description')
    list_filter = ('action_type', 'timestamp')


@admin.register(CourseSkillMap, site=superuser_admin_site)
class CourseSkillMapAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'skill')
    list_filter = ('skill',)
    search_fields = ('course_code', 'skill')


@admin.register(TranscriptIssue, site=superuser_admin_site)
class TranscriptIssueAdmin(admin.ModelAdmin):
    list_display = ('token_short', 'student', 'issued_at', 'is_revoked')
    list_filter = ('is_revoked', 'issued_at')
    search_fields = ('token', 'student__user__username', 'student__roll_number')

    def token_short(self, obj):
        return f"{obj.token[:8]}..."
