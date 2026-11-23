# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development
- Run development server: `python manage.py runserver`
- Load sample recruitment companies: `python manage.py load_sample_companies`
- Load sample technical course-to-skill map: `python manage.py load_sample_skill_map`
- Remove demo data safely: `python manage.py remove_demo_data --dry-run` / `--yes`
- Apply database migrations: `python manage.py migrate`
- Create migrations: `python manage.py makemigrations`
- Check database integrity: `python manage.py check_database`

### Testing
- Run all Django unit and integration tests (146 tests): `python manage.py test`
- Run test suite in reverse order: `python manage.py test --reverse`
- Run route, API, and RBAC permission tests: `python test_routes.py`
- Run ReactPy component mounting test: `python test_reactpy.py`

## Code Architecture

### High-Level Structure
EduGrade AI is an Academic Digital Twin and Career Readiness Platform with a Django REST Backend and a ReactPy Single-Page Application:

- `edugrade/`: Django configuration (`settings.py`, `asgi.py`, `urls.py`).
- `core/`: Core Django application:
  - `models.py`: Defines `UserProfile`, `SemesterRecord`, `CourseResult`, `CompanyPlacementCriteria`, `AdvisorChatMessage`, `AcademicAuditLog`, `CourseSkillMap`, `TranscriptIssue`.
  - `regulation.py`: **Single source of truth** for academic regulations, internal/external marks weighting (40/60), pass minimums (45% external, 50% combined), and letter grade cutoff boundaries.
  - `api_views.py`: REST API endpoints (Auth, Students, Academics, Placements, AI Advisor, Admin, Analytics, CSV upload, PDF transcript, Digital Twin Simulator, Next Best Move, Marks Target, Skills, Drive Manager, Journey & Badges).
  - `views.py`: Legacy template views and public QR transcript verification view (`/verify/<token>/`).
  - `services/academic_service.py`: Grade points (CBCS 10-point scale), SGPA/CGPA formulas, Target CGPA Planner, Arrear tracking & clearance engine, Placement Readiness 100-point score, Marks Target calculator, CSV bulk parser.
  - `services/twin_service.py`: Monte Carlo academic future simulation (`simulate_future`) and Next Best Move arrear clearance impact ranking (`rank_next_moves`).
  - `services/skill_service.py`: Credit-weighted technical skill scoring (`skill_scores`) and company fit evaluation (`company_skill_match`).
  - `services/transcript_service.py`: Anti-tamper transcript snapshot generation, HMAC-SHA256 digital signing, token verification, and PII masking.
  - `services/journey_service.py`: Milestone badge detection (`get_badges`), chronological timeline (`get_journey`), and least-squares linear regression risk prediction (`predict_next_sgpa`, `evaluate_student_risk`).
  - `services/ai_service.py`: Hybrid AI advisor powered by Groq Cloud (`llama-3.3-70b-versatile`) with optional OpenAI secondary and built-in deterministic academic intelligence fallback (English + Tamil support, Next Best Move integration, conversation memory, weakest course 4-week study plan, strict PII protection).
  - `services/security_service.py`: Cache-backed login brute-force rate limiter (5 failed attempts locks for 5 minutes).
  - `services/pdf_service.py`: Official academic transcript PDF generator using ReportLab with embedded tamper-proof verification QR code widget (`reportlab.graphics.barcode.qr`).
  - `tests/`: Modular test suite (146 tests) with reusable factory helpers (`helpers.py`) covering all services, models, permissions, CSV, PDF, Arrears, Analytics, AI, Regulation, Digital Twin, Marks Target, Skills, Drive Manager, Transcripts, and Journey.
- `ui/`: Modern ReactPy Single-Page Application (SPA):
  - `app.py`: Root component, client routing, session management, and theme state.
  - `pages/`: ReactPy pages (`landing.py`, `auth_page.py`, `student_dashboard.py`, `future_lab.py`, `journey_page.py`, `drive_manager.py`, `results_page.py`, `cgpa_planner.py`, `placement_page.py`, `ai_advisor.py`, `admin_dashboard.py`, `profile_page.py`, `regulations_page.py`).
  - `services/data_service.py`: Secure bridge between ReactPy components and the Django ORM/services.
  - `components/`: Layout (`layout.py`), shared UI widgets (`common.py`), and SVG icons (`icons.py`).
- `templates/`: Contains `reactpy_index.html` (the primary host template with Web Speech API voice bridge), `verify.html` (public transcript verification page), and legacy `.html` templates preserved for backward compatibility.
- `static/`: Contains `css/reactpy_styles.css` (primary design system) and legacy `css/style.css`.

### Key Policies & Rules
- **Regulation Constants**: `core/regulation.py` is the single source of truth for all regulation values (`INTERNAL_MAX`, `EXTERNAL_PAPER_MAX`, `EXTERNAL_WEIGHT`, `MIN_EXTERNAL_PERCENT`, `MIN_TOTAL_TO_PASS`, `GRADE_BOUNDARIES`). Never hardcode these anywhere else.
- **No Extra Dependencies**: Use standard library and existing packages (`reportlab`). No new packages in `requirements.txt`.
- **Legacy Compatibility**: Do not delete legacy templates in `templates/` or `static/`.
- **CBCS 10-Point Scale**: O=10, A+=9, A=8, B+=7, B=6, C=5, U/RA/SA/W=0. Fail grades count as backlogs with 0 credits earned.
- **Role-Based Access Control (RBAC)**: Student accounts can only access their own data. Faculty/Admin routes require staff privileges.
