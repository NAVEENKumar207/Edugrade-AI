# EduGrade AI — Academic Digital Twin and Career Readiness Platform

> *"Your Academic Digital Twin — See Your Future, Not Just Your Past."*

An enterprise-grade, full-stack academic intelligence platform, credit-weighted CGPA/SGPA calculation engine, predictive milestone simulator, campus placement eligibility platform, and hybrid AI Academic Advisor.

Built with a unified, high-performance **Django REST Backend** and an interactive, real-time **ReactPy Python Frontend** powered by `reactpy-django` and Django Channels over WebSockets.

---

## 🌟 What Makes EduGrade AI Unique

EduGrade AI transforms traditional student record keeping into an active, forward-looking academic and career co-pilot through 9 specialized capabilities:

1. **Regulation-Aware Grading Engine & Anna University CBCS Configuration**:
   All grading logic, assessment weighting, and passing thresholds are consolidated into `core/regulation.py` as a single source of truth. Under the default 40% Continuous Internal Assessment (CIA) and 60% End-Semester Examination model, students must achieve $\ge 45\%$ on external theory and $\ge 50\%$ total to pass.
2. **Academic Digital Twin Simulator (Future Lab)**:
   A Monte Carlo simulation engine (`core/services/twin_service.py`) that projects thousands of possible academic trajectories through graduation. By analyzing historical grade distributions, remaining degree credits, and student effort parameters (*lower*, *same*, *higher*), it calculates expected final CGPA, confidence intervals (P10–P90), and company unlock probabilities.
3. **Next Best Move (Impact-Ranked Arrear Recovery)**:
   Simulates the marginal CGPA and placement unlock impact of clearing each outstanding backlog at a target grade without mutating stored student records. Courses are automatically ranked by maximum return on effort to give students an immediate recovery priority.
4. **Marks Target Calculator**:
   A deterministic reverse-calculation tool that takes continuous internal assessment marks (out of 40) and determines the exact external exam marks (out of 100) needed to achieve desired letter grades (O down to C), warning when higher grades are mathematically unattainable.
5. **Academic Skill Map & Placement Match**:
   Maps completed coursework to industry technical competencies (Algorithms, Web, Systems, AI/ML, Cloud, Data, Security) via `CourseSkillMap` and title keyword fallback. Computes credit-weighted mastery percentages and benchmarks students against corporate recruitment criteria.
6. **Drive Manager for Faculty & TPO**:
   A dedicated campus placement dashboard (`ui/pages/drive_manager.py`) enabling faculty and Training & Placement Officers to review eligible and almost-eligible candidates (within 0.50 CGPA or 1 backlog) with specific gap diagnostics and one-click CSV export.
7. **QR-Verified Anti-Tamper Transcripts**:
   Cryptographically secured academic transcripts using HMAC-SHA256 digital signatures, embedded ReportLab QR codes, and a public verification gateway (`/verify/<token>/`) providing instant verification while strictly masking student PII.
8. **Academic Journey, Badges & Early Warning**:
   A chronological visual timeline celebrating student progress paired with 7 milestone badges (*Zero Arrears*, *Comeback*, *Rising Star*, *Steady*, *Distinction*, *Full Credit Semester*, *Placement Ready*). For faculty, least-squares linear regression flags at-risk students with specific early warning diagnostic indicators.
9. **Tamil Voice-Assisted AI Advisor**:
   A bilingual academic counseling interface supporting both English and Tamil. Uses the browser Web Speech API for voice dictation and speech synthesis, allowing students to speak and listen in their preferred language.

---

## 🏗️ System Architecture

