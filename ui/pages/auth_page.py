"""
Authentication Components (Login & Registration) for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design System (Swiss-Brutalist 0px geometry, Vermilion signals).
Matches New Ui/authentication_login_signup/code.html.
"""

from django.conf import settings
from reactpy import component, html, use_state
from ui.components.theme_toggle import ThemeToggle
from ui.services.data_service import authenticate_user, register_user, quick_demo_login

@component
def LoginPage(set_page, set_user, theme='dark', toggle_theme=None):
    username, set_username = use_state("")
    password, set_password = use_state("")
    show_password, set_show_password = use_state(False)
    error, set_error = use_state("")
    loading, set_loading = use_state(False)

    is_debug = getattr(settings, 'DEBUG', False)

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
                set_page("dashboard")
            else:
                set_error(auth_err or "Invalid credentials. Please verify your username and password.")
        except Exception as err:
            set_error(f"Authentication error: {str(err)}")
        finally:
            set_loading(False)

    def handle_submit(e=None):
        do_login(username, password)

    def handle_1click_demo():
        set_error("")
        set_loading(True)
        try:
            demo_user, demo_err = quick_demo_login()
            if demo_user:
                set_user(demo_user)
                set_page("dashboard")
            else:
                set_error(demo_err or "Unable to initialize demo account.")
        except Exception as err:
            set_error(f"Demo access error: {str(err)}")
        finally:
            set_loading(False)

    return html.div(
        {
            "className": "min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-light-surface text-light-on-surface font-body antialiased selection:bg-light-primary selection:text-white"
        },
        # Left Matte Carbon Institutional Showcase Panel (5 cols on lg)
        html.aside(
            {"className": "hidden lg:flex lg:col-span-5 bg-stone-950 text-stone-100 p-10 flex-col justify-between border-r border-stone-800 relative overflow-hidden"},
            # Top Brand header
            html.div(
                {"className": "flex items-center justify-between gap-4"},
                html.div(
                    {
                        "className": "inline-flex items-center gap-3 bg-light-surface px-3 py-1.5 border border-light-outline-variant cursor-pointer",
                        "on_click": lambda e: set_page("landing")
                    },
                    html.img({
                        "src": "/static/images/edugrade_ai_logo.jpeg",
                        "className": "h-7 w-auto object-contain",
                        "alt": "EduGrade AI"
                    }),
                    html.span({"className": "font-headline font-bold text-sm tracking-tight text-light-on-surface uppercase"}, "EduGrade AI")
                ),
                html.span({"className": "font-mono text-mono-sm uppercase text-stone-400"}, "CBCS 2026")
            ),

            # Mid Showcase Bento Grid
            html.div(
                {"className": "flex flex-col gap-6 my-auto py-8"},
                html.div(
                    {"className": "flex flex-col gap-2"},
                    html.span({"className": "font-mono text-mono-sm uppercase text-orange-400 tracking-wider font-semibold"}, "Institutional Portal"),
                    html.h1({"className": "font-headline text-3xl font-bold uppercase tracking-tight leading-tight"}, "Precision Grading. Guaranteed Placement Clearance.")
                ),
                html.div(
                    {"className": "grid grid-cols-1 gap-4 font-mono text-mono-sm"},
                    # Telemetry Card 1
                    html.div(
                        {"className": "p-4 bg-stone-900 border border-stone-800 flex flex-col gap-1"},
                        html.span({"className": "text-stone-400 uppercase text-[11px]"}, "Target Simulator"),
                        html.div(
                            {"className": "flex items-baseline justify-between"},
                            html.span({"className": "text-white font-bold text-base"}, "Target: 8.50 CGPA"),
                            html.span({"className": "text-orange-400 font-bold"}, "Req: 8.78 SGPA")
                        ),
                        html.span({"className": "text-[11px] text-emerald-400 uppercase mt-1"}, "● Status: Feasible Clearance")
                    ),
                    # Telemetry Card 2
                    html.div(
                        {"className": "p-4 bg-stone-900 border border-stone-800 flex flex-col gap-1"},
                        html.span({"className": "text-stone-400 uppercase text-[11px]"}, "Placement Cutoff Matrix"),
                        html.div(
                            {"className": "flex items-baseline justify-between"},
                            html.span({"className": "text-white font-bold text-base"}, "Microsoft • Tier 1"),
                            html.span({"className": "text-stone-300"}, "Cutoff: 8.50")
                        ),
                        html.span({"className": "text-[11px] text-emerald-400 uppercase mt-1"}, "● Eligible with Zero Arrears")
                    )
                )
            ),

            # Bottom Security Footnote
            html.div(
                {"className": "flex items-center justify-between font-mono text-mono-sm uppercase text-stone-400 border-t border-stone-800 pt-4"},
                html.span("PBKDF2 SHA-256 Encryption"),
                html.span("Atomic Audit Log")
            )
        ),

        # Right Authentication Panel (7 cols on lg)
        html.div(
            {"className": "col-span-1 lg:col-span-7 flex flex-col justify-between p-6 sm:p-10 lg:p-12 bg-light-surface min-h-screen"},
            # Top Action Bar
            html.div(
                {"className": "flex items-center justify-between gap-4 border-b border-light-outline-variant pb-4"},
                # Mode Tabs
                html.div(
                    {"className": "flex items-center gap-2 font-mono text-mono-sm uppercase"},
                    html.button(
                        {
                            "type": "button",
                            "disabled": True,
                            "aria-selected": "true",
                            "className": "px-4 py-1.5 bg-light-secondary text-light-on-secondary font-semibold cursor-default"
                        },
                        "Sign In"
                    ),
                    html.button(
                        {
                            "data-demo": "goto-signup-btn",
                            "className": "px-4 py-1.5 text-light-on-surface-variant hover:text-light-on-surface transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("signup")
                        },
                        "Create Account"
                    )
                ),
                # Quick Action buttons
                html.div(
                    {"className": "flex items-center gap-3"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.button(
                        {
                            "className": "px-3 py-1 border border-light-outline-variant font-mono text-mono-sm uppercase hover:border-light-secondary transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("landing")
                        },
                        "← Home"
                    )
                )
            ),

            # Main Form Body
            html.div(
                {"className": "max-w-xl w-full mx-auto my-auto py-8 flex flex-col gap-6"},
                # Header & Portal Badge
                html.div(
                    {"className": "flex flex-col gap-4"},
                    html.h2({"className": "font-headline text-3xl font-bold uppercase tracking-tight text-light-on-surface"}, "Secure Access Gateway"),
                    html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Authenticate using student credentials to access academic records."),
                    html.div(
                        {"className": "p-3 border border-light-primary bg-light-primary text-light-on-primary font-mono text-mono-sm uppercase text-left flex flex-col gap-1"},
                        html.span({"className": "text-[11px] opacity-75"}, "Undergraduate Academic Portal"),
                        html.span({"className": "text-sm font-bold"}, "Student Sign In")
                    )
                ),

                # 1-Click Demo Buttons (Only when DEBUG is True)
                html.div(
                    {"className": "p-3.5 bg-light-surface-container-low border border-light-outline-variant flex flex-col gap-2.5"},
                    html.div(
                        {"className": "flex items-center justify-between font-mono text-[11px] uppercase text-light-on-surface-variant"},
                        html.span({"className": "font-semibold flex items-center gap-1.5"}, html.span({"className": "material-symbols-outlined text-sm text-light-primary"}, "bolt"), "1-Click Demo Credentials (DEBUG Active)"),
                        html.span({"className": "text-[10px] text-emerald-600 dark:text-emerald-400 font-bold"}, "● Auto Sign In")
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 gap-2"},
                        html.button(
                            {
                                "id": "login-quick-demo-btn",
                                "data-demo": "login-quick-demo-btn",
                                "type": "button",
                                "disabled": loading,
                                "className": "px-3 py-2 bg-light-surface border border-light-outline-variant hover:border-light-primary font-mono text-[11px] uppercase text-left transition-colors cursor-pointer flex items-center justify-between shadow-sm",
                                "on_click": lambda e: handle_1click_demo()
                            },
                            html.div(
                                {"className": "flex flex-col"},
                                html.span({"className": "font-bold text-light-on-surface"}, "Demo Student"),
                                html.span({"className": "text-[10px] text-light-on-surface-variant"}, "student01 • Naveenkumar S")
                            ),
                            html.span({"className": "text-[10px] font-bold text-light-primary px-2 py-0.5 bg-light-primary/10 rounded"}, "SIGN IN ⚡")
                        )
                    )
                ) if is_debug else None,

                # Error Alert
                html.div(
                    {"className": "p-3.5 bg-red-50 dark:bg-red-950/40 border border-light-error text-light-error font-mono text-mono-sm flex items-center gap-2.5"},
                    html.span({"className": "material-symbols-outlined text-lg"}, "warning"),
                    html.span(error)
                ) if error else None,

                # Form Inputs
                html.form(
                    {
                        "className": "flex flex-col gap-4",
                        "on_submit": lambda e: handle_submit()
                    },
                    # Username / Register Number
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label(
                            {"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium flex items-center justify-between"},
                            html.span("Username or Register Number"),
                            html.span({"className": "text-[11px] opacity-75"}, "REQUIRED")
                        ),
                        html.div(
                            {"className": "relative flex items-center"},
                            html.span({"className": "material-symbols-outlined absolute left-3 text-light-on-surface-variant pointer-events-none text-lg"}, "badge"),
                            html.input({
                                "id": "login-username",
                                "data-demo": "login-username",
                                "type": "text",
                                "value": username,
                                "className": "w-full pl-10 pr-3 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                                "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                                "placeholder": "e.g. 22CSE041 or student01",
                                "on_change": lambda e: set_username(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            })
                        )
                    ),
                    # Password
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.div(
                            {"className": "flex items-center justify-between font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"},
                            html.span("Password"),
                            html.button(
                                {
                                    "type": "button",
                                    "className": "text-[11px] hover:text-light-primary transition-colors cursor-pointer",
                                    "on_click": lambda e: set_error("Contact your institutional department administrator to reset credentials.")
                                },
                                "Forgot Password?"
                            )
                        ),
                        html.div(
                            {"className": "relative flex items-center"},
                            html.span({"className": "material-symbols-outlined absolute left-3 text-light-on-surface-variant pointer-events-none text-lg"}, "lock"),
                            html.input({
                                "id": "login-password",
                                "data-demo": "login-password",
                                "type": "text" if show_password else "password",
                                "value": password,
                                "className": "w-full pl-10 pr-10 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                                "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                                "placeholder": "Enter institutional password",
                                "on_change": lambda e: set_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            }),
                            html.button(
                                {
                                    "type": "button",
                                    "className": "absolute right-3 text-light-on-surface-variant hover:text-light-on-surface transition-colors cursor-pointer flex items-center",
                                    "on_click": lambda e: set_show_password(not show_password)
                                },
                                html.span({"className": "material-symbols-outlined text-lg"}, "visibility_off" if show_password else "visibility")
                            )
                        )
                    ),
                    # Submit Button
                    html.button(
                        {
                            "id": "login-submit-btn",
                            "data-demo": "login-submit-btn",
                            "type": "button",
                            "disabled": loading,
                            "className": "w-full py-3.5 bg-light-primary text-light-on-primary hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm mt-2 disabled:opacity-50",
                            "on_click": lambda e: handle_submit()
                        },
                        html.span("Verifying..." if loading else "Sign In to Student Portal"),
                        html.span({"className": "material-symbols-outlined text-base"}, "login")
                    )
                ),

                # Bottom Switcher
                html.div(
                    {"className": "text-center font-mono text-mono-sm text-light-on-surface-variant border-t border-light-outline-variant pt-4"},
                    html.span("Don't have an institutional profile? "),
                    html.button(
                        {
                            "className": "text-light-primary font-semibold hover:underline uppercase cursor-pointer",
                            "on_click": lambda e: set_page("signup")
                        },
                        "Create Account"
                    )
                )
            ),

            # Bottom Compliance Strip
            html.div(
                {"className": "flex flex-wrap items-center justify-between gap-4 font-mono text-[11px] uppercase text-light-on-surface-variant/75 border-t border-light-outline-variant pt-4"},
                html.span("256-Bit SSL Encryption"),
                html.span("ISO 27001 Audited"),
                html.span("Zero Data Leakage Guarantee")
            )
        )
    )

