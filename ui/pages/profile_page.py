"""
Student & Faculty Profile Page Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Fully responsive, accessible, with high-contrast text and interactive profile editing.
"""

from reactpy import component, html, use_state
from ui.services.data_service import update_user_profile, change_user_password


@component
def ProfilePage(user):
    profile = getattr(user, 'profile', None)
    is_admin = profile.is_admin() if profile else False

    # State for edit mode toggle
    is_editing, set_is_editing = use_state(False)

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
    is_placement_ok = getattr(profile, 'is_placement_eligible', True) if profile else True

    initials = f"{user.first_name[:1] if user and user.first_name else ''}{user.last_name[:1] if user and user.last_name else ''}".upper() or (user.username[:2].upper() if user else "EG")

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
            set_is_editing(False)
        else:
            set_save_error(msg)

    def handle_cancel_edit(e=None):
        set_first_name(user.first_name if user else "")
        set_last_name(user.last_name if user else "")
        set_email(user.email if user else "")
        set_target_cgpa(str(profile.target_cgpa) if profile else "8.80")
        set_department(profile.department if profile else "Computer Science & Engineering")
        set_save_error("")
        set_is_editing(False)

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

    input_style = {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"}
    input_class = "w-full bg-light-surface border-2 border-light-outline-variant focus:border-light-primary focus:ring-0 p-2.5 font-mono text-mono-md text-light-on-surface outline-none transition-colors"

    return html.div(
        {"className": "flex-1 p-gutter-lg max-w-[1200px] w-full mx-auto flex flex-col gap-section overflow-y-auto text-light-on-surface"},
        
        # 1. Header with Edit Button & Badges
        html.header(
            {"className": "pb-gutter-md border-b border-light-outline-variant flex flex-wrap items-center justify-between gap-gutter-md"},
            html.div(
                html.h1({"className": "font-headline text-headline-md tracking-tight uppercase text-light-on-surface font-bold"}, "Institutional Profile & Credentials"),
                html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase mt-1"}, f"Identity • {profile.role.upper() if profile else 'STUDENT'} Standing • Security")
            ),
            html.div(
                {"className": "flex items-center gap-3 flex-wrap"},
                html.span({"className": "font-mono text-mono-sm font-bold bg-light-surface-container-highest text-light-on-surface px-3 py-1.5 border border-light-outline-variant"}, "2021 CBCS REGULATION"),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: (handle_cancel_edit() if is_editing else (set_is_editing(True), set_save_status(""), set_save_error(""))),
                        "className": (
                            "inline-flex items-center gap-2 px-4 py-2 border-2 border-light-outline-variant text-light-on-surface hover:bg-light-surface-container-high font-headline font-bold text-label-md uppercase transition-colors cursor-pointer"
                            if is_editing else
                            "inline-flex items-center gap-2 px-4 py-2 bg-light-primary text-white hover:bg-light-primary-container font-headline font-bold text-label-md uppercase transition-colors cursor-pointer shadow-sm"
                        )
                    },
                    html.span({"className": "material-symbols-outlined text-[18px]"}, "close" if is_editing else "edit"),
                    html.span("Cancel Edit" if is_editing else "Edit Profile")
                )
            )
        ),

        # 2. Bento Grid: Identity Card & Academic Standing
        html.div(
            {"className": "grid grid-cols-1 md:grid-cols-3 gap-gutter-lg"},
            
            # Identity Box
            html.div(
                {"className": "md:col-span-1 border-2 border-light-secondary p-gutter-lg bg-light-surface-container-lowest text-light-on-surface flex flex-col gap-gutter-md items-center text-center shadow-sm"},
                html.div(
                    {"className": "w-24 h-24 bg-light-secondary text-light-on-secondary flex items-center justify-center font-headline text-display-lg font-bold border border-light-outline-variant"},
                    initials
                ),
                html.div(
                    {"className": "flex flex-col items-center gap-1"},
                    html.h2({"className": "font-headline text-headline-md text-light-on-surface uppercase font-bold"}, f"{first_name} {last_name}".strip() or (user.username if user else "STUDENT")),
                    html.p({"className": "font-mono text-mono-sm text-light-primary font-bold tracking-wider"}, getattr(profile, 'roll_number', user.username if user else "2026")),
                    html.span({"className": "mt-2 inline-block px-3 py-1 bg-light-surface-container-highest text-light-on-surface font-mono text-mono-sm font-semibold border border-light-outline-variant"}, f"{department} • {profile.role.upper() if profile else 'STUDENT'}"),
                    html.span(
                        {"className": "mt-2 inline-flex items-center gap-1.5 font-mono text-mono-xs uppercase text-success font-semibold"},
                        html.span({"className": "material-symbols-outlined text-[15px]"}, "verified"),
                        "Institutional Account Verified"
                    )
                ),
                (
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: (set_is_editing(True), set_save_status(""), set_save_error("")),
                            "className": "mt-1 inline-flex items-center gap-1 font-mono text-mono-sm text-light-primary hover:underline font-bold uppercase cursor-pointer"
                        },
                        html.span({"className": "material-symbols-outlined text-[16px]"}, "edit"),
                        "Edit Profile Info"
                    )
                    if not is_editing else None
                )
            ),

            # Academic Standing
            html.div(
                {"className": "md:col-span-2 border border-light-outline-variant bg-light-surface-container-lowest text-light-on-surface p-gutter-lg flex flex-col justify-between gap-gutter-md shadow-sm"},
                html.div(
                    {"className": "flex items-center justify-between border-b border-light-outline-variant pb-2"},
                    html.h3({"className": "font-headline text-title-lg text-light-on-surface uppercase font-bold"}, "Academic Standing & Metrics"),
                    html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "analytics")
                ),
                html.div(
                    {"className": "grid grid-cols-2 sm:grid-cols-4 gap-gutter-md"},
                    html.div(
                        {"className": "p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        html.span({"className": "font-mono text-mono-xs text-light-on-surface-variant uppercase font-bold block"}, "CURRENT CGPA"),
                        html.p({"className": "font-headline text-headline-lg text-light-primary font-bold tabular-nums mt-1"}, f"{cgpa:.2f}")
                    ),
                    html.div(
                        {"className": "p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        html.span({"className": "font-mono text-mono-xs text-light-on-surface-variant uppercase font-bold block"}, "TARGET CGPA"),
                        html.p({"className": "font-headline text-headline-lg text-light-on-surface font-bold tabular-nums mt-1"}, f"{float(target_cgpa):.2f}" if target_cgpa else "8.80")
                    ),
                    html.div(
                        {"className": "p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        html.span({"className": "font-mono text-mono-xs text-light-on-surface-variant uppercase font-bold block"}, "CREDITS"),
                        html.p({"className": "font-headline text-headline-lg text-light-on-surface font-bold tabular-nums mt-1"}, f"{credits_earned} / {total_credits}")
                    ),
                    html.div(
                        {"className": "p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        html.span({"className": "font-mono text-mono-xs text-light-on-surface-variant uppercase font-bold block"}, "ACTIVE ARREARS"),
                        html.p({"className": f"font-headline text-headline-lg font-bold tabular-nums mt-1 {'text-light-primary' if backlogs > 0 else 'text-success'}"}, f"{backlogs} Active")
                    )
                ),
                html.div(
                    {"className": "pt-2 border-t border-light-outline-variant/60 flex flex-wrap items-center justify-between text-mono-xs font-mono text-light-on-surface-variant uppercase"},
                    html.span(f"Current Standing: Semester {curr_sem} • Regulation CBCS 2021"),
                    html.span({"className": "text-success font-bold" if is_placement_ok else "text-warning font-bold"}, "● " + ("Placement Eligible" if is_placement_ok else "Remediation Needed"))
                )
            )
        ),

        # 3. Personal & Institutional Details Section (View Mode vs Edit Mode)
        html.section(
            {"className": "border border-light-outline-variant bg-light-surface-container-lowest text-light-on-surface p-gutter-lg flex flex-col gap-gutter-md shadow-sm"},
            html.div(
                {"className": "flex flex-wrap items-center justify-between gap-4 border-b border-light-outline-variant pb-gutter-sm"},
                html.div(
                    html.h3({"className": "font-headline text-title-lg text-light-on-surface uppercase font-bold flex items-center gap-2"}, html.span({"className": "material-symbols-outlined text-light-primary text-[20px]"}, "badge"), html.span("Personal & Institutional Details")),
                    html.p({"className": "font-body text-body-sm text-light-on-surface-variant mt-0.5"}, "Keep your contact information, department, and target CGPA up to date.")
                ),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: (handle_cancel_edit() if is_editing else (set_is_editing(True), set_save_status(""), set_save_error(""))),
                        "className": (
                            "inline-flex items-center gap-2 px-4 py-2 border-2 border-light-outline-variant text-light-on-surface hover:bg-light-surface-container font-headline font-bold text-label-md uppercase transition-colors cursor-pointer"
                            if is_editing else
                            "inline-flex items-center gap-2 px-4 py-2 bg-light-secondary text-light-on-secondary hover:bg-light-primary hover:text-white font-headline font-bold text-label-md uppercase transition-colors cursor-pointer"
                        )
                    },
                    html.span({"className": "material-symbols-outlined text-[18px]"}, "close" if is_editing else "edit"),
                    html.span("Cancel Edit" if is_editing else "Edit Details")
                )
            ),

            # Status and Error Banners
            html.div(
                {"className": f"{'flex items-center gap-2' if save_status else 'hidden'} p-3 bg-success/15 border border-success text-success font-mono text-mono-sm font-semibold"},
                html.span({"className": "material-symbols-outlined text-[18px]"}, "check_circle"),
                save_status
            ),
            html.div(
                {"className": f"{'flex items-center gap-2' if save_error else 'hidden'} p-3 bg-light-error/15 border border-light-error text-light-error font-mono text-mono-sm font-semibold"},
                html.span({"className": "material-symbols-outlined text-[18px]"}, "error"),
                save_error
            ),

            # If NOT editing: Read-only display cards
            (
                html.div(
                    {"className": "flex flex-col gap-6"},
                    html.div(
                        {"className": "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6"},
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "First Name"),
                            html.p({"className": "font-body text-body-md font-semibold text-light-on-surface"}, first_name or "—")
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "Last Name"),
                            html.p({"className": "font-body text-body-md font-semibold text-light-on-surface"}, last_name or "—")
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "Email Address"),
                            html.p({"className": "font-mono text-mono-sm font-medium text-light-on-surface truncate"}, email or "—")
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "Department"),
                            html.p({"className": "font-body text-body-md font-semibold text-light-on-surface"}, department or "Computer Science & Engineering")
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "Roll Number / ID"),
                            html.p({"className": "font-mono text-mono-md font-bold text-light-primary"}, getattr(profile, 'roll_number', user.username if user else "—"))
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.span({"className": "font-mono text-mono-xs font-bold text-light-on-surface-variant uppercase"}, "Target CGPA"),
                            html.p({"className": "font-mono text-mono-md font-bold text-light-on-surface"}, f"{float(target_cgpa):.2f}" if target_cgpa else "8.80")
                        )
                    ),
                    html.div(
                        {"className": "pt-2 flex items-center gap-3"},
                        html.button(
                            {
                                "type": "button",
                                "on_click": lambda e: (set_is_editing(True), set_save_status(""), set_save_error("")),
                                "className": "inline-flex items-center gap-2 px-6 py-2.5 bg-light-primary text-white hover:bg-light-primary-container font-headline font-bold text-label-md uppercase transition-colors cursor-pointer shadow-sm"
                            },
                            html.span({"className": "material-symbols-outlined text-[18px]"}, "edit"),
                            "Edit Profile Details"
                        )
                    )
                )
                if not is_editing else
                # If editing: Active Form with high-contrast inputs
                html.form(
                    {"className": "flex flex-col gap-gutter-md", "on_submit": lambda e: None},
                    html.div(
                        {"className": "grid grid-cols-1 sm:grid-cols-2 gap-gutter-md"},
                        html.div(
                            {"className": "flex flex-col gap-1"},
                            html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "First Name"),
                            html.input(
                                {
                                    "type": "text",
                                    "value": first_name,
                                    "on_change": lambda e: set_first_name(e.get("target", {}).get("value", "")),
                                    "className": input_class,
                                    "style": input_style,
                                    "placeholder": "Enter first name"
                                }
                            )
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1"},
                            html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Last Name"),
                            html.input(
                                {
                                    "type": "text",
                                    "value": last_name,
                                    "on_change": lambda e: set_last_name(e.get("target", {}).get("value", "")),
                                    "className": input_class,
                                    "style": input_style,
                                    "placeholder": "Enter last name"
                                }
                            )
                        )
                    ),
                    html.div(
                        {"className": "grid grid-cols-1 sm:grid-cols-2 gap-gutter-md"},
                        html.div(
                            {"className": "flex flex-col gap-1"},
                            html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Email Address"),
                            html.input(
                                {
                                    "type": "email",
                                    "value": email,
                                    "on_change": lambda e: set_email(e.get("target", {}).get("value", "")),
                                    "className": input_class,
                                    "style": input_style,
                                    "placeholder": "student@institution.edu"
                                }
                            )
                        ),
                        html.div(
                            {"className": "flex flex-col gap-1"},
                            html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Target CGPA (0.00 – 10.00)"),
                            html.input(
                                {
                                    "type": "number",
                                    "step": "0.01",
                                    "min": "0",
                                    "max": "10",
                                    "value": target_cgpa,
                                    "on_change": lambda e: set_target_cgpa(e.get("target", {}).get("value", "8.80")),
                                    "className": input_class,
                                    "style": input_style,
                                    "placeholder": "8.80"
                                }
                            )
                        )
                    ),
                    html.div(
                        {"className": "flex flex-col gap-1"},
                        html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Academic Department"),
                        html.input(
                            {
                                "type": "text",
                                "value": department,
                                "on_change": lambda e: set_department(e.get("target", {}).get("value", "")),
                                "className": input_class,
                                "style": input_style,
                                "placeholder": "e.g. Computer Science & Engineering"
                            }
                        )
                    ),

                    html.div(
                        {"className": "flex items-center gap-3 pt-2 flex-wrap"},
                        html.button(
                            {
                                "type": "button",
                                "on_click": handle_save_profile,
                                "className": "inline-flex items-center gap-2 px-gutter-lg py-2.5 bg-light-primary text-white font-headline font-bold text-label-md hover:bg-light-primary-container transition-colors uppercase cursor-pointer shadow-sm"
                            },
                            html.span({"className": "material-symbols-outlined text-[18px]"}, "save"),
                            "SAVE PROFILE DETAILS"
                        ),
                        html.button(
                            {
                                "type": "button",
                                "on_click": handle_cancel_edit,
                                "className": "inline-flex items-center gap-2 px-gutter-lg py-2.5 border-2 border-light-outline-variant text-light-on-surface hover:bg-light-surface-container font-headline font-bold text-label-md uppercase transition-colors cursor-pointer"
                            },
                            html.span({"className": "material-symbols-outlined text-[18px]"}, "close"),
                            "CANCEL"
                        )
                    )
                )
            )
        ),

        # 4. Password Change Card
        html.section(
            {"className": "border border-light-outline-variant bg-light-surface-container-lowest text-light-on-surface p-gutter-lg flex flex-col gap-gutter-md shadow-sm"},
            html.div(
                {"className": "border-b border-light-outline-variant pb-gutter-sm"},
                html.h3({"className": "font-headline text-title-lg text-light-on-surface uppercase font-bold flex items-center gap-2"}, html.span({"className": "material-symbols-outlined text-light-primary text-[20px]"}, "lock"), html.span("Change Institutional Password")),
                html.p({"className": "font-body text-body-sm text-light-on-surface-variant mt-0.5"}, "Update your institutional account password with security validation.")
            ),

            # Password status / error banners
            html.div(
                {"className": f"{'flex items-center gap-2' if pw_status else 'hidden'} p-3 bg-success/15 border border-success text-success font-mono text-mono-sm font-semibold"},
                html.span({"className": "material-symbols-outlined text-[18px]"}, "check_circle"),
                pw_status
            ),
            html.div(
                {"className": f"{'flex items-center gap-2' if pw_error else 'hidden'} p-3 bg-light-error/15 border border-light-error text-light-error font-mono text-mono-sm font-semibold"},
                html.span({"className": "material-symbols-outlined text-[18px]"}, "error"),
                pw_error
            ),

            html.form(
                {"className": "flex flex-col gap-gutter-md max-w-lg", "on_submit": lambda e: None},
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Current Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": old_password,
                            "on_change": lambda e: set_old_password(e.get("target", {}).get("value", "")),
                            "className": input_class,
                            "style": input_style,
                            "placeholder": "••••••••"
                        }
                    )
                ),
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "New Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": new_password,
                            "on_change": lambda e: set_new_password(e.get("target", {}).get("value", "")),
                            "className": input_class,
                            "style": input_style,
                            "placeholder": "Minimum 8 characters"
                        }
                    )
                ),
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label({"className": "font-mono text-mono-sm font-bold text-light-on-surface uppercase"}, "Confirm New Password"),
                    html.input(
                        {
                            "type": "password",
                            "value": confirm_password,
                            "on_change": lambda e: set_confirm_password(e.get("target", {}).get("value", "")),
                            "className": input_class,
                            "style": input_style,
                            "placeholder": "Re-enter new password"
                        }
                    )
                ),

                html.button(
                    {
                        "type": "button",
                        "on_click": handle_change_password,
                        "className": "self-start inline-flex items-center gap-2 px-gutter-lg py-2.5 bg-light-secondary text-light-on-secondary hover:bg-light-primary hover:text-white font-headline font-bold text-label-md uppercase transition-colors duration-state-change cursor-pointer shadow-sm"
                    },
                    html.span({"className": "material-symbols-outlined text-[18px]"}, "lock_reset"),
                    "UPDATE PASSWORD"
                )
            )
        )
    )
