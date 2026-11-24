"""
Root ReactPy Application for EduGrade AI Platform (Student-Only Portal).
Manages global client-side routing, user session state, and component rendering.
"""

from reactpy import component, html, use_state
from ui.pages.landing import LandingPage
from ui.pages.auth_page import LoginPage, SignupPage
from ui.pages.student_dashboard import StudentDashboard
from ui.pages.results_page import ResultsPage
from ui.pages.cgpa_planner import CgpaPlanner
from ui.pages.placement_page import PlacementPage
from ui.pages.ai_advisor import AiAdvisorPage
from ui.pages.regulations_page import RegulationsPage
from ui.pages.profile_page import ProfilePage
from ui.pages.future_lab import FutureLab
from ui.pages.journey_page import JourneyPage
from ui.components.layout import AppLayout

@component
def EduGradeApp():
    # Session user, route state, and theme state
    current_page, set_current_page = use_state("landing")
    current_user, set_current_user = use_state(None)
    theme, set_theme = use_state("light")

    def toggle_theme():
        set_theme("light" if theme == "dark" else "dark")

    def handle_logout():
        set_current_user(None)
        set_current_page("landing")

    # If unauthenticated and on public pages:
    if not current_user:
        if current_page == "login":
            page_content = LoginPage(
                set_page=set_current_page,
                set_user=set_current_user,
                theme=theme,
                toggle_theme=toggle_theme
            )
        elif current_page == "signup":
            page_content = SignupPage(
                set_page=set_current_page,
                set_user=set_current_user,
                theme=theme,
                toggle_theme=toggle_theme
            )
        elif current_page == "regulations":
            from ui.components.theme_toggle import ThemeToggle
            page_content = html.div(
                {"style": {"minHeight": "100vh", "backgroundColor": "var(--bg-app)", "padding": "2rem"}},
                html.div(
                    {
                        "style": {
                            "maxWidth": "1400px",
                            "margin": "0 auto 1.5rem auto",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "space-between"
                        }
                    },
                    html.button(
                        {
                            "className": "btn btn-secondary",
                            "style": {"fontSize": "0.85rem"},
                            "on_click": lambda e: set_current_page("landing")
                        },
                        "← Back to Landing Page"
                    ),
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True)
                ),
                html.div(
                    {"style": {"maxWidth": "1400px", "margin": "0 auto"}},
                    RegulationsPage()
                )
            )
        else:
            page_content = LandingPage(
                set_page=set_current_page,
                theme=theme,
                toggle_theme=toggle_theme
            )

        return html.div(
            {
                "id": "app-root",
                "className": f"app-root theme-{theme} {'dark' if theme == 'dark' else ''}",
                "data-theme": theme,
                "style": {"minHeight": "100vh", "backgroundColor": "var(--bg-app)"}
            },
            page_content
        )

    # For authenticated student users - Student-only routing
    if current_page in ["future_lab", "futurelab", "twin"]:
        page_content = FutureLab(user=current_user, set_page=set_current_page)
    elif current_page in ["journey", "my_journey"]:
        page_content = JourneyPage(user=current_user)
    elif current_page == "results":
        page_content = ResultsPage(user=current_user)
    elif current_page == "planner":
        page_content = CgpaPlanner(user=current_user)
    elif current_page in ["placements", "placement"]:
        page_content = PlacementPage(user=current_user)
    elif current_page in ["advisor", "ai_advisor", "ai-advisor"]:
        page_content = AiAdvisorPage(user=current_user)
    elif current_page in ["regulations", "syllabus"]:
        page_content = RegulationsPage()
    elif current_page == "profile":
        page_content = ProfilePage(user=current_user, set_user=set_current_user)
    else:
        page_content = StudentDashboard(user=current_user, set_page=set_current_page)

    return html.div(
        {
            "id": "app-root",
            "className": f"app-root theme-{theme} {'dark' if theme == 'dark' else ''}",
            "data-theme": theme,
            "style": {"minHeight": "100vh", "backgroundColor": "var(--bg-app)"}
        },
        AppLayout(
            user=current_user,
            current_page=current_page,
            set_page=set_current_page,
            logout_action=handle_logout,
            theme=theme,
            toggle_theme=toggle_theme,
            children=page_content
        )
    )

