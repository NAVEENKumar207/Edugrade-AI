# CLAUDE.md

Guidance for working with the EduGrade AI codebase.

## Common Commands

### Development
- Run dev server: `python manage.py runserver`
- Run Daphne ASGI server: `daphne -b 127.0.0.1 -p 8000 edugrade.asgi:application`
- Load sample placement criteria: `python manage.py load_sample_companies`
- Load sample technical skill map: `python manage.py load_sample_skill_map`
- Remove demo data: `python manage.py remove_demo_data --yes`
- Apply migrations: `python manage.py migrate`
- Database integrity check: `python manage.py check_database`

### Testing
- Run all Django unit and integration tests (174 tests): `python manage.py test`
- Run test suite in reverse order: `python manage.py test --reverse`
- Run route, API, and RBAC tests: `python test_routes.py`
- Run ReactPy mounting tests: `python test_reactpy.py`

## Architecture Overview

EduGrade AI pairs a Django REST backend with a ReactPy SPA over WebSockets:

- `core/`: Business logic, models, and REST endpoints.
  - `models.py`: UserProfile, SemesterRecord, CourseResult, CourseSkillMap, CompanyPlacementCriteria, etc.
  - `regulation.py`: Single source of truth for CBCS regulations, mark weightings (40/60), and grade cutoffs.
  - `api_views.py`: REST API endpoints for authentication, academics, simulations, and admin actions.
  - `services/`: Specialized domain logic:
    - `academic_service.py`: SGPA/CGPA formulas, Target Planner, Arrear tracking, Marks Target calculator.
    - `twin_service.py`: Monte Carlo trajectory simulation and Next Best Move arrear ranking.
    - `skill_service.py`: Credit-weighted technical skill scoring and corporate placement match.
    - `transcript_service.py`: HMAC-SHA256 digital signing and QR verification.
    - `journey_service.py`: 7 milestone badges, chronological timeline, and linear regression risk prediction.
    - `ai_service.py`: Grounded AI advisor (Groq / OpenAI / deterministic fallback; English + Tamil).
    - `pdf_service.py`: ReportLab transcript generator with verification QR code.
- `ui/`: ReactPy SPA (mounted in `templates/reactpy_index.html` via WebSockets).
  - `app.py`: SPA routing, session state, and theme management.
  - `pages/`: Page components for student, faculty, and public views.
  - `components/`: Layout (`layout.py`), shared elements (`common.py`), icons (`icons.py`).
  - `services/data_service.py`: Secure bridge between ReactPy components and the database.
- `templates/`: ReactPy host template (`reactpy_index.html`), public verification (`verify.html`), and legacy views.
- `static/css/reactpy_styles.css`: Dark/light design system styling.

## Key Policies

- **Regulations**: `core/regulation.py` is the single source of truth for all regulation constants. Never hardcode them elsewhere.
- **Grade Scale**: O=10, A+=9, A=8, B+=7, B=6, C=5, U/RA/SA/W=0. Fail grades count as arrears.
- **Dependencies**: Use standard library and existing packages only. Do not add new packages to `requirements.txt`.
- **Legacy Views**: Keep legacy templates in `templates/` intact for backward compatibility.
- **RBAC**: Student views isolate data to the logged-in student. Faculty/Admin views require staff privileges.
