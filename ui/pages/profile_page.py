"""
Student & Faculty Profile Page Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/profile_management/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import update_user_profile, change_user_password

@component
def ProfilePage(user):
    profile = getattr(user, 'profile', None)
    is_admin = profile.is_admin() if profile else False

    # State for editable fields
    first_name, set_first_name = use_state(user.first_name if user else "")
    last_name, set_last_name = use_state(user.last_name if user else "")
    email, set_email = use_state(user.email if user else "")
    target_cgpa, set_target_cgpa = use_state(str(profile.target_cgpa) if profile else "8.80")
    department, set_department = use_state(profile.department if profile else "Computer Science & Engineering")

    save_status, set_save_status = use_state("")
    save_error, set_save_error = use_state("")

    # State for Change Password
    old_password, set_old_password = use_state("")
    new_password, set_new_password = use_state("")
    confirm_password, set_confirm_password = use_state("")
    pw_status, set_pw_status = use_state("")
    pw_error, set_pw_error = use_state("")

    cgpa = float(profile.current_cgpa) if profile else 8.64
    credits_earned = int(profile.credits_earned) if profile else 136
    total_credits = int(profile.total_credits) if profile else 160
    backlogs = int(profile.backlogs_count) if profile else 0
    curr_sem = profile.current_semester if profile and profile.current_semester else 6

    initials = f"{user.first_name[:1] if user and user.first_name else ''}{user.last_name[:1] if user and user.last_name else ''}".upper() or user.username[:2].upper()

    def handle_save_profile(e=None):
        set_save_status("")
        set_save_error("")
        ok, msg = update_user_profile(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            target_cgpa=target_cgpa,
            department=department
        )
        if ok:
            set_save_status(msg)
        else:
            set_save_error(msg)

    def handle_change_password(e=None):
        set_pw_status("")
        set_pw_error("")
        ok, msg = change_user_password(
            user=user,
            old_password=old_password,
            new_password=new_password,
            confirm_password=confirm_password
        )
        if ok:
            set_pw_status(msg)
            set_old_password("")
            set_new_password("")
            set_confirm_password("")
        else:
            set_pw_error(msg)

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1200px] w-full mx-auto flex flex-col gap-section overflow-y-auto"},
        
        # Header
        html.header(
            {"class_name": "pb-gutter-md border-b border-light-outline-variant flex items-center justify-between gap-gutter-md"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md tracking-tight uppercase"}, "Profile"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"{profile.role.upper() if profile else 'STUDENT'} • CBCS 2026")
            ),
            html.span({"class_name": "font-mono text-mono-sm font-bold bg-light-surface-container-highest px-3 py-1"}, "CBCS 2026")
        ),

        # Profile Info & Academic Summary Bento
        html.div(
            {"class_name": "grid grid-cols-1 md:grid-cols-3 gap-gutter-lg"},
            
            # Identity Box
            html.div(
                {"class_name": "md:col-span-1 border-2 border-light-secondary p-gutter-lg bg-light-surface flex flex-col gap-gutter-md items-center text-center"},
                html.div(
                    {"class_name": "w-24 h-24 bg-light-secondary text-light-on-secondary flex items-center justify-center font-headline text-display-lg font-bold"},
                    initials
                ),
                html.div(
                    html.h2({"class_name": "font-headline text-headline-md uppercase"}, f"{first_name} {last_name}".strip() or user.username),
                    html.p({"class_name": "font-mono text-mono-sm text-light-primary font-bold"}, getattr(profile, 'roll_number', user.username)),
                    html.span({"class_name": "mt-2 inline-block px-3 py-0.5 bg-light-surface-container-highest font-mono text-mono-sm"}, f"{department} • {profile.role.upper() if profile else 'STUDENT'}")
                )
            ),

            # Academic Standing
            html.div(
                {"class_name": "md:col-span-2 border border-light-outline-variant bg-light-surface p-gutter-lg flex flex-col justify-between gap-gutter-md"},
                html.h3({"class_name": "font-headline text-title-lg uppercase border-b border-light-outline-variant pb-2"}, "Academic Standing & Metrics"),
                html.div(
                    {"class_name": "grid grid-cols-2 sm:grid-cols-4 gap-gutter-md"},
                    html.div(
                        html.span({"class_name": "font-mono text-mono-sm text-light-outline uppercase font-bold"}, "CURRENT CGPA"),
                        html.p({"class_name": "font-headline text-headline-lg text-light-primary font-bold tabular-nums"}, f"{cgpa:.2f}")
                    ),
                    html.div(
                        html.span({"class_name": "font-mono text-mono-sm text-light-outline uppercase font-bold"}, "CREDITS"),
                        html.p({"class_name": "font-headline text-headline-lg font-bold tabular-nums"}, f"{credits_earned} / {total_credits}")
                    ),
                    html.div(
                        html.span({"class_name": "font-mono text-mono-sm text-light-outline uppercase font-bold"}, "SEMESTER"),
                        html.p({"class_name": "font-headline text-headline-lg font-bold tabular-nums"}, str(curr_sem))
                    ),
                    html.div(
                        html.span({"class_name": "font-mono text-mono-sm text-light-outline uppercase font-bold"}, "ARREARS"),
                        html.p({"class_name": f"font-headline text-headline-lg font-bold tabular-nums {'text-light-primary' if backlogs > 0 else 'text-success'}"}, f"{backlogs} Active")
                    )
                )
            )
        ),

        # Editable Profile Details Section
        html.section(
            {"class_name": "border border-light-outline-variant bg-light-surface p-gutter-lg flex flex-col gap-gutter-md"},
            html.div(
                {"class_name": "border-b border-light-outline-variant pb-gutter-sm"},
                html.h3({"class_name": "font-headline text-title-lg uppercase"}, "Personal & Institutional Details"),
                html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Keep your contact information and target CGPA up to date.")
            ),

            html.form(
                {"class_name": "flex flex-col gap-gutter-md", "on_submit": lambda e: None},
                html.div(
                    {"class_name": "grid grid-cols-1 sm:grid-cols-2 gap-gutter-md"},
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "First Name"),
                        html.input(
                            {
                                "type": "text",
                                "value": first_name,
                                "on_change": lambda e: set_first_name(e.get("target", {}).get("value", "")),
                                "class_name": "border border-light-outline-variant p-2 font-body text-body-md"
                            }
                        )
                    ),
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Last Name"),
                        html.input(
                            {
                                "type": "text",
                                "value": last_name,
                                "on_change": lambda e: set_last_name(e.get("target", {}).get("value", "")),
                                "class_name": "border border-light-outline-variant p-2 font-body text-body-md"
                            }
                        )
                    )
                ),
                html.div(
                    {"class_name": "grid grid-cols-1 sm:grid-cols-2 gap-gutter-md"},
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Email Address"),
                        html.input(
                            {
                                "type": "email",
                                "value": email,
                                "on_change": lambda e: set_email(e.get("target", {}).get("value", "")),
                                "class_name": "border border-light-outline-variant p-2 font-body text-body-md"
                            }
                        )
                    ),
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Target CGPA"),
                        html.input(
                            {
                                "type": "number",
                                "step": "0.01",
                                "min": "0",
                                "max": "10",
                                "value": target_cgpa,
                                "on_change": lambda e: set_target_cgpa(e.get("target", {}).get("value", "8.80")),
                                "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                            }
                        )
                    )
                ),

                html.div(
                    {"class_name": f"{'block' if save_status else 'hidden'} p-2 bg-success text-on-success font-mono text-mono-sm"},
                    save_status
                ),
                html.div(
                    {"class_name": f"{'block' if save_error else 'hidden'} p-2 bg-light-error text-light-on-error font-mono text-mono-sm"},
                    save_error
                ),

                html.button(
                    {
                        "type": "button",
                        "on_click": handle_save_profile,
                        "class_name": "self-start px-gutter-lg py-2.5 bg-light-secondary text-light-on-secondary font-headline font-bold text-label-md hover:bg-light-primary hover:text-light-on-primary transition-colors duration-state-change uppercase cursor-pointer"
                    },
                    "Save Profile"
                )
            )
        ),

        # Password Change Card (Mandatory Requirement)
        html.section(
            {"class_name": "border border-light-outline-variant bg-light-surface p-gutter-lg flex flex-col gap-gutter-md"},
            html.div(
                {"class_name": "border-b border-light-outline-variant pb-gutter-sm"},
                html.h3({"class_name": "font-headline text-title-lg uppercase"}, "Change Institutional Password"),
                html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Update your institutional account password with security validation.")
            ),

            html.form(
                {"class_name": "flex flex-col gap-gutter-md max-w-lg", "on_submit": lambda e: None},
                html.div(
                    {"class_name": "flex flex-col gap-1"},
                    html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Current Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": old_password,
                            "on_change": lambda e: set_old_password(e.get("target", {}).get("value", "")),
                            "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md",
                            "placeholder": "••••••••"
                        }
                    )
                ),
                html.div(
                    {"class_name": "flex flex-col gap-1"},
                    html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "New Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": new_password,
                            "on_change": lambda e: set_new_password(e.get("target", {}).get("value", "")),
                            "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md",
                            "placeholder": "Minimum 8 characters"
                        }
                    )
                ),
                html.div(
                    {"class_name": "flex flex-col gap-1"},
                    html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Confirm New Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": confirm_password,
                            "on_change": lambda e: set_confirm_password(e.get("target", {}).get("value", "")),
                            "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md",
                            "placeholder": "Re-enter new password"
                        }
                    )
                ),

                html.div(
                    {"class_name": f"{'block' if pw_status else 'hidden'} p-2 bg-success text-on-success font-mono text-mono-sm"},
                    pw_status
                ),
                html.div(
                    {"class_name": f"{'block' if pw_error else 'hidden'} p-2 bg-light-error text-light-on-error font-mono text-mono-sm"},
                    pw_error
                ),

                html.button(
                    {
                        "type": "button",
                        "on_click": handle_change_password,
                        "class_name": "self-start px-gutter-lg py-2.5 bg-light-primary text-light-on-primary font-headline font-bold text-label-md hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change uppercase cursor-pointer"
                    },
                    "Update Password"
                )
            )
        )
    )
