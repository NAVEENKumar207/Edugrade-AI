"""
Future Lab & Academic Digital Twin Component for EduGrade AI ReactPy Frontend.
Provides Monte Carlo future trajectory simulation, Next Best Move impact ranking,
and institutional regulation Marks Target calculator.
"""

from reactpy import component, html, use_state
from ui.services.data_service import (
    get_student_profile,
    run_digital_twin_simulation,
    get_next_moves,
    calculate_marks_target_bridge,
)

@component
def FutureLab(user, set_page=None):
    profile = get_student_profile(user)
    current_cgpa_val = float(profile.current_cgpa) if profile and profile.current_cgpa else 8.00
    default_target = float(profile.target_cgpa) if profile and profile.target_cgpa else 8.50

    # Digital Twin Simulator State
    target_cgpa, set_target_cgpa = use_state(default_target)
    effort, set_effort = use_state("same")
    sim_result, set_sim_result = use_state(None)
    is_simulating, set_is_simulating = use_state(False)

    # Next Best Move State
    assumed_grade, set_assumed_grade = use_state("B")
    moves_list, set_moves_list = use_state(None)

    # Marks Target State
    calc_mode, set_calc_mode = use_state("target") # "target" or "expected"
    internal_marks, set_internal_marks = use_state(36)
    target_letter_grade, set_target_letter_grade = use_state("A+")
    expected_paper, set_expected_paper = use_state(75)
    calc_result, set_calc_result = use_state(None)
    calc_error, set_calc_error = use_state("")

    # Fetch Next Best Move if not yet loaded
    if moves_list is None:
        moves_list = get_next_moves(user, assumed_grade=assumed_grade)

    def handle_change_assumed_grade(new_grade):
        set_assumed_grade(new_grade)
        updated = get_next_moves(user, assumed_grade=new_grade)
        set_moves_list(updated)

    def handle_run_simulation(e=None):
        set_is_simulating(True)
        res = run_digital_twin_simulation(user, target_cgpa=float(target_cgpa), effort=effort)
        set_sim_result(res)
        set_is_simulating(False)

    def handle_calculate_marks(e=None):
        set_calc_error("")
        try:
            im = float(internal_marks)
            if calc_mode == "target":
                res = calculate_marks_target_bridge(im, target_grade=target_letter_grade, mode="target")
            else:
                pm = float(expected_paper)
                res = calculate_marks_target_bridge(im, paper_marks=pm, mode="expected")
            set_calc_result(res)
        except Exception as err:
            set_calc_error(str(err))

    # Initial automatic simulation on first load if not simulated yet
    if sim_result is None and not is_simulating:
        sim_result = run_digital_twin_simulation(user, target_cgpa=default_target, effort="same")

    # Determine top move and remaining moves
    top_move = moves_list[0] if moves_list and len(moves_list) > 0 else None
    secondary_moves = moves_list[1:] if moves_list and len(moves_list) > 1 else []

    return html.div(
        {"className": "p-gutter-xl max-w-7xl mx-auto flex flex-col gap-gutter-xl animate-fade-in"},

        # Header Title
        html.div(
            {"className": "border-b border-light-outline-variant pb-gutter-md"},
            html.h1({"className": "text-headline-md font-headline font-bold text-light-on-surface uppercase"}, "Future Lab"),
            html.p(
                {"className": "text-mono-sm font-mono text-light-on-surface-variant uppercase mt-1"},
                "Predictive simulation, move ranking, and exam target modeling."
            )
        ),

        # ==============================================================
        # PART 3: NEXT BEST MOVE (IMPACT RANKING) CARD
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-md"},
            html.div(
                {"className": "flex flex-col md:flex-row md:items-center justify-between gap-gutter-md border-b border-light-outline-variant pb-gutter-sm"},
                html.div(
                    html.div(
                        {"className": "flex items-center gap-2"},
                        html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "trending_up"),
                        html.h2({"className": "text-title-lg font-headline font-bold text-light-on-surface"}, "Next Best Move")
                    ),
                    html.p({"className": "text-body-sm text-light-on-surface-variant"}, "Impact ranking: which arrear clearing or grade improvement yields the highest corporate unlock")
                ),
                html.div(
                    {"className": "flex items-center gap-2"},
                    html.span({"className": "text-label-sm font-mono text-light-on-surface-variant uppercase"}, "Assumed Grade:"),
                    html.div(
                        {"className": "inline-flex rounded-radius-md border border-light-outline-variant p-0.5 bg-light-surface-container-low"},
                        [
                            html.button(
                                {
                                    "key": g,
                                    "className": (
                                        "px-2.5 py-1 text-label-sm font-mono font-bold rounded-radius-sm transition-colors "
                                        + ("bg-light-primary text-light-on-primary" if assumed_grade == g else "text-light-on-surface-variant hover:text-light-on-surface")
                                    ),
                                    "on_click": lambda e, gr=g: handle_change_assumed_grade(gr)
                                },
                                f"Grade {g}"
                            )
                            for g in ["C", "B", "A"]
                        ]
                    )
                )
            ),

            # Top Next Move Highlight Box
            html.div(
                {"className": "p-gutter-md rounded-radius-md bg-light-surface-container border-l-4 border-light-primary flex flex-col md:flex-row md:items-center justify-between gap-gutter-md"},
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.div(
                        {"className": "flex items-center gap-2"},
                        html.span({"className": "badge badge-primary uppercase text-label-xs font-mono"}, "Highest Impact Move"),
                        html.span(
                            {"className": "text-label-sm font-mono text-light-on-surface-variant"},
                            f"Credits: {top_move['credits']}" if top_move and top_move.get('credits') else ""
                        )
                    ),
                    html.div(
                        {"className": "text-title-md font-bold text-light-on-surface mt-1"},
                        top_move["sentence"] if top_move else "No active actions detected."
                    ),
                    html.div(
                        {"className": "flex items-center gap-gutter-md mt-1 text-body-xs font-mono text-light-on-surface-variant"},
                        html.span(f"CGPA: {top_move['cgpa_before']:.2f} → {top_move['cgpa_after']:.2f} (+{top_move['cgpa_gain']:.2f})") if top_move else None,
                        html.span(f"Readiness Score: {top_move['readiness_before']} → {top_move['readiness_after']} (+{top_move['readiness_gain']})") if top_move else None,
                    )
                ),
                html.div(
                    {"className": "shrink-0 flex items-center gap-2"},
                    [
                        html.span(
                            {"key": cname, "className": "badge badge-emerald text-label-xs font-mono"},
                            f"+ {cname}"
                        )
                        for cname in (top_move.get("new_companies", []) if top_move else [])
                    ]
                )
            ),

            # Secondary ranked list if more than 1 move
            (
                html.div(
                    {"className": "flex flex-col gap-2 mt-2"},
                    html.span({"className": "text-label-sm font-mono text-light-on-surface-variant uppercase"}, "Alternative Priorities:"),
                    [
                        html.div(
                            {
                                "key": m.get("course_code", str(idx)),
                                "className": "flex items-center justify-between p-2 rounded-radius-sm border border-light-outline-variant bg-light-surface-container-low text-body-sm font-mono"
                            },
                            html.span(f"#{idx+2} {m['sentence']}"),
                            html.span(
                                {"className": "text-light-primary font-bold"},
                                f"+{m['cgpa_gain']:.2f} CGPA"
                            )
                        )
                        for idx, m in enumerate(secondary_moves)
                    ]
                )
                if secondary_moves else None
            )
        ),

        # ==============================================================
        # PART 2: DIGITAL TWIN SIMULATOR CARD
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-lg"},
            html.div(
                {"className": "border-b border-light-outline-variant pb-gutter-sm flex flex-col md:flex-row md:items-center justify-between gap-gutter-md"},
                html.div(
                    html.div(
                        {"className": "flex items-center gap-2"},
                        html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "analytics"),
                        html.h2({"className": "text-title-lg font-headline font-bold text-light-on-surface"}, "Digital Twin Trajectory Simulator")
                    ),
                    html.p({"className": "text-body-sm text-light-on-surface-variant"}, "Monte Carlo simulation (2,000 runs) weighted by your historical grade probabilities")
                )
            ),

            # Simulation Controls
            html.div(
                {"className": "grid grid-cols-1 md:grid-cols-3 gap-gutter-md p-gutter-md rounded-radius-md bg-light-surface-container-low border border-light-outline-variant"},
                # Target CGPA slider
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label(
                        {"className": "text-label-sm font-mono text-light-on-surface font-bold flex justify-between"},
                        html.span("Target Final CGPA:"),
                        html.span({"className": "text-light-primary"}, f"{float(target_cgpa):.2f}")
                    ),
                    html.input({
                        "type": "range",
                        "min": "5.00",
                        "max": "10.00",
                        "step": "0.05",
                        "value": str(target_cgpa),
                        "className": "w-full cursor-pointer accent-light-primary",
                        "on_change": lambda e: set_target_cgpa(e.get("target", {}).get("value", 8.5))
                    }),
                    html.span({"className": "text-label-xs text-light-on-surface-variant font-mono"}, f"Current: {current_cgpa_val:.2f}")
                ),

                # Effort Selector
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Academic Effort Level:"),
                    html.div(
                        {"className": "grid grid-cols-3 gap-1 rounded-radius-md border border-light-outline-variant p-1 bg-light-surface-container"},
                        [
                            html.button(
                                {
                                    "key": eff,
                                    "className": (
                                        "py-1.5 text-center text-label-xs font-mono font-bold rounded-radius-sm transition-colors "
                                        + ("bg-light-primary text-light-on-primary" if effort == eff else "text-light-on-surface-variant hover:text-light-on-surface")
                                    ),
                                    "on_click": lambda e, ef=eff: set_effort(ef)
                                },
                                eff.capitalize()
                            )
                            for eff in ["lower", "same", "higher"]
                        ]
                    ),
                    html.span({"className": "text-label-xs text-light-on-surface-variant font-mono"}, "Shifts grade sampling by ±1 grade tier")
                ),

                # Action Button
                html.div(
                    {"className": "flex items-end"},
                    html.button(
                        {
                            "className": "btn btn-primary w-full py-2.5 flex items-center justify-center gap-2",
                            "on_click": handle_run_simulation
                        },
                        html.span({"className": "material-symbols-outlined text-[18px]"}, "play_arrow"),
                        "Run Simulation (2,000 Runs)" if not is_simulating else "Simulating..."
                    )
                )
            ),

            # Simulation Results Display or Empty State
            (
                # Not enough data empty state
                html.div(
                    {"className": "p-gutter-xl text-center border border-dashed border-light-outline-variant rounded-radius-md"},
                    html.span({"className": "material-symbols-outlined text-light-on-surface-variant text-[48px]"}, "lock"),
                    html.h3({"className": "text-title-md font-headline font-bold text-light-on-surface mt-2"}, "Simulator Locked"),
                    html.p({"className": "text-body-sm text-light-on-surface-variant max-w-md mx-auto mt-1"}, sim_result.get("message", "Add at least 5 course results to unlock the simulator."))
                )
                if sim_result and not sim_result.get("enough_data", False) else

                # Active Results
                html.div(
                    {"className": "flex flex-col gap-gutter-lg animate-fade-in"},

                    # Top Metrics Row
                    html.div(
                        {"className": "grid grid-cols-1 md:grid-cols-4 gap-gutter-md"},
                        # Target Probability
                        html.div(
                            {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, f"Prob. of CGPA ≥ {float(target_cgpa):.2f}"),
                            html.div(
                                {
                                    "className": (
                                        "text-display-sm font-headline font-bold my-1 "
                                        + ("text-light-emerald" if sim_result.get("probability", 0) >= 70 else "text-light-amber" if sim_result.get("probability", 0) >= 40 else "text-light-danger")
                                    )
                                },
                                f"{sim_result.get('probability', 0):.1f}%"
                            ),
                            html.span({"className": "badge badge-primary text-label-xs font-mono"}, f"Effort: {effort.upper()}")
                        ),

                        # Expected Final CGPA
                        html.div(
                            {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Expected Final CGPA"),
                            html.div({"className": "text-display-sm font-headline font-bold text-light-on-surface my-1"}, f"{sim_result.get('expected_cgpa', 0):.2f}"),
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "Monte Carlo Mean")
                        ),

                        # 10th - 90th Percentile Range
                        html.div(
                            {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "10th - 90th Percentile Range"),
                            html.div({"className": "text-title-lg font-headline font-bold text-light-primary my-1"}, f"{sim_result.get('p10_cgpa', 0):.2f} — {sim_result.get('p90_cgpa', 0):.2f}"),
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "80% Confidence Band")
                        ),

                        # Zero Backlogs Probability
                        html.div(
                            {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Zero Backlogs Probability"),
                            html.div(
                                {
                                    "className": (
                                        "text-display-sm font-headline font-bold my-1 "
                                        + ("text-light-emerald" if sim_result.get("zero_backlogs_probability", 0) >= 80 else "text-light-amber")
                                    )
                                },
                                f"{sim_result.get('zero_backlogs_probability', 0):.1f}%"
                            ),
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "Clean Record Probability")
                        )
                    ),

                    # CSS Range Bar
                    html.div(
                        {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col gap-2"},
                        html.div(
                            {"className": "flex justify-between text-label-xs font-mono text-light-on-surface-variant"},
                            html.span(f"10th Percentile: {sim_result.get('p10_cgpa', 0):.2f}"),
                            html.span(f"Expected: {sim_result.get('expected_cgpa', 0):.2f}", {"className": "text-light-primary font-bold"}),
                            html.span(f"90th Percentile: {sim_result.get('p90_cgpa', 0):.2f}")
                        ),
                        html.div(
                            {"className": "h-3 w-full bg-light-surface-container rounded-radius-full overflow-hidden relative border border-light-outline-variant"},
                            html.div({
                                "className": "h-full bg-light-primary opacity-80",
                                "style": {
                                    "marginLeft": f"{max(0, min(100, (sim_result.get('p10_cgpa', 5.0) - 5.0) * 20))}%",
                                    "width": f"{max(5, min(100, (sim_result.get('p90_cgpa', 10.0) - sim_result.get('p10_cgpa', 5.0)) * 20))}%"
                                }
                            })
                        )
                    ),

                    # Corporate Placement Eligibility Forecast
                    html.div(
                        {"className": "flex flex-col gap-2"},
                        html.h3({"className": "text-title-sm font-mono uppercase tracking-wider text-light-on-surface font-bold"}, "Placement Eligibility Forecast"),
                        html.div(
                            {"className": "grid grid-cols-1 md:grid-cols-2 gap-gutter-sm"},
                            [
                                html.div(
                                    {
                                        "key": comp["company_name"],
                                        "className": "p-3 rounded-radius-sm border border-light-outline-variant bg-light-surface-container-low flex flex-col gap-1.5"
                                    },
                                    html.div(
                                        {"className": "flex justify-between items-center"},
                                        html.div(
                                            html.strong({"className": "text-body-sm text-light-on-surface"}, comp["company_name"]),
                                            html.span({"className": "text-label-xs text-light-on-surface-variant ml-2 font-mono"}, f"Min CGPA: {comp['min_cgpa']:.2f}")
                                        ),
                                        html.span(
                                            {
                                                "className": (
                                                    "text-label-sm font-mono font-bold "
                                                    + ("text-light-emerald" if comp["probability"] >= 70 else "text-light-amber" if comp["probability"] >= 40 else "text-light-danger")
                                                )
                                            },
                                            f"{comp['probability']:.1f}%"
                                        )
                                    ),
                                    # CSS Progress Bar
                                    html.div(
                                        {"className": "h-2 w-full bg-light-surface-container rounded-radius-full overflow-hidden"},
                                        html.div({
                                            "className": (
                                                "h-full "
                                                + ("bg-light-emerald" if comp["probability"] >= 70 else "bg-light-amber" if comp["probability"] >= 40 else "bg-light-danger")
                                            ),
                                            "style": {"width": f"{comp['probability']}%"}
                                        })
                                    )
                                )
                                for comp in (sim_result.get("companies", []) if sim_result else [])
                            ]
                        )
                    ),

                    # Disclaimer
                    html.div(
                        {"className": "p-2 text-center text-label-xs font-mono text-light-on-surface-variant border-t border-light-outline-variant"},
                        "Estimates outcomes from your history."
                    )
                )
                if sim_result else None
            )
        ),

        # ==============================================================
        # PART 4: MARKS TARGET CALCULATOR CARD
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-md"},
            html.div(
                {"className": "flex flex-col md:flex-row md:items-center justify-between gap-gutter-md border-b border-light-outline-variant pb-gutter-sm"},
                html.div(
                    html.div(
                        {"className": "flex items-center gap-2"},
                        html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "calculate"),
                        html.h2({"className": "text-title-lg font-headline font-bold text-light-on-surface"}, "Marks Target Calculator")
                    ),
                    html.p({"className": "text-body-sm text-light-on-surface-variant"}, "Institutional examination calculation tool based on core/regulation.py")
                ),
                # Mode Tabs
                html.div(
                    {"className": "inline-flex rounded-radius-md border border-light-outline-variant p-0.5 bg-light-surface-container-low"},
                    html.button(
                        {
                            "className": (
                                "px-3 py-1 text-label-sm font-mono font-bold rounded-radius-sm transition-colors "
                                + ("bg-light-primary text-light-on-primary" if calc_mode == "target" else "text-light-on-surface-variant hover:text-light-on-surface")
                            ),
                            "on_click": lambda e: set_calc_mode("target")
                        },
                        "I Want a Grade"
                    ),
                    html.button(
                        {
                            "className": (
                                "px-3 py-1 text-label-sm font-mono font-bold rounded-radius-sm transition-colors "
                                + ("bg-light-primary text-light-on-primary" if calc_mode == "expected" else "text-light-on-surface-variant hover:text-light-on-surface")
                            ),
                            "on_click": lambda e: set_calc_mode("expected")
                        },
                        "I Expect These Marks"
                    )
                )
            ),

            # Calculator Form Fields
            html.div(
                {"className": "grid grid-cols-1 md:grid-cols-3 gap-gutter-md items-end"},
                # Internal Marks (0 - 40)
                html.div(
                    {"className": "flex flex-col gap-1"},
                    html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Internal Marks (out of 40):"),
                    html.input({
                        "type": "number",
                        "min": "0",
                        "max": "40",
                        "value": str(internal_marks),
                        "className": "input w-full font-mono",
                        "on_change": lambda e: set_internal_marks(e.get("target", {}).get("value", 0))
                    })
                ),

                # Mode Specific Field
                (
                    html.div(
                        {"className": "flex flex-col gap-1"},
                        html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Desired Grade:"),
                        html.select(
                            {
                                "className": "input w-full font-mono",
                                "value": target_letter_grade,
                                "on_change": lambda e: set_target_letter_grade(e.get("target", {}).get("value", "A+"))
                            },
                            [
                                html.option({"value": "O"}, "O (Outstanding — 91+)"),
                                html.option({"value": "A+"}, "A+ (Excellent — 81+)"),
                                html.option({"value": "A"}, "A (Very Good — 71+)"),
                                html.option({"value": "B+"}, "B+ (Good — 61+)"),
                                html.option({"value": "B"}, "B (Above Average — 56+)"),
                                html.option({"value": "C"}, "C (Average Pass — 50+)"),
                                html.option({"value": "pass"}, "Minimum Pass (50)"),
                            ]
                        )
                    )
                    if calc_mode == "target" else
                    html.div(
                        {"className": "flex flex-col gap-1"},
                        html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Expected Paper Marks (out of 100):"),
                        html.input({
                            "type": "number",
                            "min": "0",
                            "max": "100",
                            "value": str(expected_paper),
                            "className": "input w-full font-mono",
                            "on_change": lambda e: set_expected_paper(e.get("target", {}).get("value", 0))
                        })
                    )
                ),

                # Calculate Button
                html.div(
                    html.button(
                        {
                            "className": "btn btn-primary w-full py-2 flex items-center justify-center gap-2",
                            "on_click": handle_calculate_marks
                        },
                        html.span({"className": "material-symbols-outlined text-[18px]"}, "functions"),
                        "Calculate Targets"
                    )
                )
            ),

            # Calculator Results or Error
            (
                html.div(
                    {"className": "p-3 rounded-radius-md bg-light-surface-container border-l-4 border-light-primary text-body-sm font-mono"},
                    html.div(
                        {"className": "flex items-center gap-2 mb-1"},
                        html.span(
                            {
                                "className": (
                                    "badge font-mono "
                                    + ("badge-emerald" if calc_result.get("status") == "possible" or calc_result.get("passed_external") else "badge-danger")
                                )
                            },
                            calc_result.get("status", "").upper() if "status" in calc_result else ("PASS" if calc_result.get("passed_external") else "FAIL (U)")
                        ),
                        html.strong(f"Resulting Grade: {calc_result.get('grade')}")
                    ),
                    html.p(calc_result.get("message", ""))
                )
                if calc_result else
                (
                    html.div(
                        {"className": "p-3 rounded-radius-md bg-light-surface-container border-l-4 border-light-danger text-body-sm text-light-danger font-mono"},
                        calc_error
                    )
                    if calc_error else None
                )
            ),

            # Regulation Citation Note
            html.div(
                {"className": "text-label-xs font-mono text-light-on-surface-variant"},
                "Rules from Regulation 2026. Verify with your college."
            )
        )
    )
