from django.core.management.base import BaseCommand
from core.models import CompanyPlacementCriteria


class Command(BaseCommand):
    help = "Loads standard corporate placement partner criteria into the database."

    def handle(self, *args, **options):
        criteria_list = [
            ('Google', 'Software Engineer (L3)', 8.50, 0, 24.00, 'Data Structures, Algorithms, Distributed Systems, Python/Go'),
            ('Microsoft', 'Software Development Engineer', 8.00, 0, 18.50, 'Algorithms, OOP, Cloud Computing, C++/C#'),
            ('Zoho Corporation', 'Software Developer', 7.00, 1, 9.00, 'Problem Solving, Java/C, Web Tech, Aptitude'),
            ('TCS Digital', 'Digital Systems Engineer', 7.50, 0, 7.50, 'Full Stack, AI/ML basics, Python, SQL'),
            ('Infosys Specialist', 'Specialist Programmer', 7.50, 0, 9.50, 'Advanced Data Structures, Java, Cloud, DevOps'),
            ('Amazon AWS', 'Cloud Support Associate', 7.20, 0, 12.00, 'Networking, Linux, Cloud Architecture, Troubleshooting'),
        ]

        created_count = 0
        updated_count = 0
        for name, role, min_cgpa, max_bl, pkg, skills in criteria_list:
            obj, created = CompanyPlacementCriteria.objects.update_or_create(
                company_name=name,
                defaults={
                    'role_title': role,
                    'min_cgpa': min_cgpa,
                    'max_backlogs': max_bl,
                    'package_lpa': pkg,
                    'required_skills': skills,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully processed {len(criteria_list)} placement partners ({created_count} created, {updated_count} updated)."
        ))
