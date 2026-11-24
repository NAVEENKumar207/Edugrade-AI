"""
Academic Regulations & Curriculum Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/curriculum_regulations/code.html.
"""

from reactpy import component, html, use_state

@component
def RegulationsPage():
    selected_sem, set_selected_sem = use_state(1)

    grade_scale = [
        {"grade": "O", "points": "10.0", "meaning": "Outstanding", "range": "91 – 100", "badge_cls": "bg-light-secondary text-light-on-secondary"},
        {"grade": "A+", "points": "9.0", "meaning": "Excellent", "range": "81 – 90", "badge_cls": "bg-light-surface-container-high text-light-on-surface"},
        {"grade": "A", "points": "8.0", "meaning": "Very Good", "range": "71 – 80", "badge_cls": "bg-light-surface-container-high text-light-on-surface"},
        {"grade": "B+", "points": "7.0", "meaning": "Good", "range": "61 – 70", "badge_cls": "bg-light-surface-container-high text-light-on-surface"},
        {"grade": "B", "points": "6.0", "meaning": "Average", "range": "51 – 60", "badge_cls": "bg-light-surface-container-high text-light-on-surface"},
        {"grade": "C", "points": "5.0", "meaning": "Satisfactory (Pass)", "range": "50", "badge_cls": "bg-light-surface-container-high text-light-on-surface"},
        {"grade": "U / RA", "points": "0.0", "meaning": "Re-appear / Standing Arrear", "range": "< 50", "badge_cls": "bg-light-primary text-light-on-primary font-bold"},
        {"grade": "SA", "points": "0.0", "meaning": "Shortage of Attendance", "range": "—", "badge_cls": "bg-light-error text-light-on-error font-bold"},
        {"grade": "W", "points": "0.0", "meaning": "Withdrawal from Exam", "range": "—", "badge_cls": "bg-light-surface-container-high text-light-outline"}
    ]

    classifications = [
        {"title": "First Class with Distinction", "cutoff": "CGPA ≥ 8.50", "criteria": "Zero active or cleared arrears in academic history; degree completed within minimum specified period (4 years / 8 semesters).", "badge_cls": "bg-light-primary text-light-on-primary font-bold"},
        {"title": "First Class", "cutoff": "CGPA ≥ 6.50", "criteria": "Eligible for students completing degree within maximum allowable time (up to 5 years).", "badge_cls": "bg-light-secondary text-light-on-secondary font-bold"},
        {"title": "Second Class", "cutoff": "CGPA ≥ 5.00", "criteria": "Minimum passing threshold for degree conferral under CBCS UGC guidelines.", "badge_cls": "bg-light-surface-container-high text-light-on-surface"}
    ]

    semester_curriculum = [
        {
            "sem": 1, "credits": 20,
            "courses": [
                ("60 EN 003", "Business Communication and Value Science I", 2.0),
                ("60 MA 002", "Statistics and Probability", 4.0),
                ("61 PH 008", "Fundamentals of Physics", 3.0),
                ("61 CB 101", "Computer Programming (Python)", 3.0),
                ("60 EE 003", "Principles of Electrical Engineering and Lab", 4.0),
                ("60 CB 1P1", "Computer Programming Lab (Python)", 2.0),
                ("60 PH 0P3", "Fundamentals of Physics Lab", 2.0),
            ]
        },
        {
            "sem": 2, "credits": 20,
            "courses": [
                ("60 EN 004", "Business Communication and Value Science II", 2.0),
                ("60 HS 001", "Fundamentals of Economics", 3.0),
                ("60 MA 005", "Statistical Modeling", 5.0),
                ("60 CB 201", "Computer Organization and Architecture", 3.0),
                ("61 CB 202", "Object Oriented Programming", 3.0),
                ("60 ME 0P1", "Fabrication and Reverse Engineering Laboratory", 2.0),
                ("61 CB 2P1", "Object Oriented Programming Lab", 2.0),
            ]
        },
        {
            "sem": 3, "credits": 24,
            "courses": [
                ("60 HS 004", "Introduction to Innovation, IP Management & Entrepreneurship", 3.0),
                ("60 MA 013", "Computational Statistics", 4.0),
                ("61 CB 301", "Automata and Compiler Design", 4.0),
                ("60 CB 302", "Database Management Systems", 3.0),
                ("60 CB 303", "Data Structures", 3.0),
                ("60 CB 304", "Software Engineering", 3.0),
                ("60 CB 3P1", "Database Management Systems Lab", 2.0),
                ("60 CB 3P2", "Data Structures Lab", 2.0),
            ]
        },
        {
            "sem": 4, "credits": 23,
            "courses": [
                ("60 MA 018", "Optimization Techniques", 4.0),
                ("60 CB 401", "Operating Systems", 3.0),
                ("60 CB 402", "Design and Analysis of Algorithms", 3.0),
                ("60 CB 403", "Software Design with UML", 3.0),
                ("60 CB 404", "MERN Stack", 3.0),
                ("60 OE L01", "Open Elective-I", 3.0),
                ("60 CB 4P1", "Operating Systems Lab", 2.0),
                ("60 CB 4P2", "Design and Analysis of Algorithms Lab", 2.0),
            ]
        },
        {
            "sem": 5, "credits": 22,
            "courses": [
                ("60 CB 501", "Computer Networks", 3.0),
                ("60 CB 502", "C# and .NET Programming", 3.0),
                ("60 CB 503", "Artificial Intelligence", 3.0),
                ("60 IT 003", "Design Thinking", 3.0),
                ("60 CB E11", "Professional Elective I: Modern Software Engineering", 3.0),
                ("60 OE L02", "Open Elective-II", 3.0),
                ("60 CB 5P1", "Computer Networks Laboratory", 2.0),
                ("60 CB 5P2", "C# and .NET Programming Laboratory", 2.0),
            ]
        },
        {
            "sem": 6, "credits": 22,
            "courses": [
                ("60 HS 005", "Business Strategy", 3.0),
                ("60 HS 006", "Financial and Cost Accounting", 3.0),
                ("60 CB 601", "Machine Learning", 3.0),
                ("60 CB 602", "Usability Design of Software Applications", 3.0),
                ("60 CB E21", "Professional Elective II: Marketing Research", 3.0),
                ("60 OE L03", "Open Elective-III", 3.0),
                ("60 CB 6P1", "Machine Learning Laboratory", 2.0),
                ("60 CB 6P2", "Usability Design Laboratory", 2.0),
            ]
        },
        {
            "sem": 7, "credits": 22,
            "courses": [
                ("60 HS 007", "Human Resource Management", 3.0),
                ("60 CB 701", "Cloud Application Development", 3.0),
                ("60 CB 702", "Data Analytics", 3.0),
                ("60 CB 703", "Software Testing and Automation", 3.0),
                ("60 CB E31", "Professional Elective III", 3.0),
                ("60 CB E41", "Professional Elective IV", 3.0),
                ("60 CB 7P1", "Data Analytics Laboratory", 2.0),
                ("60 CB 7P2", "Project Work Phase-I", 2.0),
            ]
        },
        {
            "sem": 8, "credits": 11,
            "courses": [
                ("60 CB E51", "Professional Elective V: Exploratory Data Analysis", 3.0),
                ("60 CB 8P1", "Project Work Phase-II", 8.0),
            ]
        }
    ]

    active_sem_data = next((s for s in semester_curriculum if s["sem"] == selected_sem), semester_curriculum[0])

    sem_selector_buttons = []
    for s_item in semester_curriculum:
        sn = s_item["sem"]
        def make_sem_click(sem_val):
            def handle_click(e):
                set_selected_sem(sem_val)
            return handle_click

        is_act = (selected_sem == sn)
        sem_selector_buttons.append(
            html.button(
                {
                    "key": str(sn),
                    "type": "button",
                    "data-demo": f"curriculum-tab-{sn}",
                    "id": f"curriculum-tab-{sn}",
                    "on_click": make_sem_click(sn),
                    "class_name": "px-3 py-2 font-mono text-mono-sm uppercase whitespace-nowrap cursor-pointer transition-colors duration-state-change " +
                        ("bg-light-primary text-light-on-primary font-bold" if is_act else "bg-light-surface-container-lowest border border-light-outline-variant text-light-on-surface-variant hover:bg-light-surface-container-low")
                },
                f"Sem {sn}"
            )
        )

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto text-light-on-surface"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight font-bold"}, "Curriculum & Academic Regulations"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase mt-1"}, "UGC 10-Point CBCS Scale • Degree Classifications • B.Tech CSBS Syllabus")
            ),
            html.span({"class_name": "font-mono text-mono-sm font-bold bg-light-surface-container-highest text-light-on-surface px-3 py-1 border border-light-outline-variant"}, "REGULATION 2022 (2024-2028)")
        ),

        # Top 2-Column: 10-Point Scale & Degree Classification
        html.div(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-start"},
            
            # UGC CBCS Scale (7 cols)
            html.article(
                {
                    "class_name": "xl:col-span-7 bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden",
                    "data-demo": "regulations-grade-table",
                    "id": "regulations-grade-table"
                },
                html.header(
                    {"class_name": "px-gutter-lg py-gutter-md bg-light-surface-container-low border-b border-light-outline-variant"},
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "UGC 10-Point CBCS Grade Scale"),
                    html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Deterministic Grade Point to Mark Mapping")
                ),

                html.div(
                    {"class_name": "overflow-x-auto"},
                    html.table(
                        {"class_name": "w-full text-left border-collapse"},
                        html.thead(
                            html.tr(
                                {"class_name": "border-b border-light-outline-variant text-light-on-surface-variant font-label text-label-md bg-light-surface-container-lowest"},
                                html.th({"class_name": "py-3 px-gutter-lg"}, "Grade"),
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "Points"),
                                html.th({"class_name": "py-3 px-gutter-md"}, "Mark Range"),
                                html.th({"class_name": "py-3 px-gutter-lg"}, "Academic Meaning")
                            )
                        ),
                        html.tbody(
                            {"class_name": "divide-y divide-light-outline-variant font-body text-body-md"},
                            [
                                html.tr(
                                    {"key": g["grade"], "class_name": "hover:bg-light-surface-container-low transition-colors duration-state-change"},
                                    html.td(
                                        {"class_name": "py-3 px-gutter-lg"},
                                        html.span({"class_name": f"px-2.5 py-0.5 rounded-full font-mono text-mono-sm font-bold {g['badge_cls']}"}, g["grade"])
                                    ),
                                    html.td({"class_name": "py-3 px-gutter-md text-right font-mono text-mono-md font-bold tabular-nums"}, g["points"]),
                                    html.td({"class_name": "py-3 px-gutter-md font-mono text-mono-sm text-light-on-surface-variant"}, g["range"]),
                                    html.td({"class_name": "py-3 px-gutter-lg font-mono text-mono-sm text-light-on-surface font-semibold"}, g["meaning"])
                                ) for g in grade_scale
                            ]
                        )
                    )
                )
            ),

            # Degree Classification Criteria (5 cols)
            html.article(
                {"class_name": "xl:col-span-5 bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
                html.header(
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, "Degree Classification Rules"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, "Statutory graduation classification standards")
                ),

                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm"},
                    [
                        html.div(
                            {"key": cl["title"], "class_name": "p-gutter-md bg-light-surface-container-low border border-light-outline-variant flex flex-col gap-1"},
                            html.div(
                                {"class_name": "flex items-center justify-between"},
                                html.h3({"class_name": "font-headline text-title-md text-light-on-surface uppercase font-bold"}, cl["title"]),
                                html.span({"class_name": f"px-2.5 py-0.5 rounded-full font-mono text-mono-sm {cl['badge_cls']}"}, cl["cutoff"])
                            ),
                            html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant mt-1"}, cl["criteria"])
                        ) for cl in classifications
                    ]
                )
            )
        ),

        # Bottom: Semester Curriculum Explorer
        html.article(
            {"class_name": "bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden"},
            html.header(
                {"class_name": "px-gutter-lg py-gutter-md bg-light-surface-container-low border-b border-light-outline-variant flex flex-wrap items-center justify-between gap-gutter-md"},
                html.div(
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, f"B.Tech CSBS Curriculum — Semester {selected_sem}"),
                    html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"{len(active_sem_data['courses'])} Prescribed Courses • {active_sem_data['credits']} Credits")
                ),
                html.div({"class_name": "flex flex-wrap items-center gap-gutter-xs"}, sem_selector_buttons)
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
                            html.th({"class_name": "py-3 px-gutter-lg text-right"}, "Credits")
                        )
                    ),
                    html.tbody(
                        {"class_name": "divide-y divide-light-outline-variant font-body text-body-md"},
                        [
                            html.tr(
                                {"key": code, "class_name": "hover:bg-light-surface-container-low transition-colors duration-state-change"},
                                html.td({"class_name": "py-3 px-gutter-lg font-mono text-mono-md text-light-primary font-bold"}, code),
                                html.td({"class_name": "py-3 px-gutter-md font-title text-title-md text-light-on-surface font-semibold"}, title),
                                html.td({"class_name": "py-3 px-gutter-lg text-right font-mono text-mono-md font-bold tabular-nums"}, f"{cr:.1f}")
                            ) for code, title, cr in active_sem_data["courses"]
                        ]
                    )
                )
            )
        )
    )
