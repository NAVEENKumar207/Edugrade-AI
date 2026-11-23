"""
Placement Drive Manager Component for EduGrade AI ReactPy Frontend (Faculty/Admin).
Provides corporate drive candidate cohort filtering, eligibility and almost-eligible breakdowns,
department filtering, and official CSV candidate roster export.
"""

from reactpy import component, html, use_state
from ui.services.data_service import get_admin_drives_data

@component
def DriveManager(user):
    selected_company_id, set_selected_company_id = use_state(None)
    dept_filter, set_dept_filter = use_state("")

    # Load drives data
    data = get_admin_drives_data(company_id=selected_company_id, department=dept_filter or None)
    companies = data.get("companies", [])
    selected_company = data.get("selected_company")
    eligible_students = data.get("eligible_students", [])
    almost_students = data.get("almost_eligible_students", [])
    counts = data.get("counts", {})

    if not companies:
        return html.div(
            {"className": "p-gutter-xl max-w-7xl mx-auto flex flex-col gap-gutter-xl animate-fade-in"},
            html.div(
                {"className": "border-b border-light-outline-variant pb-gutter-md"},
                html.h1({"className": "text-display-sm font-headline font-bold text-light-on-surface"}, "Placement Drives Manager"),
                html.p({"className": "text-body-md text-light-on-surface-variant mt-1"}, "Campus recruitment drives and student cohort eligibility analysis.")
            ),
            html.div(
                {"className": "p-gutter-xl text-center border border-dashed border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest"},
                html.span({"className": "material-symbols-outlined text-light-on-surface-variant text-[48px]"}, "domain_disabled"),
                html.h3({"className": "text-title-md font-headline font-bold text-light-on-surface mt-2"}, "No Placement Drives Configured"),
                html.p({"className": "text-body-sm text-light-on-surface-variant max-w-md mx-auto mt-1"}, "Corporate recruitment criteria can be configured via Django Admin or populated from sample criteria.")
            )
        )

    export_url = f"/api/admin/drives/{selected_company['id']}/export/" if selected_company else "#"

    return html.div(
        {"className": "p-gutter-xl max-w-7xl mx-auto flex flex-col gap-gutter-xl animate-fade-in"},

        # Header Title
        html.div(
            {"className": "border-b border-light-outline-variant pb-gutter-md flex flex-col md:flex-row md:items-center justify-between gap-gutter-md"},
            html.div(
                html.div(
                    {"className": "flex items-center gap-gutter-sm text-label-sm uppercase tracking-wider text-light-primary font-mono font-bold"},
                    html.span({"className": "material-symbols-outlined text-[18px]"}, "business_center"),
                    "Corporate Recruitment & Career Readiness"
                ),
                html.h1({"className": "text-display-sm font-headline font-bold text-light-on-surface mt-1"}, "Placement Drives Manager"),
                html.p({"className": "text-body-md text-light-on-surface-variant mt-1"}, "Inspect corporate partner eligibility cohorts, review borderline candidates, and export candidate rosters.")
            ),
            html.div(
                html.a(
                    {
                        "href": export_url,
                        "className": "btn btn-primary flex items-center gap-2",
                        "download": True
                    },
                    html.span({"className": "material-symbols-outlined text-[18px]"}, "download"),
                    "Download Candidates CSV"
                )
            )
        ),

        # Company Selector & Department Filter Bar
        html.div(
            {"className": "card p-gutter-md border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm grid grid-cols-1 md:grid-cols-2 gap-gutter-md items-center"},
            # Company Dropdown
            html.div(
                {"className": "flex flex-col gap-1"},
                html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Select Recruitment Drive:"),
                html.select(
                    {
                        "className": "input w-full font-mono",
                        "value": str(selected_company["id"]) if selected_company else "",
                        "on_change": lambda e: set_selected_company_id(e.get("target", {}).get("value"))
                    },
                    [
                        html.option(
                            {"key": c["id"], "value": str(c["id"])},
                            f"{c['company_name']} — {c['role_title']} (Min CGPA: {c['min_cgpa']:.2f}, {c['package_lpa']:.1f} LPA)"
                        )
                        for c in companies
                    ]
                )
            ),

            # Department Filter
            html.div(
                {"className": "flex flex-col gap-1"},
                html.label({"className": "text-label-sm font-mono text-light-on-surface font-bold"}, "Filter by Department:"),
                html.select(
                    {
                        "className": "input w-full font-mono",
                        "value": dept_filter,
                        "on_change": lambda e: set_dept_filter(e.get("target", {}).get("value", ""))
                    },
                    [
                        html.option({"value": ""}, "All Departments (Entire Cohort)"),
                        html.option({"value": "Computer Science & Engineering"}, "Computer Science & Engineering"),
                        html.option({"value": "Information Technology"}, "Information Technology"),
                        html.option({"value": "Electronics & Communication"}, "Electronics & Communication"),
                        html.option({"value": "Electrical & Electronics"}, "Electrical & Electronics"),
                        html.option({"value": "Mechanical Engineering"}, "Mechanical Engineering"),
                        html.option({"value": "Civil Engineering"}, "Civil Engineering"),
                    ]
                )
            )
        ),

        # Drive Criteria & Summary Stats
        (
            html.div(
                {"className": "grid grid-cols-1 md:grid-cols-4 gap-gutter-md"},
                html.div(
                    {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Minimum CGPA"),
                    html.div({"className": "text-display-sm font-headline font-bold text-light-primary my-1"}, f"{selected_company['min_cgpa']:.2f}"),
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, f"Max Backlogs: {selected_company['max_backlogs']}")
                ),
                html.div(
                    {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Eligible Candidates"),
                    html.div({"className": "text-display-sm font-headline font-bold text-light-emerald my-1"}, str(counts.get("eligible", 0))),
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "Meets 100% of criteria")
                ),
                html.div(
                    {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Almost Eligible Candidates"),
                    html.div({"className": "text-display-sm font-headline font-bold text-light-amber my-1"}, str(counts.get("almost_eligible", 0))),
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "Within 0.5 CGPA / 1 arrear")
                ),
                html.div(
                    {"className": "p-gutter-md rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col items-center justify-center text-center"},
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant uppercase"}, "Required Skills"),
                    html.div({"className": "text-body-sm font-mono font-bold text-light-on-surface my-1 truncate w-full px-2"}, selected_company.get("required_skills", "Standard Tech Stack")),
                    html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, f"Package: {selected_company['package_lpa']:.2f} LPA")
                )
            )
            if selected_company else None
        ),

        # ==============================================================
        # TABLE 1: ELIGIBLE STUDENTS
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-md"},
            html.div(
                {"className": "flex items-center gap-2 border-b border-light-outline-variant pb-gutter-xs"},
                html.span({"className": "badge badge-emerald text-label-xs font-mono uppercase"}, "Eligible Cohort"),
                html.h2({"className": "text-title-md font-headline font-bold text-light-on-surface"}, f"Eligible Students ({len(eligible_students)})")
            ),
            (
                html.div(
                    {"className": "overflow-x-auto"},
                    html.table(
                        {"className": "w-full border-collapse text-body-sm font-mono"},
                        html.thead(
                            {"className": "border-b border-light-outline-variant bg-light-surface-container-low text-light-on-surface-variant text-label-xs"},
                            html.tr(
                                html.th({"className": "p-2.5 text-left"}, "Roll Number"),
                                html.th({"className": "p-2.5 text-left"}, "Candidate Name"),
                                html.th({"className": "p-2.5 text-left"}, "Department"),
                                html.th({"className": "p-2.5 text-right"}, "CGPA"),
                                html.th({"className": "p-2.5 text-right"}, "Backlogs"),
                                html.th({"className": "p-2.5 text-right"}, "Skill Match"),
                                html.th({"className": "p-2.5 text-center"}, "Status"),
                            )
                        ),
                        html.tbody(
                            [
                                html.tr(
                                    {
                                        "key": s["id"],
                                        "className": "border-b border-light-outline-variant hover:bg-light-surface-container-low transition-colors"
                                    },
                                    html.td({"className": "p-2.5 font-bold"}, s.get("roll_number") or "N/A"),
                                    html.td({"className": "p-2.5 font-sans font-medium text-light-on-surface"}, s["name"]),
                                    html.td({"className": "p-2.5 text-light-on-surface-variant font-sans text-body-xs"}, s["department"]),
                                    html.td({"className": "p-2.5 text-right font-bold text-light-primary"}, f"{s['current_cgpa']:.2f}"),
                                    html.td({"className": "p-2.5 text-right text-light-emerald font-bold"}, str(s["backlogs_count"])),
                                    html.td({"className": "p-2.5 text-right font-bold text-light-emerald"}, f"{s['skill_match']:.1f}%"),
                                    html.td({"className": "p-2.5 text-center"}, html.span({"className": "badge badge-emerald text-label-xs"}, "ELIGIBLE")),
                                )
                                for s in eligible_students
                            ]
                        )
                    )
                )
                if eligible_students else
                html.div(
                    {"className": "p-gutter-md text-center text-body-sm text-light-on-surface-variant"},
                    "No students currently meet the academic eligibility criteria for this recruitment drive."
                )
            )
        ),

        # ==============================================================
        # TABLE 2: ALMOST ELIGIBLE STUDENTS
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-md"},
            html.div(
                {"className": "flex items-center gap-2 border-b border-light-outline-variant pb-gutter-xs"},
                html.span({"className": "badge badge-amber text-label-xs font-mono uppercase"}, "Borderline Cohort"),
                html.h2({"className": "text-title-md font-headline font-bold text-light-on-surface"}, f"Almost Eligible Students ({len(almost_students)})")
            ),
            (
                html.div(
                    {"className": "overflow-x-auto"},
                    html.table(
                        {"className": "w-full border-collapse text-body-sm font-mono"},
                        html.thead(
                            {"className": "border-b border-light-outline-variant bg-light-surface-container-low text-light-on-surface-variant text-label-xs"},
                            html.tr(
                                html.th({"className": "p-2.5 text-left"}, "Roll Number"),
                                html.th({"className": "p-2.5 text-left"}, "Candidate Name"),
                                html.th({"className": "p-2.5 text-left"}, "Department"),
                                html.th({"className": "p-2.5 text-right"}, "CGPA"),
                                html.th({"className": "p-2.5 text-right"}, "Backlogs"),
                                html.th({"className": "p-2.5 text-right"}, "Skill Match"),
                                html.th({"className": "p-2.5 text-left"}, "Gap Analysis / Remediation"),
                            )
                        ),
                        html.tbody(
                            [
                                html.tr(
                                    {
                                        "key": s["id"],
                                        "className": "border-b border-light-outline-variant hover:bg-light-surface-container-low transition-colors"
                                    },
                                    html.td({"className": "p-2.5 font-bold"}, s.get("roll_number") or "N/A"),
                                    html.td({"className": "p-2.5 font-sans font-medium text-light-on-surface"}, s["name"]),
                                    html.td({"className": "p-2.5 text-light-on-surface-variant font-sans text-body-xs"}, s["department"]),
                                    html.td({"className": "p-2.5 text-right font-bold text-light-on-surface"}, f"{s['current_cgpa']:.2f}"),
                                    html.td({"className": "p-2.5 text-right text-light-amber font-bold"}, str(s["backlogs_count"])),
                                    html.td({"className": "p-2.5 text-right font-bold text-light-amber"}, f"{s['skill_match']:.1f}%"),
                                    html.td({"className": "p-2.5 text-left text-light-amber font-sans text-body-xs font-semibold"}, s.get("gap_text", "Close to criteria")),
                                )
                                for s in almost_students
                            ]
                        )
                    )
                )
                if almost_students else
                html.div(
                    {"className": "p-gutter-md text-center text-body-sm text-light-on-surface-variant"},
                    "No borderline candidates found within 0.5 CGPA or 1 arrear of the requirements."
                )
            )
        )
    )
