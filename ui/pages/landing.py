"""
ReactPy Landing Page Component for EduGrade AI.
Ultra-Professional Enterprise Academic Intelligence Platform.
"""

from reactpy import component, html
from ui.components.icons import (
    icon_sparkles, icon_trending_up, icon_briefcase, icon_shield_check, icon_bot, icon_award, icon_layers
)
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import get_landing_stats

@component
def LandingPage(set_page, set_auth_role=None, theme="dark", toggle_theme=None):
    stats = get_landing_stats()

    def go_to_login(role="student"):
        if set_auth_role:
            set_auth_role(role)
        set_page("login")

    return html.div(
        {"style": {"minHeight": "100vh", "backgroundColor": "var(--bg-app)", "color": "var(--text-primary)"}},
        
        # 1. Sleek Navigation Header
        html.header(
            {
                "style": {
                    "position": "fixed",
                    "top": "0", "left": "0", "right": "0",
                    "zIndex": "50",
                    "padding": "1rem 3rem",
                    "backdropFilter": "blur(16px)",
                    "backgroundColor": "var(--topbar-bg)",
                    "borderBottom": "1px solid var(--border-subtle)",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "transition": "background-color 0.25s ease, border-color 0.25s ease"
                }
            },
            html.div(
                {"style": {"display": "flex", "alignItems": "center", "gap": "0.75rem", "cursor": "pointer"}, "on_click": lambda e: set_page("landing")},
                html.div(
                    {
                        "style": {
                            "width": "34px", "height": "34px",
                            "borderRadius": "8px",
                            "background": "linear-gradient(135deg, #38BDF8, #6366F1)",
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "boxShadow": "0 0 15px rgba(56, 189, 248, 0.3)"
                        }
                    },
                    icon_sparkles(18, "#FFFFFF")
                ),
                html.span(
                    {"style": {"fontSize": "1.25rem", "fontWeight": "800", "letterSpacing": "-0.02em", "color": "var(--text-primary)"}},
                    "EduGrade",
                    html.span({"style": {"color": "#38BDF8"}}, " AI")
                )
            ),
            html.nav(
                {"style": {"display": "flex", "gap": "2.25rem", "fontSize": "0.9rem", "fontWeight": "600", "color": "var(--text-secondary)"}},
                html.a({"href": "#features", "style": {"transition": "color 0.15s ease", "cursor": "pointer"}}, "Capabilities"),
                html.a({"href": "#matrix", "style": {"transition": "color 0.15s ease", "cursor": "pointer"}}, "Placement Matrix"),
                html.a({"href": "#regulations", "style": {"transition": "color 0.15s ease", "cursor": "pointer"}, "on_click": lambda e: set_page("regulations")}, "CBCS Syllabus")
            ),
            html.div(
                {"style": {"display": "flex", "gap": "0.75rem", "alignItems": "center"}},
                ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                html.button(
                    {
                        "className": "btn btn-secondary",
                        "style": {"fontSize": "0.825rem", "padding": "0.55rem 1.25rem"},
                        "on_click": lambda e: go_to_login("student")
                    },
                    "Student Portal"
                ),
                html.button(
                    {
                        "className": "btn btn-primary",
                        "style": {"fontSize": "0.825rem", "padding": "0.55rem 1.25rem"},
                        "on_click": lambda e: go_to_login("admin")
                    },
                    "Faculty Access"
                )
            )
        ),

        # 2. Hero Section
        html.section(
            {
                "style": {
                    "position": "relative",
                    "paddingTop": "8.5rem",
                    "paddingBottom": "6rem",
                    "paddingLeft": "1.5rem",
                    "paddingRight": "1.5rem",
                    "textAlign": "center",
                    "background": "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(56, 189, 248, 0.18), transparent 70%)"
                }
            },
            html.div(
                {"style": {"maxWidth": "960px", "margin": "0 auto"}},
                # Pill Badge
                html.div(
                    {
                        "style": {
                            "display": "inline-flex",
                            "alignItems": "center",
                            "gap": "0.5rem",
                            "padding": "0.4rem 1rem",
                            "borderRadius": "var(--radius-full)",
                            "backgroundColor": "rgba(56, 189, 248, 0.08)",
                            "border": "1px solid rgba(56, 189, 248, 0.25)",
                            "color": "#38BDF8",
                            "fontSize": "0.825rem",
                            "fontWeight": "700",
                            "letterSpacing": "0.03em",
                            "marginBottom": "2rem"
                        }
                    },
                    icon_sparkles(15, "#38BDF8"),
                    "NEXT-GENERATION ACADEMIC INTELLIGENCE PLATFORM"
                ),
                # Headline
                html.h1(
                    {
                        "style": {
                            "fontSize": "clamp(2.5rem, 5.5vw, 4.25rem)",
                            "fontWeight": "800",
                            "lineHeight": "1.15",
                            "letterSpacing": "-0.03em",
                            "marginBottom": "1.75rem",
                            "color": "var(--text-primary)"
                        }
                    },
                    "Transform Academic Performance with ",
                    html.span(
                        {
                            "style": {
                                "background": "linear-gradient(135deg, #38BDF8 0%, #818CF8 100%)",
                                "WebkitBackgroundClip": "text",
                                "WebkitTextFillColor": "transparent"
                            }
                        },
                        "Predictive Analytics & AI"
                    )
                ),
                # Subtitle
                html.p(
                    {
                        "style": {
                            "fontSize": "1.15rem",
                            "color": "var(--text-secondary)",
                            "maxWidth": "720px",
                            "margin": "0 auto 2.75rem auto",
                            "lineHeight": "1.65"
                        }
                    },
                    "Accurate credit-weighted CGPA/SGPA calculations, target milestone what-if simulations, campus recruitment criteria matrices, and personalized bilingual AI mentorship."
                ),
                # CTAs
                html.div(
                    {"style": {"display": "flex", "gap": "1rem", "justifyContent": "center", "flexWrap": "wrap"}},
                    html.button(
                        {
                            "className": "btn btn-primary",
                            "style": {"fontSize": "0.95rem", "padding": "0.85rem 2rem", "borderRadius": "var(--radius-sm)"},
                            "on_click": lambda e: go_to_login("student")
                        },
                        "Explore Student Portal →"
                    ),
                    html.button(
                        {
                            "className": "btn btn-secondary",
                            "style": {"fontSize": "0.95rem", "padding": "0.85rem 2rem", "borderRadius": "var(--radius-sm)"},
                            "on_click": lambda e: go_to_login("admin")
                        },
                        "Faculty Dashboard"
                    )
                )
            )
        ),

        # 3. Institutional Stat Highlights
        html.section(
            {
                "style": {
                    "padding": "2rem 1.5rem",
                    "borderTop": "1px solid var(--border-subtle)",
                    "borderBottom": "1px solid var(--border-subtle)",
                    "backgroundColor": "var(--bg-surface-elevated)"
                }
            },
            html.div(
                {
                    "style": {
                        "maxWidth": "1100px", "margin": "0 auto",
                        "display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                        "gap": "1.5rem", "textAlign": "center"
                    }
                },
                html.div(
                    html.div({"style": {"fontSize": "1.85rem", "fontWeight": "800", "color": "var(--primary)"}}, f"{stats['students_count']} Enrolled"),
                    html.div({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, "Active Student Cohort")
                ),
                html.div(
                    html.div({"style": {"fontSize": "1.85rem", "fontWeight": "800", "color": "var(--text-primary)"}}, f"{stats['grades_count']} Course Records"),
                    html.div({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, "Published Grade Breakdown")
                ),
                html.div(
                    html.div({"style": {"fontSize": "1.85rem", "fontWeight": "800", "color": "var(--success)"}}, f"{stats['recruiters_count']} Partners"),
                    html.div({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, "Placement Criteria Matrix")
                ),
                html.div(
                    html.div({"style": {"fontSize": "1.85rem", "fontWeight": "800", "color": "var(--accent-purple)"}}, "English & தமிழ்"),
                    html.div({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, "Bilingual AI Advisor")
                )
            )
        ),

        # 4. Enterprise Capabilities Grid
        html.section(
            {
                "id": "features",
                "style": {"maxWidth": "1200px", "margin": "5rem auto", "padding": "0 1.5rem"}
            },
            html.div(
                {"style": {"textAlign": "center", "marginBottom": "3.5rem"}},
                html.h2(
                    {"style": {"fontSize": "2.25rem", "fontWeight": "800", "letterSpacing": "-0.02em", "color": "var(--text-primary)"}},
                    "Comprehensive Academic Intelligence"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.5rem"}}, "Built for students striving for tier-1 placements and faculties managing cohort excellence.")
            ),
            html.div(
                {
                    "style": {
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                        "gap": "1.5rem"
                    }
                },
                # Card 1: CGPA Calculation
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--primary)"}}, icon_award(32, "var(--primary)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "Credit-Weighted Calculations"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Mathematical SGPA and CGPA computation aligned with university Choice Based Credit System regulations. Zero rounding discrepancies.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: go_to_login("student")},
                        "Explore Calculator →"
                    )
                ),
                # Card 2: What-if Planner
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--accent-indigo)"}}, icon_trending_up(32, "var(--accent-indigo)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "Target CGPA Simulator"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Interactive what-if scenario forecasting. Instantly computes the exact SGPA required across your remaining semesters to reach your graduation goal.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: go_to_login("student")},
                        "Simulate Trajectory →"
                    )
                ),
                # Card 3: Placement Matrix
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--success)"}}, icon_briefcase(32, "var(--success)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "Placement Eligibility Matrix"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Real-time auditing against verified corporate package cutoffs and standing backlog constraints.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: go_to_login("student")},
                        "Check Eligibility →"
                    )
                ),
                # Card 4: AI Advisor
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--accent-purple)"}}, icon_bot(32, "var(--accent-purple)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "Bilingual AI Advisor"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Personalized guidance in English and Tamil grounded in your authentic grade record, weak subjects, and upcoming campus drives.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: go_to_login("student")},
                        "Consult AI Mentor →"
                    )
                ),
                # Card 5: Faculty Intelligence
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--warning)"}}, icon_shield_check(32, "var(--warning)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "Cohort Analytics & Audits"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Departmental pass ratios, student performance directories, and single or batch course grade publication with automatic CGPA recalculation.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: go_to_login("admin")},
                        "Faculty Dashboard →"
                    )
                ),
                # Card 6: Academic Regulations
                html.div(
                    {"className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                    html.div(
                        html.div({"style": {"marginBottom": "1.25rem", "color": "var(--primary)"}}, icon_layers(32, "var(--primary)")),
                        html.h3({"style": {"fontSize": "1.25rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem"}}, "CBCS Curriculum Reference"),
                        html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "lineHeight": "1.6"}}, "Complete semester-by-semester course directory, credit weighting schedules, and university grade boundaries.")
                    ),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"marginTop": "1.5rem", "fontSize": "0.85rem"}, "on_click": lambda e: set_page("regulations")},
                        "View Regulations →"
                    )
                )
            )
        ),

        # 5. Footer CTA
        html.footer(
            {
                "style": {
                    "borderTop": "1px solid var(--border-subtle)",
                    "padding": "4rem 2rem",
                    "textAlign": "center",
                    "backgroundColor": "var(--bg-surface)"
                }
            },
            html.h2(
                {"style": {"fontSize": "2rem", "fontWeight": "800", "color": "var(--text-primary)", "marginBottom": "1rem"}},
                "Ready to Optimize Your Academic Trajectory?"
            ),
            html.p(
                {"style": {"color": "var(--text-secondary)", "maxWidth": "600px", "margin": "0 auto 2rem auto"}},
                "Sign in to your dashboard to review credit milestones and placement readiness."
            ),
            html.div(
                {"style": {"display": "flex", "gap": "1rem", "justifyContent": "center"}},
                html.button(
                    {"className": "btn btn-primary", "style": {"padding": "0.75rem 2rem"}, "on_click": lambda e: go_to_login("student")},
                    "Launch Student Portal"
                ),
                html.button(
                    {"className": "btn btn-secondary", "style": {"padding": "0.75rem 2rem"}, "on_click": lambda e: go_to_login("admin")},
                    "Faculty Sign In"
                )
            ),
            html.div(
                {"style": {"marginTop": "3rem", "color": "var(--text-muted)", "fontSize": "0.8rem"}},
                "EduGrade AI Academic Intelligence Platform • Built with Django & ReactPy"
            )
        )
    )

