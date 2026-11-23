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
                ("HS8151", "Communicative English", 3.0),
                ("MA8151", "Engineering Mathematics - I", 4.0),
                ("PH8151", "Engineering Physics", 3.0),
                ("CY8151", "Engineering Chemistry", 3.0),
                ("GE8151", "Problem Solving & Python Programming", 3.0),
                ("GE8161", "Python Programming Laboratory", 2.0),
                ("BS8161", "Physics & Chemistry Laboratory", 2.0),
            ]
        },
        {
            "sem": 2, "credits": 20,
            "courses": [
                ("HS8251", "Technical English", 3.0),
                ("MA8251", "Engineering Mathematics - II", 4.0),
                ("PH8252", "Physics for Information Science", 3.0),
                ("BE8255", "Basic Electrical & Electronics Engineering", 3.0),
                ("GE8292", "Engineering Graphics", 4.0),
                ("CS8261", "C Programming Laboratory", 2.0),
            ]
        },
        {
            "sem": 3, "credits": 19,
            "courses": [
                ("MA8351", "Discrete Mathematics", 4.0),
                ("CS8351", "Digital Principles & System Design", 4.0),
                ("CS8391", "Data Structures", 3.0),
                ("CS8392", "Object Oriented Programming", 3.0),
                ("EC8395", "Communication Engineering", 3.0),
                ("CS8381", "Data Structures Laboratory", 2.0),
            ]
        },
        {
            "sem": 4, "credits": 21,
            "courses": [
                ("MA8402", "Probability & Queueing Theory", 4.0),
                ("CS8491", "Design & Analysis of Algorithms", 4.0),
                ("CS8492", "Database Management Systems", 3.0),
                ("CS8451", "Operating Systems", 3.0),
                ("CS8461", "Operating Systems Laboratory", 2.0),
                ("CS8481", "Database Management Systems Laboratory", 2.0),
                ("GE8291", "Environmental Science & Engineering", 3.0),
            ]
        },
        {
            "sem": 5, "credits": 23,
            "courses": [
                ("MA8551", "Algebra and Number Theory", 4.0),
                ("CS8591", "Computer Networks", 3.0),
                ("EC8691", "Microprocessors and Microcontrollers", 3.0),
                ("CS8501", "Theory of Computation", 3.0),
                ("CS8592", "Object Oriented Analysis and Design", 3.0),
                ("EC8681", "Microprocessors and Microcontrollers Lab", 2.0),
                ("CS8581", "Networks Laboratory", 2.0),
                ("CS8582", "Object Oriented Analysis & Design Lab", 2.0),
            ]
        },
        {
            "sem": 6, "credits": 24,
            "courses": [
                ("CS8651", "Internet Programming", 3.0),
                ("CS8691", "Artificial Intelligence", 3.0),
                ("CS8601", "Mobile Computing", 3.0),
                ("CS8602", "Compiler Design", 4.0),
                ("CS8603", "Distributed Systems", 3.0),
                ("CS8661", "Internet Programming Laboratory", 2.0),
                ("CS8662", "Mobile Application Development Lab", 2.0),
                ("CS8611", "Mini Project", 2.0),
            ]
        },
        {
            "sem": 7, "credits": 20,
            "courses": [
                ("MG8591", "Principles of Management", 3.0),
                ("CS8792", "Cryptography & Network Security", 3.0),
                ("CS8791", "Cloud Computing", 3.0),
                ("PE8701", "Professional Elective II", 3.0),
                ("PE8702", "Professional Elective III", 3.0),
                ("OE8701", "Open Elective II", 3.0),
                ("CS8711", "Cloud & Security Laboratory", 2.0),
            ]
        },
        {
            "sem": 8, "credits": 13,
            "courses": [
                ("PE8801", "Professional Elective IV", 3.0),
                ("PE8802", "Professional Elective V", 3.0),
                ("CS8811", "Project Work", 7.0),
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
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase mt-1"}, "UGC 10-Point CBCS Scale • Degree Classifications • B.E. Syllabus")
            ),
            html.span({"class_name": "font-mono text-mono-sm font-bold bg-light-surface-container-highest text-light-on-surface px-3 py-1 border border-light-outline-variant"}, "REGULATION 2021 CBCS")
        ),

        # Top 2-Column: 10-Point Scale & Degree Classification
        html.div(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-start"},
            
            # UGC CBCS Scale (7 cols)
            html.article(
                {"class_name": "xl:col-span-7 bg-light-surface-container-lowest border border-light-outline-variant overflow-hidden"},
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
                    html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase"}, f"B.E. CSE Curriculum — Semester {selected_sem}"),
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
