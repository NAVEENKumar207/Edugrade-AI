"""
Faculty & Admin Academic Intelligence Portal Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import (
    icon_users, icon_award, icon_briefcase, icon_layers,
    icon_alert, icon_check
)
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
    up_roll, set_up_roll = use_state("71762104012")
    up_sem, set_up_sem = use_state("6")
    up_code, set_up_code = use_state("CS8601")
    up_name, set_up_name = use_state("Mobile Computing")
    up_credits, set_up_credits = use_state("3")
    up_grade, set_up_grade = use_state("A+")
    up_gp, set_up_gp = use_state("9.0")
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

    def handle_filter_submit(e=None):
        set_students(get_faculty_students_list(search, status_filter, dept_filter))

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

    metrics = overview["metrics"]
    department_stats = overview["department_stats"]
    recent_audits = overview["recent_audits"]

    # Student Table Rows
    student_rows = []
    for s in students:
        student_rows.append(
            html.tr(
                {"key": str(s.id)},
                html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "600", "color": "var(--brand-navy)"}}, s.roll_number),
                html.td({"style": {"fontWeight": "700"}}, f"{s.user.first_name} {s.user.last_name}".strip() or s.user.username),
                html.td({"style": {"color": "var(--text-secondary)"}}, s.department),
                html.td(f"Sem {s.current_semester}"),
                html.td({"style": {"fontWeight": "800", "color": "var(--brand-vermillion)"}}, f"{float(s.current_cgpa):.2f}"),
                html.td(str(s.credits_earned)),
                html.td({"style": {"color": "var(--text-muted)" if s.backlogs_count == 0 else "var(--danger)", "fontWeight": "700"}}, str(s.backlogs_count)),
                html.td(html.span({"className": "badge badge-success" if s.is_placement_eligible else "badge badge-warning"}, "✓ Eligible" if s.is_placement_eligible else "⚠️ Arrears Pending")),
                html.td(
                    html.a(
                        {
                            "href": f"/api/transcript/pdf/?student_id={s.id}",
                            "download": f"transcript_{s.roll_number}.pdf",
                            "className": "btn btn-secondary",
                            "style": {"padding": "0.3rem 0.65rem", "fontSize": "0.75rem", "textDecoration": "none", "display": "inline-flex", "alignItems": "center", "gap": "0.25rem"}
                        },
                        "📄 PDF"
                    )
                )
            )
        )

    # Department Cards
    dept_cards = []
    for d in department_stats:
        dept_cards.append(
            html.div(
                {"key": d["department"], "style": {"padding": "1.25rem", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-md)", "border": "1px solid var(--border-subtle)"}},
                html.div({"style": {"fontWeight": "800", "fontSize": "1rem", "color": "var(--brand-navy)", "marginBottom": "0.35rem"}}, d["department"]),
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem", "color": "var(--text-secondary)"}},
                    html.span(f"Students Enrolled: {d['student_count']}"),
                    html.span({"style": {"fontWeight": "700", "color": "var(--brand-vermillion)"}}, f"Batch CGPA: {d['avg_cgpa']:.2f}")
                )
            )
        )

    # Audit Rows
    audit_rows = []
    for a in recent_audits:
        audit_rows.append(
            html.div(
                {"key": str(a.id), "style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "0.85rem 1rem", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-sm)", "fontSize": "0.85rem", "border": "1px solid var(--border-subtle)"}},
                html.div(
                    html.span({"className": "badge badge-vermillion", "style": {"marginRight": "0.75rem"}}, a.action_type),
                    html.span({"style": {"color": "var(--brand-navy)", "fontWeight": "500"}}, a.description)
                ),
                html.small({"style": {"color": "var(--text-muted)"}}, a.timestamp.strftime("%b %d, %H:%M"))
            )
        )

    # 1. Grade Distribution CSS Bars
    grade_dist = analytics.get("grade_distribution", {}) if analytics else {}
    total_grade_count = sum(grade_dist.values()) if grade_dist else 0
    max_count = max(list(grade_dist.values()) + [1])
    grade_bars = []
    for g, count in grade_dist.items():
        pct = max(8, int((count / max_count) * 100)) if max_count > 0 else 8
        is_fail = g in ['U', 'RA', 'SA', 'W']
        bar_bg = "linear-gradient(180deg, #EF4444 0%, #991B1B 100%)" if is_fail else "linear-gradient(180deg, #F93812 0%, #051E34 100%)"
        grade_bars.append(
            html.div(
                {"key": g, "style": {"flex": "1", "display": "flex", "flexDirection": "column", "alignItems": "center", "height": "100%", "justifyContent": "flex-end"}},
                html.span({"style": {"fontFamily": "var(--font-sans)", "fontSize": "0.75rem", "fontWeight": "700", "color": "var(--danger)" if is_fail else "var(--brand-vermillion)", "marginBottom": "0.35rem"}}, str(count)),
                html.div({
                    "style": {
                        "width": "100%",
                        "maxWidth": "38px",
                        "height": f"{pct}%",
                        "background": bar_bg,
                        "borderRadius": "6px 6px 0 0",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
                    }
                }),
                html.span({"style": {"fontSize": "0.75rem", "color": "var(--text-secondary)", "marginTop": "0.5rem", "fontWeight": "700"}}, g)
            )
        )

    # 2. Department Average CGPA Progress Bars
    dept_bars = []
    for d in (analytics.get("department_stats", []) if analytics else []):
        d_avg = d["avg_cgpa"]
        pct = max(10, min(100, int((d_avg / 10.0) * 100)))
        dept_bars.append(
            html.div(
                {"key": d["department"], "style": {"marginBottom": "1.1rem"}},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "fontSize": "0.85rem", "marginBottom": "0.35rem"}},
                    html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, d["department"]),
                    html.span({"style": {"fontWeight": "800", "color": "var(--brand-vermillion)"}}, f"{d_avg:.2f} CGPA ({d['student_count']} enrolled)")
                ),
                html.div(
                    {"style": {"height": "10px", "width": "100%", "backgroundColor": "var(--border-subtle)", "borderRadius": "5px", "overflow": "hidden"}},
                    html.div({"style": {"width": f"{pct}%", "height": "100%", "background": "linear-gradient(90deg, #F93812 0%, #051E34 100%)", "borderRadius": "5px"}})
                )
            )
        )

    # 3. At-Risk Students Table Rows
    at_risk_list = analytics.get("at_risk_students", []) if analytics else []
    at_risk_rows = []
    for s in at_risk_list:
        at_risk_rows.append(
            html.tr(
                {"key": str(s["id"])},
                html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "700", "color": "var(--brand-navy)"}}, s["roll_number"]),
                html.td({"style": {"fontWeight": "700"}}, s["name"]),
                html.td({"style": {"color": "var(--text-secondary)"}}, s["department"]),
                html.td(f"Sem {s['current_semester']}"),
                html.td({"style": {"fontWeight": "800", "color": "var(--danger)" if s["current_cgpa"] < 6.0 else "var(--brand-navy)"}}, f"{s['current_cgpa']:.2f}"),
                html.td({"style": {"fontWeight": "800", "color": "var(--danger)" if s["backlogs_count"] >= 2 else "var(--text-muted)"}}, str(s["backlogs_count"])),
                html.td(html.span({"className": "badge badge-danger", "style": {"fontWeight": "600"}}, s["reason"])),
                html.td(
                    html.a(
                        {
                            "href": f"/api/transcript/pdf/?student_id={s['id']}",
                            "download": f"transcript_{s['roll_number']}.pdf",
                            "className": "btn btn-secondary",
                            "style": {"padding": "0.25rem 0.6rem", "fontSize": "0.75rem", "textDecoration": "none"}
                        },
                        "📄 PDF"
                    )
                )
            )
        )


    return html.div(
        # Top Header
        html.div(
            {
                "style": {
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "marginBottom": "2.25rem",
                    "flexWrap": "wrap",
                    "gap": "1rem"
                }
            },
            html.div(
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
                    "Faculty & Administrative Intelligence"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, "Institutional cohort analytics, automated grade calculations, and single/batch result recording.")
            ),
            html.div(
                {"style": {"display": "flex", "gap": "0.75rem", "flexWrap": "wrap"}},
                html.a(
                    {"href": "/api/admin/grades/sample-csv/", "className": "btn btn-secondary", "download": "sample_grades.csv", "style": {"textDecoration": "none", "display": "inline-flex", "alignItems": "center"}},
                    "📥 Sample CSV"
                ),
                html.button(
                    {"className": "btn btn-secondary", "on_click": lambda e: set_csv_modal_open(True)},
                    "📁 Bulk Upload CSV"
                ),
                html.button(
                    {"className": "btn btn-primary", "on_click": lambda e: set_upload_open(True)},
                    icon_award(16), " + Record Course Result"
                )
            )
        ),

        # Metrics KPI Grid
        html.div(
            {"className": "stat-grid"},
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Total Registered Students"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, str(metrics.get("total_students", 0))),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, "Across all departments")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_users(26, "var(--brand-navy)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Cohort Average CGPA"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-vermillion)"}}, f"{float(metrics.get('average_cgpa', metrics.get('avg_cgpa', 0.0))):.2f}" if metrics.get("total_students", 0) > 0 else "0.00"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, "10-Point CBCS Scale")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_award(26, "var(--brand-vermillion)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Placement Eligibility Rate"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, f"{float(metrics.get('eligibility_rate', metrics.get('placement_eligible_pct', 0.0))):.0f}%"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, f"{metrics.get('eligible_count', metrics.get('placement_eligible_count', 0))} students meet 0-backlog criteria")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_briefcase(26, "#53B7CF"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Academic Pass Ratio"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, f"{float(metrics.get('pass_rate', 0.0)):.0f}%"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, f"{metrics.get('total_passed', 0)} / {metrics.get('total_courses', 0)} courses passed")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_layers(26, "#10B981"))
            )
        ),

        # Department Breakdown
        html.div(
            {"className": "card", "style": {"marginBottom": "2rem"}},
            html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)", "marginBottom": "1.25rem"}}, "Departmental Cohort Breakdown"),
            html.div(
                {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))", "gap": "1.25rem"}},
                dept_cards if dept_cards else [html.div({"style": {"gridColumn": "1 / -1", "padding": "2rem", "textAlign": "center", "color": "var(--text-muted)", "fontSize": "0.9rem"}}, "No data yet")]
            )
        ),

        # Cohort Analytics: Grade Distribution & Department CGPA Benchmark
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "1.75rem", "marginBottom": "2rem"}},
            # Grade Distribution Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Institution Grade Distribution"),
                    html.span({"className": "badge badge-cyan"}, "CBCS Scale (O to W)")
                ),
                html.div(
                    {"style": {"display": "flex", "alignItems": "flex-end", "height": "220px", "gap": "0.75rem", "padding": "1rem 0", "borderBottom": "1.5px solid var(--border-subtle)"}},
                    grade_bars if total_grade_count > 0 else [html.div({"style": {"width": "100%", "height": "100%", "display": "flex", "alignItems": "center", "justifyContent": "center", "color": "var(--text-muted)", "fontSize": "0.9rem"}}, "No data yet")]
                )
            ),
            # Department Benchmark Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Departmental CGPA Benchmarks"),
                    html.span({"className": "badge badge-vermillion"}, "10-Point Scale")
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "0.5rem", "padding": "0.5rem 0"}},
                    dept_bars if dept_bars else [html.div({"style": {"padding": "2rem", "textAlign": "center", "color": "var(--text-muted)", "fontSize": "0.9rem"}}, "No data yet")]
                )
            )
        ),

        # Academic Intervention Cohort - At-Risk Students Table
        html.div(
            {"className": "card", "style": {"marginBottom": "2rem", "borderLeft": "4px solid var(--danger)"}},
            html.div(
                {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem", "flexWrap": "wrap", "gap": "0.75rem"}},
                html.div(
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Academic Intervention Cohort — At-Risk Students"),
                    html.p({"style": {"fontSize": "0.85rem", "color": "var(--text-secondary)", "marginTop": "0.2rem"}}, "Identifies enrolled students with CGPA < 6.00 or active standing backlogs >= 2 requiring faculty mentoring.")
                ),
                html.span(
                    {"className": "badge badge-danger" if at_risk_rows else "badge badge-success", "style": {"fontSize": "0.85rem", "padding": "0.4rem 0.85rem"}},
                    f"{len(at_risk_rows)} Student{'s' if len(at_risk_rows) != 1 else ''} Flagged" if at_risk_rows else "No at-risk students"
                )
            ),
            html.div(
                {"className": "table-container"},
                html.table(
                    html.thead(
                        html.tr(
                            html.th("Roll Number"),
                            html.th("Student Name"),
                            html.th("Department"),
                            html.th("Semester"),
                            html.th("CGPA"),
                            html.th("Arrears"),
                            html.th("Intervention Reason"),
                            html.th("Transcript")
                        )
                    ),
                    html.tbody(at_risk_rows if at_risk_rows else [
                        html.tr(html.td({"colSpan": "8", "style": {"textAlign": "center", "padding": "1.5rem", "color": "var(--success)", "fontWeight": "600"}}, "✓ No at-risk students"))
                    ])
                )
            )
        ),

        # Student Directory & Filters
        html.div(
            {"className": "card", "style": {"marginBottom": "2rem"}},
            html.div(
                {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem", "flexWrap": "wrap", "gap": "1rem"}},
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Enrolled Student Directory"),
                html.div(
                    {"style": {"display": "flex", "gap": "0.75rem", "alignItems": "center"}},
                    html.input({
                        "type": "text", "className": "input", "value": search,
                        "placeholder": "Search name or roll no...",
                        "style": {"width": "220px", "padding": "0.5rem 0.85rem"},
                        "on_change": lambda e: set_search(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    }),
                    html.button(
                        {"className": "btn btn-secondary", "style": {"padding": "0.5rem 1rem"}, "on_click": handle_filter_submit},
                        "Filter Records"
                    )
                )
            ),
            html.div(
                {"className": "table-container"},
                html.table(
                    html.thead(
                        html.tr(
                            html.th("Roll Number"),
                            html.th("Student Name"),
                            html.th("Department"),
                            html.th("Semester"),
                            html.th("CGPA"),
                            html.th("Credits"),
                            html.th("Arrears"),
                            html.th("Recruitment Status"),
                            html.th("Transcript")
                        )
                    ),
                    html.tbody(student_rows if student_rows else [
                        html.tr(html.td({"colSpan": "9", "style": {"textAlign": "center", "padding": "2rem", "color": "var(--text-muted)"}}, "No enrolled students found in directory."))
                    ])
                )
            )
        ),

        # Recent Audit Logs
        html.div(
            {"className": "card"},
            html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)", "marginBottom": "1.25rem"}}, "Institutional Academic Audit Trail"),
            html.div({"style": {"display": "flex", "flexDirection": "column", "gap": "0.75rem"}}, audit_rows)
        ),

        # Result Recording Modal
        html.div(
            {
                "style": {
                    "position": "fixed",
                    "top": "0", "left": "0", "right": "0", "bottom": "0",
                    "backgroundColor": "rgba(5, 30, 52, 0.65)",
                    "backdropFilter": "blur(6px)",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "zIndex": "100", "padding": "1rem"
                }
            },
            html.div(
                {
                    "className": "card",
                    "style": {"width": "100%", "maxWidth": "540px", "padding": "2.5rem", "borderRadius": "var(--radius-xl)", "boxShadow": "var(--shadow-xl)"}
                },
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.5rem", "color": "var(--brand-navy)"}}, "Record Course Result"),
                    html.button(
                        {"style": {"background": "none", "border": "none", "fontSize": "1.5rem", "cursor": "pointer", "color": "var(--text-muted)"}, "on_click": lambda e: set_upload_open(False)},
                        "×"
                    )
                ),
                html.div(
                    {"className": "badge-success", "style": {"padding": "0.75rem", "borderRadius": "var(--radius-sm)", "marginBottom": "1rem"}}
                    if up_msg else None,
                    icon_check(16, "var(--success)"), html.span(f" {up_msg}")
                ) if up_msg else None,
                html.div(
                    {"className": "badge-danger", "style": {"padding": "0.75rem", "borderRadius": "var(--radius-sm)", "marginBottom": "1rem"}}
                    if up_err else None,
                    icon_alert(16, "var(--danger)"), html.span(f" {up_err}")
                ) if up_err else None,
                # Form Grid
                html.div(
                    {"style": {"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem", "marginBottom": "1.5rem"}},
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Roll Number"),
                        html.input({
                            "type": "text", "className": "input", "value": up_roll,
                            "on_change": lambda e: set_up_roll(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Semester (1-8)"),
                        html.input({
                            "type": "number", "className": "input", "value": up_sem,
                            "on_change": lambda e: set_up_sem(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Course Code"),
                        html.input({
                            "type": "text", "className": "input", "value": up_code,
                            "on_change": lambda e: set_up_code(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Course Title"),
                        html.input({
                            "type": "text", "className": "input", "value": up_name,
                            "on_change": lambda e: set_up_name(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Credits"),
                        html.input({
                            "type": "number", "className": "input", "value": up_credits,
                            "on_change": lambda e: set_up_credits(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Letter Grade"),
                        html.input({
                            "type": "text", "className": "input", "value": up_grade,
                            "on_change": lambda e: set_up_grade(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    ),
                    html.div(
                        {"style": {"gridColumn": "span 2"}},
                        html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.3rem"}}, "Grade Point (0-10)"),
                        html.input({
                            "type": "number", "step": "0.1", "className": "input", "value": up_gp,
                            "on_change": lambda e: set_up_gp(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                        })
                    )
                ),
                html.div(
                    {"style": {"display": "flex", "gap": "1rem", "justifyContent": "flex-end"}},
                    html.button(
                        {"className": "btn btn-secondary", "on_click": lambda e: set_upload_open(False)},
                        "Cancel"
                    ),
                    html.button(
                        {"className": "btn btn-primary", "on_click": lambda e: handle_upload()},
                        "Save Course Result →"
                    )
                )
            )
        ) if upload_open else None,

        # Bulk CSV Grade Upload Modal
        html.div(
            {
                "style": {
                    "position": "fixed",
                    "top": "0", "left": "0", "right": "0", "bottom": "0",
                    "backgroundColor": "rgba(5, 30, 52, 0.65)",
                    "backdropFilter": "blur(6px)",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "zIndex": "100", "padding": "1rem"
                }
            },
            html.div(
                {
                    "className": "card",
                    "style": {"width": "100%", "maxWidth": "680px", "maxHeight": "90vh", "overflowY": "auto", "padding": "2.25rem", "borderRadius": "var(--radius-xl)", "boxShadow": "var(--shadow-xl)"}
                },
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                    html.div(
                        html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.5rem", "color": "var(--brand-navy)"}}, "Bulk CSV Grade Upload"),
                        html.p({"style": {"fontSize": "0.85rem", "color": "var(--text-secondary)", "marginTop": "0.25rem"}}, "Import student grade results in bulk from a comma-separated file.")
                    ),
                    html.button(
                        {"style": {"background": "none", "border": "none", "fontSize": "1.5rem", "cursor": "pointer", "color": "var(--text-muted)"}, "on_click": lambda e: set_csv_modal_open(False)},
                        "×"
                    )
                ),
                # Download sample template banner
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "0.85rem 1.25rem", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-md)", "border": "1px solid var(--border-subtle)", "marginBottom": "1.25rem", "flexWrap": "wrap", "gap": "0.75rem"}},
                    html.div(
                        html.strong({"style": {"fontSize": "0.85rem", "color": "var(--brand-navy)"}}, "Required Header: "),
                        html.code({"style": {"fontSize": "0.75rem", "color": "var(--brand-vermillion)"}}, "roll_number,semester,course_code,course_title,credits,grade")
                    ),
                    html.a(
                        {"href": "/api/admin/grades/sample-csv/", "className": "btn btn-secondary", "download": "sample_grades.csv", "style": {"textDecoration": "none", "fontSize": "0.8rem", "padding": "0.4rem 0.85rem"}},
                        "📥 Download Sample CSV"
                    )
                ),
                # Error banner if header/file level error
                html.div(
                    {"className": "badge-danger", "style": {"padding": "0.75rem", "borderRadius": "var(--radius-sm)", "marginBottom": "1rem"}},
                    icon_alert(16, "var(--danger)"), html.span(f" {csv_error}")
                ) if csv_error else None,
                # Summary card if processed
                html.div(
                    {"style": {"marginBottom": "1.25rem"}},
                    html.div(
                        {"style": {"display": "flex", "gap": "1rem", "marginBottom": "1rem"}},
                        html.div(
                            {"style": {"flex": "1", "padding": "0.85rem", "backgroundColor": "rgba(16, 185, 129, 0.1)", "border": "1px solid var(--success)", "borderRadius": "var(--radius-md)", "textAlign": "center"}},
                            html.div({"style": {"fontSize": "1.5rem", "fontWeight": "800", "color": "var(--success)"}}, str(csv_summary["saved"])),
                            html.div({"style": {"fontSize": "0.8rem", "color": "var(--text-secondary)", "fontWeight": "600"}}, "Rows Saved")
                        ),
                        html.div(
                            {"style": {"flex": "1", "padding": "0.85rem", "backgroundColor": "rgba(234, 88, 12, 0.1)", "border": "1px solid var(--brand-vermillion)", "borderRadius": "var(--radius-md)", "textAlign": "center"}},
                            html.div({"style": {"fontSize": "1.5rem", "fontWeight": "800", "color": "var(--brand-vermillion)"}}, str(csv_summary["skipped"])),
                            html.div({"style": {"fontSize": "0.8rem", "color": "var(--text-secondary)", "fontWeight": "600"}}, "Rows Skipped")
                        )
                    ),
                    # Error details table if any skipped rows
                    html.div(
                        {"style": {"maxHeight": "180px", "overflowY": "auto", "border": "1px solid var(--border-subtle)", "borderRadius": "var(--radius-md)", "padding": "0.5rem"}},
                        html.table(
                            {"style": {"width": "100%", "fontSize": "0.8rem"}},
                            html.thead(
                                html.tr(
                                    html.th({"style": {"textAlign": "left", "padding": "0.4rem"}}, "Row"),
                                    html.th({"style": {"textAlign": "left", "padding": "0.4rem"}}, "Reason for Skip")
                                )
                            ),
                            html.tbody([
                                html.tr(
                                    {"key": f"err-{idx}"},
                                    html.td({"style": {"fontWeight": "700", "padding": "0.4rem", "color": "var(--brand-navy)"}}, f"Row {err_item.get('row')}"),
                                    html.td({"style": {"padding": "0.4rem", "color": "var(--danger)"}}, err_item.get("reason", "Validation error"))
                                ) for idx, err_item in enumerate(csv_summary.get("errors", []))
                            ])
                        )
                    ) if csv_summary.get("errors") else None
                ) if csv_summary else None,
                # File picker & CSV textarea
                html.div(
                    {"style": {"marginBottom": "1.25rem"}},
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.4rem"}}, "Select CSV File (auto-fills content below):"),
                    html.input({
                        "type": "file",
                        "accept": ".csv",
                        "id": "csv-file-picker",
                        "style": {"marginBottom": "0.75rem", "fontSize": "0.85rem"}
                    }),
                    html.label({"style": {"display": "block", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-navy)", "marginBottom": "0.4rem"}}, "CSV Data Preview / Direct Entry:"),
                    html.textarea({
                        "className": "input",
                        "id": "csv-raw-textarea",
                        "rows": 8,
                        "style": {"width": "100%", "fontFamily": "var(--font-mono)", "fontSize": "0.8rem", "whiteSpace": "pre", "overflowX": "auto"},
                        "placeholder": "roll_number,semester,course_code,course_title,credits,grade\n71762104012,6,CS8601,Mobile Computing,3,A+",
                        "value": csv_text,
                        "on_change": lambda e: set_csv_text(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e))
                    })
                ),
                # Modal actions
                html.div(
                    {"style": {"display": "flex", "gap": "1rem", "justifyContent": "flex-end"}},
                    html.button(
                        {"className": "btn btn-secondary", "on_click": lambda e: set_csv_modal_open(False)},
                        "Close"
                    ),
                    html.button(
                        {"className": "btn btn-primary", "on_click": handle_csv_submit},
                        "Process & Import CSV →"
                    )
                )
            )
        ) if csv_modal_open else None
    )
