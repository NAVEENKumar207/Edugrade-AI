"""
Authentication Components (Login & Registration) for EduGrade AI ReactPy Frontend.
Enterprise Dark SaaS Aesthetic (Plus Jakarta Sans, Obsidian Slate, Electric Cyan).
"""

from reactpy import component, html, use_state
from ui.components.icons import icon_sparkles, icon_alert, icon_shield_check, icon_users, icon_check
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import authenticate_user, register_user

@component
def LoginPage(set_page, set_user, current_role='student', theme='dark', toggle_theme=None):
    role, set_role = use_state(current_role)
    username, set_username = use_state("")
    password, set_password = use_state("")
    error, set_error = use_state("")
    loading, set_loading = use_state(False)

    def do_login(u_val, p_val):
        set_error("")
        u_val = u_val.strip()
        if not u_val or not p_val:
            set_error("Please enter both username and password.")
            return

        set_loading(True)
        try:
            auth_res = authenticate_user(u_val, p_val)
            if isinstance(auth_res, tuple):
                user, auth_err = auth_res
            else:
                user, auth_err = auth_res, None

            if user:
                set_user(user)
                profile = getattr(user, 'profile', None)
                if profile and profile.is_admin():
                    set_page("admin_dashboard")
                else:
                    set_page("dashboard")
            else:
                set_error(auth_err or "Invalid credentials. Please verify your username and password.")
        except Exception as err:
            set_error(f"Authentication error: {str(err)}")
        finally:
            set_loading(False)

    def handle_submit(e=None):
        do_login(username, password)

    return html.div(
        {
            "style": {
                "minHeight": "100vh",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "2rem 1rem",
                "backgroundColor": "var(--bg-app)",
                "backgroundImage": "radial-gradient(circle at 50% 20%, rgba(56, 189, 248, 0.12) 0%, transparent 60%)",
                "position": "relative"
            }
        },
        # Top-right quick actions
        html.div(
            {
                "style": {
                    "position": "fixed",
                    "top": "1.25rem",
                    "right": "1.5rem",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "0.75rem",
                    "zIndex": "30"
                }
            },
            html.button(
                {
                    "className": "btn btn-secondary",
                    "style": {"fontSize": "0.8rem", "padding": "0.45rem 0.85rem"},
                    "on_click": lambda e: set_page("landing")
                },
                "← Home"
            ),
            ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None
        ),
        html.div(
            {
                "className": "card",
                "style": {
                    "width": "100%",
                    "maxWidth": "460px",
                    "padding": "2.75rem 2.25rem",
                    "borderRadius": "var(--radius-xl)",
                    "boxShadow": "var(--shadow-lg)",
                    "border": "1px solid var(--border-medium)",
                    "background": "var(--card-bg)"
                }
            },
            # Brand Header
            html.div(
                {"style": {"textAlign": "center", "marginBottom": "2rem"}},
                html.div(
                    {
                        "style": {
                            "width": "46px", "height": "46px",
                            "borderRadius": "12px",
                            "background": "linear-gradient(135deg, #38BDF8, #2563EB)",
                            "display": "flex", "alignItems": "center", "justifyContent": "center",
                            "margin": "0 auto 1rem auto",
                            "boxShadow": "0 0 20px rgba(56, 189, 248, 0.35)"
                        }
                    },
                    icon_sparkles(24, "#FFFFFF")
                ),
                html.h2(
                    {"style": {"fontSize": "1.75rem", "fontWeight": "800", "letterSpacing": "-0.02em", "color": "var(--text-primary)"}},
                    "Sign in to EduGrade"
                ),
                html.p(
                    {"style": {"color": "var(--text-secondary)", "fontSize": "0.9rem", "marginTop": "0.35rem"}},
                    "Access real-time CGPA tracking and placement intelligence"
                )
            ),

            # Role Switcher Toggle
            html.div(
                {
                    "style": {
                        "display": "flex",
                        "backgroundColor": "var(--bg-surface-elevated)",
                        "borderRadius": "var(--radius-sm)",
                        "padding": "0.25rem",
                        "marginBottom": "1.5rem",
                        "border": "1px solid var(--border-subtle)"
                    }
                },
                html.button(
                    {
                        "style": {
                            "flex": "1",
                            "padding": "0.6rem 1rem",
                            "borderRadius": "var(--radius-sm)",
                            "border": "none",
                            "cursor": "pointer",
                            "fontWeight": "700",
                            "fontSize": "0.85rem",
                            "backgroundColor": "rgba(56, 189, 248, 0.15)" if role == "student" else "transparent",
                            "color": "#38BDF8" if role == "student" else "var(--text-muted)",
                            "border": "1px solid rgba(56, 189, 248, 0.3)" if role == "student" else "1px solid transparent",
                            "transition": "all 0.15s ease"
                        },
                        "on_click": lambda e: set_role("student")
                    },
                    "Student"
                ),
                html.button(
                    {
                        "style": {
                            "flex": "1",
                            "padding": "0.6rem 1rem",
                            "borderRadius": "var(--radius-sm)",
                            "border": "none",
                            "cursor": "pointer",
                            "fontWeight": "700",
                            "fontSize": "0.85rem",
                            "backgroundColor": "rgba(56, 189, 248, 0.15)" if role == "admin" else "transparent",
                            "color": "#38BDF8" if role == "admin" else "var(--text-muted)",
                            "border": "1px solid rgba(56, 189, 248, 0.3)" if role == "admin" else "1px solid transparent",
                            "transition": "all 0.15s ease"
                        },
                        "on_click": lambda e: set_role("admin")
                    },
                    "Faculty / Admin"
                )
            ),

            # Error Notice
            html.div(
                {
                    "className": "badge-danger",
                    "style": {
                        "padding": "0.75rem 1rem",
                        "borderRadius": "var(--radius-sm)",
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "0.5rem",
                        "marginBottom": "1.25rem",
                        "fontSize": "0.85rem"
                    }
                },
                icon_alert(16, "#F87171"),
                html.span(error)
            ) if error else None,

            # Form Fields
            html.div(
                {"style": {"display": "flex", "flexDirection": "column", "gap": "1.25rem"}},
                html.div(
                    html.label(
                        {"style": {"display": "block", "fontSize": "0.825rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.4rem"}},
                        "Username or University Email"
                    ),
                    html.input({
                        "type": "text",
                        "className": "input",
                        "value": username,
                        "placeholder": "student" if role == "student" else "admin",
                        "on_change": lambda e: set_username(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.div(
                    html.label(
                        {"style": {"display": "block", "fontSize": "0.825rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.4rem"}},
                        "Password"
                    ),
                    html.input({
                        "type": "password",
                        "className": "input",
                        "value": password,
                        "placeholder": "••••••••",
                        "on_change": lambda e: set_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.button(
                    {
                        "className": "btn btn-primary",
                        "style": {
                            "width": "100%",
                            "padding": "0.85rem",
                            "marginTop": "0.5rem",
                            "fontSize": "0.95rem"
                        },
                        "disabled": loading,
                        "on_click": handle_submit
                    },
                    "Authenticating..." if loading else f"Sign in as {'Student' if role == 'student' else 'Faculty'} →"
                )
            ),

            # Navigation Links
            html.div(
                {"style": {"marginTop": "1.75rem", "textAlign": "center", "fontSize": "0.875rem", "color": "var(--text-secondary)"}},
                "Don't have an account? ",
                html.span(
                    {"style": {"color": "#38BDF8", "fontWeight": "600", "cursor": "pointer"}, "on_click": lambda e: set_page("signup")},
                    "Create Account"
                ),
                html.div(
                    {"style": {"marginTop": "0.75rem"}},
                    html.span(
                        {"style": {"color": "var(--text-muted)", "fontSize": "0.8rem", "cursor": "pointer"}, "on_click": lambda e: set_page("landing")},
                        "← Return to Landing Page"
                    )
                )
            )
        )
    )

@component
def SignupPage(set_page, set_user, theme='dark', toggle_theme=None):
    role, set_role = use_state("student")
    fullname, set_fullname = use_state("")
    username, set_username = use_state("")
    department, set_department = use_state("Computer Science & Engineering")
    roll_number, set_roll_number = use_state("")
    semester, set_semester = use_state(1)
    password, set_password = use_state("")
    admin_key, set_admin_key = use_state("")
    error, set_error = use_state("")
    loading, set_loading = use_state(False)

    def handle_submit(e=None):
        set_error("")
        if not username.strip() or not password:
            set_error("Username and password are required.")
            return

        set_loading(True)
        try:
            ok, result = register_user(
                role=role,
                fullname=fullname,
                username=username.strip(),
                department=department,
                password=password,
                roll_number=roll_number,
                semester=semester,
                admin_key=admin_key
            )
            if ok:
                set_user(result)
                if role == "admin":
                    set_page("admin_dashboard")
                else:
                    set_page("dashboard")
            else:
                set_error(str(result))
        except Exception as err:
            set_error(f"Registration error: {str(err)}")
        finally:
            set_loading(False)

    return html.div(
        {
            "style": {
                "minHeight": "100vh",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "2rem 1rem",
                "backgroundColor": "var(--bg-app)",
                "position": "relative"
            }
        },
        # Top-right quick actions
        html.div(
            {
                "style": {
                    "position": "fixed",
                    "top": "1.25rem",
                    "right": "1.5rem",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "0.75rem",
                    "zIndex": "30"
                }
            },
            html.button(
                {
                    "className": "btn btn-secondary",
                    "style": {"fontSize": "0.8rem", "padding": "0.45rem 0.85rem"},
                    "on_click": lambda e: set_page("landing")
                },
                "← Home"
            ),
            ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None
        ),
        html.div(
            {
                "className": "card",
                "style": {
                    "width": "100%",
                    "maxWidth": "500px",
                    "padding": "2.75rem 2.25rem",
                    "borderRadius": "var(--radius-xl)",
                    "boxShadow": "var(--shadow-lg)",
                    "border": "1px solid var(--border-medium)",
                    "background": "var(--card-bg)"
                }
            },
            html.div(
                {"style": {"textAlign": "center", "marginBottom": "1.75rem"}},
                html.h2(
                    {"style": {"fontSize": "1.65rem", "fontWeight": "800", "color": "var(--text-primary)"}},
                    "Create Your Account"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "fontSize": "0.85rem", "marginTop": "0.25rem"}}, "Register to access academic intelligence tools.")
            ),

            # Role Switcher
            html.div(
                {
                    "style": {
                        "display": "flex",
                        "backgroundColor": "var(--bg-surface-elevated)",
                        "borderRadius": "var(--radius-sm)",
                        "padding": "0.25rem",
                        "marginBottom": "1.5rem",
                        "border": "1px solid var(--border-subtle)"
                    }
                },
                html.button(
                    {
                        "style": {
                            "flex": "1",
                            "padding": "0.5rem",
                            "borderRadius": "var(--radius-sm)",
                            "border": "none",
                            "cursor": "pointer",
                            "fontWeight": "700",
                            "fontSize": "0.85rem",
                            "backgroundColor": "rgba(56, 189, 248, 0.15)" if role == "student" else "transparent",
                            "color": "#38BDF8" if role == "student" else "var(--text-muted)"
                        },
                        "on_click": lambda e: set_role("student")
                    },
                    "Student"
                ),
                html.button(
                    {
                        "style": {
                            "flex": "1",
                            "padding": "0.5rem",
                            "borderRadius": "var(--radius-sm)",
                            "border": "none",
                            "cursor": "pointer",
                            "fontWeight": "700",
                            "fontSize": "0.85rem",
                            "backgroundColor": "rgba(56, 189, 248, 0.15)" if role == "admin" else "transparent",
                            "color": "#38BDF8" if role == "admin" else "var(--text-muted)"
                        },
                        "on_click": lambda e: set_role("admin")
                    },
                    "Faculty / Admin"
                )
            ),

            # Error Alert
            html.div(
                {
                    "className": "badge-danger",
                    "style": {"padding": "0.75rem 1rem", "borderRadius": "var(--radius-sm)", "marginBottom": "1.25rem", "display": "flex", "alignItems": "center", "gap": "0.5rem"}
                },
                icon_alert(16, "#F87171"),
                html.span(error)
            ) if error else None,

            # Form Fields
            html.div(
                {"style": {"display": "flex", "flexDirection": "column", "gap": "1rem"}},
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Full Name"),
                    html.input({
                        "type": "text", "className": "input", "value": fullname,
                        "placeholder": "e.g. John Doe",
                        "on_change": lambda e: set_fullname(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Username"),
                    html.input({
                        "type": "text", "className": "input", "value": username,
                        "placeholder": "e.g. student01",
                        "on_change": lambda e: set_username(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Department"),
                    html.input({
                        "type": "text", "className": "input", "value": department,
                        "on_change": lambda e: set_department(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Roll Number"),
                    html.input({
                        "type": "text", "className": "input", "value": roll_number,
                        "placeholder": "e.g. 21CS042",
                        "on_change": lambda e: set_roll_number(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ) if role == "student" else None,
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Faculty Key"),
                    html.input({
                        "type": "password", "className": "input", "value": admin_key,
                        "placeholder": "Enter Authorization Key",
                        "on_change": lambda e: set_admin_key(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ) if role == "admin" else None,
                html.div(
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "600", "color": "var(--text-secondary)", "marginBottom": "0.3rem"}}, "Password"),
                    html.input({
                        "type": "password", "className": "input", "value": password,
                        "placeholder": "••••••••",
                        "on_change": lambda e: set_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                html.button(
                    {
                        "className": "btn btn-primary",
                        "style": {"width": "100%", "padding": "0.85rem", "marginTop": "0.5rem"},
                        "disabled": loading,
                        "on_click": handle_submit
                    },
                    "Creating Account..." if loading else "Register Account →"
                )
            ),

            html.div(
                {"style": {"marginTop": "1.5rem", "textAlign": "center", "fontSize": "0.85rem", "color": "var(--text-secondary)"}},
                "Already registered? ",
                html.span(
                    {"style": {"color": "#38BDF8", "fontWeight": "600", "cursor": "pointer"}, "on_click": lambda e: set_page("login")},
                    "Sign In"
                )
            )
        )
    )
