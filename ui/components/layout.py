"""
Layout Component for EduGrade AI ReactPy Frontend.
Provides responsive sidebar, top navbar, and user badges with Editorial Consultancy styling.
"""

from reactpy import component, html
from ui.components.icons import (
    icon_user, icon_sparkles, icon_trending_up, icon_book_open, icon_briefcase,
    icon_calculator, icon_bot, icon_layers, icon_shield_check,
    icon_award, icon_logout
)
from ui.components.theme_toggle import ThemeToggle

@component
def AppLayout(user, current_page, set_page, logout_action, children, theme="dark", toggle_theme=None):
    profile = getattr(user, 'profile', None)
    is_admin = profile.is_admin() if profile else False
    cgpa_val = float(profile.current_cgpa) if profile else 0.0

    nav_items = [
        {"id": "admin_dashboard", "label": "Cohort Intelligence", "icon": icon_shield_check(18)},
        {"id": "regulations", "label": "CBCS Regulations", "icon": icon_layers(18)},
        {"id": "profile", "label": "Faculty Profile", "icon": icon_user(18)},
    ] if is_admin else [
        {"id": "dashboard", "label": "Overview Dashboard", "icon": icon_trending_up(18)},
        {"id": "results", "label": "Semester Results", "icon": icon_book_open(18)},
        {"id": "planner", "label": "Target CGPA Planner", "icon": icon_calculator(18)},
        {"id": "placements", "label": "Placement Matrix", "icon": icon_briefcase(18)},
        {"id": "advisor", "label": "AI Academic Mentor", "icon": icon_bot(18)},
        {"id": "regulations", "label": "CBCS Framework", "icon": icon_layers(18)},
        {"id": "profile", "label": "Academic Profile", "icon": icon_user(18)},
    ]

    nav_elements = []
    for item in nav_items:
        is_active = current_page == item["id"]
        nav_elements.append(
            html.li(
                {"key": item["id"], "style": {"listStyle": "none"}},
                html.div(
                    {
                        "className": f"nav-link {'active' if is_active else ''}",
                        "on_click": lambda e, page_id=item["id"]: set_page(page_id)
                    },
                    item["icon"],
                    html.span(item["label"])
                )
            )
        )

    return html.div(
        {"className": "app-container"},
        # Responsive Editorial Sidebar
        html.aside(
            {"className": "sidebar"},
            html.div(
                {
                    "style": {
                        "padding": "1.75rem 1.5rem",
                        "borderBottom": "1px solid var(--border-subtle)",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "0.75rem",
                        "cursor": "pointer"
                    },
                    "on_click": lambda e: set_page("landing")
                },
                html.div(
                    {
                        "style": {
                            "width": "34px",
                            "height": "34px",
                            "borderRadius": "10px",
                            "background": "linear-gradient(135deg, var(--primary), var(--accent-indigo))",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "boxShadow": "0 0 16px rgba(56, 189, 248, 0.35)",
                            "flexShrink": "0"
                        }
                    },
                    icon_sparkles(18, "#FFFFFF")
                ),
                html.div(
                    html.div(
                        {"style": {"fontFamily": "var(--font-sans)", "fontSize": "1.25rem", "fontWeight": "800", "letterSpacing": "-0.02em", "color": "var(--text-primary)"}},
                        "EduGrade",
                        html.span({"style": {"color": "var(--primary)"}}, " AI")
                    ),
                    html.small({"style": {"color": "var(--text-muted)", "fontSize": "0.7rem", "fontWeight": "700", "letterSpacing": "0.08em", "textTransform": "uppercase"}}, "Academic Portal")
                )
            ),
            html.ul({"style": {"padding": "1rem 0", "flex": "1"}}, nav_elements),
            html.div(
                {
                    "style": {
                        "padding": "1.25rem",
                        "borderTop": "1px solid var(--border-subtle)",
                        "display": "flex",
                        "flexDirection": "column",
                        "gap": "0.75rem"
                    }
                },
                ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=False, style={"width": "100%", "justifyContent": "center"}) if toggle_theme else None,
                html.button(
                    {
                        "className": "btn",
                        "style": {
                            "width": "100%",
                            "justifyContent": "center",
                            "backgroundColor": "var(--bg-surface-elevated)",
                            "color": "var(--text-primary)",
                            "border": "1px solid var(--border-medium)",
                            "borderRadius": "var(--radius-full)",
                            "padding": "0.6rem 1rem",
                            "fontSize": "0.85rem"
                        },
                        "on_click": lambda e: logout_action()
                    },
                    icon_logout(16),
                    html.span({"style": {"marginLeft": "0.4rem"}}, "Sign Out")
                )
            )
        ),
        # Main Workspace
        html.div(
            {"className": "main-content"},
            html.header(
                {"className": "topbar"},
                html.div(
                    {"style": {"display": "flex", "alignItems": "center", "gap": "1rem"}},
                    html.span(
                        {
                            "style": {
                                "fontFamily": "var(--font-sans)",
                                "fontWeight": "600",
                                "fontSize": "1.05rem",
                                "color": "var(--text-primary)"
                            }
                        },
                        profile.department if profile else "Academic Intelligence Platform"
                    )
                ),
                html.div(
                    {"style": {"display": "flex", "alignItems": "center", "gap": "0.85rem"}},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.span(
                        {"className": "badge badge-vermillion", "style": {"padding": "0.4rem 0.85rem"}},
                        icon_shield_check(14, "var(--brand-vermillion)"), " Faculty / Admin"
                    ) if is_admin else html.span(
                        {"className": "badge", "style": {"backgroundColor": "var(--bg-surface-elevated)", "color": "var(--text-primary)", "border": "1px solid var(--border-medium)", "padding": "0.4rem 0.85rem"}},
                        icon_award(14, "var(--primary)"), f" CGPA: {cgpa_val:.2f}"
                    ),
                    html.div(
                        {
                            "style": {"textAlign": "right", "cursor": "pointer"},
                            "title": "View Academic Profile",
                            "on_click": lambda e: set_page("profile")
                        },
                        html.div({"style": {"fontSize": "0.9rem", "fontWeight": "700", "color": "var(--text-primary)"}}, f"{user.first_name} {user.last_name}".strip() or user.username),
                        html.div({"style": {"fontSize": "0.75rem", "color": "var(--text-muted)"}}, profile.roll_number if profile and profile.roll_number else user.email)
                    )
                )
            ),
            html.main({"className": "page-body"}, children)
        )
    )

