"""
Student & Faculty Profile Page Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import (
    icon_user, icon_award, icon_book_open, icon_shield_check,
    icon_check, icon_alert, icon_layers, icon_briefcase
)
from ui.services.data_service import update_user_profile, change_user_password

@component
def ProfilePage(user):
    profile = getattr(user, 'profile', None)
    is_admin = profile.is_admin() if profile else False

    # State for editable fields
    first_name, set_first_name = use_state(user.first_name if user else "")
    last_name, set_last_name = use_state(user.last_name if user else "")
    email, set_email = use_state(user.email if user else "")
    target_cgpa, set_target_cgpa = use_state(str(profile.target_cgpa) if profile else "9.00")
    department, set_department = use_state(profile.department if profile else "Computer Science & Engineering")

    save_status, set_save_status = use_state("")
    save_error, set_save_error = use_state("")

    # State for Change Password
    old_password, set_old_password = use_state("")
    new_password, set_new_password = use_state("")
    confirm_password, set_confirm_password = use_state("")
    pw_status, set_pw_status = use_state("")
    pw_error, set_pw_error = use_state("")
    pw_loading, set_pw_loading = use_state(False)

    # Metrics
    cgpa = float(profile.current_cgpa) if profile else 0.0
    credits_earned = int(profile.credits_earned) if profile else 0
    total_credits = int(profile.total_credits) if profile else 160
    credits_pct = min(100, int((credits_earned / total_credits * 100))) if total_credits > 0 else 0
    backlogs = int(profile.backlogs_count) if profile else 0
    is_eligible = profile.is_placement_eligible if profile else True

    # Academic semester and year
    curr_sem = profile.current_semester if profile and profile.current_semester else 5
    curr_year = ((curr_sem + 1) // 2)

    # Classification
    if cgpa >= 8.50:
        standing_label = "First Class with Distinction"
    elif cgpa >= 6.50:
        standing_label = "First Class"
    elif cgpa >= 5.00:
        standing_label = "Second Class"
    else:
        standing_label = "Under Evaluation"

    initials = f"{user.first_name[:1] if user and user.first_name else ''}{user.last_name[:1] if user and user.last_name else ''}".upper() or user.username[:2].upper()

    def handle_save(e=None):
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

    def handle_password_change(e=None):
        set_pw_status("")
        set_pw_error("")
        set_pw_loading(True)
        try:
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
        finally:
            set_pw_loading(False)

    return html.div(
        # Page Title Banner
        html.div(
            {"style": {"marginBottom": "2.25rem"}},
            html.h1(
                {
                    "style": {
                        "fontFamily": "var(--font-serif)",
                        "fontSize": "2.25rem",
                        "fontWeight": "400",
                        "color": "var(--brand-navy)",
                        "lineHeight": "1.2"
                    }
                },
                "Academic Profile & Institutional Identity"
            ),
            html.p(
                {"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}},
                "Verified student credentials, CBCS curriculum progress, academic standing, and goal configuration."
            )
        ),
        # Main Grid Layout
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(340px, 1fr))", "gap": "2rem"}},
            # Left Column: Identity & Academic Overview
            html.div(
                {"style": {"display": "flex", "flexDirection": "column", "gap": "1.75rem"}},
                # Identity Card
                html.div(
                    {"className": "card"},
                    html.div(
                        {"style": {"display": "flex", "alignItems": "center", "gap": "1.25rem", "marginBottom": "1.5rem"}},
                        html.div(
                            {
                                "style": {
                                    "width": "64px",
                                    "height": "64px",
                                    "borderRadius": "var(--radius-md)",
                                    "background": "linear-gradient(135deg, var(--brand-navy), #1E293B)",
                                    "color": "#FFFFFF",
                                    "fontFamily": "var(--font-display)",
                                    "fontSize": "1.75rem",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "boxShadow": "0 4px 14px rgba(10, 25, 47, 0.25)"
                                }
                            },
                            initials
                        ),
                        html.div(
                            html.h2(
                                {"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.5rem", "color": "var(--brand-navy)", "marginBottom": "0.2rem"}},
                                f"{user.first_name} {user.last_name}".strip() or user.username
                            ),
                            html.div(
                                {"style": {"display": "flex", "gap": "0.5rem", "alignItems": "center"}},
                                html.span(
                                    {"className": "badge badge-vermillion" if is_admin else "badge badge-success"},
                                    "Faculty / Staff" if is_admin else "Registered Student"
                                ),
                                html.span(
                                    {"style": {"fontSize": "0.8rem", "color": "var(--text-muted)", "fontWeight": "600"}},
                                    f"Roll: {profile.roll_number}" if profile and profile.roll_number else f"ID: #{user.id}"
                                )
                            )
                        )
                    ),
                    html.div(
                        {"style": {"display": "flex", "flexDirection": "column", "gap": "0.85rem", "borderTop": "1px solid var(--border-subtle)", "paddingTop": "1.25rem"}},
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "Department"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, profile.department if profile else "Computer Science")
                        ),
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "Current Semester"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, f"Semester {curr_sem} (Year {curr_year})")
                        ),
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "Degree Program"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, "B.E. (Autonomous CBCS 2026)")
                        ),
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "Academic Classification"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-vermillion)"}}, standing_label)
                        )
                    )
                ),
                # Credit Progress Card
                html.div(
                    {"className": "card"},
                    html.div(
                        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem"}},
                        html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.25rem", "color": "var(--brand-navy)"}}, "Degree Credit Completion"),
                        html.span({"style": {"fontFamily": "var(--font-display)", "fontSize": "1.5rem", "color": "var(--brand-navy)"}}, f"{credits_pct}%")
                    ),
                    html.div(
                        {"style": {"width": "100%", "height": "10px", "backgroundColor": "var(--border-subtle)", "borderRadius": "var(--radius-full)", "overflow": "hidden", "marginBottom": "0.75rem"}},
                        html.div(
                            {
                                "style": {
                                    "width": f"{credits_pct}%",
                                    "height": "100%",
                                    "background": "linear-gradient(90deg, var(--brand-navy), var(--brand-vermillion))",
                                    "borderRadius": "var(--radius-full)"
                                }
                            }
                        )
                    ),
                    html.div(
                        {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.8rem", "color": "var(--text-muted)"}},
                        html.span(f"Completed: {credits_earned} credits"),
                        html.span(f"Degree Requirement: {total_credits} credits")
                    )
                )
            ),
            # Right Column: Academic Metrics & Settings Form
            html.div(
                {"style": {"display": "flex", "flexDirection": "column", "gap": "1.75rem"}},
                # 3 KPI Stat Tiles
                html.div(
                    {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))", "gap": "1rem"}},
                    # CGPA Tile
                    html.div(
                        {"className": "card", "style": {"textAlign": "center", "padding": "1.25rem 1rem"}},
                        html.div({"style": {"fontSize": "0.75rem", "textTransform": "uppercase", "color": "var(--text-muted)", "fontWeight": "700"}}, "Current CGPA"),
                        html.div({"style": {"fontFamily": "var(--font-display)", "fontSize": "2.25rem", "color": "var(--brand-vermillion)", "margin": "0.25rem 0"}}, f"{cgpa:.2f}"),
                        html.span({"className": "badge badge-success"}, "10.0 Scale")
                    ),
                    # Backlogs Tile
                    html.div(
                        {"className": "card", "style": {"textAlign": "center", "padding": "1.25rem 1rem"}},
                        html.div({"style": {"fontSize": "0.75rem", "textTransform": "uppercase", "color": "var(--text-muted)", "fontWeight": "700"}}, "Standing Arrears"),
                        html.div({"style": {"fontFamily": "var(--font-display)", "fontSize": "2.25rem", "color": "var(--brand-navy)" if backlogs == 0 else "var(--danger)", "margin": "0.25rem 0"}}, str(backlogs)),
                        html.span(
                            {"className": "badge badge-success" if backlogs == 0 else "badge badge-warning"},
                            "Clean Record" if backlogs == 0 else f"{backlogs} Backlog"
                        )
                    ),
                    # Placement Readiness
                    html.div(
                        {"className": "card", "style": {"textAlign": "center", "padding": "1.25rem 1rem"}},
                        html.div({"style": {"fontSize": "0.75rem", "textTransform": "uppercase", "color": "var(--text-muted)", "fontWeight": "700"}}, "Campus Placement"),
                        html.div({"style": {"fontFamily": "var(--font-display)", "fontSize": "1.35rem", "color": "#059669" if is_eligible else "var(--danger)", "margin": "0.6rem 0"}}, "Eligible" if is_eligible else "Audit Req."),
                        html.span({"className": "badge badge-success" if is_eligible else "badge badge-danger"}, "Tier-1 Ready" if is_eligible else "Review Arrears")
                    )
                ),
                # Profile Configuration Form Card
                html.div(
                    {"className": "card"},
                    html.div(
                        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                        html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Edit Profile & Academic Goals"),
                        html.span({"className": "badge badge-vermillion"}, "Live Sync")
                    ),
                    html.div(
                        {"style": {"display": "flex", "flexDirection": "column", "gap": "1rem"}},
                        # Name Grid
                        html.div(
                            {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem"}},
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "First Name"),
                                html.input({
                                    "type": "text",
                                    "className": "input",
                                    "value": str(first_name),
                                    "on_change": lambda e: set_first_name(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                                })
                            ),
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Last Name"),
                                html.input({
                                    "type": "text",
                                    "className": "input",
                                    "value": str(last_name),
                                    "on_change": lambda e: set_last_name(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                                })
                            )
                        ),
                        # Email & Department
                        html.div(
                            {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem"}},
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Institutional Email"),
                                html.input({
                                    "type": "email",
                                    "className": "input",
                                    "value": str(email),
                                    "on_change": lambda e: set_email(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                                })
                            ),
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Target Graduation CGPA"),
                                html.input({
                                    "type": "number",
                                    "step": "0.05",
                                    "min": "5.00",
                                    "max": "10.00",
                                    "className": "input",
                                    "value": str(target_cgpa),
                                    "on_change": lambda e: set_target_cgpa(e.get("target", {}).get("value", "9.00") if isinstance(e, dict) else str(e))
                                })
                            )
                        ),
                        # Department
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Department"),
                            html.input({
                                "type": "text",
                                "className": "input",
                                "value": str(department),
                                "on_change": lambda e: set_department(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            })
                        ),
                        # Feedback message
                        html.div(
                            {"style": {"color": "#059669", "fontSize": "0.85rem", "fontWeight": "700", "display": "block" if save_status else "none"}},
                            f"✓ {save_status}"
                        ),
                        html.div(
                            {"style": {"color": "var(--danger)", "fontSize": "0.85rem", "fontWeight": "700", "display": "block" if save_error else "none"}},
                            f"⚠ {save_error}"
                        ),
                        # Submit Button
                        html.button(
                            {
                                "className": "btn btn-primary",
                                "style": {"width": "100%", "marginTop": "0.5rem"},
                                "on_click": handle_save
                            },
                            "Save Profile Changes"
                        )
                    )
                ),
                # Change Password Section
                html.div(
                    {"className": "card", "style": {"marginTop": "1.75rem"}},
                    html.div(
                        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                        html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Security & Change Password"),
                        html.span({"className": "badge badge-cyan"}, "Encrypted")
                    ),
                    html.div(
                        {"style": {"display": "flex", "flexDirection": "column", "gap": "1rem"}},
                        # Current Password
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Current Password"),
                            html.input({
                                "type": "password",
                                "className": "input",
                                "placeholder": "Enter your current password",
                                "value": str(old_password),
                                "on_change": lambda e: set_old_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                            })
                        ),
                        # New and Confirm Password
                        html.div(
                            {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem"}},
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "New Password"),
                                html.input({
                                    "type": "password",
                                    "className": "input",
                                    "placeholder": "Min. 8 characters",
                                    "value": str(new_password),
                                    "on_change": lambda e: set_new_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                                })
                            ),
                            html.div(
                                html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Confirm New Password"),
                                html.input({
                                    "type": "password",
                                    "className": "input",
                                    "placeholder": "Re-enter new password",
                                    "value": str(confirm_password),
                                    "on_change": lambda e: set_confirm_password(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                                })
                            )
                        ),
                        # Feedback messages
                        html.div(
                            {"style": {"color": "#059669", "fontSize": "0.85rem", "fontWeight": "700", "display": "block" if pw_status else "none"}},
                            f"✓ {pw_status}"
                        ),
                        html.div(
                            {"style": {"color": "var(--danger)", "fontSize": "0.85rem", "fontWeight": "700", "display": "block" if pw_error else "none"}},
                            f"⚠ {pw_error}"
                        ),
                        # Submit Button
                        html.button(
                            {
                                "className": "btn btn-secondary",
                                "style": {"width": "100%", "marginTop": "0.5rem"},
                                "disabled": pw_loading,
                                "on_click": handle_password_change
                            },
                            "Updating Password..." if pw_loading else "Update Password"
                        )
                    )
                )
            )
        )
    )
