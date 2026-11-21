"""
Student Performance Dashboard Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import (
    icon_award, icon_trending_up, icon_book_open, icon_briefcase,
    icon_sparkles, icon_check, icon_alert, icon_calculator, icon_bot
)
from ui.services.data_service import get_student_dashboard_data, get_arrears

@component
def StudentDashboard(user, set_page):
    data, set_data = use_state(lambda: get_student_dashboard_data(user))

    if not data:
        data = get_student_dashboard_data(user)

    student = data["student"]
    semesters = data["semesters"]
    subject_insights = data["subject_insights"]
    recent_courses = data["recent_courses"]

    # Render semester progression bars in clean SVG/HTML with vermillion-to-navy gradient
    bars = []
    for s in semesters:
        sgpa_val = float(s.sgpa)
        pct = max(10, min(100, int((sgpa_val / 10.0) * 100)))
        bars.append(
            html.div(
                {"key": str(s.semester_number), "style": {"flex": "1", "display": "flex", "flexDirection": "column", "alignItems": "center", "height": "100%", "justifyContent": "flex-end"}},
                html.span({"style": {"fontFamily": "var(--font-sans)", "fontSize": "0.8rem", "fontWeight": "700", "color": "var(--brand-vermillion)", "marginBottom": "0.35rem"}}, f"{sgpa_val:.2f}"),
                html.div({
                    "style": {
                        "width": "100%",
                        "maxWidth": "44px",
                        "height": f"{pct}%",
                        "background": "linear-gradient(180deg, #F93812 0%, #051E34 100%)",
                        "borderRadius": "8px 8px 0 0",
                        "boxShadow": "0 4px 14px rgba(249, 56, 18, 0.25)"
                    }
                }),
                html.span({"style": {"fontSize": "0.75rem", "color": "var(--text-secondary)", "marginTop": "0.5rem", "fontWeight": "700"}}, f"Sem {s.semester_number}")
            )
        )

    # Subject insight cards
    insight_items = []
    for ins in subject_insights:
        is_strong = ins.status_label == 'Strong'
        is_needs = ins.status_label == 'Needs attention'
        badge_cls = "badge badge-success" if is_strong else "badge badge-danger" if is_needs else "badge badge-warning"
        insight_items.append(
            html.div(
                {
                    "key": str(ins.id),
                    "style": {
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "padding": "0.85rem 1rem",
                        "backgroundColor": "var(--bg-surface-elevated)",
                        "borderRadius": "var(--radius-sm)",
                        "border": "1px solid var(--border-subtle)"
                    }
                },
                html.div(
                    html.div({"style": {"fontSize": "0.9rem", "fontWeight": "700", "color": "var(--brand-navy)"}}, ins.subject_name),
                    html.small({"style": {"color": "var(--text-muted)"}}, f"Grade Point: {ins.grade_point} / 10.0")
                ),
                html.span({"className": badge_cls}, ins.status_label)
            )
        )

    # Course table rows
    course_rows = []
    for c in recent_courses:
        course_rows.append(
            html.tr(
                {"key": str(c.id)},
                html.td(f"Sem {c.semester_number}"),
                html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "600", "color": "var(--brand-navy)"}}, c.course_code),
                html.td({"style": {"fontWeight": "600"}}, c.course_name),
                html.td(str(c.credits)),
                html.td(html.span({"className": "badge badge-vermillion", "style": {"fontWeight": "700"}}, c.grade)),
                html.td({"style": {"fontWeight": "700"}}, str(c.grade_point))
            )
        )

    # Arrears Tracker Card
    arrears_data = get_arrears(user)
    active_arrears = arrears_data.get("active", [])
    cleared_arrears = arrears_data.get("cleared", [])

    if not active_arrears and not cleared_arrears:
        arrears_card = html.div(
            {"className": "card", "style": {"marginBottom": "2rem"}},
            html.div(
                {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.75rem"}},
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Academic Arrears & Clearance Tracker"),
                html.span({"className": "badge badge-success"}, icon_check(13), " Clean Record")
            ),
            html.div(
                {"style": {"padding": "1.25rem", "textAlign": "center", "color": "var(--text-secondary)", "fontWeight": "600", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-sm)"}},
                "No arrears"
            )
        )
    else:
        active_items = []
        if active_arrears:
            for item in active_arrears:
                active_items.append(
                    html.tr(
                        {"key": str(item["id"])},
                        html.td(f"Sem {item['semester']}"),
                        html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "700", "color": "var(--brand-navy)"}}, item["course_code"]),
                        html.td({"style": {"fontWeight": "600"}}, item["course_name"]),
                        html.td(html.span({"className": "badge badge-danger", "style": {"fontWeight": "700"}}, item["grade"]))
                    )
                )
            active_section = html.div(
                {"style": {"marginBottom": "1.5rem"}},
                html.h4({"style": {"fontSize": "0.95rem", "color": "var(--danger)", "fontWeight": "700", "marginBottom": "0.5rem"}}, f"Active Standing Arrears ({len(active_arrears)})"),
                html.div(
                    {"className": "table-container"},
                    html.table(
                        html.thead(
                            html.tr(
                                html.th("Semester"),
                                html.th("Course Code"),
                                html.th("Course Title"),
                                html.th("Current Grade")
                            )
                        ),
                        html.tbody(active_items)
                    )
                )
            )
        else:
            active_section = html.div(
                {"style": {"marginBottom": "1.5rem", "padding": "0.75rem 1rem", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-sm)", "color": "var(--success)", "fontSize": "0.85rem", "fontWeight": "600"}},
                "✓ Zero active backlogs. All enrolled courses currently cleared."
            )

        cleared_items = []
        if cleared_arrears:
            for item in cleared_arrears:
                cleared_items.append(
                    html.tr(
                        {"key": str(item["id"])},
                        html.td(f"Sem {item['semester']}"),
                        html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "700", "color": "var(--brand-navy)"}}, item["course_code"]),
                        html.td({"style": {"fontWeight": "600"}}, item["course_name"]),
                        html.td(
                            html.span({"style": {"color": "var(--danger)", "fontWeight": "700"}}, item["previous_grade"]),
                            " → ",
                            html.span({"className": "badge badge-success", "style": {"fontWeight": "700"}}, item["current_grade"])
                        ),
                        html.td({"style": {"color": "var(--text-muted)", "fontSize": "0.85rem"}}, item["cleared_on"])
                    )
                )
            cleared_section = html.div(
                html.h4({"style": {"fontSize": "0.95rem", "color": "var(--success)", "fontWeight": "700", "marginBottom": "0.5rem"}}, f"Cleared Arrears History ({len(cleared_arrears)})"),
                html.div(
                    {"className": "table-container"},
                    html.table(
                        html.thead(
                            html.tr(
                                html.th("Semester"),
                                html.th("Course Code"),
                                html.th("Course Title"),
                                html.th("Progression"),
                                html.th("Cleared Date")
                            )
                        ),
                        html.tbody(cleared_items)
                    )
                )
            )
        else:
            cleared_section = html.div(
                {"style": {"padding": "0.75rem 1rem", "backgroundColor": "var(--bg-surface-elevated)", "borderRadius": "var(--radius-sm)", "color": "var(--text-secondary)", "fontSize": "0.85rem"}},
                "No past arrears recorded."
            )

        arrears_card = html.div(
            {"className": "card", "style": {"marginBottom": "2rem"}},
            html.div(
                {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Academic Arrears & Clearance Tracker"),
                html.span({"className": "badge badge-warning" if active_arrears else "badge badge-success"}, f"{len(active_arrears)} Active Arrear{'s' if len(active_arrears) != 1 else ''}")
            ),
            active_section,
            cleared_section
        )

    # Placement Readiness Score Progress Meter Card
    has_results = len(semesters) > 0 or len(recent_courses) > 0
    readiness = data.get("placement_readiness") or {}
    score_raw = readiness.get("score", 0) if isinstance(readiness, dict) else int(readiness or 0)

    if not has_results:
        display_score = "Not available yet"
        readiness_score = 0
        readiness_tip = "Not available yet — grades are not published yet."
        meter_color = "var(--text-muted)"
    else:
        display_score = f"{score_raw} / 100"
        readiness_score = score_raw
        readiness_tip = readiness.get("tip", "") if isinstance(readiness, dict) else ""
        meter_color = "var(--danger)" if readiness_score < 40 else ("var(--brand-vermillion)" if readiness_score < 70 else "var(--success)")

    readiness_card = html.div(
        {"className": "card", "style": {"marginBottom": "2rem", "borderLeft": f"4px solid {meter_color}"}},
        html.div(
            {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.75rem", "flexWrap": "wrap", "gap": "0.75rem"}},
            html.div(
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.3rem", "color": "var(--brand-navy)"}}, "Placement Readiness Score"),
                html.small({"style": {"color": "var(--text-secondary)"}}, "Comprehensive 100-pt index: CGPA (50%) + Zero-Arrears (30%) + Corporate Partner Eligibility (20%)")
            ),
            html.div(
                {"style": {"display": "flex", "alignItems": "baseline", "gap": "0.3rem"}},
                html.span({"style": {"fontFamily": "var(--font-display)", "fontSize": "1.5rem" if not has_results else "2rem", "color": meter_color, "fontWeight": "800"}}, display_score)
            )
        ),
        # Progress Bar
        html.div(
            {"style": {"height": "10px", "width": "100%", "backgroundColor": "var(--border-subtle)", "borderRadius": "5px", "overflow": "hidden", "marginBottom": "0.75rem"}},
            html.div({"style": {"width": f"{readiness_score}%", "height": "100%", "backgroundColor": meter_color, "transition": "width 0.4s ease"}})
        ),
        # Action Tip
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "fontSize": "0.85rem", "color": "var(--brand-navy)", "fontWeight": "600", "backgroundColor": "var(--bg-surface-elevated)", "padding": "0.6rem 0.85rem", "borderRadius": "var(--radius-sm)"}},
            html.span({"style": {"color": meter_color, "fontWeight": "800"}}, "🎯 Improvement Tip:"),
            html.span(readiness_tip)
        )
    )

    return html.div(
        # Welcome Banner
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
                    "Academic Intelligence Dashboard"
                ),
                html.p(
                    {"style": {"color": "var(--text-secondary)", "fontSize": "0.95rem", "marginTop": "0.25rem"}},
                    f"Welcome back, ",
                    html.strong({"style": {"color": "var(--brand-navy)"}}, student["name"]),
                    f" • Roll No: {student['roll_number']} • {student['department']}"
                )
            ),
            html.div(
                {"style": {"display": "flex", "gap": "0.75rem"}},
                html.button(
                    {"className": "btn btn-secondary", "on_click": lambda e: set_page("planner")},
                    icon_calculator(16), " Target CGPA Planner"
                ),
                html.button(
                    {"className": "btn btn-primary", "on_click": lambda e: set_page("advisor")},
                    icon_bot(16), " Consult AI Mentor"
                )
            )
        ),

        # KPI Stats Grid with Anton Numerals
        html.div(
            {"className": "stat-grid"},
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Cumulative CGPA"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-vermillion)"}}, f"{student['current_cgpa']:.2f}" if has_results else "N/A"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, f"Target: {student['target_cgpa']:.2f}" if has_results else "No results published yet")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_award(26, "var(--brand-vermillion)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Latest Semester SGPA"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, f"{student['latest_sgpa']:.2f}" if has_results else "N/A"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, f"Semester {len(semesters)} CBCS" if has_results else "No results published yet")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_trending_up(26, "var(--brand-navy)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Credits Completed"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, f"{student['credits_earned']}"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, f"{int(student['credits_earned'] / (student['total_credits'] or 160) * 100)}% of 160 credits completed")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_book_open(26, "#53B7CF"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Placement Eligibility"),
                    html.div(
                        {"style": {"margin": "0.5rem 0"}},
                        html.span({"className": "badge badge-success"}, icon_check(13), " Eligible (0 Arrears)") if student["is_placement_eligible"] else html.span({"className": "badge badge-warning"}, icon_alert(13), f" {student['backlogs_count']} Arrear Pending")
                    ),
                    html.small({"style": {"color": "var(--text-muted)", "display": "block"}}, "Target recruitment benchmark: 7.0+ CGPA")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_briefcase(26, "#F59E0B"))
            )
        ),

        # Placement Readiness Progress Meter Card
        readiness_card,

        # Trend Chart & Subject Insights
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(350px, 1fr))", "gap": "1.75rem", "marginBottom": "2rem"}},
            # Chart Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Semester SGPA Trend History"),
                    html.span({"className": "badge badge-vermillion"}, "CBCS Scale")
                ),
                html.div(
                    {"style": {"display": "flex", "alignItems": "flex-end", "height": "220px", "gap": "1.25rem", "padding": "1rem 0", "borderBottom": "1.5px solid var(--border-subtle)", "justifyContent": "center" if not bars else "flex-start"}},
                    bars if bars else [html.div({"style": {"color": "var(--text-muted)", "fontSize": "0.9rem", "alignSelf": "center"}}, "No semester records published yet.")]
                )
            ),
            # Insights Card
            html.div(
                {"className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                    html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Academic Subject Insights"),
                    html.span({"style": {"fontSize": "0.75rem", "fontWeight": "700", "color": "var(--text-muted)"}}, "TOP PERFORMANCE")
                ),
                html.div(
                    {"style": {"display": "flex", "flexDirection": "column", "gap": "0.75rem"}},
                    insight_items if insight_items else [html.div({"style": {"padding": "1.5rem", "textAlign": "center", "color": "var(--text-muted)", "fontSize": "0.9rem"}}, "No subject insights available yet.")]
                )
            )
        ),

        # Academic Arrears Tracker Card
        arrears_card,

        # Recent Courses Table
        html.div(
            {"className": "card"},
            html.div(
                {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.25rem"}},
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Current Semester Course Breakdown"),
                html.button(
                    {"className": "btn btn-secondary", "style": {"fontSize": "0.775rem", "padding": "0.4rem 0.85rem"}, "on_click": lambda e: set_page("results")},
                    "Full Transcript →"
                )
            ),
            html.div(
                {"className": "table-container"},
                html.table(
                    html.thead(
                        html.tr(
                            html.th("Semester"),
                            html.th("Course Code"),
                            html.th("Course Title"),
                            html.th("Credits"),
                            html.th("Grade"),
                            html.th("Points")
                        )
                    ),
                    html.tbody(course_rows if course_rows else [html.tr(html.td({"colSpan": "6", "style": {"textAlign": "center", "padding": "2rem", "color": "var(--text-muted)"}}, "No course results published yet."))])
                )
            )
        )
    )
