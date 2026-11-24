"""
CGPA Planner & Simulator Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/cgpa_planner_simulator/code.html.
"""

from reactpy import component, html, use_state
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
    initial_cgpa = float(profile.current_cgpa) if profile else 8.64
    initial_credits = int(profile.credits_earned) if profile else 136
    initial_target = float(profile.target_cgpa) if profile and profile.target_cgpa else 8.80
    initial_total_cr = int(profile.total_credits) if profile and profile.total_credits else 160
    initial_rem_sems = max(1, 8 - (profile.current_semester if profile and profile.current_semester else 6))

    current_cgpa, set_current_cgpa = use_state(initial_cgpa)
    completed_credits, set_completed_credits = use_state(initial_credits)
    target_cgpa, set_target_cgpa = use_state(initial_target)
    remaining_semesters, set_remaining_semesters = use_state(initial_rem_sems)
    total_credits, set_total_credits = use_state(initial_total_cr)

    # Compute plan using safe numeric values
    cur_f = _to_float(current_cgpa, 0.0)
    done_f = _to_float(completed_credits, 0.0)
    target_f = _to_float(target_cgpa, 0.0)
    rem_sems_i = _to_int(remaining_semesters, 1)
    total_cr_f = _to_float(total_credits, 160.0)
    rem_cr_f = max(0.0, total_cr_f - done_f)

    plan = plan_target_cgpa(
        current_cgpa=cur_f,
        completed_credits=done_f,
        target_cgpa=target_f,
        remaining_semesters=rem_sems_i,
        degree_total_credits=total_cr_f
    )

    status = plan.get("status", "feasible")
    is_achievable = plan.get("is_achievable", False)
    req_sgpa = plan.get("required_average_sgpa")
    max_cgpa = plan.get("max_achievable_cgpa", 0.0)
    message = plan.get("message", "")
    scenarios = plan.get("scenarios", [])

    # Feasibility badge styles
    if status == "already_achieved":
        badge_cls = "bg-light-secondary text-light-on-secondary"
        badge_text = "Already Achieved"
    elif status == "easily_achievable":
        badge_cls = "bg-light-secondary text-light-on-secondary"
        badge_text = "Easily Achievable"
    elif status == "feasible":
        badge_cls = "bg-light-secondary text-light-on-secondary"
        badge_text = "Feasible"
    elif status == "impossible":
        badge_cls = "bg-light-primary text-light-on-primary font-bold"
        badge_text = "Impossible"
    else:
        badge_cls = "bg-light-surface-container-high text-light-on-surface"
        badge_text = "Invalid Parameters"

    # Difficulty percentage for meter
    if req_sgpa is not None:
        diff_pct = max(0, min(100, int((req_sgpa / 10.0) * 100)))
    else:
        diff_pct = 100 if status == 'impossible' else 0

    def persist_target(new_val):
        set_target_cgpa(new_val)
        if profile and new_val:
            try:
                tg = float(new_val)
                if 0.0 <= tg <= 10.0:
                    profile.target_cgpa = tg
                    profile.save(update_fields=['target_cgpa'])
            except (ValueError, TypeError):
                pass

    def handle_target_change(e):
        val = e.get("target", {}).get("value", "")
        persist_target(val)

    # Scenarios table rows
    scenario_rows = []
    for sc in scenarios:
        fut_sgpa = sc.get("future_average_sgpa", 0.0)
        proj_cgpa = sc.get("projected_final_cgpa", 0.0)
        meets = sc.get("meets_target", False)
        diff = proj_cgpa - target_f

        if meets:
            status_text = f"Meets {target_f:.2f}"
            status_cls = "text-light-secondary font-bold"
        else:
            status_text = f"{diff:.2f} Short"
            status_cls = "text-light-on-surface-variant font-medium"

        scenario_rows.append(
            html.tr(
                {"key": f"{fut_sgpa:.2f}"},
                html.td({"class_name": "py-3 px-gutter-lg tabular-nums font-mono text-light-on-surface font-medium"}, f"{fut_sgpa:.2f}"),
                html.td({"class_name": "py-3 px-gutter-md tabular-nums font-mono font-bold text-light-on-surface"}, f"{proj_cgpa:.2f}"),
                html.td({"class_name": f"py-3 px-gutter-lg text-right font-label text-label-md {status_cls}"}, status_text)
            )
        )

    input_style = {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"}
    input_class = "w-full border-2 border-light-outline-variant bg-light-surface-container-lowest px-3 py-2.5 font-mono text-mono-md text-light-on-surface tabular-nums focus:border-light-primary focus:ring-1 focus:ring-light-primary focus:outline-none transition-colors"

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto text-light-on-surface"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight font-bold"}, "CGPA Planner & Simulator"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase mt-1"}, "Predictive Milestone Modeling • Remaining Credits Feasibility Engine")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm"},
                html.span(
                    {"class_name": f"inline-flex items-center gap-gutter-xs px-3 py-1.5 rounded-full font-mono text-mono-sm uppercase whitespace-nowrap {badge_cls}"},
                    html.span({"class_name": "material-symbols-outlined text-[14px]"}, "verified" if is_achievable else "warning"),
                    html.span(badge_text)
                )
            )
        ),

        # Grid Layout
        html.div(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-start"},
            
            # Left: Simulator Parameters (5 cols)
            html.article(
                {"class_name": "xl:col-span-5 bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md shadow-sm"},
                html.header(
                    {"class_name": "border-b border-light-outline-variant pb-gutter-sm"},
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase font-bold"}, "Simulation Parameters"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant mt-0.5"}, "Adjust values or slide target CGPA to model mathematical feasibility")
                ),

                html.form(
                    {"class_name": "flex flex-col gap-gutter-md", "on_submit": lambda e: None},
                    
                    # Current CGPA
                    html.div(
                        {"class_name": "flex flex-col gap-1.5"},
                        html.label({"class_name": "font-mono text-mono-sm text-light-on-surface uppercase font-bold"}, "Current CGPA"),
                        html.input(
                            {
                                "type": "number",
                                "step": "0.01",
                                "min": "0",
                                "max": "10",
                                "value": str(current_cgpa),
                                "on_change": lambda e: set_current_cgpa(e.get("target", {}).get("value", 0.0)),
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),

                    # Completed Credits & Remaining Credits
                    html.div(
                        {"class_name": "grid grid-cols-2 gap-gutter-md"},
                        html.div(
                            {"class_name": "flex flex-col gap-1.5"},
                            html.label({"class_name": "font-mono text-mono-sm text-light-on-surface uppercase font-bold"}, "Earned Credits"),
                            html.input(
                                {
                                    "data-demo": "planner-completed-credits",
                                    "id": "planner-completed-credits",
                                    "type": "number",
                                    "min": "0",
                                    "max": "200",
                                    "value": str(completed_credits),
                                    "on_change": lambda e: set_completed_credits(e.get("target", {}).get("value", 0)),
                                    "class_name": input_class,
                                    "style": input_style
                                }
                            )
                        ),
                        html.div(
                            {"class_name": "flex flex-col gap-1.5"},
                            html.label({"class_name": "font-mono text-mono-sm text-light-on-surface uppercase font-bold"}, "Degree Total Credits"),
                            html.input(
                                {
                                    "type": "number",
                                    "min": "1",
                                    "max": "240",
                                    "value": str(total_credits),
                                    "on_change": lambda e: set_total_credits(e.get("target", {}).get("value", 160)),
                                    "class_name": input_class,
                                    "style": input_style
                                }
                            )
                        )
                    ),

                    # Remaining Semesters
                    html.div(
                        {"class_name": "flex flex-col gap-1.5"},
                        html.label({"class_name": "font-mono text-mono-sm text-light-on-surface uppercase font-bold"}, "Remaining Semesters"),
                        html.input(
                            {
                                "data-demo": "planner-remaining-sem",
                                "id": "planner-remaining-sem",
                                "type": "number",
                                "min": "1",
                                "max": "8",
                                "value": str(remaining_semesters),
                                "on_change": lambda e: set_remaining_semesters(e.get("target", {}).get("value", 1)),
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),

                    # Target CGPA Range Slider & Numeric Input
                    html.div(
                        {"class_name": "flex flex-col gap-2"},
                        html.div(
                            {"class_name": "flex items-center justify-between"},
                            html.label({"class_name": "font-mono text-mono-sm text-light-on-surface uppercase font-bold"}, "Target Graduation CGPA"),
                            html.span({"class_name": "font-mono text-mono-sm text-light-primary font-bold tabular-nums"}, f"{target_f:.2f}")
                        ),
                        html.input(
                            {
                                "data-demo": "planner-target-slider",
                                "id": "planner-target-slider",
                                "type": "range",
                                "min": "6.0",
                                "max": "10.0",
                                "step": "0.05",
                                "value": str(target_cgpa),
                                "on_change": handle_target_change,
                                "class_name": "w-full accent-light-primary cursor-pointer",
                                "style": {"accentColor": "var(--primary)"}
                            }
                        ),
                        html.input(
                            {
                                "data-demo": "planner-target-input",
                                "id": "planner-target-input",
                                "type": "number",
                                "step": "0.01",
                                "min": "0",
                                "max": "10",
                                "value": str(target_cgpa),
                                "on_change": handle_target_change,
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),

                    # Preset Quick Targets
                    html.div(
                        {"class_name": "flex flex-wrap gap-2 pt-1"},
                        [
                            html.button(
                                {
                                    "key": f"{q_val:.1f}",
                                    "data-demo": f"planner-preset-{int(q_val*10)}",
                                    "type": "button",
                                    "on_click": lambda e, v=q_val: persist_target(v),
                                    "class_name": f"px-2.5 py-1 font-mono text-mono-sm border border-light-outline-variant hover:bg-light-surface-container-low transition-colors duration-state-change cursor-pointer {'bg-light-secondary text-light-on-secondary font-bold' if abs(target_f - q_val) < 0.05 else 'bg-light-surface-container-lowest text-light-on-surface'}"
                                },
                                f"{q_val:.2f}"
                            ) for q_val in [7.50, 8.00, 8.50, 9.00, 9.50]
                        ]
                    )
                )
            ),

            # Right: Feasibility Result & 7 What-If Scenarios (7 cols)
            html.div(
                {"class_name": "xl:col-span-7 flex flex-col gap-gutter-lg"},
                
                # Feasibility Output Card
                html.article(
                    {
                        "class_name": "bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md",
                        "data-demo": "planner-verdict-card",
                        "id": "planner-verdict-card"
                    },
                    html.header(
                        {"class_name": "flex items-center justify-between gap-gutter-sm"},
                        html.div(
                            html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Required Future SGPA"),
                            html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"Average needed across your {rem_cr_f:.0f} remaining credits")
                        ),
                        html.span(
                            {"class_name": f"px-3 py-1 rounded-full font-mono text-mono-sm uppercase whitespace-nowrap shrink-0 {badge_cls}"},
                            badge_text
                        )
                    ),

                    # Bento 2-block
                    html.div(
                        {"class_name": "grid grid-cols-1 sm:grid-cols-2 border border-light-outline-variant"},
                        html.div(
                            {"class_name": "p-gutter-md bg-light-primary-container text-light-on-primary-container"},
                            html.span({"class_name": "font-mono text-mono-sm uppercase font-bold"}, "Required Avg SGPA"),
                            html.p(
                                {"class_name": "font-headline text-display-lg tabular-nums mt-1 font-bold"},
                                f"{req_sgpa:.2f}" if req_sgpa is not None else "N/A"
                            )
                        ),
                        html.div(
                            {"class_name": "p-gutter-md bg-light-surface-container-low border-t sm:border-t-0 sm:border-l border-light-outline-variant"},
                            html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "Max Achievable CGPA"),
                            html.p(
                                {"class_name": "font-headline text-display-lg text-light-on-surface tabular-nums mt-1 font-bold"},
                                f"{max_cgpa:.2f}"
                            )
                        )
                    ),

                    # Visual Feasibility Meter
                    html.div(
                        {"class_name": "flex flex-col gap-1.5 pt-gutter-xs"},
                        html.div(
                            {"class_name": "flex items-center justify-between font-mono text-mono-sm text-light-on-surface-variant"},
                            html.span("TARGET DIFFICULTY (0.0 – 10.0)"),
                            html.span(
                                {"class_name": "text-light-on-surface font-bold"},
                                "First Class with Distinction (≥ 8.50)" if target_f >= 8.5 else "First Class (≥ 7.50)" if target_f >= 7.5 else "Second Class (≥ 6.00)"
                            )
                        ),
                        html.div(
                            {"class_name": "w-full h-2 bg-light-surface-container-high overflow-hidden"},
                            html.div(
                                {
                                    "class_name": "h-full transition-all duration-surface-enter " + ("bg-light-primary" if is_achievable else "bg-light-error"),
                                    "style": {"width": f"{diff_pct}%"}
                                }
                            )
                        )
                    ),

                    # Advisory Explanation Note
                    html.p(
                        {"class_name": "font-body text-body-sm text-light-on-surface-variant p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        message
                    )
                ),

                # 7 What-If Scenario Projections
                html.article(
                    {
                        "class_name": "bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden",
                        "data-demo": "planner-scenarios-table",
                        "id": "planner-scenarios-table"
                    },
                    html.header(
                        {"class_name": "px-gutter-lg py-gutter-md bg-light-surface-container-low border-b border-light-outline-variant"},
                        html.h3({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "What-If Graduation Projections"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"Resulting final CGPA across future SGPA benchmarks with {rem_cr_f:.0f} credits remaining")
                    ),

                    html.div(
                        {"class_name": "overflow-x-auto"},
                        html.table(
                            {"class_name": "w-full text-left border-collapse"},
                            html.thead(
                                html.tr(
                                    {"class_name": "border-b border-light-outline-variant text-light-on-surface-variant font-label text-label-md bg-light-surface-container-lowest"},
                                    html.th({"class_name": "py-3 px-gutter-lg"}, "Future Avg SGPA"),
                                    html.th({"class_name": "py-3 px-gutter-md"}, "Projected Final CGPA"),
                                    html.th({"class_name": "py-3 px-gutter-lg text-right"}, "Target Status")
                                )
                            ),
                            html.tbody(
                                {"class_name": "divide-y divide-light-outline-variant font-mono text-mono-md"},
                                scenario_rows
                            )
                        )
                    )
                )
            )
        )
    )
