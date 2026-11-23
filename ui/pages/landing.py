"""
ReactPy Landing Page Component for EduGrade AI.
Industrial Academic Precision Design System (Swiss-Brutalist 0px geometry, Vermilion signals, Space Grotesk / Inter / IBM Plex Mono).
Matches New Ui/landing_page/code.html.
"""

from reactpy import component, html, use_state
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import get_landing_stats

@component
def LandingPage(set_page, set_auth_role=None, theme="dark", toggle_theme=None):
    stats = get_landing_stats()
    selected_role, set_selected_role = use_state("student")

    def go_to_login(role="student"):
        if set_auth_role:
            set_auth_role(role)
        set_page("login")

    role_data = {
        "student": {
            "tags": ["NO SPREADSHEETS", "AUTO-AUDIT SGPA", "FLAG ARREARS", "EN / தமிழ் AI"],
            "title": "Breakdown of your degree progression",
            "value": str(stats.get("avg_cgpa", "8.64")),
            "sub": f"{stats.get('total_credits', 136)} / 160 Credits",
            "left": "11 / 14 DRIVES ELIGIBLE",
            "right": "0 ARREARS"
        },
        "faculty": {
            "tags": ["1,240 COHORT", "ATOMIC ENTRY", "AUDIT TRAIL", "82.4% ELIGIBLE"],
            "title": "Department cohort standing snapshot",
            "value": "8.18",
            "sub": f"{stats.get('total_students', 1240):,} Active Students",
            "left": "ATOMIC LEDGER SYNCED",
            "right": "CBCS 2026"
        },
        "placement": {
            "tags": ["14 DRIVES TRACKED", "CUTOFF AUDIT", "BACKLOG FILTER", "TIER-1 READY"],
            "title": "Corporate drive eligibility matrix",
            "value": f"{stats.get('placement_eligible_percent', 82.4)}%",
            "sub": "Cohort Qualified",
            "left": "ZOHO • MICROSOFT • GOOGLE",
            "right": "LIVE CUTOFFS"
        },
        "mentor": {
            "tags": ["GROUNDED AI", "EN & தமிழ்", "REMEDIATION PLAN", "TARGET SGPA"],
            "title": "Bilingual academic advisor telemetry",
            "value": "9.10",
            "sub": "Required Sem VII SGPA",
            "left": "CS3601 • MA3351 FOCUS",
            "right": "TAMIL + ENG"
        }
    }

    current = role_data.get(selected_role, role_data["student"])

    return html.div(
        {
            "id": "top",
            "className": "min-h-screen flex flex-col bg-light-surface text-light-on-surface font-body antialiased selection:bg-light-primary selection:text-white"
        },
        # 1. Top Site Navigation (Industrial Precision Style)
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
                        html.span({"className": "font-mono text-[10px] text-light-on-surface-variant uppercase tracking-wider leading-none mt-0.5"}, "INDUSTRIAL ACADEMIC INTELLIGENCE")
                    )
                ),
                # Nav links
                html.nav(
                    {"className": "hidden md:flex items-center gap-8 font-mono text-mono-sm uppercase text-light-on-surface-variant"},
                    html.a({"href": "#features", "className": "hover:text-light-primary transition-colors"}, "Capabilities"),
                    html.a({"href": "#workflow", "className": "hover:text-light-primary transition-colors"}, "Workflow"),
                    html.a({"href": "#effect", "className": "hover:text-light-primary transition-colors"}, "Effect"),
                    html.button(
                        {
                            "className": "hover:text-light-primary transition-colors uppercase font-mono text-mono-sm cursor-pointer",
                            "on_click": lambda e: set_page("regulations")
                        },
                        "CBCS 2026 Spec"
                    )
                ),
                # Actions & Theme Toggle
                html.div(
                    {"className": "flex items-center gap-3"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.button(
                        {
                            "className": "px-4 py-2 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                            "on_click": lambda e: go_to_login("student")
                        },
                        "Portal Login"
                    ),
                    html.button(
                        {
                            "className": "px-4 py-2 bg-light-primary text-white hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors cursor-pointer",
                            "on_click": lambda e: go_to_login("admin")
                        },
                        "Faculty Access"
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
                            "Academic Excellence Is Not Random. It Is Simulated."
                        ),
                        # Subtext
                        html.p(
                            {"className": "font-mono text-mono-sm md:text-body-lg text-light-on-surface-variant uppercase max-w-2xl leading-relaxed"},
                            "EduGrade AI models semester grades, predicts target CGPAs, audits placement cutoffs, and delivers bilingual EN/தமிழ் remediation plans."
                        ),
                        # CTAs
                        html.div(
                            {"className": "flex flex-wrap items-center gap-4 pt-2"},
                            html.button(
                                {
                                    "className": "px-6 py-3.5 bg-light-primary text-white hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors flex items-center gap-2 cursor-pointer shadow-sm",
                                    "on_click": lambda e: go_to_login("student")
                                },
                                html.span("Launch CGPA Simulator"),
                                html.span({"className": "material-symbols-outlined text-base"}, "arrow_forward")
                            ),
                            html.button(
                                {
                                    "className": "px-6 py-3.5 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                                    "on_click": lambda e: go_to_login("student")
                                },
                                "Audit Placement Eligibility"
                            )
                        ),
                        # Telemetry Strip
                        html.div(
                            {"className": "grid grid-cols-3 gap-4 border-t border-light-outline-variant pt-6 mt-4"},
                            html.div(
                                {"className": "flex flex-col gap-1"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-on-surface"}, "10.0"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Max CBCS Scale")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-primary"}, "< 1.0s"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Simulation Latency")
                            ),
                            html.div(
                                {"className": "flex flex-col gap-1"},
                                html.span({"className": "font-headline text-2xl lg:text-3xl font-bold tabular-nums text-light-on-surface"}, "EN / தமிழ்"),
                                html.span({"className": "font-mono text-[11px] text-light-on-surface-variant uppercase"}, "Bilingual AI Advisor")
                            )
                        )
                    ),

                    # Right Column: 3D Telemetry Bento Box (5 cols)
                    html.div(
                        {"className": "lg:col-span-5 bg-light-primary-container text-light-on-primary-container p-6 lg:p-8 flex flex-col justify-between min-h-[460px] border border-light-primary"},
                        # Role Switcher Tabs
                        html.div(
                            {"className": "flex flex-col gap-6"},
                            html.div(
                                {"className": "flex flex-wrap items-center gap-4 border-b border-light-on-primary-container/20 pb-4 font-mono text-mono-sm uppercase"},
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_role == 'student' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_role("student")
                                    },
                                    "Student"
                                ),
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_role == 'faculty' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_role("faculty")
                                    },
                                    "Faculty / Admin"
                                ),
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_role == 'placement' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_role("placement")
                                    },
                                    "Placement Cell"
                                ),
                                html.button(
                                    {
                                        "className": f"cursor-pointer transition-colors {'underline underline-offset-4 font-bold' if selected_role == 'mentor' else 'text-light-on-primary-container/70 hover:text-light-on-primary-container'}",
                                        "on_click": lambda e: set_selected_role("mentor")
                                    },
                                    "AI Mentor"
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
                            html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums uppercase"}, "160 Credits"),
                            html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Tracked across 8 semesters on official 10-point scale")
                        ),
                        html.div(
                            {"className": "p-8 bg-light-primary-container text-light-on-primary-container flex flex-col justify-between gap-2"},
                            html.span({"className": "font-headline text-4xl font-bold tabular-nums"}, f"{stats.get('placement_eligible_percent', 82.4)}%"),
                            html.span({"className": "font-mono text-mono-sm uppercase"}, "Cohort placement eligibility audited")
                        ),
                        html.div(
                            {"className": "p-8 bg-light-surface border-t sm:border-t-0 sm:border-l border-light-outline-variant flex flex-col justify-between gap-2"},
                            html.span({"className": "font-headline text-4xl font-bold text-light-on-surface tabular-nums"}, "100%"),
                            html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Atomic audit logging on every grade entry")
                        )
                    )
                )
            )
        ),

        # 5. Matte Carbon Dark Footer
        html.footer(
            {"className": "bg-light-inverse-surface text-light-inverse-on-surface py-12 px-6"},
            html.div(
                {"className": "max-w-[1440px] mx-auto flex flex-col gap-8"},
                html.div(
                    {"className": "flex flex-wrap items-center justify-between gap-4 border-b border-light-inverse-on-surface/20 pb-4"},
                    html.span({"className": "font-mono text-mono-sm uppercase"}, "© EduGrade AI 2026 • Regulation CBCS"),
                    html.a({"href": "#top", "className": "font-mono text-mono-sm uppercase hover:text-light-inverse-primary transition-colors"}, "Back to the Top ↑")
                ),
                html.div(
                    {"className": "grid grid-cols-2 md:grid-cols-4 gap-6 font-mono text-mono-sm"},
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.span({"className": "text-light-inverse-on-surface/60 uppercase font-semibold"}, "Portal"),
                        html.a({"href": "#features", "className": "hover:text-light-inverse-primary transition-colors"}, "Student Dashboard"),
                        html.a({"href": "#workflow", "className": "hover:text-light-inverse-primary transition-colors"}, "CGPA Simulator"),
                        html.a({"href": "#effect", "className": "hover:text-light-inverse-primary transition-colors"}, "Placement Matrix")
                    ),
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.span({"className": "text-light-inverse-on-surface/60 uppercase font-semibold"}, "Institution"),
                        html.button(
                            {
                                "className": "text-left hover:text-light-inverse-primary transition-colors cursor-pointer",
                                "on_click": lambda e: set_page("regulations")
                            },
                            "CBCS 2026 Rules"
                        ),
                        html.button(
                            {
                                "className": "text-left hover:text-light-inverse-primary transition-colors cursor-pointer",
                                "on_click": lambda e: go_to_login("admin")
                            },
                            "Faculty Admin"
                        )
                    ),
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.span({"className": "text-light-inverse-on-surface/60 uppercase font-semibold"}, "Languages"),
                        html.span("English (EN)"),
                        html.span("தமிழ் (Tamil)")
                    ),
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.span({"className": "text-light-inverse-on-surface/60 uppercase font-semibold"}, "Scale"),
                        html.span("O (10) → RA (0)"),
                        html.span("Credits: 160 Total")
                    )
                )
            )
        )
    )
