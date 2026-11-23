"""
Management command to safely remove demo user accounts and associated records
without impacting real users or reference data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from core.models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog
)

DEMO_USERNAMES = ['admin', 'student', 'priya', 'student01', 'admin01']


class Command(BaseCommand):
    help = "Safely removes demo accounts ('admin', 'student', 'priya', 'student01', 'admin01') and their linked records."

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Execute the deletion. Without this flag, command runs in dry-run mode.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Preview changes without modifying the database.'
        )

    def print_table_counts(self, stage_label: str):
        self.stdout.write(f"\n--- Database Record Statistics ({stage_label}) ---")
        self.stdout.write(f"  Auth Users:                 {User.objects.count()}")
        self.stdout.write(f"  User Profiles:              {UserProfile.objects.count()}")
        self.stdout.write(f"  Semester Records:           {SemesterRecord.objects.count()}")
        self.stdout.write(f"  Course Results:             {CourseResult.objects.count()}")
        self.stdout.write(f"  Subject Insights:           {SubjectInsight.objects.count()}")
        self.stdout.write(f"  Placement Criteria:         {CompanyPlacementCriteria.objects.count()} (Reference data - preserved)")
        self.stdout.write(f"  Advisor Chat Messages:      {AdvisorChatMessage.objects.count()}")
        self.stdout.write(f"  Academic Audit Logs:        {AcademicAuditLog.objects.count()}")

    def handle(self, *args, **options):
        execute_delete = options.get('yes', False) and not options.get('dry_run', False)

        self.stdout.write("=== EduGrade AI Demo Data Cleanup Tool ===")
        self.print_table_counts("BEFORE")

        # Find target demo users
        demo_users = list(User.objects.filter(username__in=DEMO_USERNAMES))
        other_users = list(User.objects.exclude(username__in=DEMO_USERNAMES))

        if other_users:
            other_names = [u.username for u in other_users]
            self.stdout.write(self.style.WARNING(f"\nNon-demo user accounts identified (will be PRESERVED): {other_names}"))
        else:
            self.stdout.write("\nNo non-demo user accounts found in database.")

        if not demo_users:
            self.stdout.write(self.style.SUCCESS("\nNo demo user accounts ('admin', 'student', 'priya') found. Nothing to delete."))
            return

        demo_profiles = list(UserProfile.objects.filter(user__in=demo_users))
        demo_semesters = list(SemesterRecord.objects.filter(student__in=demo_profiles))
        demo_courses = list(CourseResult.objects.filter(student__in=demo_profiles))
        demo_insights = list(SubjectInsight.objects.filter(student__in=demo_profiles))
        demo_chats = list(AdvisorChatMessage.objects.filter(user__in=demo_users))
        demo_audits = list(AcademicAuditLog.objects.filter(action_by__in=demo_users))

        self.stdout.write("\nTarget records scheduled for removal:")
        self.stdout.write(f"  Users:                      {len(demo_users)} ({[u.username for u in demo_users]})")
        self.stdout.write(f"  User Profiles:              {len(demo_profiles)}")
        self.stdout.write(f"  Semester Records:           {len(demo_semesters)}")
        self.stdout.write(f"  Course Results:             {len(demo_courses)}")
        self.stdout.write(f"  Subject Insights:           {len(demo_insights)}")
        self.stdout.write(f"  Advisor Chat Messages:      {len(demo_chats)}")
        self.stdout.write(f"  Academic Audit Logs:        {len(demo_audits)}")

        if not execute_delete:
            self.stdout.write(self.style.WARNING(
                "\n[DRY RUN COMPLETE] No records were deleted. Run with '--yes' to execute permanent deletion."
            ))
            return

        # Execute atomic deletion
        with transaction.atomic():
            # Delete child records explicitly before user cascades
            AcademicAuditLog.objects.filter(action_by__in=demo_users).delete()
            AdvisorChatMessage.objects.filter(user__in=demo_users).delete()
            CourseResult.objects.filter(student__in=demo_profiles).delete()
            SubjectInsight.objects.filter(student__in=demo_profiles).delete()
            SemesterRecord.objects.filter(student__in=demo_profiles).delete()
            UserProfile.objects.filter(user__in=demo_users).delete()
            User.objects.filter(username__in=DEMO_USERNAMES).delete()

        self.stdout.write(self.style.SUCCESS("\n[DELETION EXECUTED] Demo accounts and associated records deleted successfully."))
        self.print_table_counts("AFTER")