```text
EduGrade AI/
│
├── core/                                → Django Application (Business Logic & APIs)
│   ├── models.py                        → UserProfile, SemesterRecord, CourseResult, CourseSkillMap, TranscriptIssue, etc.
│   ├── regulation.py                    → Single source of truth for academic regulation constants & marks boundaries
│   ├── api_views.py                     → Secure REST API endpoints (Auth, Students, Academics, Placements, AI, Admin)
│   ├── views.py                         → Legacy template views, QR transcript verification view & session management
│   ├── services/
│   │   ├── academic_service.py          → Pure deterministic calculation engine (SGPA/CGPA/Planner/Arrears/Marks Target)
│   │   ├── twin_service.py              → Monte Carlo academic future simulator & Next Best Move ranking engine
│   │   ├── skill_service.py             → Credit-weighted skill mapping & corporate placement fit evaluator
│   │   ├── transcript_service.py        → HMAC-SHA256 transcript token generation & tamper verification
│   │   ├── journey_service.py           → Milestone badge evaluator, chronological journey timeline & risk prediction
│   │   ├── ai_service.py                → Grounded AI Academic Advisor powered by Groq Cloud & bilingual fallback
│   │   ├── security_service.py          → Cache-backed login brute-force rate limiter (5 attempts / 5-min lockout)
│   │   └── pdf_service.py               → ReportLab official transcript generator with embedded verification QR code
│   ├── tests/                           → Comprehensive automated unit and integration test suite (146 test cases)
│   │   ├── helpers.py                   → Reusable factory functions (create_student, create_admin, add_result)
│   │   ├── test_regulation.py           → Internal/external marks-to-grade boundaries and passing rules
│   │   ├── test_twin.py                 → Monte Carlo simulation determinism, seed repeatability & next moves
│   │   ├── test_marks_target.py         → Reverse marks target calculator and validation
│   │   ├── test_skills.py               → Skill map scoring and company fit matching
│   │   ├── test_admin_drives.py         → Drive Manager candidate classification, query count & CSV export
│   │   ├── test_transcript_verification.py → Anti-tamper transcript verification, QR token & PII masking
│   │   ├── test_journey.py              → Journey timeline, milestone badges & least-squares predictive risk
│   │   ├── test_academic_service.py     → Grade points, SGPA, CGPA, target planner, what-if simulator
│   │   ├── test_models_integration.py   → Referential integrity, models, cascade deletions
│   │   ├── test_permissions.py          → DRF API client authentication & role-based access control guards
│   │   ├── test_arrears.py              → Backlog tracking, arrear clearance, and audit logging
│   │   ├── test_csv_upload.py           → Bulk faculty CSV grade ingestion and error validation
│   │   ├── test_pdf_transcript.py       → PDF transcript generation and student data isolation
│   │   ├── test_placement_readiness.py  → 100-point placement readiness index & actionable guidance
│   │   ├── test_admin_analytics.py      → Grade distribution, department CGPA benchmark, at-risk criteria
│   │   ├── test_ai_advisor.py           → Contextual memory, weakest course fallback, and chat history deletion
│   │   ├── test_ai_groq.py              → Mocked Groq Cloud integration, failure resilience, and privacy tests
│   │   └── test_empty_state.py          → Fresh empty database state handling across all views & APIs
│   ├── management/commands/
│   │   ├── check_database.py            → Database health, migration, and referential integrity diagnostic tool
│   │   ├── load_sample_companies.py     → Loads standard corporate campus placement criteria
│   │   ├── load_sample_skill_map.py     → Populates standard technical course-to-skill mappings
│   │   └── remove_demo_data.py          → Safely purges demo accounts and associated academic records
│   └── urls.py                          → Unified URL routing for REST APIs and application views
│
├── ui/                                  → ReactPy Python Frontend (100% Python Single-Page Interface)
│   ├── app.py                           → Root application component, routing, navigation & state management
│   ├── components/
│   │   ├── layout.py                    → Responsive layout with sidebar, topbar, role badges & signout
│   │   ├── common.py                    → Reusable UI cards (EmptyStateCard, StatCard, AlertBanner)
│   │   └── icons.py                     → Crisp SVG vector icons (Sparkles, Award, Trending, Bot, etc.)
│   ├── services/
│   │   └── data_service.py              → Secure ORM and academic calculation data bridge for ReactPy
│   └── pages/
│       ├── landing.py                   → Academic intelligence landing page & portal triggers
│       ├── auth_page.py                 → Student & Faculty login & registration
│       ├── student_dashboard.py         → Real-time CGPA, SGPA, credits, placement readiness & Next Best Move
│       ├── future_lab.py                → Academic Digital Twin, Next Best Move card & Marks Target Calculator
│       ├── journey_page.py              → Milestone badge shelf & vertical chronological journey timeline
│       ├── drive_manager.py             → Campus placement candidate manager, gap analysis & CSV exporter
│       ├── results_page.py              → Detailed semester transcripts, course grade breakdown & PDF export
│       ├── cgpa_planner.py              → Interactive Target CGPA slider & what-if simulator
│       ├── placement_page.py            → Corporate criteria matrix, Academic Skill Map & 100-pt readiness
│       ├── ai_advisor.py                → Contextual AI advisor chat with prompt chips, Tamil voice mode
│       ├── admin_dashboard.py           → Faculty analytics, student directory, CSV upload & early warning table
│       ├── profile_page.py              → Student profile management & secure change password card
│       └── regulations_page.py          → Curriculum & Choice Based Credit System (CBCS) explorer
│
├── edugrade/                            → Django & ASGI Configuration
│   ├── settings.py                      → Configured for reactpy_django, Channels, CORS, DRF, Cache & Sessions
│   ├── asgi.py                          → ASGI application with ProtocolTypeRouter & ReactPy WebSocket route
│   └── urls.py                          → Root URL router mounting ReactPy, REST APIs, and verify routes
│
├── static/
│   ├── css/
│   │   ├── reactpy_styles.css           → High-contrast academic navy design system with responsive layouts
│   │   └── style.css                    → Legacy CSS for backward compatibility views
│   └── js/
│       └── script.js                    → Legacy JavaScript for backward compatibility views
│
├── templates/
│   ├── reactpy_index.html               → Host template mounting ReactPy component root with Web Speech bridge
│   ├── verify.html                      → Public tamper-proof transcript verification portal
│   └── *.html                           → Legacy Django template frontend views (see Legacy Compatibility Notice)
│
├── test_reactpy.py                      → Verification test for ReactPy component mounting & host view
├── test_routes.py                       → Comprehensive end-to-end route, API, and permission test runner
├── requirements.txt                     → Python dependencies (Django, DRF, ReactPy, reactpy-django, Channels, ReportLab)
├── manage.py                            → Django management script
├── .env.example                         → Template for required environment variables
└── db.sqlite3                           → SQLite database
```

