import sys
from django.core.management.base import BaseCommand
from django.db import connections, connection
from django.db.migrations.executor import MigrationExecutor
from django.contrib.auth.models import User
from core.models import (
    UserProfile, SemesterRecord, SubjectInsight,
    CourseResult, CompanyPlacementCriteria, AdvisorChatMessage, AcademicAuditLog
)

class Command(BaseCommand):
    help = "Performs comprehensive database connectivity, migration status, and integrity checks."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== EduGrade AI Database Health Check ==="))
        
        # 1. Connection check
        try:
            db_conn = connections['default']
            db_conn.cursor()
            vendor = db_conn.vendor
            db_name = db_conn.settings_dict.get('NAME')
            self.stdout.write(self.style.SUCCESS(f"[OK] Database connection active: engine='{vendor}', target='{db_name}'"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"[FAIL] Database connection failed: {e}"))
            sys.exit(1)

        # 2. Migration status check
        try:
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            plan = executor.migration_plan(targets)
            if plan:
                self.stdout.write(self.style.WARNING(f"[WARNING] Pending migrations detected: {len(plan)} migrations need to be applied."))
                for migration, backwards in plan:
                    self.stdout.write(f"   - {migration.app_label}.{migration.name}")
            else:
                self.stdout.write(self.style.SUCCESS("[OK] All database migrations are fully applied."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"[FAIL] Migration check error: {e}"))

        # 3. Model & Table presence check
        tables_to_check = [
            UserProfile._meta.db_table,
            SemesterRecord._meta.db_table,
            SubjectInsight._meta.db_table,
            CourseResult._meta.db_table,
            CompanyPlacementCriteria._meta.db_table,
            AdvisorChatMessage._meta.db_table,
            AcademicAuditLog._meta.db_table,
            User._meta.db_table,
        ]
        existing_tables = connection.introspection.table_names()
        missing_tables = [t for t in tables_to_check if t not in existing_tables]
        if missing_tables:
            self.stderr.write(self.style.ERROR(f"[FAIL] Missing required tables: {missing_tables}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"[OK] Core tables verified ({len(tables_to_check)} tables)."))

        # 4. Record counts & Integrity check
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        semester_count = SemesterRecord.objects.count()
        insight_count = SubjectInsight.objects.count()
        course_count = CourseResult.objects.count()
        company_count = CompanyPlacementCriteria.objects.count()
        chat_count = AdvisorChatMessage.objects.count()
        audit_count = AcademicAuditLog.objects.count()

        self.stdout.write(self.style.MIGRATE_LABEL("\n--- Record Statistics ---"))
        self.stdout.write(f"  Total Auth Users:          {user_count}")
        self.stdout.write(f"  Total Student Profiles:    {profile_count} (Superusers: {superuser_count})")
        self.stdout.write(f"  Semester Records:          {semester_count}")
        self.stdout.write(f"  Subject Insights:          {insight_count}")
        self.stdout.write(f"  Course Results:            {course_count}")
        self.stdout.write(f"  Placement Criteria:        {company_count}")
        self.stdout.write(f"  Advisor Chat Messages:     {chat_count}")
        self.stdout.write(f"  Academic Audit Logs:       {audit_count}")

        # 5. Referential Integrity Check
        orphaned_profiles = UserProfile.objects.filter(user__isnull=True).count()
        orphaned_semesters = SemesterRecord.objects.filter(student__isnull=True).count()
        orphaned_insights = SubjectInsight.objects.filter(student__isnull=True).count()
        orphaned_courses = CourseResult.objects.filter(student__isnull=True).count()
        
        integrity_ok = True
        if orphaned_profiles > 0 or orphaned_semesters > 0 or orphaned_insights > 0 or orphaned_courses > 0:
            integrity_ok = False
            self.stdout.write(self.style.ERROR(
                f"[WARNING] Referential integrity anomalies found: "
                f"profiles={orphaned_profiles}, semesters={orphaned_semesters}, insights={orphaned_insights}, courses={orphaned_courses}"
            ))

        users_without_profile = User.objects.filter(profile__isnull=True).count()
        if users_without_profile > 0:
            self.stdout.write(self.style.WARNING(f"[INFO] {users_without_profile} auth users currently have no associated profile."))

        if integrity_ok:
            self.stdout.write(self.style.SUCCESS("[OK] Referential integrity check passed. No orphaned records found."))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] EduGrade AI Database health check completed successfully."))
