"""
ReactPy Landing Page Component for EduGrade AI.
Industrial Academic Precision Design System (Swiss-Brutalist 0px geometry, Vermilion signals, Space Grotesk / Inter / IBM Plex Mono).
Matches New Ui/landing_page/code.html.
"""

from reactpy import component, html, use_state
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import get_landing_stats, is_demo_mode_enabled

@component
def LandingPage(set_page, theme="dark", toggle_theme=None):
    stats = get_landing_stats()
    selected_feature, set_selected_feature = use_state("twin")
    demo_enabled = is_demo_mode_enabled()

    feature_data = {
        "twin": {
            "tags": ["DIGITAL TWIN", "MONTE CARLO", "P10 - P90 INTERVALS", "OUTCOME SIMULATION"],
            "title": "Probabilistic Graduation Forecasting",
            "value": f"{stats.get('grades_count', 0)}",
            "sub": "Academic Records Modelled",
            "left": "2,000 MONTE CARLO RUNS",
            "right": "EFFORT-AWARE ENGINE"
        },
        "moves": {
            "tags": ["NEXT BEST MOVE", "ARREAR RECOVERY", "MARGINAL CGPA", "DRIVE UNLOCKS"],
            "title": "Highest-Impact Arrear Prioritization",
            "value": "Top Move",
            "sub": "Impact-Ranked Remediation",
            "left": "PLACEMENT BENEFIT",
            "right": "ROI RANKING"
        },
        "target": {
            "tags": ["MARKS TARGET", "CIA 40 / ESE 60", "ANNA UNIV CBCS", "PASS THRESHOLD"],
            "title": "Reverse Exam Score Calculation",
            "value": "45%",
            "sub": "Min Theory Passing Paper",
            "left": "REVERSE MARKS TARGET",
            "right": "FEASIBILITY CHECK"
        },
        "advisor": {
            "tags": ["GROUNDED AI", "EN & தமிழ்", "WEB SPEECH VOICE", "STUDY PLANS"],
            "title": "Bilingual Voice Academic Mentor",
            "value": "24/7",
            "sub": "Automated Guidance",
            "left": "VOICE DICTATION",
            "right": "TAMIL + ENGLISH"
        },
        "badges": {
            "tags": ["7 BADGES", "TIMELINE", "LEAST-SQUARES", "TREND ALERT"],
            "title": "Milestone Badges & Growth Timeline",
            "value": "7 Badges",
            "sub": "Career Milestones",
            "left": "REGRESSION PREDICTION",
            "right": "CHRONOLOGICAL JOURNEY"
        }
    }

    current = feature_data.get(selected_feature, feature_data["twin"])

    return html.div(
        {
            "id": "top",
            "className": "min-h-screen flex flex-col bg-light-surface text-light-on-surface font-body antialiased selection:bg-light-primary selection:text-white"
        },
        # 1. Top Site Navigation
        html.header(
            {"className": "bg-light-surface border-b border-light-outline-variant sticky top-0 z-30"},
            html.div(
                {"className": "max-w-[1440px] mx-auto px-6 py-2.5 flex items-center justify-between gap-4"},
                # Brand Logo
                html.div(
                    {
                        "className": "flex items-center gap-3 cursor-pointer",
                        "on_click": lambda e: set_page("landing")
                    },
                    html.img({
                        "src": "/static/images/edugrade_ai_logo.jpeg",
                        "className": "h-9 w-auto object-contain border border-light-outline-variant",
                        "alt": "EduGrade AI"
                    }),
                    html.div(
                        {"className": "flex flex-col"},
                        html.span({"className": "font-headline font-bold text-lg tracking-tight uppercase leading-none"}, "EduGrade AI"),
                        html.span({"className": "font-mono text-[10px] text-light-on-surface-variant uppercase tracking-wider leading-none mt-0.5"}, "STUDENT ACADEMIC DIGITAL TWIN")
                    )
                ),

                # Actions & Theme Toggle
                html.div(
                    {"className": "flex items-center gap-3"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.button(
                        {
                            "id": "btn-watch-demo",
                            "data-demo": "watch-demo",
                            "className": "px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 text-white hover:from-amber-600 hover:to-orange-700 font-mono text-mono-sm uppercase font-bold transition-all shadow-md flex items-center gap-1.5 cursor-pointer border border-amber-400 animate-pulse hover:animate-none",
                            "style": {"backgroundColor": "#b45309", "color": "#ffffff"},
                            "on_click": lambda e: None
                        },
                        html.span({"className": "material-symbols-outlined text-base"}, "play_circle"),
                        html.span("Watch Demo ⚡")
                    ) if demo_enabled else None,
                    html.button(
                        {
                            "id": "btn-landing-register",
                            "data-demo": "landing-register-btn",
                            "className": "px-4 py-2 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("signup")
                        },
                        "Register"
                    ),
                    html.button(
                        {
                            "id": "btn-landing-login",
                            "data-demo": "landing-login-btn",
                            "className": "px-4 py-2 bg-light-primary text-light-on-primary hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("login")
                        },
                        "Student Portal Login"
                    )
                )
            )
        ),

        # 2. Hero Section: 12-Column Asymmetric Grid
        html.main(
            {"className": "flex-1"},
            html.section(
                {"id": "features", "className": "border-b border-light-outline-variant py-12 md:py-16 px-6 bg-light-surface"},
                html.div(
                    {"className": "max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-start"},
                    # Left Column (7 cols)
                    html.div(
                        {"className": "lg:col-span-7 flex flex-col gap-6"},
                        # Badge
                        html.div(
                            {"className": "inline-flex items-center gap-2 self-start px-3 py-1 bg-light-surface-container-low border border-light-outline-variant font-mono text-mono-sm uppercase"},
                            html.span({"className": "w-2 h-2 rounded-full bg-light-primary animate-pulse"}),
                            html.span("10-Pt CBCS System • Regulation 2026")
                        ),
                        # Headline
                        html.h1(
                            {"className": "font-headline text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-light-on-surface uppercase leading-none"},
                            "Your Academic Digital Twin — See Your Future, Not Just Your Past."
                        ),
                        # Subtext
                        html.p(
                            {"className": "font-mono text-mono-sm md:text-body-lg text-light-on-surface-variant uppercase max-w-2xl leading-relaxed"},
                            "A probabilistic academic intelligence platform forecasting degree outcomes with Monte Carlo simulations, ranking career unlock moves, and verifying transcripts with HMAC-SHA256 cryptography."
                        ),
                        # CTAs
                        html.div(
                            {"className": "flex flex-wrap items-center gap-4 pt-2"},
                            (
                                html.button(
                                    {
                                        "id": "btn-hero-watch-demo",
                                        "data-demo": "hero-watch-demo",
                                        "className": "px-6 py-3.5 bg-gradient-to-r from-amber-500 to-orange-600 text-white hover:from-amber-600 hover:to-orange-700 font-mono text-mono-sm uppercase font-bold transition-all shadow-md flex items-center gap-2 cursor-pointer border border-amber-400 animate-pulse hover:animate-none",
                                        "style": {"backgroundColor": "#b45309", "color": "#ffffff"},
                                        "on_click": lambda e: None
                                    },
                                    html.span({"className": "material-symbols-outlined text-base"}, "play_circle"),
                                    html.span("Watch Auto-Play Demo ⚡")
                                )
                                if demo_enabled else None
                            ),
                            html.button(
                                {
                                    "className": "px-6 py-3.5 bg-light-primary text-light-on-primary hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors flex items-center gap-2 cursor-pointer shadow-sm",
                                    "on_click": lambda e: set_page("login")
                                },
                                html.span("Launch CGPA Simulator"),
                                html.span({"className": "material-symbols-outlined text-base"}, "arrow_forward")
                            ),
                            html.button(
                                {
                                    "className": "px-6 py-3.5 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                                    "on_click": lambda e: set_page("login")
                                },
                                "Audit Placement Eligibility"
                            )
                        ),
                        # Telemetry Strip
                        html.div(
                            {"className": "grid grid-cols-3 gap-4 border-t border-light-outline-variant pt-6 mt-4"},
                            html.div(
                                {"className": "flex flex-col gap-1", "data-demo": "hero-stat-scale"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-on-surface"}, "10.0"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Max CBCS Scale")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1", "data-demo": "hero-stat-latency"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-primary"}, "< 1.0s"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Simulation Latency")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1", "data-demo": "hero-stat-voice"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-on-surface"}, "EN / தமிழ்"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Bilingual AI Advisor")
                            )
                        )
                    ),

                    # Right Column: 3D Telemetry Bento Box (5 cols)
                    html.div(
                        {"className": "lg:col-span-5 bg-light-primary-container text-light-on-primary-container p-6 lg:p-8 flex flex-col justify-between min-h-[460px] border border-light-primary"},
                        # Feature Switcher Tabs
                        html.div(
                            {"className": "flex flex-col gap-6"},
                            html.div(
                                {"className": "flex flex-wrap items-center gap-4 border-b border-light-on-primary-container/20 pb-4 font-mono text-mono-sm uppercase"},
                                html.button(
                                    {
                                        "data-demo": "feat-tab-twin",
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'twin' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("twin")
                                    },
                                    "Digital Twin"
                                ),
                                html.button(
                                    {
                                        "data-demo": "feat-tab-moves",
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'moves' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("moves")
                                    },
                                    "Next Best Move"
                                ),
                                html.button(
                                    {
                                        "data-demo": "feat-tab-target",
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'target' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("target")
                                    },
                                    "Marks Target"
                                ),
                                html.button(
                                    {
                                        "data-demo": "feat-tab-journey",
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'journey' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("journey")
                                    },
                                    "Journey & Badges"
                                ),
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'advisor' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("advisor")
                                    },
                                    "AI Advisor"
                                ),
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_feature == 'badges' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_feature("badges")
                                    },
                                    "Milestones"
                                )
                            ),
                            # Dynamic Tags
                            html.div(
                                {"className": "flex flex-wrap gap-2"},
                                [
                                    html.span(
                                        {"key": tag, "className": "px-3 py-1 rounded-full border border-light-on-primary-container font-mono text-[11px] uppercase tracking-wider"},
                                        tag
                                    ) for tag in current["tags"]
                                ]
                            ),
                            # Telemetry Title
                            html.h3(
                                {"className": "font-headline text-2xl font-bold uppercase tracking-tight leading-tight mt-2"},
                                current["title"]
                            )
                        ),
                        # Metric Block
                        html.div(
                            {"className": "mt-8 pt-6 border-t border-light-on-primary-container/20 flex flex-col gap-4"},
                            html.div(
                                {"className": "flex items-baseline justify-between"},
                                html.span({"className": "font-headline text-5xl font-bold tabular-nums"}, current["value"]),
                                html.span({"className": "font-mono text-mono-sm uppercase opacity-90"}, current["sub"])
                            ),
                            html.div(
                                {"className": "flex items-center justify-between font-mono text-[11px] uppercase tracking-wider opacity-85"},
                                html.span(current["left"]),
                                html.span(current["right"])
                            )
                        )
                    )
                )
            ),

            # 3. Workflow Section (01 SYNC / 02 SIMULATE / 03 UNLOCK)
            html.section(
                {"id": "workflow", "className": "border-b border-light-outline-variant py-14 px-6 bg-light-surface-container-low"},
                html.div(
                    {"className": "max-w-[1440px] mx-auto flex flex-col gap-10"},
                    html.h2(
                        {"className": "font-headline text-2xl md:text-3xl font-bold text-light-on-surface uppercase tracking-tight max-w-3xl leading-tight"},
                        "EduGrade Doesn't Change Curriculum, We Build On Existing Transcripts"
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 md:grid-cols-3 gap-6"},
                        # Card 01
                        html.article(
                            {"className": "bg-light-surface border border-light-outline-variant hover:border-light-secondary transition-colors p-6 flex flex-col justify-between min-h-[240px]"},
                            html.div(
                                {"className": "flex items-start justify-between"},
                                html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums"}, "01"),
                                html.span({"className": "px-2.5 py-1 bg-light-surface-container-low border border-light-outline-variant font-mono text-[11px] uppercase font-medium"}, "Input")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1.5 mt-6"},
                                html.h3({"className": "font-headline text-lg font-bold text-light-on-surface uppercase"}, "Sync"),
                                html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase leading-relaxed"}, "Import semester grades & credit weights with zero manual spreadsheets.")
                            )
                        ),
                        # Card 02
                        html.article(
                            {"className": "bg-light-surface border border-light-outline-variant hover:border-light-secondary transition-colors p-6 flex flex-col justify-between min-h-[240px]"},
                            html.div(
                                {"className": "flex items-start justify-between"},
                                html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums"}, "02"),
                                html.span({"className": "px-2.5 py-1 bg-light-surface-container-low border border-light-outline-variant font-mono text-[11px] uppercase font-medium"}, "Model")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1.5 mt-6"},
                                html.h3({"className": "font-headline text-lg font-bold text-light-on-surface uppercase"}, "Simulate"),
                                html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase leading-relaxed"}, "Model exact required SGPA across remaining credits in under 1 second.")
                            )
                        ),
                        # Card 03
                        html.article(
                            {"className": "bg-light-surface border border-light-outline-variant hover:border-light-primary transition-colors p-6 flex flex-col justify-between min-h-[240px]"},
                            html.div(
                                {"className": "flex items-start justify-between"},
                                html.span({"className": "font-headline text-4xl font-bold text-light-primary tabular-nums"}, "03"),
                                html.span({"className": "px-2.5 py-1 bg-light-primary-container text-light-on-primary-container font-mono text-[11px] uppercase font-bold"}, "Outcome")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1.5 mt-6"},
                                html.h3({"className": "font-headline text-lg font-bold text-light-on-surface uppercase"}, "Unlock"),
                                html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase leading-relaxed"}, "Audit placement cutoffs & follow bilingual EN / தமிழ் AI study plans.")
                            )
                        )
                    )
                )
            ),

            # 4. Asymmetric Bento KPI Grid ("THE EDUGRADE EFFECT")
            html.section(
                {"id": "effect", "className": "border-b border-light-outline-variant py-14 px-6 bg-light-surface"},
                html.div(
                    {"className": "max-w-[1440px] mx-auto grid grid-cols-1 lg:grid-cols-12 border border-light-outline-variant"},
                    html.div(
                        {"className": "lg:col-span-5 p-8 flex flex-col justify-between gap-6 border-b lg:border-b-0 lg:border-r border-light-outline-variant"},
                        html.h2({"className": "font-headline text-3xl font-bold text-light-on-surface uppercase tracking-tight"}, "The EduGrade Effect"),
                        html.p(
                            {"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase leading-relaxed"},
                            "In one portal, we uncover CGPA leverage, audit placement eligibility, and eliminate manual GPA calculations."
                        )
                    ),
                    html.div(
                        {"className": "lg:col-span-7 grid grid-cols-1 sm:grid-cols-2"},
                        html.div(
                            {"className": "sm:col-span-2 p-8 border-b border-light-outline-variant flex flex-col justify-between gap-2 bg-light-surface"},
                            html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums uppercase"}, str(stats.get('students_count', 0))),
                            html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Students enrolled in institutional database")
                        ),
                        html.div(
                            {"className": "p-8 bg-light-primary-container text-light-on-primary-container flex flex-col justify-between gap-2"},
                            html.span({"className": "font-headline text-4xl font-bold tabular-nums"}, str(stats.get('recruiters_count', 0))),
                            html.span({"className": "font-mono text-mono-sm uppercase"}, "Corporate Placement Partner Drives")
                        ),
                        html.div(
                            {"className": "p-8 bg-light-surface border-t sm:border-t-0 sm:border-l border-light-outline-variant flex flex-col justify-between gap-2"},
                            html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums"}, str(stats.get('grades_count', 0))),
                            html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Published course examination records")
                        )
                    )
                )
            ),

            # 4b. 9 Unique Digital Twin & Career Readiness Features
            html.section(
                {"id": "capabilities", "className": "border-b border-light-outline-variant py-14 px-6 bg-light-surface-container-low"},
                html.div(
                    {"className": "max-w-[1440px] mx-auto flex flex-col gap-10"},
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.span({"className": "text-label-sm font-mono text-light-primary uppercase font-bold tracking-wider"}, "Platform Capabilities"),
                        html.h2({"className": "font-headline text-2xl md:text-3xl font-bold text-light-on-surface uppercase tracking-tight"}, "9 Unique Capabilities Powering Your Academic Digital Twin")
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"},
                        [
                            html.article(
                                {"key": f["title"], "className": "bg-light-surface border border-light-outline-variant p-6 flex flex-col justify-between gap-4 rounded-radius-md hover:border-light-primary transition-colors"},
                                html.div(
                                    {"className": "flex flex-col gap-2"},
                                    html.div(
                                        {"className": "flex items-center gap-2 text-light-primary"},
                                        html.span({"className": "material-symbols-outlined text-[22px]"}, f["icon"]),
                                        html.span({"className": "text-label-xs font-mono font-bold uppercase"}, f["num"])
                                    ),
                                    html.h3({"className": "font-headline text-title-md font-bold text-light-on-surface uppercase"}, f["title"]),
                                    html.p({"className": "font-body text-body-sm text-light-on-surface-variant leading-relaxed"}, f["desc"])
                                )
                            )
                            for f in [
                                {"num": "01", "icon": "menu_book", "title": "Regulation Config", "desc": "Institutional regulation rules (core/regulation.py) defining internal marks, end-semester paper weights, passing minimums, and letter grade thresholds."},
                                {"num": "02", "icon": "model_training", "title": "Future Lab Simulator", "desc": "Probabilistic Monte Carlo digital twin forecasting your graduation CGPA and placement eligibility from your historical grade patterns."},
                                {"num": "03", "icon": "trending_up", "title": "Next Best Move", "desc": "Impact ranking analyzing your active arrears to identify which subject to clear first for the maximum CGPA boost and corporate recruiter unlocks."},
                                {"num": "04", "icon": "calculate", "title": "Marks Target Calculator", "desc": "Instant dual-mode examination target calculator determining exactly what paper marks you need to score your desired grade."},
                                {"num": "05", "icon": "psychology", "title": "Skill Map & Placement Fit", "desc": "Course-to-skill alignment comparing your academic mastery against corporate recruitment requirements with clear fit labels (Ready, Almost, Not yet)."},
                                {"num": "06", "icon": "receipt_long", "title": "Student Results & CSV Import", "desc": "Direct ownership of your semester records with interactive course CRUD, bulk CSV upload, downloadable template, and automatic SGPA/CGPA updates."},
                                {"num": "07", "icon": "verified", "title": "QR-Verified Transcripts", "desc": "Tamper-proof ReportLab academic transcripts embedding an autonomous cryptographic HMAC-SHA256 snapshot verification QR code."},
                                {"num": "08", "icon": "route", "title": "Journey & Milestone Badges", "desc": "Chronological semester progression timeline tracking SGPA changes and gamified achievement badges (Zero Arrears, Comeback, Distinction)."},
                                {"num": "09", "icon": "mic", "title": "Tamil & English Voice Mode", "desc": "Grounded bilingual academic advising with speech recognition and read-aloud playback right in the browser."},
                            ]
                        ]
                    )
                )
            )
        ),

        # 5. Matte Carbon Dark Footer
        html.footer(
            {"className": "bg-light-inverse-surface text-light-inverse-on-surface py-8 px-6"},
            html.div(
                {"className": "max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-4 font-mono text-mono-sm uppercase text-light-inverse-on-surface/60"},
                html.span("© EduGrade AI 2026 • Regulation CBCS"),
                html.span("Industrial Academic Intelligence Platform")
            )
        )
    )
