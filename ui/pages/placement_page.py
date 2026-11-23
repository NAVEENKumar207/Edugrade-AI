"""
Placement Eligibility Matrix Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/placement_eligibility_matrix/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import get_placement_matrix_data

@component
def PlacementPage(user):
    data, set_data = use_state(lambda: get_placement_matrix_data(user))
    filter_mode, set_filter_mode = use_state("all")
    search_query, set_search_query = use_state("")

    if not data:
        data = get_placement_matrix_data(user)

    companies = data.get("companies", []) if data else []
    student = data.get("student", {}) if data else {}
    summary = data.get("summary", {}) if data else {}
    readiness = data.get("placement_readiness", {})

    current_cgpa = float(student.get("current_cgpa", 8.64))
    backlogs_count = int(student.get("backlogs_count", 0))

    eligible_count = summary.get("eligible_count", sum(1 for c in companies if c.get("is_eligible")))
    total_count = len(companies)
    ineligible_count = max(0, total_count - eligible_count)

    # Filter logic
    q = search_query.strip().lower()
    filtered_companies = []
    for c in companies:
        c_name = str(c.get("company_name", "")).lower()
        r_title = str(c.get("role_title", "")).lower()
        skills = str(c.get("required_skills", "")).lower()

        if q and not (q in c_name or q in r_title or q in skills):
            continue

        is_el = c.get("is_eligible", False)
        if filter_mode == "eligible" and not is_el:
            continue
        if filter_mode == "ineligible" and is_el:
            continue

        filtered_companies.append(c)

    # Filter tab buttons
    tabs = [
        ("all", f"All Drives ({total_count})"),
        ("eligible", f"Eligible ({eligible_count})"),
        ("ineligible", f"Action Needed ({ineligible_count})")
    ]

    filter_buttons = []
    for mode_key, mode_label in tabs:
        def make_tab_handler(m):
            def handle_click(e):
                set_filter_mode(m)
            return handle_click

        is_active = (filter_mode == mode_key)
        filter_buttons.append(
            html.button(
                {
                    "key": mode_key,
                    "type": "button",
                    "on_click": make_tab_handler(mode_key),
                    "class_name": "px-3 py-2 font-mono text-mono-sm uppercase whitespace-nowrap cursor-pointer transition-colors duration-state-change " +
                        ("bg-light-primary text-light-on-primary font-bold" if is_active else "bg-light-surface-container-lowest border border-light-outline-variant text-light-on-surface-variant hover:bg-light-surface-container-low")
                },
                mode_label
            )
        )

    # Company cards
    cards = []
    for c in filtered_companies:
        is_el = c.get("is_eligible", False)
        c_name = c.get("company_name", "Company")
        r_title = c.get("role_title", "Role")
        pkg = float(c.get("package_lpa", 0.0))
        min_cgpa = float(c.get("min_cgpa", 7.0))
        max_arr = int(c.get("max_backlogs", 0))
        skills_str = c.get("required_skills", "") or ""
        skill_tags = [s.strip() for s in skills_str.split(",") if s.strip()] if skills_str else ["Engineering Fundamentals"]
        reasons = c.get("reasons", [])

        cgpa_diff = current_cgpa - min_cgpa

        if is_el:
            status_badge = html.span(
                {"class_name": "px-2.5 py-1 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm uppercase whitespace-nowrap shrink-0"},
                "Eligible"
            )
            footer_text = f"Clears CGPA cutoff by +{cgpa_diff:.2f} points." if cgpa_diff >= 0 else "Eligible based on relaxed institutional criteria."
            footer_cls = "text-light-secondary font-semibold"
        else:
            status_badge = html.span(
                {"class_name": "px-2.5 py-1 rounded-full bg-light-primary-container text-light-on-primary-container font-mono text-mono-sm uppercase whitespace-nowrap shrink-0 font-bold"},
                f"{abs(cgpa_diff):.2f} Short" if cgpa_diff < 0 else "Ineligible"
            )
            footer_text = " • ".join(reasons) if reasons else f"Current CGPA ({current_cgpa:.2f}) is below minimum ({min_cgpa:.2f})."
            footer_cls = "text-light-error font-medium"

        cards.append(
            html.article(
                {"key": str(c.get("id", c_name)), "class_name": "company-card h-full bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col justify-between gap-gutter-md"},
                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm"},
                    html.header(
                        {"class_name": "flex items-start justify-between gap-gutter-sm"},
                        html.div(
                            html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase font-bold"}, c_name),
                            html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, r_title)
                        ),
                        status_badge
                    ),
                    html.div(
                        {"class_name": "flex items-center gap-2 font-mono text-mono-sm text-light-on-surface tabular-nums flex-wrap"},
                        html.span({"class_name": "font-bold text-light-primary"}, f"{pkg:.1f} LPA"),
                        html.span("•"),
                        html.span(f"Min {min_cgpa:.2f} CGPA"),
                        html.span("•"),
                        html.span("0 Arrears" if max_arr == 0 else f"Max {max_arr} Arrear")
                    ),
                    html.div(
                        {"class_name": "flex flex-wrap gap-1.5 pt-1"},
                        [
                            html.span(
                                {"key": st, "class_name": "px-2 py-0.5 rounded bg-light-surface-container-low border border-light-outline-variant font-mono text-label-sm text-light-on-surface"},
                                st
                            ) for st in skill_tags[:4]
                        ]
                    )
                ),
                html.footer(
                    {"class_name": "pt-gutter-sm border-t border-light-outline-variant"},
                    html.p({"class_name": f"font-body text-body-sm {footer_cls}"}, footer_text)
                )
            )
        )

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "Placement Eligibility Matrix"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"{current_cgpa:.2f} CGPA • {backlogs_count} Active Arrears • {total_count} Corporate Recruitment Drives")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm"},
                html.span(
                    {"class_name": "inline-flex items-center gap-gutter-xs px-3 py-1.5 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm uppercase whitespace-nowrap font-bold"},
                    html.span({"class_name": "material-symbols-outlined text-[14px]"}, "verified"),
                    html.span(f"{eligible_count} / {total_count} Eligible")
                )
            )
        ),

        # Filter & Search Controls
        html.section(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md"},
            html.div(
                {"class_name": "flex flex-wrap items-center gap-gutter-xs"},
                filter_buttons
            ),
            html.div(
                {"class_name": "w-full sm:w-auto flex items-center border border-light-outline-variant bg-light-surface-container-lowest px-3 py-1.5"},
                html.span({"class_name": "material-symbols-outlined text-light-on-surface-variant text-[18px] mr-2"}, "search"),
                html.input(
                    {
                        "type": "search",
                        "placeholder": "Search company or skill...",
                        "value": search_query,
                        "on_change": lambda e: set_search_query(e.get("target", {}).get("value", "")),
                        "class_name": "border-none bg-transparent p-0 font-mono text-mono-sm text-light-on-surface focus:outline-none focus:ring-0 w-full sm:w-64"
                    }
                )
            )
        ),

        # Company Cards Grid
        html.section(
            {"class_name": "grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-gutter-lg items-stretch"},
            cards if cards else [
                html.div(
                    {"class_name": "col-span-full p-12 text-center border border-light-outline-variant bg-light-surface-container-lowest"},
                    html.span({"class_name": "material-symbols-outlined text-[48px] text-light-outline"}, "work_off"),
                    html.p({"class_name": "font-headline text-title-lg text-light-on-surface mt-2"}, "No Company Criteria Found"),
                    html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant mt-1"}, "No placement criteria matched the current filter criteria.")
                )
            ]
        )
    )
