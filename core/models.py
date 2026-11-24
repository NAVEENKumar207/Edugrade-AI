from django.db import models
from django.contrib.auth.models import User
import uuid

def generate_transcript_token():
    return uuid.uuid4().hex

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    institution_name = models.CharField(max_length=200, default='K.S. Rangasamy College of Technology (Autonomous)', blank=True)
    department = models.CharField(max_length=100, default='Computer Science & Business Systems')
    syllabus_regulation = models.CharField(max_length=100, default='Regulation 2021 (R2021 CBCS)', blank=True)
    current_semester = models.IntegerField(default=5, blank=True, null=True)
    target_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=9.00)
    current_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=8.42)
    credits_earned = models.IntegerField(default=72)
    total_credits = models.IntegerField(default=164)
    backlogs_count = models.IntegerField(default=0)
    is_placement_eligible = models.BooleanField(default=True)

    def is_admin(self):
        return self.user.is_staff or self.user.is_superuser

    def __str__(self):
        return f"{self.user.username} - {self.department} ({self.institution_name})"

# Backwards compatibility alias
StudentProfile = UserProfile

class SemesterRecord(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='semesters')
    semester_number = models.IntegerField()
    sgpa = models.DecimalField(max_digits=4, decimal_places=2)
    credits_earned = models.IntegerField(default=20)

    class Meta:
        ordering = ['semester_number']

    def __str__(self):
        return f"{self.student.user.username} - Semester {self.semester_number} (SGPA: {self.sgpa})"

class SubjectInsight(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subject_insights')
    subject_name = models.CharField(max_length=150)
    grade_point = models.DecimalField(max_digits=4, decimal_places=1)
    status_label = models.CharField(max_length=50, default='Strong') # Strong, Good, Needs attention

    def __str__(self):
        return f"{self.subject_name} ({self.grade_point})"

class CourseResult(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='course_results')
    semester_record = models.ForeignKey(SemesterRecord, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    semester_number = models.IntegerField(default=1)
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=150)
    credits = models.IntegerField(default=3)
    grade = models.CharField(max_length=5, default='A')
    grade_point = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    previous_grade = models.CharField(max_length=3, blank=True, default="")
    arrear_cleared = models.BooleanField(default=False)
    cleared_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['semester_number', 'course_code']

    def __str__(self):
        return f"{self.course_code}: {self.course_name} ({self.grade})"

class CompanyPlacementCriteria(models.Model):
    company_name = models.CharField(max_length=100)
    role_title = models.CharField(max_length=100)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=7.00)
    max_backlogs = models.IntegerField(default=0)
    package_lpa = models.DecimalField(max_digits=5, decimal_places=2, default=8.50)
    required_skills = models.TextField(blank=True, default='Data Structures, Algorithms, Python, SQL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} - {self.role_title} (Min CGPA: {self.min_cgpa})"

class AdvisorChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advisor_messages')
    sender = models.CharField(max_length=10, choices=(('user', 'User'), ('ai', 'AI Advisor')))
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user.username} - {self.sender}: {self.message[:30]}"

class AcademicAuditLog(models.Model):
    action_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.action_type}: {self.description[:40]}"


class CourseSkillMap(models.Model):
    """Maps course codes to industry career skills for skill gap analysis."""
    course_code = models.CharField(max_length=50)
    skill = models.CharField(max_length=100)

    class Meta:
        unique_together = ('course_code', 'skill')
        ordering = ['course_code', 'skill']

    def __str__(self):
        return f"{self.course_code} -> {self.skill}"


class TranscriptIssue(models.Model):
    """Cryptographically signed verifiable academic transcript snapshot."""
    token = models.CharField(max_length=64, unique=True, default=generate_transcript_token)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transcript_issues')
    issued_at = models.DateTimeField(auto_now_add=True)
    snapshot = models.JSONField()
    snapshot_hash = models.CharField(max_length=64)
    signature = models.CharField(max_length=64)
    is_revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        status_lbl = "REVOKED" if self.is_revoked else "VALID"
        return f"Transcript {self.token[:8]}... - {self.student.user.username} ({status_lbl})"

