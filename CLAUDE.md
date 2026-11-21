# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development
- Run development server: `python manage.py runserver`
- Load sample recruitment companies: `python manage.py load_sample_companies`
- Remove demo data safely: `python manage.py remove_demo_data --dry-run` / `--yes`
- Apply database migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- Check database integrity: `python manage.py check_database`

### Testing
- Run all Django unit and integration tests (102 tests): `python manage.py test`
- Run route, API, and RBAC permission tests: `python test_routes.py`
- Run ReactPy component mounting test: `python test_reactpy.py`

## Code Architecture

### High-Level Structure
EduGrade AI is an academic platform with a Django REST Backend and a ReactPy Single-Page Application:

- `edugrade/`: Django configuration (`settings.py`, `asgi.py`, `urls.py`).
- `core/`: Core Django application:
  - `models.py`: Defines `UserProfile`, `SemesterRecord`, `CourseResult`, `CompanyPlacementCriteria`, `AdvisorChatMessage`, `AcademicAuditLog`.
  - `api_views.py`: REST API endpoints (Auth, Students, Academics, Placements, AI Advisor, Admin, Analytics, CSV upload, PDF transcript).
  - `views.py`: Legacy template views for backward compatibility.
  - `services/academic_service.py`: Grade points (CBCS 10-point scale), SGPA/CGPA formulas, Target CGPA Planner, Arrear tracking & clearance engine, Placement Readiness 100-point score, CSV bulk parser.
  - `services/ai_service.py`: Hybrid AI advisor powered by Groq Cloud (`llama-3.3-70b-versatile`) with optional OpenAI secondary and built-in deterministic academic intelligence fallback (English + Tamil support, conversation memory, weakest course 4-week study plan, strict PII protection).
  - `services/security_service.py`: Cache-backed login brute-force rate limiter (5 failed attempts locks for 5 minutes).
  - `services/pdf_service.py`: Official academic transcript PDF generator using ReportLab.
  - `tests/`: Modular test suite covering all services, models, permissions, CSV, PDF, Arrears, Analytics, and AI.
- `ui/`: Modern ReactPy Single-Page Application (SPA):
  - `app.py`: Root component, client routing, session management, and theme state.
  - `pages/`: 10 ReactPy pages (`landing.py`, `auth_page.py`, `student_dashboard.py`, `results_page.py`, `cgpa_planner.py`, `placement_page.py`, `ai_advisor.py`, `admin_dashboard.py`, `profile_page.py`, `regulations_page.py`).
  - `services/data_service.py`: Secure bridge between ReactPy components and the Django ORM/services.
  - `components/`: Layout, navigation bar, sidebar, and SVG icons.
- `templates/`: Contains `reactpy_index.html` (the primary host template for the ReactPy SPA) and legacy `.html` templates preserved for backward compatibility.
- `static/`: Contains `css/reactpy_styles.css` (primary design system) and legacy `css/style.css`.

### Key Policies & Rules
- **No Extra Dependencies**: Only `reportlab` was added (in `requirements.txt`).
- **Legacy Compatibility**: Do not delete legacy templates in `templates/` or `static/`.
- **CBCS 10-Point Scale**: O=10, A+=9, A=8, B+=7, B=6, C=5, U/RA/SA/W=0. Fail grades count as backlogs with 0 credits earned.
- **Role-Based Access Control (RBAC)**: Student accounts can only access their own data. Faculty/Admin routes require staff privileges.
