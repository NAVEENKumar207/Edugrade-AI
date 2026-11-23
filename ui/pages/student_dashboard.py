"""
Student Performance Dashboard Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/student_dashboard/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import (
    get_student_dashboard_data, get_placement_matrix_data, get_arrears,
    get_next_moves, get_journey_and_badges
)

@component
def StudentDashboard(user, set_page):
    data, set_data = use_state(lambda: get_student_dashboard_data(user))
    placement_data, set_placement_data = use_state(lambda: get_placement_matrix_data(user))
    arrears_data, set_arrears_data = use_state(lambda: get_arrears(user))
    moves_data, set_moves_data = use_state(lambda: get_next_moves(user, assumed_grade="B"))
    journey_data, set_journey_data = use_state(lambda: get_journey_and_badges(user))

    if not data:
        data = get_student_dashboard_data(user)
    if not placement_data:
        placement_data = get_placement_matrix_data(user)
    if not arrears_data:
        arrears_data = get_arrears(user)
    if not moves_data:
        moves_data = get_next_moves(user, assumed_grade="B")
    if not journey_data:
        journey_data = get_journey_and_badges(user)

    top_move_sentence = moves_data[0].get("sentence", "") if moves_data and len(moves_data) > 0 else ""
    earned_badges = journey_data.get("badges", {}).get("earned_badges", [])[:3]

    student = data.get("student", {})
    semesters = data.get("semesters", [])
    recent_courses = data.get("recent_courses", [])
    readiness = data.get("placement_readiness", {})

    # Calculate active semester for trajectory pill
    latest_sem_num = semesters[0].semester_number if semesters else 1
    selected_sem_num, set_selected_sem_num = use_state(latest_sem_num)

    selected_sem = next((s for s in semesters if s.semester_number == selected_sem_num), None)
    if not selected_sem and semesters:
        selected_sem = semesters[0]

    # Selected semester metadata for detail pill
    if selected_sem:
        top_course = next((c for c in recent_courses if c.semester_number == selected_sem.semester_number), None)
        top_meta = f"{top_course.course_code} ({top_course.grade})" if top_course else "Core Subjects Cleared"
        pill_title = f"Sem {selected_sem.semester_number}"
        pill_sgpa = f"{float(selected_sem.sgpa):.2f} SGPA"
        pill_meta = f"{selected_sem.credits_earned} Cr • {top_meta}"
    else:
        pill_title = "Sem I"
        pill_sgpa = "N/A"
        pill_meta = "No record logged"

    # Grade breakdown counts
    o_count = sum(1 for c in recent_courses if c.grade == 'O')
    aplus_count = sum(1 for c in recent_courses if c.grade == 'A+')
    a_count = sum(1 for c in recent_courses if c.grade == 'A')
    bplus_count = sum(1 for c in recent_courses if c.grade == 'B+')

    # Credits %
    total_credits = student.get("total_credits", 160) or 160
    credits_earned = student.get("credits_earned", 0)
    credits_pct = max(0, min(100, int((credits_earned / total_credits) * 100))) if total_credits else 0
    remaining_credits = max(0, total_credits - credits_earned)

    # Trajectory Bars
    bar_elements = []
    # Display in ascending order (Sem 1 to N)
    sorted_sems = sorted(semesters, key=lambda s: s.semester_number)
    for s in sorted_sems:
        sgpa_val = float(s.sgpa)
        pct = max(10, min(100, int((sgpa_val / 10.0) * 100)))
        is_selected = (s.semester_number == (selected_sem.semester_number if selected_sem else None))
        
        def make_select_handler(sem_n):
            def handle_click(e):
                set_selected_sem_num(sem_n)
            return handle_click

        fill_cls = "bg-light-primary" if is_selected else "bg-light-surface-container-highest group-hover:bg-light-primary-container"
        text_cls = "text-light-primary font-bold" if is_selected else "text-light-on-surface-variant"

        bar_elements.append(
            html.button(
                {
                    "key": str(s.semester_number),
                    "type": "button",
                    "on_click": make_select_handler(s.semester_number),
                    "class_name": "sem-bar group flex flex-col items-center gap-gutter-xs p-1 focus:outline-none flex-1",
                    "title": f"Semester {s.semester_number}: {sgpa_val:.2f} SGPA",
                },
                html.span({"class_name": f"font-mono text-mono-sm tabular-nums {text_cls}"}, f"{sgpa_val:.2f}"),
                html.div(
                    {"class_name": "w-full max-w-[52px] h-36 sm:h-40 bg-light-surface-container-low flex items-end overflow-hidden border border-light-outline-variant/30"},
                    html.div({
                        "class_name": f"bar-fill w-full transition-all duration-state-change {fill_cls}",
                        "style": {"height": f"{pct}%"}
                    })
                ),
                html.span({"class_name": f"font-mono text-mono-sm uppercase whitespace-nowrap {text_cls}"}, f"Sem {s.semester_number}")
            )
        )

    # Placement Summary
    comp_list = placement_data.get("companies", [])
    eligible_count = sum(1 for c in comp_list if c.get("is_eligible", False))
    total_companies = len(comp_list)
    top_3_companies = comp_list[:3]

    # Strengths (Grade O or A+)
    strong_courses = [c for c in recent_courses if c.grade in ['O', 'A+']][:3]
    # Weakness / Remediation (Grade B+, B, C, or U)
    remediation_courses = [c for c in recent_courses if c.grade in ['B+', 'B', 'C', 'U', 'RA']][:3]

    return html.div(
        {"class_name": "flex-1 flex flex-col gap-section overflow-y-auto"},
        
        # Identity Banner
        html.section(
            {"class_name": "border-2 border-light-secondary p-gutter-lg bg-light-surface flex flex-col md:flex-row justify-between items-start md:items-center gap-gutter-md"},
            html.div(
                {"class_name": "flex flex-col gap-1"},
                html.div(
                    {"class_name": "flex items-center gap-gutter-md flex-wrap"},
                    html.h2({"class_name": "font-headline text-headline-lg tracking-tight uppercase"}, student.get("name", "STUDENT RECORD")),
                    html.span({"class_name": "px-2.5 py-0.5 bg-light-secondary text-light-on-secondary font-mono text-mono-sm font-bold"}, student.get("roll_number", "21CS001")),
                    html.span({"class_name": "px-2.5 py-0.5 bg-light-surface-container-high text-light-on-surface font-mono text-mono-sm font-bold"}, f"SEM {student.get('current_semester', 6)}")
                ),
                html.p(
                    {"class_name": "text-body-md text-light-on-surface-variant font-mono mt-1"},
                    f"{student.get('department', 'Computer Science')} • CBCS 2026 • Target: {student.get('target_cgpa', 8.5):.2f}"
                )
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-md flex-wrap"},
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: set_page("planner"),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 border-2 border-light-secondary text-light-secondary font-headline font-bold text-label-md hover:bg-light-secondary hover:text-light-on-secondary transition-colors duration-state-change uppercase cursor-pointer"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "calculate"),
                    html.span("Simulate Target")
                ),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: set_page("advisor"),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 bg-light-primary text-light-on-primary font-headline font-bold text-label-md hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change uppercase cursor-pointer"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "psychology"),
                    html.span("Ask Advisor")
                )
            )
        ),

        # Next Best Move Quick Line
        (
            html.div(
                {
                    "class_name": "p-3 px-4 rounded-radius-md bg-light-surface-container-low border border-light-outline-variant flex items-center justify-between gap-2 cursor-pointer hover:border-light-primary transition-colors",
                    "on_click": lambda e: set_page("future_lab")
                },
                html.div(
                    {"class_name": "flex items-center gap-2 overflow-hidden"},
                    html.span({"class_name": "material-symbols-outlined text-light-primary text-[20px] shrink-0"}, "trending_up"),
                    html.span({"class_name": "text-label-sm font-mono text-light-primary font-bold uppercase shrink-0"}, "Next Best Move:"),
                    html.span({"class_name": "text-body-sm text-light-on-surface truncate font-medium"}, top_move_sentence)
                ),
                html.span({"class_name": "text-label-xs font-mono text-light-primary shrink-0 flex items-center gap-1 font-bold"}, "Future Lab →")
            )
            if top_move_sentence else None
        ),

        # Top 3 Earned Badges Row
        (
            html.div(
                {"class_name": "card p-3 px-4 border border-light-outline-variant bg-light-surface-container-lowest flex flex-col md:flex-row md:items-center justify-between gap-gutter-md rounded-radius-md"},
                html.div(
                    {"class_name": "flex items-center gap-2"},
                    html.span({"class_name": "material-symbols-outlined text-light-primary text-[20px]"}, "military_tech"),
                    html.strong({"class_name": "text-label-sm font-mono uppercase text-light-on-surface"}, "Badges:"),
                ),
                html.div(
                    {"class_name": "flex items-center gap-2 flex-wrap"},
                    [
                        html.span(
                            {"key": b["id"], "class_name": f"badge font-mono text-label-xs {b.get('badge_class', 'badge-primary')}"},
                            f"🏆 {b['name']}"
                        )
                        for b in earned_badges
                    ]
                ),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: set_page("journey"),
                        "class_name": "text-label-xs font-mono text-light-primary font-bold hover:underline cursor-pointer"
                    },
                    "Journey →"
                )
            )
            if earned_badges else None
        ),

        # 4-KPI Bento Row
        html.section(
            {"class_name": "grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 border border-light-outline-variant bg-light-surface-container-lowest items-stretch"},
            
            # Card 1: Vermilion Highlight Block
            html.article(
                {"class_name": "h-full bg-light-primary-container text-light-on-primary-container p-gutter-lg flex flex-col justify-between gap-gutter-md border-b sm:border-b-0 sm:border-r border-light-outline-variant"},
                html.header(
                    {"class_name": "flex items-start justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-mono text-mono-sm uppercase font-bold"}, "Current CGPA"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-primary-container"}, "10-point scale")
                    ),
                    html.span({"class_name": "material-symbols-outlined text-[20px]"}, "analytics")
                ),
                html.div(
                    {"class_name": "flex items-center justify-between gap-gutter-sm mt-3"},
                    html.p({"class_name": "font-headline text-display-lg tabular-nums"}, f"{student.get('current_cgpa', 0.0):.2f}"),
                    html.span(
                        {"class_name": "inline-flex items-center px-2.5 py-1 rounded-full border border-light-on-primary-container font-mono text-mono-sm tabular-nums whitespace-nowrap shrink-0 font-bold"},
                        "FIRST CLASS" if student.get("current_cgpa", 0.0) >= 8.5 else "GOOD STANDING"
                    )
                )
            ),

            # Card 2: Latest SGPA
            html.article(
                {"class_name": "h-full bg-light-surface-container-lowest p-gutter-lg flex flex-col justify-between gap-gutter-md border-b xl:border-b-0 xl:border-r border-light-outline-variant"},
                html.header(
                    {"class_name": "flex items-start justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "Latest SGPA"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"Semester {latest_sem_num}")
                    ),
                    html.span({"class_name": "material-symbols-outlined text-[20px] text-light-primary"}, "trending_up")
                ),
                html.div(
                    {"class_name": "flex items-center justify-between gap-gutter-sm mt-3"},
                    html.p({"class_name": "font-headline text-display-lg text-light-on-surface tabular-nums"}, f"{student.get('latest_sgpa', 0.0):.2f}"),
                    html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant tabular-nums whitespace-nowrap"}, f"{credits_earned} Credits")
                )
            ),

            # Card 3: Credits Earned
            html.article(
                {"class_name": "h-full bg-light-surface-container-lowest p-gutter-lg flex flex-col justify-between gap-gutter-md border-b sm:border-b-0 sm:border-r border-light-outline-variant"},
                html.header(
                    {"class_name": "flex items-start justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "Credits"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"{remaining_credits} remaining")
                    ),
                    html.span({"class_name": "material-symbols-outlined text-[20px] text-light-on-surface"}, "task_alt")
                ),
                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm mt-3"},
                    html.div(
                        {"class_name": "flex items-center justify-between"},
                        html.p({"class_name": "font-headline text-headline-lg text-light-on-surface tabular-nums"}, f"{credits_earned} ", html.span({"class_name": "text-body-md text-light-on-surface-variant font-mono"}, f"/ {total_credits}")),
                        html.span({"class_name": "font-mono text-mono-md text-light-primary font-bold tabular-nums"}, f"{credits_pct}%")
                    ),
                    html.div(
                        {"class_name": "w-full h-2 bg-light-surface-container-high overflow-hidden"},
                        html.div({"class_name": "h-full bg-light-secondary", "style": {"width": f"{credits_pct}%"}})
                    )
                )
            ),

            # Card 4: Deep Espresso Contrast Block
            html.article(
                {"class_name": "h-full bg-light-secondary text-light-on-secondary p-gutter-lg flex flex-col justify-between gap-gutter-md"},
                html.header(
                    {"class_name": "flex items-start justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-mono text-mono-sm uppercase text-light-on-secondary/80 font-bold"}, "Arrears"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-secondary/75"}, "Active backlogs")
                    ),
                    html.span({"class_name": "material-symbols-outlined text-[20px]"}, "verified_user")
                ),
                html.div(
                    {"class_name": "flex items-center justify-between gap-gutter-sm mt-3"},
                    html.p({"class_name": "font-headline text-display-lg tabular-nums"}, str(student.get("backlogs_count", 0))),
                    html.span(
                        {
                            "class_name": "inline-flex items-center px-2.5 py-1 rounded-full border border-light-on-secondary/40 font-mono text-mono-sm uppercase whitespace-nowrap shrink-0 font-bold " + 
                                ("bg-light-primary text-light-on-primary" if student.get("backlogs_count", 0) > 0 else "")
                        },
                        "All Clear" if student.get("backlogs_count", 0) == 0 else f"{student.get('backlogs_count')} Active"
                    )
                )
            )
        ),

        # Analytics & Placement Row
        html.section(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-stretch"},
            
            # Interactive Semester SGPA Bar Chart (7 cols)
            html.article(
                {"class_name": "xl:col-span-7 bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col justify-between gap-gutter-lg"},
                html.header(
                    {"class_name": "flex flex-wrap items-start justify-between gap-gutter-md"},
                    html.div(
                        html.h3({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "SGPA Trajectory"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Click bar to inspect semester")
                    ),
                    html.div(
                        {"class_name": "px-3 py-1.5 bg-light-surface-container-low border border-light-outline-variant flex items-center gap-gutter-sm"},
                        html.span({"class_name": "font-mono text-mono-sm text-light-primary uppercase font-bold whitespace-nowrap"}, pill_title),
                        html.span({"class_name": "font-mono text-mono-md text-light-on-surface tabular-nums font-bold whitespace-nowrap"}, pill_sgpa),
                        html.span({"class_name": "font-body text-body-sm text-light-on-surface-variant hidden sm:inline"}, pill_meta)
                    )
                ),

                # Bars Container
                html.div(
                    {"class_name": "flex gap-gutter-md items-end pt-gutter-md border-b border-light-outline-variant pb-gutter-sm overflow-x-auto min-h-[180px]"},
                    bar_elements if bar_elements else [html.p({"class_name": "font-mono text-mono-sm text-light-outline p-4"}, "No records.")]
                ),

                # Grade Distribution Pill Strip
                html.div(
                    {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md text-body-sm text-light-on-surface-variant"},
                    html.div(
                        {"class_name": "flex flex-wrap items-center gap-gutter-xs"},
                        html.span({"class_name": "px-2.5 py-0.5 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm tabular-nums"}, f"O: {o_count}"),
                        html.span({"class_name": "px-2.5 py-0.5 rounded-full bg-light-surface-container-low border border-light-outline-variant font-mono text-mono-sm tabular-nums"}, f"A+: {aplus_count}"),
                        html.span({"class_name": "px-2.5 py-0.5 rounded-full bg-light-surface-container-low border border-light-outline-variant font-mono text-mono-sm tabular-nums"}, f"A: {a_count}"),
                        html.span({"class_name": "px-2.5 py-0.5 rounded-full bg-light-surface-container-low border border-light-outline-variant font-mono text-mono-sm tabular-nums"}, f"B+: {bplus_count}")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_page("results"),
                            "class_name": "inline-flex items-center gap-1 font-mono text-mono-sm uppercase text-light-primary hover:underline whitespace-nowrap shrink-0 cursor-pointer"
                        },
                        html.span("Full Transcript"),
                        html.span({"class_name": "material-symbols-outlined text-[16px]"}, "arrow_forward")
                    )
                )
            ),

            # Placement Matrix Snapshot (5 cols)
            html.article(
                {"class_name": "xl:col-span-5 bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col justify-between gap-gutter-md"},
                html.header(
                    {"class_name": "flex items-start justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Placement Matrix"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"{total_companies} drives")
                    ),
                    html.span({"class_name": "font-headline text-headline-md text-light-primary tabular-nums whitespace-nowrap shrink-0"}, f"{eligible_count} / {total_companies}")
                ),

                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm"},
                    [
                        html.div(
                            {"key": str(idx), "class_name": "flex items-center justify-between gap-gutter-sm p-3 bg-light-surface-container-low border border-light-outline-variant"},
                            html.div(
                                {"class_name": "min-w-0"},
                                html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold truncate"}, f"{c.get('company_name', 'Company')} • {c.get('role_title', 'Role')}"),
                                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant tabular-nums"}, f"Min {c.get('min_cgpa', 7.0):.2f} CGPA • {c.get('package_lpa', 0.0):.1f} LPA")
                            ),
                            html.span(
                                {
                                    "class_name": "px-2.5 py-1 rounded-full font-mono text-mono-sm uppercase whitespace-nowrap shrink-0 " + 
                                        ("bg-light-secondary text-light-on-secondary" if c.get("is_eligible") else "bg-light-primary-container text-light-on-primary-container font-bold")
                                },
                                "Eligible" if c.get("is_eligible") else f"{(float(c.get('min_cgpa', 0)) - float(student.get('current_cgpa', 0))):.2f} Short"
                            )
                        ) for idx, c in enumerate(top_3_companies)
                    ] if top_3_companies else [html.p({"class_name": "font-mono text-mono-sm text-light-outline p-2"}, "No placement criteria.")]
                ),

                html.footer(
                    {"class_name": "pt-gutter-sm border-t border-light-outline-variant flex items-center justify-between gap-gutter-sm"},
                    html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"Readiness: {readiness.get('score', 85) if readiness else 85}%"),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_page("placement"),
                            "class_name": "inline-flex items-center gap-gutter-xs font-mono text-mono-sm uppercase text-light-primary hover:underline whitespace-nowrap shrink-0 cursor-pointer"
                        },
                        html.span(f"View All ({total_companies})"),
                        html.span({"class_name": "material-symbols-outlined text-[16px]"}, "arrow_forward")
                    )
                )
            )
        ),

        # Strengths & Remediation Section
        html.section(
            {"class_name": "grid grid-cols-1 lg:grid-cols-2 gap-gutter-lg items-stretch"},
            
            # Top Academic Strengths
            html.article(
                {"class_name": "h-full bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
                html.header(
                    {"class_name": "flex items-center justify-between gap-gutter-sm"},
                    html.div(
                        html.h3({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Strengths"),
                        html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Top credit-weighted grades")
                    ),
                    html.span({"class_name": "material-symbols-outlined text-[22px] text-light-on-surface"}, "workspace_premium")
                ),
                html.div(
                    {"class_name": "flex flex-col divide-y divide-light-outline-variant"},
                    [
                        html.div(
                            {"key": str(c.id), "class_name": "py-3 flex items-center justify-between gap-gutter-md"},
                            html.div(
                                html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold"}, c.course_name),
                                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant tabular-nums"}, f"{c.course_code} • {c.credits} Cr • Sem {c.semester_number}")
                            ),
                            html.span({"class_name": "px-2.5 py-1 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm tabular-nums whitespace-nowrap shrink-0"}, f"{c.grade} ({c.grade_point:.1f})")
                        ) for c in strong_courses
                    ] if strong_courses else [html.p({"class_name": "font-mono text-mono-sm text-light-outline py-2"}, "No grades logged.")]
                )
            ),

            # Focus & Remediation
            html.article(
                {"class_name": "h-full bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col justify-between gap-gutter-md"},
                html.div(
                    {"class_name": "flex flex-col gap-gutter-md"},
                    html.header(
                        {"class_name": "flex items-center justify-between gap-gutter-sm"},
                        html.div(
                            html.h3({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Remediation"),
                            html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, f"Courses below {student.get('current_cgpa', 8.5):.2f} CGPA")
                        ),
                        html.span({"class_name": "material-symbols-outlined text-[22px] text-light-primary"}, "target")
                    ),
                    html.div(
                        {"class_name": "flex flex-col divide-y divide-light-outline-variant"},
                        [
                            html.div(
                                {"key": str(c.id), "class_name": "py-3 flex items-center justify-between gap-gutter-md"},
                                html.div(
                                    html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold"}, c.course_name),
                                    html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant tabular-nums"}, f"{c.course_code} • {c.credits} Cr • Sem {c.semester_number}")
                                ),
                                html.span({"class_name": "px-2.5 py-1 rounded-full bg-light-primary-container text-light-on-primary-container font-mono text-mono-sm tabular-nums whitespace-nowrap shrink-0 font-bold"}, f"{c.grade} ({c.grade_point:.1f})")
                            ) for c in remediation_courses
                        ] if remediation_courses else [html.p({"class_name": "font-mono text-mono-sm text-success py-2"}, "No low-performing courses.")]
                    )
                ),
                html.footer(
                    {"class_name": "pt-gutter-sm border-t border-light-outline-variant flex items-center justify-between gap-gutter-sm"},
                    html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Study Plan"),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_page("advisor"),
                            "class_name": "inline-flex items-center gap-gutter-xs font-mono text-mono-sm uppercase text-light-primary hover:underline whitespace-nowrap shrink-0 cursor-pointer"
                        },
                        html.span("AI Plan"),
                        html.span({"class_name": "material-symbols-outlined text-[16px]"}, "arrow_forward")
                    )
                )
            )
        )
    )
