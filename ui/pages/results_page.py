"""
Semester Transcripts & Results Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import icon_award, icon_book_open, icon_shield_check, icon_check
from ui.components.common import StatCard, EmptyStateCard
from ui.services.data_service import get_semester_results_data

@component
def ResultsPage(user):
    data, set_data = use_state(lambda: get_semester_results_data(user))
    selected_sem, set_selected_sem = use_state("all")

    if not data:
        data = get_semester_results_data(user)

    semesters = data["semesters"]
    filtered_sems = [s for s in semesters if selected_sem == "all" or str(s["semester_number"]) == selected_sem]

    sem_cards = []
    for sem in filtered_sems:
        courses = sem["courses"]
        course_trs = []
        for c in courses:
            is_distinction = c.grade in ['O', 'A+']
            badge_cls = "badge badge-success" if is_distinction else "badge badge-vermillion"
            course_trs.append(
                html.tr(
                    {"key": str(c.id)},
                    html.td({"style": {"fontFamily": "var(--font-mono)", "fontWeight": "600", "color": "var(--brand-navy)"}}, c.course_code),
                    html.td({"style": {"fontWeight": "600"}}, c.course_name),
                    html.td(str(c.credits)),
                    html.td(html.span({"className": badge_cls, "style": {"fontWeight": "700"}}, c.grade)),
                    html.td({"style": {"fontWeight": "700"}}, str(c.grade_point)),
                    html.td(html.span({"style": {"display": "flex", "alignItems": "center", "gap": "0.35rem", "color": "var(--success)", "fontWeight": "700", "fontSize": "0.85rem"}}, icon_check(14), " Completed"))
                )
            )

        sem_cards.append(
            html.div(
                {"key": str(sem["semester_number"]), "className": "card", "style": {"marginBottom": "1.75rem"}},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "borderBottom": "1.5px solid var(--border-subtle)", "paddingBottom": "1rem", "marginBottom": "1rem"}},
                    html.div(
                        html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.4rem", "color": "var(--brand-navy)"}}, f"Semester {sem['semester_number']} Grade Record"),
                        html.span({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, f"Credits Earned: {sem['credits_earned']} • Published Transcript")
                    ),
                    html.span({"className": "badge badge-cyan", "style": {"fontSize": "0.95rem", "padding": "0.4rem 0.85rem", "fontWeight": "700"}}, f"SGPA: {sem['sgpa']:.2f}")
                ),
                html.div(
                    {"className": "table-container"},
                    html.table(
                        html.thead(
                            html.tr(
                                html.th("Course Code"),
                                html.th("Course Title"),
                                html.th("Credits"),
                                html.th("Letter Grade"),
                                html.th("Grade Points"),
                                html.th("Status")
                            )
                        ),
                        html.tbody(course_trs if course_trs else [html.tr(html.td({"colSpan": "6", "style": {"textAlign": "center", "color": "var(--text-muted)"}}, "Subject breakdown logged in semester summary."))])
                    )
                )
            )
        )

    options = [html.option({"value": "all"}, "All Semesters")]
    for s in semesters:
        options.append(html.option({"value": str(s["semester_number"])}, f"Semester {s['semester_number']}"))

    return html.div(
        # Header
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
                    "Semester Transcripts & Grade History"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, f"Verified academic transcript for {data['student_name']} • Roll No: {data['roll_number']}")
            ),
            html.div(
                {"style": {"display": "flex", "alignItems": "center", "gap": "0.75rem", "flexWrap": "wrap"}},
                html.a(
                    {
                        "href": f"/api/transcript/pdf/{'' if selected_sem == 'all' else f'?semester={selected_sem}'}",
                        "download": f"transcript_{data['roll_number'] or 'student'}.pdf",
                        "className": "btn btn-primary",
                        "style": {"textDecoration": "none", "display": "inline-flex", "alignItems": "center", "gap": "0.4rem", "fontSize": "0.85rem", "padding": "0.5rem 1rem"}
                    },
                    "📄 Download Transcript (PDF)"
                ),
                html.label({"style": {"fontSize": "0.85rem", "color": "var(--brand-navy)", "fontWeight": "700"}}, "Filter Semester:"),
                html.select(
                    {
                        "className": "input",
                        "style": {"width": "auto", "padding": "0.5rem 1.25rem", "borderRadius": "var(--radius-full)"},
                        "value": selected_sem,
                        "on_change": lambda e: set_selected_sem(e.get("target", {}).get("value", "all") if isinstance(e, dict) else str(e))
                    },
                    options
                )
            )
        ),
        # Summary Cards
        html.div(
            {"className": "stat-grid", "style": {"marginBottom": "2rem"}},
            StatCard(
                label="Cumulative CGPA",
                value=f"{data['current_cgpa']:.2f}" if len(semesters) > 0 else "N/A",
                subtitle="Credit-weighted official standing" if len(semesters) > 0 else "No results yet",
                icon=icon_award(26, "var(--brand-vermillion)"),
                value_color="var(--brand-vermillion)"
            ),
            StatCard(
                label="Total Credits Earned",
                value=str(data["credits_earned"]),
                subtitle=f"Out of {data['total_credits']} required credits",
                icon=icon_book_open(26, "var(--brand-navy)")
            ),
            StatCard(
                label="Completed Semesters",
                value=str(len(semesters)),
                subtitle="Regulation 2026 CBCS Cycle",
                icon=icon_shield_check(26, "#10B981")
            )
        ),
        # Semester Cards List
        html.div(
            {"style": {"display": "flex", "flexDirection": "column"}},
            sem_cards if sem_cards else [
                EmptyStateCard(
                    title="No Results Yet",
                    description="No semester course results or grade transcripts have been published yet."
                )
            ]
        )
    )
