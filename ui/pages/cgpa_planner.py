"""
Target CGPA Simulator & Planner Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import icon_sparkles, icon_check, icon_alert
from core.services.academic_service import plan_target_cgpa

def _to_float(val, fallback=0.0):
    if isinstance(val, dict):
        val = val.get("target", {}).get("value", fallback)
    try:
        s = str(val).strip()
        return float(s) if s else fallback
    except (ValueError, TypeError):
        return fallback

def _to_int(val, fallback=1):
    if isinstance(val, dict):
        val = val.get("target", {}).get("value", fallback)
    try:
        s = str(val).strip()
        return int(float(s)) if s else fallback
    except (ValueError, TypeError):
        return fallback

@component
def CgpaPlanner(user):
    profile = getattr(user, 'profile', None)
    initial_cgpa = float(profile.current_cgpa) if profile else 0.0
    initial_credits = int(profile.credits_earned) if profile else 0
    initial_target = float(profile.target_cgpa) if profile and profile.target_cgpa else 8.50
    initial_total_cr = int(profile.total_credits) if profile and profile.total_credits else 160
    initial_rem_sems = max(1, 8 - (profile.current_semester if profile and profile.current_semester else 1))

    current_cgpa, set_current_cgpa = use_state(initial_cgpa)
    completed_credits, set_completed_credits = use_state(initial_credits)
    target_cgpa, set_target_cgpa = use_state(initial_target)
    remaining_semesters, set_remaining_semesters = use_state(initial_rem_sems)
    total_credits, set_total_credits = use_state(initial_total_cr)

    # Compute plan using safe numeric values
    plan = plan_target_cgpa(
        current_cgpa=_to_float(current_cgpa, 0.0),
        completed_credits=_to_float(completed_credits, 0.0),
        target_cgpa=_to_float(target_cgpa, 0.0),
        remaining_semesters=_to_int(remaining_semesters, 1),
        degree_total_credits=_to_float(total_credits, 160.0)
    )

    status = plan.get("status", "feasible")
    is_achievable = plan.get("is_achievable", False)
    req_sgpa = plan.get("required_average_sgpa")
    message = plan.get("message", "")

    # Determine badge style & label
    if status == "already_achieved":
        badge_class = "badge badge-success"
        badge_icon = icon_check(13)
        badge_text = " Target Already Achieved"
    elif status == "easily_achievable":
        badge_class = "badge badge-success"
        badge_icon = icon_check(13)
        badge_text = " Easily Achievable"
    elif status == "feasible":
        badge_class = "badge badge-success"
        badge_icon = icon_check(13)
        badge_text = " Mathematically Feasible"
    elif status == "impossible":
        badge_class = "badge badge-danger"
        badge_icon = icon_alert(13)
        badge_text = " Mathematically Impossible"
    else:
        badge_class = "badge badge-danger"
        badge_icon = icon_alert(13)
        badge_text = " Invalid Parameters"

    # Big display value for required SGPA
    if req_sgpa is not None:
        display_sgpa = f"{req_sgpa:.2f}"
    elif status == "already_achieved":
        display_sgpa = "Target Met"
    elif status == "impossible":
        display_sgpa = "N/A"
    else:
        display_sgpa = "—"

    # Color coding for SGPA display
    if not is_achievable:
        sgpa_color = "var(--danger)"
    elif status == "already_achieved":
        sgpa_color = "#059669"
    else:
        sgpa_color = "var(--brand-vermillion)"

    scenario_rows = []
    for sc in plan.get("scenarios", []):
        meets = sc.get("meets_target", False)
        scenario_rows.append(
            html.tr(
                {"key": str(sc.get("future_average_sgpa", 0.0))},
                html.td({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, f"{sc.get('future_average_sgpa', 0.0):.2f}"),
                html.td({"style": {"fontWeight": "800", "color": "var(--brand-vermillion)" if meets else "var(--text-secondary)"}}, f"{sc.get('projected_final_cgpa', 0.0):.2f}"),
                html.td(html.span({"className": "badge badge-success" if meets else "badge badge-warning"}, "✓ Target Met" if meets else "Below Target"))
            )
        )

    return html.div(
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
                "Target CGPA Simulator & What-If Planner"
            ),
            html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, "Credit-weighted predictive milestone modeling. Determine the exact SGPA required across your remaining CBCS semesters.")
        ),
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(340px, 1fr))", "gap": "2rem"}},
            # Controls Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Goal Parameters"),
                    html.span({"className": "badge badge-vermillion"}, "Interactive Simulator")
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "1.5rem"}},
                    # Zero Credits Info Banner
                    html.div(
                        {
                            "style": {
                                "padding": "0.75rem 1rem",
                                "backgroundColor": "var(--bg-surface-elevated)",
                                "borderRadius": "var(--radius-sm)",
                                "border": "1px solid var(--border-subtle)",
                                "fontSize": "0.85rem",
                                "color": "var(--text-secondary)"
                            }
                        },
                        "ℹ️ You have 0 completed credits logged. Simulating required average SGPA across all remaining semesters."
                    ) if _to_float(completed_credits, 0.0) == 0.0 else None,
                    # Target CGPA Slider
                    html.div(
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "marginBottom": "0.5rem"}},
                            html.label({"style": {"fontSize": "0.85rem", "fontWeight": "700", "color": "var(--brand-navy)"}}, "Target Graduation CGPA"),
                            html.span({"style": {"fontFamily": "var(--font-display)", "fontSize": "1.75rem", "color": "var(--brand-vermillion)"}}, f"{_to_float(target_cgpa, 0.0):.2f}")
                        ),
                        html.input({
                            "type": "range",
                            "min": "5.00",
                            "max": "10.00",
                            "step": "0.05",
                            "value": str(target_cgpa),
                            "style": {"width": "100%", "cursor": "pointer", "accentColor": "var(--brand-vermillion)"},
                            "on_change": lambda e: set_target_cgpa(_to_float(e, target_cgpa))
                        }),
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.75rem", "color": "var(--text-muted)", "marginTop": "0.25rem"}},
                            html.span("5.00 (Passing)"),
                            html.span("8.50 (Distinction)"),
                            html.span("10.00 (Max)")
                        )
                    ),
                    # Input Grid
                    html.div(
                        {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem"}},
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Current CGPA"),
                            html.input({
                                "type": "number",
                                "step": "0.01",
                                "min": "0.00",
                                "max": "10.00",
                                "className": "input",
                                "value": str(current_cgpa),
                                "on_change": lambda e: set_current_cgpa(_to_float(e, current_cgpa))
                            })
                        ),
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Completed Credits"),
                            html.input({
                                "type": "number",
                                "min": "0",
                                "className": "input",
                                "value": str(completed_credits),
                                "on_change": lambda e: set_completed_credits(_to_float(e, completed_credits))
                            })
                        ),
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Remaining Semesters"),
                            html.input({
                                "type": "number",
                                "min": "1",
                                "max": "8",
                                "className": "input",
                                "value": str(remaining_semesters),
                                "on_change": lambda e: set_remaining_semesters(_to_int(e, remaining_semesters))
                            })
                        ),
                        html.div(
                            html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, "Degree Total Credits"),
                            html.input({
                                "type": "number",
                                "min": "1",
                                "className": "input",
                                "value": str(total_credits),
                                "on_change": lambda e: set_total_credits(_to_float(e, total_credits))
                            })
                        )
                    )
                )
            ),
            # Feasibility Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Milestone Feasibility"),
                    html.span(
                        {"className": badge_class},
                        badge_icon,
                        badge_text
                    )
                ),
                html.div(
                    {"style": {"padding": "1.75rem", "backgroundColor": "#F8FAFC", "borderRadius": "var(--radius-md)", "border": "1px solid var(--border-subtle)", "marginBottom": "1.5rem", "textAlign": "center"}},
                    html.div({"style": {"fontSize": "0.8rem", "textTransform": "uppercase", "color": "var(--text-muted)", "fontWeight": "700", "letterSpacing": "0.05em"}}, "Required Average SGPA Per Semester"),
                    html.div(
                        {"style": {"fontFamily": "var(--font-display)", "fontSize": "3.5rem", "color": sgpa_color, "margin": "0.5rem 0"}},
                        display_sgpa
                    ),
                    html.p(
                        {"style": {"fontSize": "0.9rem", "color": "var(--text-secondary)", "lineHeight": "1.5", "maxWidth": "440px", "margin": "0 auto"}},
                        message
                    )
                ),
                html.h4({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.1rem", "color": "var(--brand-navy)", "marginBottom": "0.75rem"}}, "Future Performance Projections"),
                html.div(
                    {"className": "table-container"},
                    html.table(
                        html.thead(
                            html.tr(
                                html.th("Future Average SGPA"),
                                html.th("Projected Final CGPA"),
                                html.th("Target Status")
                            )
                        ),
                        html.tbody(scenario_rows)
                    )
                )
            )
        )
    )
