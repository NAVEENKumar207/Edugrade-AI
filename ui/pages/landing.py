"""
ReactPy Landing Page Component for EduGrade AI.
Clean, scannable academic landing page matching design system.
"""

from reactpy import component, html, use_state
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import get_landing_stats

@component
def LandingPage(set_page, set_auth_role=None, theme="light", toggle_theme=None):
    stats = get_landing_stats()
    selected_role, set_selected_role = use_state("student")

    def go_to_login(role="student"):
        if set_auth_role:
            set_auth_role(role)
        set_page("login")

    role_data = {
        "student": {
            "title": "Academic Digital Twin",
            "value": str(stats.get('grades_count', 0)),
            "sub": "Records Evaluated"
        },
        "faculty": {
            "title": "Cohort Oversight",
            "value": str(stats.get('students_count', 0)),
            "sub": "Enrolled Students"
        },
        "placement": {
            "title": "Recruitment Drives",
            "value": str(stats.get('recruiters_count', 0)),
            "sub": "Active Drives"
        },
        "mentor": {
            "title": "Bilingual Mentor",
            "value": "24/7",
            "sub": "Tamil & English"
        }
    }

    current = role_data.get(selected_role, role_data["student"])

    capabilities = [
        {"num": "01", "icon": "menu_book", "title": "Regulation Config", "desc": "Marks rules and passing thresholds."},
        {"num": "02", "icon": "model_training", "title": "Digital Twin", "desc": "Monte Carlo degree forecast."},
        {"num": "03", "icon": "trending_up", "title": "Next Best Move", "desc": "Rank arrears by career unlock."},
        {"num": "04", "icon": "calculate", "title": "Marks Target", "desc": "Calculate needed paper marks."},
        {"num": "05", "icon": "psychology", "title": "Skill Fit", "desc": "Match courses to recruiter criteria."},
        {"num": "06", "icon": "business_center", "title": "Drive Manager", "desc": "Cohort tracking and CSV export."},
        {"num": "07", "icon": "verified", "title": "Verified Transcripts", "desc": "Cryptographic HMAC-SHA256 QR snapshots."},
        {"num": "08", "icon": "route", "title": "Journey Badges", "desc": "Semester milestones and achievements."},
        {"num": "09", "icon": "mic", "title": "Bilingual Voice", "desc": "English and Tamil speech advising."},
    ]

    return html.div(
        {
            "id": "top",
            "className": "min-h-screen flex flex-col bg-light-surface text-light-on-surface font-body antialiased"
        },
        # Header
        html.header(
            {"className": "bg-light-surface border-b border-light-outline-variant sticky top-0 z-30"},
            html.div(
                {"className": "max-w-[1200px] mx-auto px-6 py-3 flex items-center justify-between gap-4"},
                html.div(
                    {
                        "className": "flex items-center gap-3 cursor-pointer",
                        "on_click": lambda e: set_page("landing")
                    },
                    html.img({
                        "src": "/static/images/edugrade_ai_logo.jpeg",
                        "className": "h-8 w-auto object-contain border border-light-outline-variant",
                        "alt": "EduGrade AI"
                    }),
                    html.span({"className": "font-headline font-bold text-lg uppercase tracking-tight"}, "EduGrade AI")
                ),
                html.nav(
                    {"className": "hidden md:flex items-center gap-6 font-mono text-mono-sm uppercase text-light-on-surface-variant"},
                    html.a({"href": "#features", "className": "hover:text-light-primary transition-colors"}, "Capabilities"),
                    html.a({"href": "#stats", "className": "hover:text-light-primary transition-colors"}, "Metrics"),
                    html.button(
                        {
                            "className": "hover:text-light-primary transition-colors uppercase font-mono text-mono-sm cursor-pointer",
                            "on_click": lambda e: set_page("regulations")
                        },
                        "Regulations"
                    )
                ),
                html.div(
                    {"className": "flex items-center gap-3"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.button(
                        {
                            "className": "px-3 py-1.5 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                            "on_click": lambda e: go_to_login("student")
                        },
                        "Student Login"
                    ),
                    html.button(
                        {
                            "className": "px-3 py-1.5 bg-light-primary text-white hover:bg-light-primary-container font-mono text-mono-sm uppercase font-semibold transition-colors cursor-pointer",
                            "on_click": lambda e: go_to_login("admin")
                        },
                        "Faculty Access"
                    )
                )
            )
        ),

        # Hero Section
        html.main(
            {"className": "flex-1"},
            html.section(
                {"id": "hero", "className": "border-b border-light-outline-variant py-12 md:py-16 px-6 bg-light-surface"},
                html.div(
                    {"className": "max-w-[1200px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 items-center"},
                    html.div(
                        {"className": "lg:col-span-7 flex flex-col gap-4"},
                        html.span({"className": "font-mono text-mono-sm text-light-primary uppercase font-bold tracking-wider"}, "Academic Digital Twin"),
                        html.h1(
                            {"className": "font-headline text-3xl sm:text-4xl lg:text-5xl font-bold uppercase tracking-tight text-light-on-surface"},
                            "See Your Future, Not Just Your Past."
                        ),
                        html.p(
                            {"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"},
                            "Forecast graduation outcomes, rank career moves, and verify transcripts."
                        ),
                        html.div(
                            {"className": "flex flex-wrap items-center gap-3 pt-2"},
                            html.button(
                                {
                                    "className": "px-5 py-2.5 bg-light-primary text-white font-mono text-mono-sm uppercase font-semibold transition-colors cursor-pointer",
                                    "on_click": lambda e: go_to_login("student")
                                },
                                "Launch Simulator"
                            ),
                            html.button(
                                {
                                    "className": "px-5 py-2.5 border border-light-outline-variant hover:border-light-secondary font-mono text-mono-sm uppercase transition-colors cursor-pointer",
                                    "on_click": lambda e: go_to_login("student")
                                },
                                "Audit Placement"
                            )
                        )
                    ),
                    # Role Bento Card
                    html.div(
                        {"className": "lg:col-span-5 bg-light-surface-container-low border border-light-outline-variant p-6 flex flex-col justify-between min-h-[300px]"},
                        html.div(
                            {"className": "flex flex-col gap-4"},
                            html.div(
                                {"className": "flex flex-wrap items-center gap-3 border-b border-light-outline-variant pb-3 font-mono text-mono-sm uppercase"},
                                [
                                    html.button(
                                        {
                                            "key": r_key,
                                            "className": f"cursor-pointer transition-colors {'font-bold text-light-primary border-b-2 border-light-primary pb-1' if selected_role == r_key else 'text-light-on-surface-variant hover:text-light-on-surface'}",
                                            "on_click": lambda e, rk=r_key: set_selected_role(rk)
                                        },
                                        r_label
                                    )
                                    for r_key, r_label in [
                                        ("student", "Student"),
                                        ("faculty", "Faculty"),
                                        ("placement", "Placement"),
                                        ("mentor", "AI Mentor")
                                    ]
                                ]
                            ),
                            html.h3({"className": "font-headline text-xl font-bold uppercase"}, current["title"])
                        ),
                        html.div(
                            {"className": "pt-4 border-t border-light-outline-variant flex items-baseline justify-between"},
                            html.span({"className": "font-headline text-4xl font-bold tabular-nums text-light-primary"}, current["value"]),
                            html.span({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant"}, current["sub"])
                        )
                    )
                )
            ),

            # Capabilities Grid (9 Unique Features)
            html.section(
                {"id": "features", "className": "border-b border-light-outline-variant py-12 px-6 bg-light-surface-container-low"},
                html.div(
                    {"className": "max-w-[1200px] mx-auto flex flex-col gap-8"},
                    html.div(
                        {"className": "flex flex-col gap-1"},
                        html.span({"className": "text-label-xs font-mono text-light-primary uppercase font-bold tracking-wider"}, "Capabilities"),
                        html.h2({"className": "font-headline text-2xl font-bold text-light-on-surface uppercase"}, "Platform Features")
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"},
                        [
                            html.article(
                                {"key": f["title"], "className": "bg-light-surface border border-light-outline-variant p-5 flex flex-col gap-2"},
                                html.div(
                                    {"className": "flex items-center gap-2 text-light-primary"},
                                    html.span({"className": "material-symbols-outlined text-[20px]"}, f["icon"]),
                                    html.span({"className": "text-label-xs font-mono font-bold"}, f["num"])
                                ),
                                html.h3({"className": "font-headline text-base font-bold text-light-on-surface uppercase"}, f["title"]),
                                html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant"}, f["desc"])
                            )
                            for f in capabilities
                        ]
                    )
                )
            ),

            # Real Data Metrics Strip
            html.section(
                {"id": "stats", "className": "border-b border-light-outline-variant py-10 px-6 bg-light-surface"},
                html.div(
                    {"className": "max-w-[1200px] mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6"},
                    html.div(
                        {"className": "p-5 border border-light-outline-variant flex flex-col gap-1"},
                        html.span({"className": "font-headline text-3xl font-bold tabular-nums text-light-on-surface"}, str(stats.get('students_count', 0))),
                        html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Enrolled Students")
                    ),
                    html.div(
                        {"className": "p-5 border border-light-outline-variant bg-light-surface-container-low flex flex-col gap-1"},
                        html.span({"className": "font-headline text-3xl font-bold tabular-nums text-light-primary"}, str(stats.get('recruiters_count', 0))),
                        html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Corporate Drives")
                    ),
                    html.div(
                        {"className": "p-5 border border-light-outline-variant flex flex-col gap-1"},
                        html.span({"className": "font-headline text-3xl font-bold tabular-nums text-light-on-surface"}, str(stats.get('grades_count', 0))),
                        html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Course Records")
                    )
                )
            )
        ),

        # Compact One-line Footer
        html.footer(
            {"className": "bg-light-inverse-surface text-light-inverse-on-surface py-6 px-6"},
            html.div(
                {"className": "max-w-[1200px] mx-auto flex flex-wrap items-center justify-between gap-4 font-mono text-mono-sm"},
                html.span("© 2026 EduGrade AI • 10-Point CBCS System"),
                html.div(
                    {"className": "flex items-center gap-4"},
                    html.button(
                        {"className": "hover:text-light-inverse-primary cursor-pointer uppercase", "on_click": lambda e: set_page("regulations")},
                        "Regulations"
                    ),
                    html.button(
                        {"className": "hover:text-light-inverse-primary cursor-pointer uppercase", "on_click": lambda e: go_to_login("admin")},
                        "Faculty"
                    ),
                    html.a({"href": "#top", "className": "hover:text-light-inverse-primary uppercase"}, "Top ↑")
                )
            )
        )
    )
