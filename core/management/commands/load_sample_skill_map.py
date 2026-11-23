"""
Management command to map existing course codes to sample career skills.
Creates mappings only for courses that already exist in CourseResult records.
Administrators can edit, refine, or add mappings via the Django Admin interface.
Safe to execute multiple times (idempotent).
"""

from django.core.management.base import BaseCommand
from core.models import CourseResult, CourseSkillMap
from core.services.skill_service import _match_keywords_for_title

class Command(BaseCommand):
    help = "Loads sample course-to-skill mappings for existing courses. Safe to run multiple times."

    def handle(self, *args, **options):
        self.stdout.write("Scanning existing CourseResult records for course codes...")
        distinct_courses = (
            CourseResult.objects.values('course_code', 'course_name')
            .distinct()
        )

        if not distinct_courses:
            self.stdout.write(self.style.WARNING("No CourseResult records found in the database. No mappings created."))
            return

        created_count = 0
        existing_count = 0

        for row in distinct_courses:
            code = row['course_code'].strip().upper()
            name = row['course_name'].strip()
            skills = _match_keywords_for_title(name)

            for sk in skills:
                obj, created = CourseSkillMap.objects.get_or_create(
                    course_code=code,
                    skill=sk
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed course skills: {created_count} new mappings created, "
            f"{existing_count} already existed.\n"
            f"Note: These are sample mappings that administrators can edit or extend in Django Admin (/admin/)."
        ))
