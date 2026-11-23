from django.contrib import admin
from .models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog,
    CourseSkillMap, TranscriptIssue
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'roll_number', 'department', 'current_semester', 'current_cgpa', 'is_placement_eligible')
    list_filter = ('role', 'department', 'is_placement_eligible')
    search_fields = ('user__username', 'roll_number', 'user__first_name', 'user__last_name')

@admin.register(SemesterRecord)
class SemesterRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester_number', 'sgpa', 'credits_earned', 'is_published')
    list_filter = ('semester_number', 'is_published')
    search_fields = ('student__user__username', 'student__roll_number')

@admin.register(SubjectInsight)
class SubjectInsightAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject_name', 'grade_point', 'status_label')
    list_filter = ('status_label',)
    search_fields = ('student__user__username', 'subject_name')

@admin.register(CourseResult)
class CourseResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester_number', 'course_code', 'course_name', 'grade', 'grade_point', 'credits')
    list_filter = ('semester_number', 'grade')
    search_fields = ('course_code', 'course_name', 'student__user__username')

@admin.register(CompanyPlacementCriteria)
class CompanyPlacementCriteriaAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'role_title', 'min_cgpa', 'max_backlogs', 'package_lpa', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('company_name', 'role_title')

@admin.register(AdvisorChatMessage)
class AdvisorChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'timestamp', 'short_message')
    list_filter = ('sender', 'timestamp')
    search_fields = ('user__username', 'message')

    def short_message(self, obj):
        return obj.message[:50]

@admin.register(AcademicAuditLog)
class AcademicAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'action_by', 'timestamp', 'description')
    list_filter = ('action_type', 'timestamp')

@admin.register(CourseSkillMap)
class CourseSkillMapAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'skill')
    list_filter = ('skill',)
    search_fields = ('course_code', 'skill')

@admin.register(TranscriptIssue)
class TranscriptIssueAdmin(admin.ModelAdmin):
    list_display = ('token_short', 'student', 'issued_at', 'is_revoked')
    list_filter = ('is_revoked', 'issued_at')
    search_fields = ('token', 'student__user__username', 'student__roll_number')

    def token_short(self, obj):
        return f"{obj.token[:8]}..."

