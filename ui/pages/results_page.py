"""
Transcripts & Results Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/transcripts_results/code.html with full student-owned CRUD and CSV import.
"""

from reactpy import component, html, use_state
from ui.services.data_service import (
    get_semester_results_data,
    save_student_course_result,
    update_student_course_result,
    delete_student_course_result,
    import_student_grades_csv,
)

GRADE_CHOICES = ["O", "A+", "A", "B+", "B", "C", "U", "RA"]


@component
def ResultsPage(user):
    data, set_data = use_state(lambda: get_semester_results_data(user))
    selected_sem, set_selected_sem = use_state("all")
    search_query, set_search_query = use_state("")

    # Student-Owned CRUD State
    show_form, set_show_form = use_state(False)
    show_csv_modal, set_show_csv_modal = use_state(False)
    editing_id, set_editing_id = use_state(None)

    form_sem, set_form_sem = use_state("1")
    form_code, set_form_code = use_state("")
    form_name, set_form_name = use_state("")
    form_credits, set_form_credits = use_state("3")
    form_grade, set_form_grade = use_state("A")
    form_status, set_form_status = use_state("")
    form_error, set_form_error = use_state("")

    # CSV Import State
    csv_text, set_csv_text = use_state("")
    csv_res, set_csv_res = use_state(None)
    csv_error, set_csv_error = use_state("")
    csv_loading, set_csv_loading = use_state(False)

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

    def refresh_data():
        fresh = get_semester_results_data(user)
        set_data(fresh)

    def handle_reset_form():
        set_editing_id(None)
        set_form_sem("1")
        set_form_code("")
        set_form_name("")
        set_form_credits("3")
        set_form_grade("A")
        set_form_status("")
        set_form_error("")
        set_show_form(False)

    def handle_open_add():
        set_editing_id(None)
        set_form_sem(str(selected_sem) if selected_sem != "all" else "1")
        set_form_code("")
        set_form_name("")
        set_form_credits("3")
        set_form_grade("A")
        set_form_status("")
        set_form_error("")
        set_show_form(True)

    def handle_start_edit(course):
        set_editing_id(course.id)
        set_form_sem(str(course.semester_number))
        set_form_code(course.course_code)
        set_form_name(course.course_name)
        set_form_credits(str(int(course.credits)))
        set_form_grade(course.grade)
        set_form_status("")
        set_form_error("")
        set_show_form(True)

    def handle_save_result(e=None):
        set_form_status("")
        set_form_error("")

        c_code = form_code.strip()
        c_name = form_name.strip()
        if not c_code or not c_name:
            set_form_error("Course Code and Course Title are required.")
            return

        try:
            sem_int = int(form_sem)
            if not (1 <= sem_int <= 8):
                set_form_error("Semester must be between 1 and 8.")
                return
        except ValueError:
            set_form_error("Semester must be a valid number.")
            return

        try:
            cr_int = int(form_credits)
            if not (1 <= cr_int <= 10):
                set_form_error("Credits must be between 1 and 10.")
                return
        except ValueError:
            set_form_error("Credits must be a valid integer.")
            return

        if editing_id:
            ok, msg = update_student_course_result(
                user=user,
                course_id=editing_id,
                semester_number=sem_int,
                course_code=c_code,
                course_name=c_name,
                credits=cr_int,
                grade=form_grade
            )
        else:
            ok, msg = save_student_course_result(
                user=user,
                semester_number=sem_int,
                course_code=c_code,
                course_name=c_name,
                credits=cr_int,
                grade=form_grade
            )

        if ok:
            set_form_status(msg)
            refresh_data()
            if not editing_id:
                set_form_code("")
                set_form_name("")
        else:
            set_form_error(msg)

    def handle_delete_course(course_id):
        ok, msg = delete_student_course_result(user, course_id)
        if ok:
            refresh_data()

    def handle_run_csv_import(e=None):
        set_csv_error("")
        set_csv_res(None)
        txt = csv_text.strip()
        if not txt:
            set_csv_error("Please paste CSV grade records or load file content.")
            return

        set_csv_loading(True)
        try:
            res = import_student_grades_csv(user, txt)
            set_csv_res(res)
            if res.get("imported_count", 0) > 0:
                refresh_data()
        except Exception as err:
            set_csv_error(f"Import failed: {str(err)}")
        finally:
            set_csv_loading(False)

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

            pill_cls = "bg-light-secondary text-light-on-secondary" if is_o else \
                       "bg-light-surface-container-highest text-light-on-surface" if is_pass else \
                       "bg-light-primary text-light-on-primary font-bold"

            course_obj = c
            course_id = c.id

            course_rows.append(
                html.tr(
                    {"key": str(c.id), "class_name": "course-row hover:bg-light-surface-container-low transition-colors duration-state-change"},
                    html.td({"class_name": "py-3.5 px-gutter-lg font-mono text-mono-md text-light-primary font-bold"}, c.course_code),
                    html.td(
                        {"class_name": "py-3.5 px-gutter-md font-title text-title-md text-light-on-surface font-semibold"},
                        html.div(
                            {"class_name": "flex flex-col gap-0.5"},
                            html.span(c.course_name),
                            html.span(
                                {"class_name": "text-[11px] font-mono text-emerald-600 dark:text-emerald-400 font-bold uppercase"},
                                f"✓ Arrear Cleared (Previous: {c.previous_grade})"
                            ) if getattr(c, 'arrear_cleared', False) else None
                        )
                    ),
                    html.td({"class_name": "py-3.5 px-gutter-md text-right font-mono text-mono-md tabular-nums"}, f"{c.credits:.1f}"),
                    html.td(
                        {"class_name": "py-3.5 px-gutter-md text-center"},
                        html.span({"class_name": f"px-2.5 py-0.5 rounded-full font-mono text-mono-sm font-bold {pill_cls}"}, c.grade)
                    ),
                    html.td({"class_name": "py-3.5 px-gutter-md text-right font-mono text-mono-md tabular-nums font-bold"}, f"{c.grade_point:.1f}"),
                    html.td(
                        {"class_name": "py-3.5 px-gutter-md text-right"},
                        html.span(
                            {"class_name": f"font-label text-label-md font-bold {'text-light-secondary' if is_pass else 'text-light-primary'}"},
                            "Pass" if is_pass else "Arrear"
                        )
                    ),
                    # Action buttons for edit / delete
                    html.td(
                        {"class_name": "py-3.5 px-gutter-lg text-right font-mono"},
                        html.div(
                            {"class_name": "inline-flex items-center gap-2"},
                            html.button(
                                {
                                    "type": "button",
                                    "title": "Edit Course Result",
                                    "on_click": (lambda cur_c=course_obj: lambda e: handle_start_edit(cur_c))(),
                                    "class_name": "p-1.5 text-light-on-surface-variant hover:text-light-primary hover:bg-light-surface-container-high transition-colors cursor-pointer"
                                },
                                html.span({"class_name": "material-symbols-outlined text-[17px]"}, "edit")
                            ),
                            html.button(
                                {
                                    "type": "button",
                                    "title": "Delete Course Result",
                                    "on_click": (lambda cid=course_id: lambda e: handle_delete_course(cid))(),
                                    "class_name": "p-1.5 text-light-on-surface-variant hover:text-light-error hover:bg-light-surface-container-high transition-colors cursor-pointer"
                                },
                                html.span({"class_name": "material-symbols-outlined text-[17px]"}, "delete")
                            )
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
                                html.th({"class_name": "py-3 px-gutter-md text-right"}, "Status"),
                                html.th({"class_name": "py-3 px-gutter-lg text-right"}, "Actions")
                            )
                        ),
                        html.tbody(
                            {"class_name": "divide-y divide-light-outline-variant font-body text-body-md"},
                            course_rows if course_rows else [
                                html.tr(
                                    html.td({"col_span": "7", "class_name": "py-6 text-center font-mono text-mono-sm text-light-outline"}, "No courses matched the filter.")
                                )
                            ]
                        )
                    )
                )
            )
        )

    input_style = {"backgroundColor": "var(--bg-input)", "color": "var(--text-primary)"}
    input_class = "w-full bg-light-surface border border-light-outline-variant focus:border-light-primary focus:ring-0 p-2 font-mono text-mono-sm text-light-on-surface outline-none transition-colors"

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header strip
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "Transcripts & Results"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"Student: {data.get('student_name', 'Student')} • Roll: {data.get('roll_number', '21CS001')} • Self-Reported Academic Ledger")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm flex-wrap"},
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: (handle_reset_form() if show_form else handle_open_add()),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 bg-light-primary text-light-on-primary font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change whitespace-nowrap cursor-pointer shadow-sm"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "close" if show_form else "add_circle"),
                    html.span("Close Form" if show_form else "+ Add Result")
                ),
                html.button(
                    {
                        "type": "button",
                        "on_click": lambda e: set_show_csv_modal(not show_csv_modal),
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 border-2 border-light-outline-variant text-light-on-surface font-mono text-mono-sm font-bold uppercase hover:bg-light-surface-container-high transition-colors whitespace-nowrap cursor-pointer"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "upload_file"),
                    html.span("Import CSV")
                ),
                html.a(
                    {
                        "href": "/api/transcript/pdf/",
                        "target": "_blank",
                        "rel": "noopener noreferrer",
                        "class_name": "inline-flex items-center gap-2 px-gutter-md py-2 bg-light-secondary text-light-on-secondary font-mono text-mono-sm font-bold uppercase hover:opacity-90 transition-opacity whitespace-nowrap cursor-pointer"
                    },
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "picture_as_pdf"),
                    html.span("Export Official PDF")
                )
            )
        ),

        # Add / Edit Result Interactive Form Section
        (
            html.section(
                {"class_name": "border-2 border-light-primary bg-light-surface-container-lowest p-gutter-lg flex flex-col gap-4 shadow-sm"},
                html.div(
                    {"class_name": "flex items-center justify-between border-b border-light-outline-variant pb-3"},
                    html.div(
                        {"class_name": "flex items-center gap-2"},
                        html.span({"class_name": "material-symbols-outlined text-light-primary text-[22px]"}, "edit_note" if editing_id else "add_box"),
                        html.h3({"class_name": "font-headline text-title-md font-bold uppercase text-light-on-surface"}, "Edit Course Record" if editing_id else "Add New Course Result")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: handle_reset_form(),
                            "class_name": "text-light-on-surface-variant hover:text-light-on-surface cursor-pointer p-1"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[20px]"}, "close")
                    )
                ),
                # Feedback Banners
                html.div(
                    {"class_name": f"{'flex items-center gap-2' if form_status else 'hidden'} p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500 text-emerald-700 dark:text-emerald-300 font-mono text-mono-sm font-semibold"},
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "check_circle"),
                    form_status
                ),
                html.div(
                    {"class_name": f"{'flex items-center gap-2' if form_error else 'hidden'} p-3 bg-red-50 dark:bg-red-950/40 border border-light-error text-light-error font-mono text-mono-sm font-semibold"},
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "warning"),
                    form_error
                ),
                # Form Grid
                html.div(
                    {"class_name": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4"},
                    # Semester
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-xs font-bold uppercase text-light-on-surface-variant"}, "Semester (1-8)"),
                        html.select(
                            {
                                "value": form_sem,
                                "on_change": lambda e: set_form_sem(e.get("target", {}).get("value", "1")),
                                "class_name": input_class,
                                "style": input_style
                            },
                            [html.option({"key": str(i), "value": str(i)}, f"Semester {i}") for i in range(1, 9)]
                        )
                    ),
                    # Course Code
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-xs font-bold uppercase text-light-on-surface-variant"}, "Course Code"),
                        html.input(
                            {
                                "type": "text",
                                "placeholder": "e.g. CS301",
                                "value": form_code,
                                "on_change": lambda e: set_form_code(e.get("target", {}).get("value", "")),
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),
                    # Course Title
                    html.div(
                        {"class_name": "flex flex-col gap-1 sm:col-span-2 lg:col-span-2"},
                        html.label({"class_name": "font-mono text-mono-xs font-bold uppercase text-light-on-surface-variant"}, "Course Title"),
                        html.input(
                            {
                                "type": "text",
                                "placeholder": "e.g. Design and Analysis of Algorithms",
                                "value": form_name,
                                "on_change": lambda e: set_form_name(e.get("target", {}).get("value", "")),
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),
                    # Credits
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.label({"class_name": "font-mono text-mono-xs font-bold uppercase text-light-on-surface-variant"}, "Credits (1-10)"),
                        html.input(
                            {
                                "type": "number",
                                "min": "1",
                                "max": "10",
                                "value": form_credits,
                                "on_change": lambda e: set_form_credits(e.get("target", {}).get("value", "3")),
                                "class_name": input_class,
                                "style": input_style
                            }
                        )
                    ),
                    # Letter Grade
                    html.div(
                        {"class_name": "flex flex-col gap-1 sm:col-span-2 lg:col-span-1"},
                        html.label({"class_name": "font-mono text-mono-xs font-bold uppercase text-light-on-surface-variant"}, "Letter Grade"),
                        html.select(
                            {
                                "value": form_grade,
                                "on_change": lambda e: set_form_grade(e.get("target", {}).get("value", "A")),
                                "class_name": input_class,
                                "style": input_style
                            },
                            [html.option({"key": g, "value": g}, f"{g} ({'10' if g=='O' else '9' if g=='A+' else '8' if g=='A' else '7' if g=='B+' else '6' if g=='B' else '5' if g=='C' else '0'})") for g in GRADE_CHOICES]
                        )
                    )
                ),
                html.div(
                    {"class_name": "flex items-center gap-3 pt-2"},
                    html.button(
                        {
                            "type": "button",
                            "on_click": handle_save_result,
                            "class_name": "px-6 py-2.5 bg-light-primary text-white font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container transition-colors cursor-pointer shadow-sm flex items-center gap-2"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[18px]"}, "save"),
                        html.span("Update Course Result" if editing_id else "Save Course Result")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: handle_reset_form(),
                            "class_name": "px-4 py-2.5 border border-light-outline-variant font-mono text-mono-sm uppercase text-light-on-surface hover:bg-light-surface-container transition-colors cursor-pointer"
                        },
                        "Cancel"
                    )
                )
            )
            if show_form else None
        ),

        # CSV Import Section / Modal
        (
            html.section(
                {"class_name": "border-2 border-light-secondary bg-light-surface-container-lowest p-gutter-lg flex flex-col gap-4 shadow-sm"},
                html.div(
                    {"class_name": "flex items-center justify-between border-b border-light-outline-variant pb-3"},
                    html.div(
                        {"class_name": "flex items-center gap-2"},
                        html.span({"class_name": "material-symbols-outlined text-light-secondary text-[22px]"}, "upload_file"),
                        html.h3({"class_name": "font-headline text-title-md font-bold uppercase text-light-on-surface"}, "Bulk Import Grades via CSV")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_show_csv_modal(False),
                            "class_name": "text-light-on-surface-variant hover:text-light-on-surface cursor-pointer p-1"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[20px]"}, "close")
                    )
                ),
                html.div(
                    {"class_name": "flex flex-wrap items-center justify-between gap-2 font-mono text-mono-xs text-light-on-surface-variant uppercase"},
                    html.span("Format: semester,course_code,course_name,credits,grade"),
                    html.a(
                        {
                            "href": "/api/academics/results/sample-csv/",
                            "download": "edugrade_sample_grades.csv",
                            "class_name": "text-light-primary font-bold hover:underline flex items-center gap-1"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[15px]"}, "download"),
                        "Download Sample CSV Template"
                    )
                ),
                # CSV Textarea
                html.textarea(
                    {
                        "rows": "6",
                        "value": csv_text,
                        "on_change": lambda e: set_csv_text(e.get("target", {}).get("value", "")),
                        "placeholder": "semester,course_code,course_name,credits,grade\n1,CS101,Programming in Python,4,A+\n1,MA101,Matrices and Calculus,4,A\n2,CS201,Data Structures,4,O\n2,MA201,Discrete Mathematics,4,B+",
                        "class_name": "w-full font-mono text-mono-sm p-3 bg-light-surface border border-light-outline-variant text-light-on-surface focus:border-light-primary focus:ring-0 outline-none",
                        "style": input_style
                    }
                ),
                # CSV Result and Error alerts
                html.div(
                    {"class_name": f"{'flex flex-col gap-1' if csv_res else 'hidden'} p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-500 text-emerald-800 dark:text-emerald-200 font-mono text-mono-sm"},
                    html.div(
                        {"class_name": "font-bold flex items-center gap-2"},
                        html.span({"class_name": "material-symbols-outlined text-[18px]"}, "task_alt"),
                        f"Import Completed: {csv_res.get('imported_count', 0)} courses saved, {csv_res.get('cleared_arrears_count', 0)} arrears cleared." if csv_res else ""
                    ),
                    html.div(
                        {"class_name": "text-[11px] text-red-600 dark:text-red-400 mt-1"},
                        [html.p({"key": str(idx)}, f"• {err}") for idx, err in enumerate(csv_res.get("errors", []))]
                    ) if csv_res and csv_res.get("errors") else None
                ),
                html.div(
                    {"class_name": f"{'flex items-center gap-2' if csv_error else 'hidden'} p-3 bg-red-50 dark:bg-red-950/40 border border-light-error text-light-error font-mono text-mono-sm font-semibold"},
                    html.span({"class_name": "material-symbols-outlined text-[18px]"}, "warning"),
                    csv_error
                ),
                # Buttons
                html.div(
                    {"class_name": "flex items-center gap-3 pt-1"},
                    html.button(
                        {
                            "type": "button",
                            "disabled": csv_loading,
                            "on_click": handle_run_csv_import,
                            "class_name": "px-6 py-2.5 bg-light-secondary text-light-on-secondary font-mono text-mono-sm font-bold uppercase hover:bg-light-primary hover:text-white transition-colors cursor-pointer shadow-sm flex items-center gap-2 disabled:opacity-50"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[18px]"}, "upload"),
                        html.span("Processing..." if csv_loading else "Process CSV Import")
                    ),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: set_show_csv_modal(False),
                            "class_name": "px-4 py-2.5 border border-light-outline-variant font-mono text-mono-sm uppercase text-light-on-surface hover:bg-light-surface-container transition-colors cursor-pointer"
                        },
                        "Close"
                    )
                )
            )
            if show_csv_modal else None
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
                    {"class_name": "p-12 text-center border border-light-outline-variant bg-light-surface-container-lowest flex flex-col items-center gap-3"},
                    html.span({"class_name": "material-symbols-outlined text-[48px] text-light-outline"}, "description"),
                    html.p({"class_name": "font-headline text-title-lg text-light-on-surface"}, "No Transcript Records Found"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant max-w-md"}, "Your academic ledger is empty. Click '+ Add Result' above to record individual course grades, or use 'Import CSV' to batch import your semester results."),
                    html.button(
                        {
                            "type": "button",
                            "on_click": lambda e: handle_open_add(),
                            "class_name": "mt-2 px-6 py-2.5 bg-light-primary text-white font-mono text-mono-sm font-bold uppercase hover:bg-light-primary-container transition-colors cursor-pointer shadow-sm inline-flex items-center gap-2"
                        },
                        html.span({"class_name": "material-symbols-outlined text-[18px]"}, "add_circle"),
                        "+ Add First Course Result"
                    )
                )
            ]
        )
    )
