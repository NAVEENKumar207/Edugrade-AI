"""
Transcripts & Results Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/transcripts_results/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import get_semester_results_data

@component
def ResultsPage(user):
    data, set_data = use_state(lambda: get_semester_results_data(user))
    selected_sem, set_selected_sem = use_state("all")
    search_query, set_search_query = use_state("")

    if not data:
        data = get_semester_results_data(user)

    semesters = data.get("semesters", [])
    cgpa = data.get("current_cgpa", 0.0)
    credits_earned = data.get("credits_earned", 0)
    total_credits = data.get("total_credits", 160) or 160

    # Calculate global grade counts across all semesters
    all_courses = []
    for s in semesters:
        all_courses.extend(s.get("courses", []))

    o_grades = sum(1 for c in all_courses if c.grade == 'O')
    arrears_count = sum(1 for c in all_courses if c.grade in ['U', 'RA', 'SA', 'W'])

    # Filter semesters
    filtered_sems = [
        s for s in semesters
        if selected_sem == "all" or str(s.get("semester_number")) == str(selected_sem)
    ]

    # Filter tabs
    sem_tab_buttons = [
        html.button(
            {
                "key": "all",
                "type": "button",
                "on_click": lambda e: set_selected_sem("all"),
                "class_name": "px-3 py-2 font-mono text-mono-sm uppercase whitespace-nowrap cursor-pointer transition-colors duration-state-change " +
                    ("bg-light-primary text-light-on-primary font-bold" if selected_sem == "all" else "bg-light-surface-container-lowest border border-light-outline-variant text-light-on-surface-variant hover:bg-light-surface-container-low")
            },
            "All Semesters"
        )
    ]

    for s in semesters:
        s_num = str(s.get("semester_number"))
        def make_tab_handler(sn):
            def handle_click(e):
                set_selected_sem(sn)
            return handle_click

        is_active = (selected_sem == s_num)
        sem_tab_buttons.append(
            html.button(
                {
                    "key": s_num,
                    "type": "button",
                    "on_click": make_tab_handler(s_num),
                    "class_name": "px-3 py-2 font-mono text-mono-sm uppercase whitespace-nowrap cursor-pointer transition-colors duration-state-change " +
                        ("bg-light-primary text-light-on-primary font-bold" if is_active else "bg-light-surface-container-lowest border border-light-outline-variant text-light-on-surface-variant hover:bg-light-surface-container-low")
                },
                f"Semester {s_num}"
            )
        )

    # Render semester transcript sections
    sem_sections = []
    q = search_query.strip().lower()

    for s in filtered_sems:
        courses = s.get("courses", [])
        matched_courses = [
            c for c in courses
            if not q or q in c.course_code.lower() or q in c.course_name.lower()
        ]

        if not matched_courses and q:
            continue

        course_rows = []
        for c in matched_courses:
            is_pass = c.grade not in ['U', 'RA', 'SA', 'W']
            is_o = c.grade == 'O'
            is_aplus = c.grade == 'A+'

            pill_cls = "bg-light-secondary text-light-on-secondary" if is_o else \
                       "bg-light-surface-container-highest text-light-on-surface" if is_pass else \
                       "bg-light-primary text-light-on-primary font-bold"

            course_rows.append(
                html.tr(
                    {"key": str(c.id), "class_name": "course-row hover:bg-light-surface-container-low transition-colors duration-state-change"},
                    html.td({"class_name": "py-3.5 px-gutter-lg font-mono text-mono-md text-light-primary font-bold"}, c.course_code),
                    html.td({"class_name": "py-3.5 px-gutter-md font-title text-title-md text-light-on-surface font-semibold"}, c.course_name),
                    html.td({"class_name": "py-3.5 px-gutter-md text-right font-mono text-mono-md tabular-nums"}, f"{c.credits:.1f}"),
                    html.td(
                        {"class_name": "py-3.5 px-gutter-md text-center"},
                        html.span({"class_name": f"px-2.5 py-0.5 rounded-full font-mono text-mono-sm font-bold {pill_cls}"}, c.grade)
                    ),
                    html.td({"class_name": "py-3.5 px-gutter-md text-right font-mono text-mono-md tabular-nums font-bold"}, f"{c.grade_point:.1f}"),
                    html.td(
                        {"class_name": "py-3.5 px-gutter-lg text-right"},
                        html.span(
                            {"class_name": f"font-label text-label-md font-bold {'text-light-secondary' if is_pass else 'text-light-primary'}"},
                            "Pass" if is_pass else "Arrear"
                        )
                    )
                )
            )

        sem_sections.append(
            html.article(
                {"key": str(s.get("semester_number")), "class_name": "bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden"},
                html.header(
                    {"class_name": "px-gutter-lg py-gutter-md bg-light-surface-container-low border-b border-light-outline-variant flex flex-wrap items-center justify-between gap-gutter-md"},
                    html.div(
                        html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, f"Semester {s.get('semester_number')} Record"),
                        html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"{len(courses)} Courses • {s.get('credits_earned', 0)} Credits Cleared")
                    ),
                    html.span(
                        {"class_name": "px-3 py-1.5 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-md tabular-nums whitespace-nowrap font-bold"},
                        f"SGPA: {s.get('sgpa', 0.0):.2f}"
                    )
                ),
                html.div(
                    {"class_name": "overflow-x-auto"},
                    html.table(
                        {"class_name": "w-full text-left border-collapse"},
                        html.thead(
                            html.tr(
                                {"class_name": "border-b border-light-outline-variant text-light-on-surface-variant font-label text-label-md bg-light-surface-container-lowest"},
                                html.th({"class_name": "py-3 px-gutter-lg"}, "Course Code"),
                                html.th({"class_name": "py-3 px-gutter-md"}, "Course Title"),
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "Credits"),
                                html.th({"class_name": "py-3 px-gutter-md text-center"}, "Letter Grade"),
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "Grade Points"),
                                html.th({"class_name": "py-3 px-gutter-lg text-right"}, "Status")
                            )
                        ),
                        html.tbody(
                            {"class_name": "divide-y divide-light-outline-variant font-body text-body-md"},
                            course_rows if course_rows else [
                                html.tr(
                                    html.td({"col_span": "6", "class_name": "py-6 text-center font-mono text-mono-sm text-light-outline"}, "No courses matched the filter.")
                                )
                            ]
                        )
                    )
                )
            )
        )

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header strip
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "Transcripts & Results"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"Student: {data.get('student_name', 'Student')} • Roll: {data.get('roll_number', '21CS001')} • Regulation: 2021 CBCS")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm flex-wrap"},
                html.span(
                    {"class_name": "inline-flex items-center gap-gutter-xs px-3 py-1.5 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm uppercase whitespace-nowrap"},
                    html.span({"class_name": "material-symbols-outlined text-[16px]"}, "verified"),
                    html.span("Official Record")
                ),
                html.a(
                    {
                        "href": "/api/transcript/pdf/",
                        "target": "_blank",
                        "rel": "noopener noreferrer",
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 bg-light-primary text-light-on-primary font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change whitespace-nowrap cursor-pointer"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "picture_as_pdf"),
                    html.span("Export Official PDF")
                )
            )
        ),

        # 4-Metric Transcript Summary Strip (Wastetide Bento)
        html.section(
            {"class_name": "grid grid-cols-2 xl:grid-cols-4 border border-light-outline-variant bg-light-surface-container-lowest"},
            html.article(
                {"class_name": "bg-light-primary-container text-light-on-primary-container p-gutter-md border-b xl:border-b-0 border-r border-light-outline-variant"},
                html.span({"class_name": "font-mono text-mono-sm uppercase font-bold"}, "01 / Cumulative CGPA"),
                html.p({"class_name": "font-headline text-headline-lg tabular-nums mt-1 font-bold"}, f"{cgpa:.2f}")
            ),
            html.article(
                {"class_name": "p-gutter-md border-b xl:border-b-0 xl:border-r border-light-outline-variant"},
                html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "02 / Credits Cleared"),
                html.p({"class_name": "font-headline text-headline-lg text-light-on-surface tabular-nums mt-1 font-bold"}, f"{credits_earned} / {total_credits}")
            ),
            html.article(
                {"class_name": "p-gutter-md border-r border-light-outline-variant"},
                html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase font-bold"}, "03 / O-Grades Earned"),
                html.p({"class_name": "font-headline text-headline-lg text-light-on-surface tabular-nums mt-1 font-bold"}, f"{o_grades} Courses")
            ),
            html.article(
                {"class_name": "bg-light-secondary text-light-on-secondary p-gutter-md"},
                html.span({"class_name": "font-mono text-mono-sm text-light-on-secondary/80 uppercase font-bold"}, "04 / Standing Arrears"),
                html.p({"class_name": "font-headline text-headline-lg tabular-nums mt-1 font-bold"}, f"{arrears_count} Active")
            )
        ),

        # Semester Filter & Course Search Bar
        html.section(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md"},
            html.div(
                {"class_name": "flex flex-wrap items-center gap-gutter-xs"},
                sem_tab_buttons
            ),
            html.div(
                {"class_name": "w-full sm:w-auto flex items-center border border-light-outline-variant bg-light-surface-container-lowest px-3 py-1.5"},
                html.span({"class_name": "material-symbols-outlined text-light-on-surface-variant text-[18px] mr-2"}, "search"),
                html.input(
                    {
                        "type": "search",
                        "placeholder": "Filter course code or title...",
                        "value": search_query,
                        "on_change": lambda e: set_search_query(e.get("target", {}).get("value", "")),
                        "class_name": "border-none bg-transparent p-0 font-mono text-mono-sm text-light-on-surface focus:outline-none focus:ring-0 w-full sm:w-64"
                    }
                )
            )
        ),

        # Semester Sections
        html.div(
            {"class_name": "flex flex-col gap-gutter-lg"},
            sem_sections if sem_sections else [
                html.div(
                    {"class_name": "p-12 text-center border border-light-outline-variant bg-light-surface-container-lowest"},
                    html.span({"class_name": "material-symbols-outlined text-[48px] text-light-outline"}, "description"),
                    html.p({"class_name": "font-headline text-title-lg text-light-on-surface mt-2"}, "No Transcript Records Found"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant mt-1"}, "Semester grade data will appear here once officially logged by faculty.")
                )
            ]
        )
    )
