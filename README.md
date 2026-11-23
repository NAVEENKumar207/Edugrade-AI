# EduGrade AI — Academic Intelligence & Career Platform

EduGrade AI is a Python full-stack academic platform providing credit-weighted CGPA/SGPA calculations, target simulation, placement eligibility auditing, and grounded AI advising.

Built with **Django 6**, **Django REST Framework**, **Django Channels**, **Daphne**, **SQLite**, and **ReactPy** (`reactpy-django`).

---

## Capabilities

1. **CBCS Grading Engine**: Unified regulation logic in `core/regulation.py` (40% internal, 60% external).
2. **Future Lab Simulator**: Probabilistic Monte Carlo trajectory simulation predicting graduation CGPA.
3. **Next Best Move**: Impact-ranked arrear recovery showing highest placement and CGPA unlocks.
4. **Marks Target Calculator**: Computes required external exam marks from internal assessment scores.
5. **Skill Map & Placement Match**: Credit-weighted technical skill scoring against corporate drive criteria.
6. **Drive Manager**: Faculty and placement coordinator dashboard with CSV roster exports.
7. **Tamper-Proof Transcripts**: HMAC-SHA256 signed PDF transcripts with embedded QR code verification.
8. **Academic Journey & Badges**: Milestone timeline with 7 achievement badges and early-warning risk detection.
9. **Bilingual AI Advisor**: Grounded English and Tamil academic guidance with browser voice dictation.

---

## Tech Stack

- **Backend**: Python 3.13, Django 6, Django REST Framework, Django Channels, Daphne, SQLite.
- **Frontend**: ReactPy (`reactpy-django`) SPA over WebSockets, host template `templates/reactpy_index.html`.
- **Services**: ReportLab for signed transcripts, Groq / OpenAI with rule-based fallback for AI advising.
- **Legacy UI**: Django templates in `templates/` preserved for backward compatibility.

---

## Quickstart

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run migrations
python manage.py migrate

# 3. Load sample placement criteria and skill mappings
python manage.py load_sample_companies
python manage.py load_sample_skill_map

# 4. Start the application
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Configuration (`.env`)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | Django secret key | Dev insecure key |
| `DEBUG` | Enable debug mode | `False` |
| `ADMIN_SIGNUP_KEY` | Secret key for faculty registration | Empty |
| `TRANSCRIPT_SIGNING_KEY` | HMAC signing key for transcript QR | Django secret key |
| `GROQ_API_KEY` | Groq Cloud API key for AI advisor | Optional |
| `GROQ_MODEL` | Groq model name | `llama-3.3-70b-versatile` |

---

## Testing

```bash
# Full test suite (174 tests)
python manage.py test

# Route, API, and permission verification
python test_routes.py

# ReactPy component mounting test
python test_reactpy.py
```

---

## Architecture

- `core/`: Django app containing models, REST APIs (`api_views.py`), regulations (`regulation.py`), and domain services (`services/`).
- `ui/`: ReactPy single-page application (`app.py`, `pages/`, `components/`, `services/data_service.py`).
- `templates/`: ReactPy host template (`reactpy_index.html`), public transcript verification (`verify.html`), and legacy views.
- `static/css/reactpy_styles.css`: Complete dark/light design system.

---

## Honesty Notes

- **Simulator**: Future projections are estimates based on academic history, not guarantees.
- **Regulations**: Assessment rules are defined in `core/regulation.py`; check them against your college regulations.
- **Transcripts**: QR verification presents a point-in-time snapshot with student PII masked.
- **Voice Service**: Speech recognition and synthesis run on the user's browser speech engine.
- **AI Advice**: Advisor recommendations are guidance, not official institutional decisions.
