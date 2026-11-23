"""
Faculty & Admin Academic Intelligence Portal Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/faculty_admin_portal/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import (
    get_faculty_overview_data, get_faculty_students_list, save_single_course_result,
    bulk_upload_grades_csv, get_admin_analytics_data
)

@component
def AdminDashboard(user):
    overview, set_overview = use_state(get_faculty_overview_data)
    analytics, set_analytics = use_state(get_admin_analytics_data)
    students, set_students = use_state(lambda: get_faculty_students_list("", "all", "all"))
    search, set_search = use_state("")
    status_filter, set_status_filter = use_state("all")
    dept_filter, set_dept_filter = use_state("all")

    # Upload Modal state
    upload_open, set_upload_open = use_state(False)
    up_roll, set_up_roll = use_state("21CS042")
    up_sem, set_up_sem = use_state("6")
    up_code, set_up_code = use_state("CS3601")
    up_name, set_up_name = use_state("Compiler Design")
    up_credits, set_up_credits = use_state("4")
    up_grade, set_up_grade = use_state("O")
    up_gp, set_up_gp = use_state("10.0")
    up_msg, set_up_msg = use_state("")
    up_err, set_up_err = use_state("")

    # Bulk CSV Modal state
    csv_modal_open, set_csv_modal_open = use_state(False)
    csv_text, set_csv_text = use_state("")
    csv_summary, set_csv_summary = use_state(None)
    csv_error, set_csv_error = use_state("")

    if not overview:
        overview = get_faculty_overview_data()
    if not analytics:
        analytics = get_admin_analytics_data()
    if students is None:
        students = get_faculty_students_list("", "all", "all")

    def reload_data():
        set_overview(get_faculty_overview_data())
        set_analytics(get_admin_analytics_data())
        set_students(get_faculty_students_list(search, status_filter, dept_filter))

    def handle_filter(dept_val):
        set_dept_filter(dept_val)
        set_students(get_faculty_students_list(search, status_filter, dept_val))

    def handle_search_change(e):
        val = e.get("target", {}).get("value", "")
        set_search(val)
        set_students(get_faculty_students_list(val, status_filter, dept_filter))

    def handle_upload():
        set_up_err("")
        set_up_msg("")
        ok, msg = save_single_course_result(
            action_user=user,
            roll_number=up_roll.strip(),
            semester_number=up_sem,
            course_code=up_code.strip(),
            course_name=up_name.strip(),
            credits=up_credits,
            grade=up_grade,
            grade_point=up_gp
        )
        if ok:
            set_up_msg(msg)
            reload_data()
        else:
            set_up_err(msg)

    def handle_csv_submit(e=None):
        set_csv_error("")
        res = bulk_upload_grades_csv(user, csv_text)
        if res.get("status_code") == 400:
            set_csv_error(res.get("error", "CSV validation failed."))
            set_csv_summary(None)
        else:
            set_csv_summary(res)
            if res.get("saved", 0) > 0:
                reload_data()

    total_students = overview.get("total_students", 0)
    avg_cgpa = overview.get("avg_cgpa", 0.0)
    eligible_count = overview.get("eligible_count", 0)
    eligibility_rate = round((eligible_count / total_students * 100), 1) if total_students > 0 else 0.0
    audit_logs = overview.get("audit_logs", [])

    # Department breakdown
    dept_stats = analytics.get("department_performance", [
        {"department": "CSE", "avg_cgpa": 8.38, "count": 120},
        {"department": "IT", "avg_cgpa": 8.21, "count": 95},
        {"department": "ECE", "avg_cgpa": 7.94, "count": 110},
        {"department": "MECH", "avg_cgpa": 7.72, "count": 80},
    ])

    # Department filter buttons
    dept_choices = ["all", "CSE", "IT", "ECE", "MECH"]
    dept_tab_elements = []
    for d in dept_choices:
        def make_dept_handler(dep):
            def handle_click(e):
                handle_filter(dep)
            return handle_click

        is_act = (dept_filter == d)
        dept_tab_elements.append(
            html.button(
                {
                    "key": d,
                    "type": "button",
                    "on_click": make_dept_handler(d),
                    "class_name": "px-2.5 py-1 font-mono text-label-sm uppercase whitespace-nowrap cursor-pointer transition-colors duration-state-change " +
                        ("bg-light-primary text-light-on-primary font-bold" if is_act else "bg-light-surface-container-lowest border border-light-outline-variant text-light-on-surface-variant hover:bg-light-surface-container-low")
                },
                "All" if d == "all" else d
            )
        )

    # Student Directory Table Rows
    student_rows = []
    for s in (students or []):
        r_num = s.get("roll_number", "N/A")
        s_name = s.get("name", "Student")
        dept_name = s.get("department", "CSE")
        s_cgpa = float(s.get("current_cgpa", 0.0))
        s_arr = int(s.get("backlogs_count", 0))

        def make_open_upload(roll):
            def handle_click(e):
                set_up_roll(roll)
                set_up_msg("")
                set_up_err("")
                set_upload_open(True)
            return handle_click

        student_rows.append(
            html.tr(
                {"key": r_num, "class_name": "student-row hover:bg-light-surface-container-low transition-colors duration-state-change"},
                html.td({"class_name": "py-3 px-gutter-lg font-mono text-mono-md text-light-primary font-bold"}, r_num),
                html.td({"class_name": "py-3 px-gutter-md font-title text-title-md font-semibold text-light-on-surface"}, s_name),
                html.td({"class_name": "py-3 px-gutter-md font-mono text-mono-sm text-light-on-surface-variant"}, dept_name),
                html.td({"class_name": "py-3 px-gutter-md text-right font-mono text-mono-md tabular-nums font-bold"}, f"{s_cgpa:.2f}"),
                html.td(
                    {"class_name": "py-3 px-gutter-md text-right font-mono text-mono-md tabular-nums font-bold " + ("text-light-primary" if s_arr > 0 else "text-light-secondary")},
                    str(s_arr)
                ),
                html.td(
                    {"class_name": "py-3 px-gutter-lg text-right"},
                    html.button(
                        {
                            "type": "button",
                            "on_click": make_open_upload(r_num),
                            "class_name": "font-label text-label-md text-light-primary hover:underline whitespace-nowrap cursor-pointer font-bold"
                        },
                        "Update Grade"
                    )
                )
            )
        )

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "Faculty & Institutional Oversight"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Cohort Academic Performance • Atomic Ingestion • Verification Trail")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm flex-wrap"},
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: (set_csv_error(""), set_csv_summary(None), set_csv_modal_open(True)),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 border border-light-secondary text-light-secondary font-mono text-mono-sm uppercase hover:bg-light-secondary hover:text-light-on-secondary transition-colors duration-state-change whitespace-nowrap cursor-pointer font-bold"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "upload_file"),
                    html.span("Bulk CSV Ingest")
                ),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: (set_up_msg(""), set_up_err(""), set_upload_open(True)),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 bg-light-primary text-light-on-primary font-mono text-mono-sm uppercase hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change whitespace-nowrap cursor-pointer font-bold"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "add"),
                    html.span("Enter Student Grade")
                )
            )
        ),

        # Department KPI Row (Wastetide 3-Column Bento)
        html.section(
            {"class_name": "grid grid-cols-1 sm:grid-cols-3 border border-light-outline-variant bg-light-surface-container-lowest items-stretch"},
            html.article(
                {"class_name": "p-gutter-lg flex flex-col gap-2 border-b sm:border-b-0 sm:border-r border-light-outline-variant"},
                html.div(
                    {"class_name": "flex items-center justify-between"},
                    html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "01 / Total Students"),
                    html.span({"class_name": "material-symbols-outlined text-[20px] text-light-on-surface"}, "groups")
                ),
                html.p({"class_name": "font-headline text-display-lg text-light-on-surface tabular-nums font-bold"}, str(total_students)),
                html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Enrolled Institutional Cohort")
            ),
            html.article(
                {"class_name": "bg-light-primary-container text-light-on-primary-container p-gutter-lg flex flex-col gap-2 border-b sm:border-b-0 sm:border-r border-light-outline-variant"},
                html.div(
                    {"class_name": "flex items-center justify-between"},
                    html.span({"class_name": "font-mono text-mono-sm uppercase font-bold"}, "02 / Cohort Avg CGPA"),
                    html.span({"class_name": "material-symbols-outlined text-[20px]"}, "monitoring")
                ),
                html.p({"class_name": "font-headline text-display-lg tabular-nums font-bold"}, f"{avg_cgpa:.2f}"),
                html.span({"class_name": "font-mono text-mono-sm uppercase font-bold"}, "Across All Departments")
            ),
            html.article(
                {"class_name": "bg-light-secondary text-light-on-secondary p-gutter-lg flex flex-col gap-2"},
                html.div(
                    {"class_name": "flex items-center justify-between"},
                    html.span({"class_name": "font-mono text-mono-sm text-light-on-secondary/80 uppercase font-bold"}, "03 / Placement Eligible"),
                    html.span({"class_name": "material-symbols-outlined text-[20px]"}, "verified")
                ),
                html.p({"class_name": "font-headline text-display-lg tabular-nums font-bold"}, f"{eligibility_rate}%"),
                html.span({"class_name": "font-mono text-mono-sm text-light-on-secondary/80 uppercase"}, f"{eligible_count} of {total_students} students")
            )
        ),

        # Department Cohort Avg CGPA Breakdown
        html.section(
            {"class_name": "bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
            html.div(
                {"class_name": "flex flex-wrap items-center justify-between gap-gutter-sm"},
                html.div(
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Cohort Performance by Department"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Mean cumulative CGPA across active departmental student bodies")
                ),
                html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant font-bold"}, f"Institutional Mean: {avg_cgpa:.2f}")
            ),
            html.div(
                {"class_name": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter-md"},
                [
                    html.div(
                        {"key": d.get("department", "CSE"), "class_name": "flex flex-col gap-1.5 p-3 bg-light-surface-container-low border border-light-outline-variant"},
                        html.div(
                            {"class_name": "flex items-center justify-between font-body text-body-sm"},
                            html.span({"class_name": "font-headline text-title-md text-light-on-surface uppercase font-bold"}, d.get("department")),
                            html.span({"class_name": "font-mono text-mono-md text-light-primary font-bold tabular-nums"}, f"{float(d.get('avg_cgpa', 8.0)):.2f}")
                        ),
                        html.div(
                            {"class_name": "w-full h-2 bg-light-surface-container-high overflow-hidden"},
                            html.div({"class_name": "h-full bg-light-primary", "style": {"width": f"{min(100, int(float(d.get('avg_cgpa', 8.0))*10))}%"}})
                        ),
                        html.span({"class_name": "font-mono text-[11px] text-light-outline"}, f"{d.get('count', 0)} Students Enrolled")
                    ) for d in dept_stats
                ]
            )
        ),

        # Directory & Audit Log Main Row
        html.div(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-start"},
            
            # Searchable & Filterable Student Directory (8 cols)
            html.article(
                {"class_name": "xl:col-span-8 bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden"},
                html.header(
                    {"class_name": "px-gutter-lg py-gutter-md bg-light-surface-container-low border-b border-light-outline-variant flex flex-wrap items-center justify-between gap-gutter-md"},
                    html.div(
                        {"class_name": "flex flex-wrap items-center gap-gutter-sm"},
                        html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Student Directory"),
                        html.div({"class_name": "flex items-center gap-1"}, dept_tab_elements)
                    ),
                    html.div(
                        {"class_name": "flex items-center border border-light-outline-variant bg-light-surface-container-lowest px-3 py-1.5"},
                        html.span({"class_name": "material-symbols-outlined text-light-on-surface-variant text-[18px] mr-2"}, "search"),
                        html.input(
                            {
                                "type": "search",
                                "placeholder": "Search roll or name...",
                                "value": search,
                                "on_change": handle_search_change,
                                "class_name": "border-none bg-transparent p-0 font-mono text-mono-sm text-light-on-surface focus:outline-none focus:ring-0 w-44"
                            }
                        )
                    )
                ),

                html.div(
                    {"class_name": "overflow-x-auto"},
                    html.table(
                        {"class_name": "w-full text-left border-collapse"},
                        html.thead(
                            html.tr(
                                {"class_name": "border-b border-light-outline-variant text-light-on-surface-variant font-label text-label-md bg-light-surface-container-lowest"},
                                html.th({"class_name": "py-3 px-gutter-lg"}, "Roll No"),
                                html.th({"class_name": "py-3 px-gutter-md"}, "Student"),
                                html.th({"class_name": "py-3 px-gutter-md"}, "Dept"),
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "CGPA"),
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "Arrears"),
                                html.th({"class_name": "py-3 px-gutter-lg text-right"}, "Action")
                            )
                        ),
                        html.tbody(
                            {"class_name": "divide-y divide-light-outline-variant font-body text-body-md"},
                            student_rows if student_rows else [
                                html.tr(
                                    html.td({"col_span": "6", "class_name": "py-6 text-center font-mono text-mono-sm text-light-outline"}, "No student records found.")
                                )
                            ]
                        )
                    )
                )
            ),

            # Real-Time Academic Audit Log (4 cols)
            html.article(
                {"class_name": "xl:col-span-4 bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
                html.header(
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Academic Audit Log"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Immutable institutional grade transactions")
                ),

                html.div(
                    {"class_name": "flex flex-col divide-y divide-light-outline-variant font-body text-body-sm max-h-[480px] overflow-y-auto"},
                    [
                        html.div(
                            {"key": str(a.get("id", idx)), "class_name": "py-3 flex flex-col gap-1"},
                            html.span({"class_name": "font-mono text-mono-sm text-light-primary font-bold"}, a.get("action_type", "GRADE_RECORD")),
                            html.p({"class_name": "font-mono text-mono-sm text-light-on-surface"}, a.get("description", "Action completed")),
                            html.span({"class_name": "font-mono text-[11px] text-light-on-surface-variant"}, str(a.get("timestamp", "")))
                        ) for idx, a in enumerate(audit_logs)
                    ] if audit_logs else [html.p({"class_name": "font-mono text-mono-sm text-light-outline py-2"}, "No audit logs recorded yet.")]
                )
            )
        ),

        # Modal: Atomic Grade Entry
        html.div(
            {
                "class_name": f"{'fixed' if upload_open else 'hidden'} inset-0 z-50 bg-light-on-surface/50 flex items-center justify-center p-gutter-lg"
            },
            html.article(
                {"class_name": "w-full max-w-lg bg-light-surface-container-lowest border-2 border-light-secondary p-gutter-xl flex flex-col gap-gutter-md shadow-2xl"},
                html.header(
                    {"class_name": "flex items-start justify-between border-b border-light-outline-variant pb-2"},
                    html.div(
                        html.h2({"class_name": "font-headline text-headline-md text-light-on-surface uppercase"}, "Enter Course Grade"),
                        html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Atomic recalculation of SGPA & CGPA")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_upload_open(False),
                            "class_name": "text-light-on-surface hover:text-light-primary cursor-pointer p-1"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[24px]"}, "close")
                    )
                ),

                html.form(
                    {"class_name": "flex flex-col gap-gutter-md", "on_submit": lambda e: None},
                    
                    html.div(
                        {"class_name": "grid grid-cols-2 gap-gutter-md"},
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Roll Number"),
                            html.input(
                                {
                                    "type": "text",
                                    "value": up_roll,
                                    "on_change": lambda e: set_up_roll(e.get("target", {}).get("value", "")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                }
                            )
                        ),
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Semester Number"),
                            html.input(
                                {
                                    "type": "number",
                                    "min": "1",
                                    "max": "8",
                                    "value": up_sem,
                                    "on_change": lambda e: set_up_sem(e.get("target", {}).get("value", "1")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                }
                            )
                        )
                    ),

                    html.div(
                        {"class_name": "grid grid-cols-2 gap-gutter-md"},
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Course Code"),
                            html.input(
                                {
                                    "type": "text",
                                    "value": up_code,
                                    "on_change": lambda e: set_up_code(e.get("target", {}).get("value", "")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                }
                            )
                        ),
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Course Title"),
                            html.input(
                                {
                                    "type": "text",
                                    "value": up_name,
                                    "on_change": lambda e: set_up_name(e.get("target", {}).get("value", "")),
                                    "class_name": "border border-light-outline-variant p-2 font-body text-body-md"
                                }
                            )
                        )
                    ),

                    html.div(
                        {"class_name": "grid grid-cols-3 gap-gutter-md"},
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Credits"),
                            html.input(
                                {
                                    "type": "number",
                                    "step": "0.5",
                                    "value": up_credits,
                                    "on_change": lambda e: set_up_credits(e.get("target", {}).get("value", "3")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                }
                            )
                        ),
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Letter Grade"),
                            html.select(
                                {
                                    "value": up_grade,
                                    "on_change": lambda e: set_up_grade(e.get("target", {}).get("value", "O")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                },
                                [html.option({"key": g, "value": g}, g) for g in ["O", "A+", "A", "B+", "B", "C", "U", "RA", "SA", "W"]]
                            )
                        ),
                        html.div(
                            {"class_name": "flex flex-col gap-1"},
                            html.label({"class_name": "font-mono text-mono-sm font-bold uppercase"}, "Grade Points"),
                            html.input(
                                {
                                    "type": "number",
                                    "step": "1",
                                    "value": up_gp,
                                    "on_change": lambda e: set_up_gp(e.get("target", {}).get("value", "10")),
                                    "class_name": "border border-light-outline-variant p-2 font-mono text-mono-md"
                                }
                            )
                        )
                    ),

                    html.div(
                        {"class_name": f"{'block' if up_msg else 'hidden'} p-2 bg-success text-on-success font-mono text-mono-sm"},
                        up_msg
                    ),
                    html.div(
                        {"class_name": f"{'block' if up_err else 'hidden'} p-2 bg-light-error text-light-on-error font-mono text-mono-sm"},
                        up_err
                    ),

                    html.div(
                        {"class_name": "flex items-center justify-end gap-gutter-sm mt-2"},
                        html.button(
                            {
                                "type": "button",
                                "on_click": lambda e: set_upload_open(False),
                                "class_name": "px-4 py-2 border border-light-outline-variant font-mono text-mono-sm uppercase hover:bg-light-surface-container cursor-pointer"
                            },
                            "Cancel"
                        ),
                        html.button(
                            {
                                "type": "button",
                                "on_click": lambda e: handle_upload(),
                                "class_name": "px-6 py-2 bg-light-primary text-light-on-primary font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container hover:text-light-on-primary-container cursor-pointer"
                            },
                            "Save Grade"
                        )
                    )
                )
            )
        ),

        # Modal: Bulk CSV Upload
        html.div(
            {
                "class_name": f"{'fixed' if csv_modal_open else 'hidden'} inset-0 z-50 bg-light-on-surface/50 flex items-center justify-center p-gutter-lg"
            },
            html.article(
                {"class_name": "w-full max-w-xl bg-light-surface-container-lowest border-2 border-light-secondary p-gutter-xl flex flex-col gap-gutter-md shadow-2xl"},
                html.header(
                    {"class_name": "flex items-start justify-between border-b border-light-outline-variant pb-2"},
                    html.div(
                        html.h2({"class_name": "font-headline text-headline-md text-light-on-surface uppercase"}, "Bulk CSV Grade Ingestion"),
                        html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Atomic batch ingestion with audit verification")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_csv_modal_open(False),
                            "class_name": "text-light-on-surface hover:text-light-primary cursor-pointer p-1"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[24px]"}, "close")
                    )
                ),

                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm"},
                    html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant"}, "Format: roll_number,semester,course_code,course_name,credits,grade,grade_point"),
                    html.textarea(
                        {
                            "rows": 8,
                            "value": csv_text,
                            "on_change": lambda e: set_csv_text(e.get("target", {}).get("value", "")),
                            "placeholder": "21CS042,6,CS3601,Compiler Design,4,O,10.0\n21CS019,6,CS3602,Distributed Systems,3,A+,9.0",
                            "class_name": "w-full border border-light-outline-variant p-2 font-mono text-mono-sm"
                        }
                    ),
                    html.div(
                        {"class_name": f"{'block' if csv_error else 'hidden'} p-2 bg-light-error text-light-on-error font-mono text-mono-sm"},
                        csv_error
                    ),
                    html.div(
                        {"class_name": f"{'block' if csv_summary else 'hidden'} p-2 bg-success text-on-success font-mono text-mono-sm"},
                        f"Processed {csv_summary.get('saved', 0)} grade records successfully." if csv_summary else ""
                    ),
                    html.div(
                        {"class_name": "flex items-center justify-between mt-2"},
                        html.a(
                            {
                                "href": "/api/admin/grades/sample-csv/",
                                "download": "sample_grades.csv",
                                "class_name": "font-mono text-mono-sm text-light-primary hover:underline uppercase"
                            },
                            "Download Sample CSV"
                        ),
                        html.div(
                            {"class_name": "flex items-center gap-gutter-sm"},
                            html.button(
                                {
                                    "type": "button",
                                    "on_click": lambda e: set_csv_modal_open(False),
                                    "class_name": "px-4 py-2 border border-light-outline-variant font-mono text-mono-sm uppercase hover:bg-light-surface-container cursor-pointer"
                                },
                                "Close"
                            ),
                            html.button(
                                {
                                    "type": "button",
                                    "on_click": handle_csv_submit,
                                    "class_name": "px-6 py-2 bg-light-primary text-light-on-primary font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container cursor-pointer"
                                },
                                "Upload CSV"
                            )
                        )
                    )
                )
            )
        )
    )