@component
def SignupPage(set_page, set_user, theme='dark', toggle_theme=None):
    fullname, set_fullname = use_state("")
    username, set_username = use_state("")
    institution_name, set_institution_name = use_state("K.S. Rangasamy College of Technology (Autonomous)")
    department, set_department = use_state("Computer Science and Business Systems")
    roll_number, set_roll_number = use_state("")
    password, set_password = use_state("")
    confirm_password, set_confirm_password = use_state("")
    show_password, set_show_password = use_state(False)
    error, set_error = use_state("")
    loading, set_loading = use_state(False)

    is_debug = getattr(settings, 'DEBUG', False)

    def handle_1click_demo():
        set_error("")
        set_loading(True)
        try:
            demo_user, demo_err = quick_demo_login()
            if demo_user:
                set_user(demo_user)
                set_page("dashboard")
            else:
                set_error(demo_err or "Unable to initialize demo account.")
        except Exception as err:
            set_error(f"Demo access error: {str(err)}")
        finally:
            set_loading(False)

    def handle_signup(e=None):
        set_error("")
        if not username.strip() or not password or not fullname.strip():
            set_error("Full name, username, and password are required.")
            return

        if password != confirm_password:
            set_error("Passwords do not match.")
            return

        if len(password) < 6:
            set_error("Password must be at least 6 characters long.")
            return

        set_loading(True)
        try:
            reg_res = register_user(
                username=username.strip(),
                password=password,
                fullname=fullname.strip(),
                institution_name=institution_name.strip(),
                department=department.strip(),
                roll_number=roll_number.strip()
            )
            # Defensively handle both (user, err) and legacy (bool, payload)
            if isinstance(reg_res, tuple) and len(reg_res) == 2:
                first, second = reg_res
                if hasattr(first, 'username') and hasattr(first, 'id'):
                    user, reg_err = first, second
                elif hasattr(second, 'username') and hasattr(second, 'id'):
                    user, reg_err = second, None
                elif first is False or first is None:
                    user, reg_err = None, (second if isinstance(second, str) else "Registration failed.")
                else:
                    user, reg_err = first, second
            else:
                user, reg_err = (reg_res if hasattr(reg_res, 'username') else None), None

            if user and hasattr(user, 'username'):
                set_user(user)
                set_page("dashboard")
            else:
                set_error(reg_err or "Registration failed. Please verify your details.")
        except Exception as err:
            set_error(f"Registration error: {str(err)}")
        finally:
            set_loading(False)

    return html.div(
        {
            "className": "min-h-screen grid grid-cols-1 lg:grid-cols-12 bg-light-surface text-light-on-surface font-body antialiased selection:bg-light-primary selection:text-white"
        },
        # Left Matte Carbon Panel
        html.aside(
            {"className": "hidden lg:flex lg:col-span-5 bg-stone-950 text-stone-100 p-10 flex-col justify-between border-r border-stone-800 relative overflow-hidden"},
            html.div(
                {"className": "flex items-center justify-between gap-4"},
                html.div(
                    {
                        "className": "inline-flex items-center gap-3 bg-light-surface px-3 py-1.5 border border-light-outline-variant cursor-pointer",
                        "on_click": lambda e: set_page("landing")
                    },
                    html.img({
                        "src": "/static/images/edugrade_ai_logo.jpeg",
                        "className": "h-7 w-auto object-contain",
                        "alt": "EduGrade AI"
                    }),
                    html.span({"className": "font-headline font-bold text-sm tracking-tight text-light-on-surface uppercase"}, "EduGrade AI")
                ),
                html.span({"className": "font-mono text-mono-sm uppercase text-stone-400"}, "CBCS 2026")
            ),
            html.div(
                {"className": "flex flex-col gap-6 my-auto py-8"},
                html.div(
                    {"className": "flex flex-col gap-2"},
                    html.span({"className": "font-mono text-mono-sm uppercase text-orange-400 tracking-wider font-semibold"}, "Institutional Enrollment"),
                    html.h1({"className": "font-headline text-3xl font-bold uppercase tracking-tight leading-tight"}, "Create Your Verified Academic Ledger Identity.")
                ),
                html.p(
                    {"className": "font-mono text-mono-sm text-stone-300 uppercase leading-relaxed"},
                    "Once registered, your transcripts, semester credits, target CGPA models, and placement audits are stored securely with zero third-party telemetry."
                )
            ),
            html.div(
                {"className": "flex items-center justify-between font-mono text-mono-sm uppercase text-stone-400 border-t border-stone-800 pt-4"},
                html.span("Anna Univ CBCS Scale"),
                html.span("Atomic Audit Trail")
            )
        ),

        # Right Form Panel
        html.div(
            {"className": "col-span-1 lg:col-span-7 flex flex-col justify-between p-6 sm:p-10 lg:p-12 bg-light-surface min-h-screen"},
            # Top Action Bar
            html.div(
                {"className": "flex items-center justify-between gap-4 border-b border-light-outline-variant pb-4"},
                html.div(
                    {"className": "flex items-center gap-2 font-mono text-mono-sm uppercase"},
                    html.button(
                        {
                            "className": "px-4 py-1.5 text-light-on-surface-variant hover:text-light-on-surface transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("login")
                        },
                        "Sign In"
                    ),
                    html.button(
                        {
                            "type": "button",
                            "disabled": True,
                            "aria-selected": "true",
                            "className": "px-4 py-1.5 bg-light-secondary text-light-on-secondary font-semibold cursor-default"
                        },
                        "Create Account"
                    )
                ),
                html.div(
                    {"className": "flex items-center gap-3"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    html.button(
                        {
                            "className": "px-3 py-1 border border-light-outline-variant font-mono text-mono-sm uppercase hover:border-light-secondary transition-colors cursor-pointer",
                            "on_click": lambda e: set_page("landing")
                        },
                        "← Home"
                    )
                )
            ),

            # Main Form Body
            html.div(
                {"className": "max-w-xl w-full mx-auto my-auto py-8 flex flex-col gap-6"},
                html.div(
                    {"className": "flex flex-col gap-2"},
                    html.h2({"className": "font-headline text-3xl font-bold uppercase tracking-tight text-light-on-surface"}, "Register New Account"),
                    html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Enroll into the official institutional academic intelligence system.")
                ),

                # Portal Badge
                html.div(
                    {"className": "p-3 border border-light-primary bg-light-primary text-light-on-primary font-mono text-mono-sm uppercase text-left flex flex-col gap-1"},
                    html.span({"className": "text-[11px] opacity-75"}, "Undergraduate Academic Portal"),
                    html.span({"className": "text-sm font-bold"}, "New Student Registration")
                ),

                # 1-Click Demo Buttons (Only when DEBUG is True)
                html.div(
                    {"className": "p-3.5 bg-light-surface-container-low border border-light-outline-variant flex flex-col gap-2.5"},
                    html.div(
                        {"className": "flex items-center justify-between font-mono text-[11px] uppercase text-light-on-surface-variant"},
                        html.span({"className": "font-semibold flex items-center gap-1.5"}, html.span({"className": "material-symbols-outlined text-sm text-light-primary"}, "bolt"), "1-Click Demo Credentials (DEBUG Active)"),
                        html.span({"className": "text-[10px] text-emerald-600 dark:text-emerald-400 font-bold"}, "● Auto Sign In")
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 gap-2"},
                        html.button(
                            {
                                "id": "login-quick-demo-btn",
                                "data-demo": "login-quick-demo-btn",
                                "type": "button",
                                "disabled": loading,
                                "className": "px-3 py-2 bg-light-surface border border-light-outline-variant hover:border-light-primary font-mono text-[11px] uppercase text-left transition-colors cursor-pointer flex items-center justify-between shadow-sm",
                                "on_click": lambda e: handle_1click_demo()
                            },
                            html.div(
                                {"className": "flex flex-col"},
                                html.span({"className": "font-bold text-light-on-surface"}, "Demo Student"),
                                html.span({"className": "text-[10px] text-light-on-surface-variant"}, "student01 • Naveenkumar S")
                            ),
                            html.span({"className": "text-[10px] font-bold text-light-primary px-2 py-0.5 bg-light-primary/10 rounded"}, "SIGN IN ⚡")
                        )
                    )
                ) if is_debug else None,

                # Error Alert
                html.div(
                    {"className": "p-3.5 bg-red-50 dark:bg-red-950/40 border border-light-error text-light-error font-mono text-mono-sm flex items-center gap-2.5"},
                    html.span({"className": "material-symbols-outlined text-lg"}, "warning"),
                    html.span(error)
                ) if error else None,

                # Form Fields
                html.form(
                    {
                        "className": "flex flex-col gap-4",
                        "on_submit": lambda e: handle_signup()
                    },
                    # Full Name
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Full Name"),
                        html.input({
                            "id": "signup-fullname",
                            "data-demo": "signup-fullname",
                            "type": "text",
                            "value": fullname,
                            "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                            "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                            "placeholder": "e.g. Anand Kumar",
                            "on_change": lambda e: set_fullname(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    # Username
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Username"),
                        html.input({
                            "id": "signup-username",
                            "data-demo": "signup-username",
                            "type": "text",
                            "value": username,
                            "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                            "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                            "placeholder": "e.g. anand01",
                            "on_change": lambda e: set_username(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    # Institution Name
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Institution Name"),
                        html.input({
                            "id": "signup-institution",
                            "data-demo": "signup-institution",
                            "type": "text",
                            "value": institution_name,
                            "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                            "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                            "placeholder": "e.g. Anna University / Affiliated Institution",
                            "on_change": lambda e: set_institution_name(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    # Department
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Department"),
                        html.input({
                            "id": "signup-dept",
                            "data-demo": "signup-dept",
                            "type": "text",
                            "value": department,
                            "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                            "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                            "placeholder": "e.g. Computer Science and Engineering",
                            "on_change": lambda e: set_department(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    # Roll Number
                    html.div(
                        {"className": "flex flex-col gap-1.5"},
                        html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Register / Roll Number"),
                        html.input({
                            "id": "signup-roll",
                            "data-demo": "signup-roll",
                            "type": "text",
                            "value": roll_number,
                            "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                            "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                            "placeholder": "e.g. 22CSE041",
                            "on_change": lambda e: set_roll_number(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    # Password & Confirm Password in 2 cols
                    html.div(
                        {"className": "grid grid-cols-1 sm:grid-cols-2 gap-4"},
                        html.div(
                            {"className": "flex flex-col gap-1.5"},
                            html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Password"),
                            html.input({
                                "id": "signup-password",
                                "data-demo": "signup-password",
                                "type": "password",
                                "value": password,
                                "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                                "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                                "placeholder": "Min. 6 chars",
                                "on_change": lambda e: set_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            })
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1.5"},
                            html.label({"className": "font-mono text-mono-sm uppercase text-light-on-surface-variant font-medium"}, "Confirm Password"),
                            html.input({
                                "id": "signup-confirm",
                                "data-demo": "signup-confirm",
                                "type": "password",
                                "value": confirm_password,
                                "className": "w-full px-3.5 py-2.5 bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 font-mono text-mono-sm text-light-on-surface outline-none transition-colors",
                                "style": {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"},
                                "placeholder": "Repeat password",
                                "on_change": lambda e: set_confirm_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            })
                        )
                    ),
                    # Submit Button
                    html.button(
                        {
                            "id": "signup-submit-btn",
                            "data-demo": "signup-submit-btn",
                            "type": "button",
                            "disabled": loading,
                            "className": "w-full py-3.5 bg-light-primary text-light-on-primary hover:bg-light-primary-container hover:text-light-secondary font-mono text-mono-sm uppercase font-semibold transition-colors flex items-center justify-center gap-2 cursor-pointer shadow-sm mt-3 disabled:opacity-50",
                            "on_click": lambda e: handle_signup()
                        },
                        html.span("Registering..." if loading else "Register Student Account"),
                        html.span({"className": "material-symbols-outlined text-base"}, "person_add")
                    )
                ),

                html.div(
                    {"className": "text-center font-mono text-mono-sm text-light-on-surface-variant border-t border-light-outline-variant pt-4"},
                    html.span("Already registered? "),
                    html.button(
                        {
                            "data-demo": "goto-login-btn",
                            "className": "text-light-primary font-semibold hover:underline uppercase cursor-pointer",
                            "on_click": lambda e: set_page("login")
                        },
                        "Sign In"
                    )
                )
            ),

            # Bottom Compliance Strip
            html.div(
                {"className": "flex flex-wrap items-center justify-between gap-4 font-mono text-[11px] uppercase text-light-on-surface-variant/75 border-t border-light-outline-variant pt-4"},
                html.span("CBCS 2026 Compatible"),
                html.span("Encrypted Credentials"),
                html.span("Instant Access")
            )
        )
    )
