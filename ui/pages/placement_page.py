"""
Placement Eligibility Matrix Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/placement_eligibility_matrix/code.html.
"""

from reactpy import component, html, use_state
from ui.services.data_service import get_placement_matrix_data, get_skills_and_fit

@component
def PlacementPage(user):
    data, set_data = use_state(lambda: get_placement_matrix_data(user))
    skills_data, set_skills_data = use_state(lambda: get_skills_and_fit(user))
    filter_mode, set_filter_mode = use_state("all")
    search_query, set_search_query = use_state("")

    if not data:
        data = get_placement_matrix_data(user)
    if not skills_data:
        skills_data = get_skills_and_fit(user)

    companies = data.get("companies", []) if data else []
    student = data.get("student", {}) if data else {}
    summary = data.get("summary", {}) if data else {}
    readiness = data.get("placement_readiness", {})

    skills_dict = skills_data.get("skills", {})
    companies_fit = skills_data.get("companies", [])
    fit_lookup = {f["company_id"]: f for f in companies_fit if "company_id" in f}

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
        ("all", f"All ({total_count})"),
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
        fit_info = fit_lookup.get(c.get("id"), {})
        fit_lbl = fit_info.get("fit_label", "Ready" if is_el else "Not yet")
        match_pct = fit_info.get("match_percent", 75.0 if is_el else 40.0)
        weak_sk = fit_info.get("weak_skills", [])
        uncov_sk = fit_info.get("uncovered_skills", [])
        imp_tip = fit_info.get("improvement_tip", "")

        fit_badge_cls = (
            "badge-emerald" if fit_lbl == "Ready" else
            "badge-amber" if fit_lbl == "Almost" else
            "bg-light-surface-container-high text-light-on-surface-variant border border-light-outline-variant"
        )

        cards.append(
            html.article(
                {"key": str(c.get("id", c_name)), "class_name": "company-card h-full bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col justify-between gap-gutter-md rounded-radius-md"},
                html.div(
                    {"class_name": "flex flex-col gap-gutter-sm"},
                    html.header(
                        {"class_name": "flex items-start justify-between gap-gutter-sm"},
                        html.div(
                            html.h2({"class_name": "font-headline text-title-lg text-light-on-surface uppercase font-bold"}, c_name),
                            html.p({"class_name": "font-body text-body-sm text-light-on-surface-variant"}, r_title)
                        ),
                        html.div(
                            {"class_name": "flex flex-col items-end gap-1"},
                            html.span({"class_name": f"badge font-mono text-label-xs font-bold uppercase {fit_badge_cls}"}, f"Fit: {fit_lbl}"),
                            html.span({"class_name": "text-label-xs font-mono text-light-on-surface-variant"}, f"{match_pct:.0f}% Match")
                        )
                    ),
                    html.div(
                        {"class_name": "flex items-center gap-2 font-mono text-mono-sm text-light-on-surface tabular-nums flex-wrap"},
                        html.span({"class_name": "font-bold text-light-primary"}, f"{pkg:.1f} LPA"),
                        html.span("•"),
                        html.span(f"Min {min_cgpa:.2f} CGPA"),
                        html.span("•"),
                        html.span("0 Arrears" if max_arr == 0 else f"Max {max_arr} Arrear")
                    ),

                    # Skill Match Bar
                    html.div(
                        {"class_name": "flex flex-col gap-1"},
                        html.div(
                            {"class_name": "h-1.5 w-full bg-light-surface-container rounded-radius-full overflow-hidden"},
                            html.div({
                                "class_name": "h-full " + ("bg-light-emerald" if match_pct >= 70 else "bg-light-amber" if match_pct >= 40 else "bg-light-danger"),
                                "style": {"width": f"{match_pct}%"}
                            })
                        )
                    ),

                    # Required Skills & Weak/Uncovered Tags
                    html.div(
                        {"class_name": "flex flex-wrap gap-1.5 pt-1"},
                        [
                            html.span(
                                {"key": st, "class_name": "px-2 py-0.5 rounded bg-light-surface-container-low border border-light-outline-variant font-mono text-label-xs text-light-on-surface"},
                                st
                            ) for st in skill_tags[:4]
                        ],
                        [
                            html.span(
                                {"key": f"w_{w}", "class_name": "badge badge-amber text-label-xs font-mono"},
                                f"Weak: {w}"
                            ) for w in weak_sk[:2]
                        ],
                        [
                            html.span(
                                {"key": f"u_{u}", "class_name": "badge bg-light-surface-container text-light-on-surface-variant text-label-xs font-mono border border-light-outline-variant"},
                                f"No Course: {u}"
                            ) for u in uncov_sk[:2]
                        ]
                    )
                ),
                html.footer(
                    {"class_name": "pt-gutter-sm border-t border-light-outline-variant flex flex-col gap-1"},
                    html.p({"class_name": "font-body text-body-xs text-light-on-surface font-medium"}, imp_tip if imp_tip else ("Clears cutoff criteria." if is_el else f"{abs(cgpa_diff):.2f} CGPA short."))
                )
            )
        )

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "Placements"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"{current_cgpa:.2f} CGPA • {backlogs_count} Arrears • {total_count} Drives")
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

        # Academic Skill Map & Gap Analysis Section
        html.section(
            {"class_name": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest flex flex-col gap-gutter-md"},
            html.div(
                {"class_name": "flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-light-outline-variant pb-gutter-xs"},
                html.div(
                    {"class_name": "flex items-center gap-2"},
                    html.span({"class_name": "material-symbols-outlined text-light-primary text-[22px]"}, "psychology"),
                    html.h2({"class_name": "font-headline text-title-md text-light-on-surface font-bold uppercase"}, "Skill Map")
                ),
                html.span({"class_name": "text-label-xs font-mono text-light-on-surface-variant"}, "Derived from completed coursework")
            ),
            (
                html.div(
                    {"class_name": "p-6 text-center text-light-on-surface-variant font-mono text-body-sm border border-dashed border-light-outline-variant rounded-radius-md"},
                    "No skill mapping available yet."
                )
                if not skills_dict else
                html.div(
                    {"class_name": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter-md"},
                    [
                        html.div(
                            {
                                "key": sk_name,
                                "class_name": "p-3 rounded-radius-md border border-light-outline-variant bg-light-surface-container-low flex flex-col gap-1.5"
                            },
                            html.div(
                                {"class_name": "flex justify-between items-center"},
                                html.strong({"class_name": "text-body-sm font-headline text-light-on-surface"}, sk_name),
                                html.span(
                                    {
                                        "class_name": (
                                            "font-mono text-label-sm font-bold "
                                            + ("text-light-emerald" if sk_info["score"] >= 70 else "text-light-amber" if sk_info["score"] >= 50 else "text-light-danger")
                                        )
                                    },
                                    f"{sk_info['score']:.1f}%"
                                )
                            ),
                            # CSS Bar
                            html.div(
                                {"class_name": "h-2 w-full bg-light-surface-container rounded-radius-full overflow-hidden"},
                                html.div({
                                    "class_name": (
                                        "h-full "
                                        + ("bg-light-emerald" if sk_info["score"] >= 70 else "bg-light-amber" if sk_info["score"] >= 50 else "bg-light-danger")
                                    ),
                                    "style": {"width": f"{sk_info['score']}%"}
                                })
                            ),
                            html.div(
                                {"class_name": "flex justify-between text-label-xs font-mono text-light-on-surface-variant mt-1"},
                                html.span(f"{sk_info['total_credits']} Credits"),
                                html.span(f"Avg GP: {sk_info['avg_grade_point']:.1f}")
                            )
                        )
                        for sk_name, sk_info in skills_dict.items()
                    ]
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