---

## ⚠️ Legacy Compatibility Notice

The HTML templates located in `templates/` (e.g., `dashboard.html`, `admin_dashboard.html`, `results.html`, `cgpa_planner.html`, `placement.html`, `ai_advisor.html`) and legacy static assets in `static/css/style.css` and `static/js/script.js` are **preserved as legacy Django template frontend views for backward compatibility**. 

The **primary modern frontend** is the reactive Single-Page Application (SPA) powered by **ReactPy (`reactpy-django`)**, mounted via `templates/reactpy_index.html` and rendered via `ui/app.py` over WebSocket channels. All contemporary interactive capabilities, theme switching, dynamic modals, and live calculations run through the ReactPy architecture.

---

## 🚀 Setup & Initialization

EduGrade AI starts with a clean database ready for institutional onboarding:

### 1. Initial Setup
1. **Configure Environment**: Copy `.env.example` to `.env` and set signing keys:
   ```bash
   cp .env.example .env
   ```
2. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```
3. **Populate Placement Criteria & Skill Mappings**:
   ```bash
   python manage.py load_sample_companies
   python manage.py load_sample_skill_map
   ```
   *Loads 6 standard corporate recruitment criteria and 15 course-to-skill mappings.*

### 2. Registering Accounts
- **Faculty / Admin Account**:
  Navigate to the Sign Up page, select **Faculty / Admin**, enter username/password, and provide the `ADMIN_SIGNUP_KEY`.
- **Student Account**:
  Select **Student**, enter username, password, roll number (e.g., `717622CS101`), department, and current semester.
- **Bulk Grade Ingestion**:
  Faculty can download the CSV template (`sample_grades.csv`) directly from the Faculty Dashboard and upload student grades in bulk.

### 3. Demo Data Management
To audit or purge demo records from the database:
```bash
# Preview records to be removed
python manage.py remove_demo_data --dry-run

