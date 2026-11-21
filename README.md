# EduGrade AI — Academic Intelligence Platform

An enterprise-grade, full-stack academic performance tracker, credit-weighted CGPA/SGPA calculation engine, predictive milestone simulator, campus placement eligibility platform, and hybrid AI Academic Advisor.

Built with a unified, high-performance **Django REST Backend** and an interactive, real-time **ReactPy Python Frontend** powered by `reactpy-django` and Django Channels over WebSockets.

---

## 🏗️ System Architecture

```text
EduGrade AI/
│
├── core/                                → Django Application (Business Logic & APIs)
│   ├── models.py                        → UserProfile, SemesterRecord, CourseResult, CompanyPlacementCriteria, etc.
│   ├── api_views.py                     → Secure REST API endpoints (Auth, Students, Academics, Placements, AI, Admin)
│   ├── views.py                         → Legacy template views & session management
│   ├── services/
│   │   ├── academic_service.py          → Pure deterministic calculation engine (SGPA/CGPA/Planner/Arrears/Readiness/CSV)
│   │   ├── ai_service.py                → Grounded AI Academic Advisor powered by Groq Cloud (llama-3.3-70b-versatile) & bilingual fallback
│   │   ├── security_service.py          → Cache-backed login brute-force rate limiter (5 attempts / 5-min lockout)
│   │   └── pdf_service.py               → ReportLab professional official academic transcript PDF generator
│   ├── tests/                           → Comprehensive automated unit and integration test suite (102 test cases)
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
│   │   └── remove_demo_data.py          → Safely purges demo accounts and associated academic records
│   └── urls.py                          → Unified URL routing for REST APIs and application views
│
├── ui/                                  → ReactPy Python Frontend (100% Python Single-Page Interface)
│   ├── app.py                           → Root application component, routing, navigation & state management
│   ├── components/
│   │   ├── layout.py                    → Responsive layout with sidebar, topbar, role badges & signout
│   │   └── icons.py                     → Crisp SVG vector icons (Sparkles, Award, Trending, Bot, etc.)
│   ├── services/
│   │   └── data_service.py              → Secure ORM and academic calculation data bridge for ReactPy
│   └── pages/
│       ├── landing.py                   → Academic intelligence landing page & portal triggers
│       ├── auth_page.py                 → Student & Faculty login & registration
│       ├── student_dashboard.py         → Real-time CGPA, SGPA, credits, placement readiness meter & arrears
│       ├── results_page.py              → Detailed semester transcripts, course grade breakdown & PDF export
│       ├── cgpa_planner.py              → Interactive Target CGPA slider & what-if simulator
│       ├── placement_page.py            → Corporate criteria matrix, cutoffs, and 100-pt readiness score
│       ├── ai_advisor.py                → Contextual AI advisor chat with prompt chips & chat history reset
│       ├── admin_dashboard.py           → Faculty analytics, student directory, CSV upload & transcript links
│       ├── profile_page.py              → Student profile management & secure change password card
│       └── regulations_page.py          → Curriculum & Choice Based Credit System (CBCS) explorer
│
├── edugrade/                            → Django & ASGI Configuration
│   ├── settings.py                      → Configured for reactpy_django, Channels, CORS, DRF, Cache & Sessions
│   ├── asgi.py                          → ASGI application with ProtocolTypeRouter & ReactPy WebSocket route
│   └── urls.py                          → Root URL router mounting ReactPy and REST APIs
│
├── static/
│   ├── css/
│   │   ├── reactpy_styles.css           → High-contrast academic navy design system with responsive layouts
│   │   └── style.css                    → Legacy CSS for backward compatibility views
│   └── js/
│       └── script.js                    → Legacy JavaScript for backward compatibility views
│
├── templates/
│   ├── reactpy_index.html               → Host template mounting ReactPy component root
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

## 🚀 Setup & User Registration

EduGrade AI starts with a clean database ready for institutional onboarding:

### 1. Initial Setup
1. **Configure Environment**: Copy `.env.example` to `.env` and set `ADMIN_SIGNUP_KEY` (e.g. `ADMIN_SIGNUP_KEY=ADMIN2026`).
2. **Apply Migrations**: `python manage.py migrate`
3. **Populate Placement Criteria**:
   ```bash
   python manage.py load_sample_companies
   ```
   *Loads 6 standard corporate recruitment criteria (Google, Microsoft, Zoho, TCS Ninja, Amazon, Infosys).*

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

```bash
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(django-insecure dev key)* | Cryptographic signing key for Django sessions and tokens |
| `DEBUG` | `True` | Debug mode toggle |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated list of host/domain names |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated origins allowed for cross-origin requests |
| `ADMIN_SIGNUP_KEY` | *(none / empty)* | Secret registration key required for creating faculty/admin accounts |
| `GROQ_API_KEY` | *(none)* | Groq Cloud API key (optional; get one at https://console.groq.com/keys) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq chat completion model (production default) |
| `GROQ_TIMEOUT_SECONDS`| `15` | Request timeout in seconds for Groq API calls |
| `OPENAI_API_KEY` | *(none)* | OpenAI API key (optional secondary provider; fallback active if empty) |

---

## 📐 Academic Calculations & Algorithms

EduGrade AI operates on standard **Choice Based Credit System (CBCS)** 10-point scale regulations:

### 1. Grade-to-Point Scale
| Grade | Points | Classification | Academic Implication |
| :---: | :---: | :--- | :--- |
| **O** | 10 | Outstanding | Earned full grade points |
| **A+** | 9 | Excellent | Earned full grade points |
| **A** | 8 | Very Good | Earned full grade points |
| **B+** | 7 | Good | Earned full grade points |
| **B** | 6 | Above Average | Earned full grade points |
| **C** | 5 | Average | Earned full grade points (Minimum passing) |
| **U** | 0 | Re-appear (Fail) | 0 credits earned; counted as active backlog |
| **RA** | 0 | Re-appear | 0 credits earned; counted as active backlog |
| **SA** | 0 | Shortage of Attendance | 0 credits earned; counted as active backlog |
| **W** | 0 | Withdrawal | 0 credits earned; counted as active backlog |

### 2. SGPA & CGPA Formulation
- **Semester Grade Point Average (SGPA)**:
  $$\text{SGPA} = \frac{\sum_{i=1}^{n} (\text{Credits}_i \times \text{GradePoints}_i)}{\sum_{i=1}^{n} \text{Credits}_i}$$
- **Cumulative Grade Point Average (CGPA)**:
  $$\text{CGPA} = \frac{\sum_{s=1}^{m} (\text{SGPA}_s \times \text{CreditsEarned}_s)}{\sum_{s=1}^{m} \text{CreditsEarned}_s}$$

### 3. Arrear Clearance Workflow
When faculty record a passing grade ($Grade \in \{O, A+, A, B+, B, C\}$) for a course previously failed ($U, RA, SA, W$):
1. The previous `CourseResult` is marked `arrear_cleared = True`, `cleared_on = timezone.now()`, and `previous_grade` is archived.
2. The student's active `backlogs` count in `UserProfile` is decremented.
3. The affected `SemesterRecord.sgpa`, overall `UserProfile.cgpa`, and placement eligibility are automatically recomputed.
4. An immutable audit record is logged in `AcademicAuditLog` (`action='ARREAR_CLEARED'`).

### 4. Placement Readiness Index (0–100 Scale)
A composite, explainable metric evaluating a student's employability:
$$\text{Readiness} = \underbrace{\min\left(50, \max\left(0, \frac{\text{CGPA}}{10} \times 50\right)\right)}_{\text{Academic Performance (50 pts)}} + \underbrace{\max\left(0, 30 - 15 \times \text{Backlogs}\right)}_{\text{Backlog Penalty (30 pts)}} + \underbrace{\left(\frac{\text{Eligible Companies}}{\text{Total Companies}} \times 20\right)}_{\text{Market Alignment (20 pts)}}$$
- **CGPA Component (50%)**: Linear scaling from 0 to 10 CGPA.
- **Backlog Component (30%)**: 30 points if 0 backlogs, 15 points if 1 backlog, 0 points if 2+ backlogs.
- **Company Eligibility (20%)**: Percentage of active recruiting companies where the student meets minimum CGPA and maximum backlog thresholds.
- **Actionable Guidance**: Deterministic tips prioritizing clearing backlogs first, lifting CGPA above 7.0/8.0 next, or maintaining competitive advantage.

### 5. At-Risk Student Criteria
Faculty dashboards flag students requiring academic intervention using configurable institutional thresholds:
- `AT_RISK_CGPA_THRESHOLD = 6.0`: CGPA strictly below 6.00.
- `AT_RISK_BACKLOG_THRESHOLD = 2`: 2 or more active/standing backlogs.

---

## 📡 Complete REST API Specification

All API endpoints are under `/api/` and enforce role-based authentication and student isolation:

| Endpoint | Method | Auth Required | Role | Description |
| :--- | :---: | :---: | :---: | :--- |
| `/api/auth/login/` | `POST` | No | Public | Authenticates user; rate-limited (5 failed attempts locks for 5 min) |
| `/api/auth/register/` | `POST` | No | Public | Registers student or faculty (requires `admin_key` for faculty) |
| `/api/auth/change-password/` | `POST` | Yes | Student/Admin | Validates old password and updates to new password |
| `/api/students/dashboard/` | `GET` | Yes | Student | Returns student metrics, CGPA, SGPA history, readiness score, and tips |
| `/api/student/arrears/` | `GET` | Yes | Student | Returns breakdown of active and cleared arrears |
| `/api/transcript/pdf/` | `GET` | Yes | Student/Admin | Streams generated PDF transcript (students restricted to own data) |
| `/api/academics/results/` | `GET` | Yes | Student | Returns semester course results and grade points |
| `/api/academics/planner/target-cgpa/` | `POST` | Yes | Student | Target CGPA simulator returning required upcoming SGPA and feasibility |
| `/api/academics/planner/what-if/` | `POST` | Yes | Student | Simulates CGPA impact given hypothetically assigned course grades |
| `/api/placements/eligibility/` | `GET` | Yes | Student | Evaluates eligibility across all corporate placement drives |
| `/api/advisor/chat/` | `POST` | Yes | Student | Context-aware AI chat with weakest subject 4-week study plan fallback |
| `/api/advisor/history/` | `DELETE` | Yes | Student | Deletes student's conversation history and creates an audit log |
| `/api/admin/dashboard/` | `GET` | Yes | Admin/Faculty | Overview of student count, average CGPA, and department roster |
| `/api/admin/analytics/` | `GET` | Yes | Admin/Faculty | Institutional grade distribution, department CGPA, and at-risk students |
| `/api/admin/grades/entry/` | `POST` | Yes | Admin/Faculty | Enters single course grade with automatic arrear clearance handling |
| `/api/admin/grades/sample-csv/` | `GET` | Yes | Admin/Faculty | Downloads standard CSV grade entry template |
| `/api/admin/grades/bulk-upload/` | `POST` | Yes | Admin/Faculty | Validates and ingests bulk grade CSV with detailed error report |

---

## 🧪 Verification & Automated Test Suites

EduGrade AI includes comprehensive automated testing:

```bash
# 1. Run all 102 Django unit and integration tests
python manage.py test

# 2. Run end-to-end route, API and permission verification
python test_routes.py

# 3. Verify ReactPy host component mounting
python test_reactpy.py

# 4. Check database referential integrity & migrations
python manage.py check_database
```

---

## 🚀 Running the Application

1. **Start the ASGI server**:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
2. **Access the portal**:
   Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in any modern web browser.