# Execute clean removal
python manage.py remove_demo_data --yes
```

---

## ⚙️ Environment Configuration

EduGrade AI uses a `.env` file for runtime configuration. Copy `.env.example` to `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(django-insecure dev key)* | Cryptographic signing key for Django sessions and tokens |
| `DEBUG` | `False` | Debug mode toggle (defaults to `False` if unset) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of host/domain names |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated origins allowed for cross-origin requests |
| `ADMIN_SIGNUP_KEY` | *(none / empty)* | Secret registration key required for creating faculty/admin accounts |
| `TRANSCRIPT_SIGNING_KEY`| *(django secret key)* | Secret key used to sign HMAC-SHA256 transcript verification tokens |
| `SITE_URL` | `http://127.0.0.1:8000` | Base public URL used in transcript QR verification links |
| `GROQ_API_KEY` | *(none)* | Groq Cloud API key (optional; get one at https://console.groq.com/keys) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq chat completion model (production default) |
| `GROQ_TIMEOUT_SECONDS`| `15` | Request timeout in seconds for Groq API calls |
| `OPENAI_API_KEY` | *(none)* | OpenAI API key (optional secondary provider; fallback active if empty) |

---

## 📐 Academic Regulations & Single Source of Truth

> [!IMPORTANT]
> **Institutional Verification**: All grading scales, internal/external assessment proportions, passing minimums, and grade cutoff boundaries are defined exclusively in `core/regulation.py`. Institutions should verify and adjust these values to conform to their specific university regulations before deploying to production.

```python
# core/regulation.py
INTERNAL_MAX = 40.0
EXTERNAL_PAPER_MAX = 100.0
EXTERNAL_WEIGHT = 0.60
MIN_EXTERNAL_PERCENT = 45.0
MIN_TOTAL_TO_PASS = 50.0

GRADE_BOUNDARIES = [
    (91.0, 100.0, "O",  10.0),
    (81.0,  90.0, "A+",  9.0),
    (71.0,  80.0, "A",   8.0),
    (61.0,  70.0, "B+",  7.0),
    (56.0,  60.0, "B",   6.0),
    (50.0,  55.0, "C",   5.0),
]
```

### Grade Calculation Formula
$$\text{Total Marks} = \text{Internal Marks (out of 40)} + \left(\frac{\text{External Marks (out of 100)}}{100} \times 60\right)$$
- If $\text{External Marks} < 45.0$: Result is **U** (Re-appear) regardless of total marks.
- If $\text{Total Marks} < 50.0$: Result is **U** (Re-appear).

---

## 📡 Complete REST API Specification

All modern API endpoints are registered in `core/urls.py` under `/api/` and enforce role-based authentication and student isolation:

| Endpoint | Method | Auth Required | Role | Description |
| :--- | :---: | :---: | :---: | :--- |
| `/api/auth/me/` | `GET` | Yes | Student/Admin | Returns authenticated user profile and session role |
| `/api/auth/login/` | `POST` | No | Public | Authenticates user; rate-limited (5 failed attempts locks for 5 min) |
| `/api/auth/signup/` | `POST` | No | Public | Registers student or faculty (requires `admin_key` for faculty) |
| `/api/auth/logout/` | `POST` | Yes | Student/Admin | Invalidates active user session |
| `/api/auth/change-password/` | `POST` | Yes | Student/Admin | Validates old password and updates to new password |
| `/api/students/dashboard/` | `GET` | Yes | Student | Returns student metrics, CGPA, SGPA history, readiness score, and tips |
| `/api/student/arrears/` | `GET` | Yes | Student | Returns breakdown of active and cleared arrears |
| `/api/academics/results/` | `GET` | Yes | Student | Returns semester course results and grade points |
| `/api/planner/cgpa/` | `POST` | No / Optional | Public/Student | Target CGPA simulator returning required upcoming SGPA and feasibility |
| `/api/twin/simulate/` | `POST` | Yes | Student | Digital Twin Monte Carlo trajectory simulation (runs, expected CGPA, P10-P90) |
| `/api/twin/next-moves/` | `GET` | Yes | Student | Impact ranking of arrear clearing on CGPA and placement eligibility |
| `/api/tools/marks-target/` | `POST` | Yes (any role) | Student/Admin | Reverse marks calculator for required external exam score |
| `/api/skills/` | `GET` | Yes | Student | Credit-weighted skill mastery scores and company placement fit |
| `/api/journey/` | `GET` | Yes | Student | Chronological academic milestone journey and earned/locked badges |
| `/api/placements/eligibility/` | `GET` | Yes | Student | Evaluates eligibility across all corporate placement drives |
| `/api/advisor/chat/` | `GET`, `POST` | Yes | Student | Retrieves chat history (`GET`) or generates grounded AI advice (`POST`) |
| `/api/advisor/history/` | `DELETE` | Yes | Student | Deletes student conversation history and creates an audit log |
| `/api/faculty/overview/` | `GET` | Yes | Admin/Faculty | Department overview, total students, average CGPA, and metrics |
| `/api/faculty/students/` | `GET` | Yes | Admin/Faculty | Searchable student directory with CGPA, credits, and backlogs |
| `/api/faculty/results/upload/` | `POST` | Yes | Admin/Faculty | Ingests semester academic records and computes metrics atomically |
| `/api/admin/drives/` | `GET` | Yes | Admin/Faculty | Campus placement drive listing with eligible candidate counts |
| `/api/admin/drives/<id>/` | `GET` | Yes | Admin/Faculty | Detailed drive candidates (Eligible and Almost-Eligible) with gap analysis |
| `/api/admin/drives/<id>/export/`| `GET` | Yes | Admin/Faculty | Exports drive candidate roster to CSV |
| `/api/admin/grades/sample-csv/` | `GET` | Yes | Admin/Faculty | Downloads standard CSV grade entry template |
| `/api/admin/grades/bulk-upload/` | `POST` | Yes | Admin/Faculty | Validates and ingests bulk grade CSV with detailed error report |
| `/api/admin/analytics/` | `GET` | Yes | Admin/Faculty | Grade distribution, department CGPA, and predictive early-warning table |
| `/api/transcript/pdf/` | `GET` | Yes | Student/Admin | Streams generated official academic PDF transcript with verification QR code |
| `/verify/<token>/` | `GET` | No | Public | HTML tamper-proof transcript verification portal |
| `/api/verify/<token>/` | `GET` | No | Public | JSON tamper-proof transcript verification API endpoint |
| `/api/health/` | `GET` | No | Public | Health check endpoint returning status 200 OK |

---

## 🧪 Verification & Automated Test Suites

EduGrade AI includes 146 automated tests across 18 specialized test suites:

```bash
# 1. Run all 146 Django unit and integration tests
python manage.py test

# 2. Run test suite in reverse order
python manage.py test --reverse

# 3. Run end-to-end route, API and permission verification
python test_routes.py

# 4. Verify ReactPy host component mounting
python test_reactpy.py

# 5. Check database referential integrity & migrations
python manage.py check_database
```

---

## 📌 Limitations & Assumptions

1. **Digital Twin Simulator**: The simulation engine provides statistical projections based on past academic patterns and user-selected effort adjustments; it serves as an advisory estimate and does not guarantee academic outcomes.
2. **Skill Mappings & Placement Criteria**: Default technical categories and company criteria represent sample institutional baselines. Faculty and administrators can configure both via Django Admin or custom management commands.
3. **Voice Recognition**: Tamil and English voice input/output utilizes the standard browser Web Speech API (`webkitSpeechRecognition` / `speechSynthesis`). Functionality and accent accuracy depend on client browser and operating system support (Google Chrome recommended).

---

## 🚀 Running the Application

### Option A: Standard Django Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

### Option B: ASGI Production Server (Daphne)
```bash
daphne -b 127.0.0.1 -p 8000 edugrade.asgi:application
```

### Accessing the Portal
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in any modern web browser.
