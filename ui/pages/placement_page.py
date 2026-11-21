"""
Placement Eligibility Matrix Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html, use_state
from ui.components.icons import icon_briefcase, icon_shield_check, icon_check, icon_alert
from ui.components.common import StatCard, EmptyStateCard
from ui.services.data_service import get_placement_matrix_data

@component
def PlacementPage(user):
    data, set_data = use_state(lambda: get_placement_matrix_data(user))
    filter_mode, set_filter_mode = use_state("all")

    if not data:
        data = get_placement_matrix_data(user)

    companies = data.get("companies", []) if data else []
    student = data.get("student", {}) if data else {}
    summary = data.get("summary", {}) if data else {}

    student_name = student.get("name") or (f"{user.first_name} {user.last_name}".strip() or getattr(user, 'username', 'Student') if user else 'Student')
    current_cgpa = float(student.get("current_cgpa", 0.0))
    backlogs_count = int(student.get("backlogs_count", 0))

    eligible_count = summary.get("eligible_count", summary.get("eligible_companies", sum(1 for c in companies if c.get("is_eligible"))))
    ineligible_count = summary.get("ineligible_count", max(0, len(companies) - eligible_count))

    filtered_companies = [
        c for c in companies
        if filter_mode == "all" or (filter_mode == "eligible" and c.get("is_eligible")) or (filter_mode == "ineligible" and not c.get("is_eligible"))
    ]

    company_cards = []
    for c in filtered_companies:
        reason_items = [html.small({"key": str(idx), "style": {"color": "var(--danger)", "display": "block", "fontWeight": "600"}}, f"• {r}") for idx, r in enumerate(c["reasons"])]
        company_cards.append(
            html.div(
                {"key": str(c["id"]), "className": "card", "style": {"display": "flex", "flexDirection": "column", "justifyContent": "space-between"}},
                html.div(
                    html.div(
                        {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "1rem"}},
                        html.div(
                            html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.4rem", "color": "var(--brand-navy)"}}, c["company_name"]),
                            html.span({"style": {"fontSize": "0.85rem", "color": "var(--text-muted)", "fontWeight": "600"}}, c["role_title"])
                        ),
                        html.span({"style": {"fontFamily": "var(--font-display)", "fontSize": "1.5rem", "color": "var(--brand-vermillion)"}}, f"{c['package_lpa']:.1f} LPA")
                    ),
                    # Criteria Specs
                    html.div(
                        {
                            "style": {
                                "padding": "0.85rem 1rem",
                                "backgroundColor": "#F8FAFC",
                                "borderRadius": "var(--radius-sm)",
                                "fontSize": "0.85rem",
                                "display": "flex",
                                "flexDirection": "column",
                                "gap": "0.4rem",
                                "marginBottom": "1rem",
                                "border": "1px solid var(--border-subtle)"
                            }
                        },
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "CGPA Cutoff:"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, f"Min {c['min_cgpa']:.2f} CGPA")
                        ),
                        html.div(
                            {"style": {"display": "flex", "justifyContent": "space-between"}},
                            html.span({"style": {"color": "var(--text-muted)"}}, "Max Standing Arrears:"),
                            html.span({"style": {"fontWeight": "700", "color": "var(--brand-navy)"}}, f"{c['max_backlogs']} Allowed")
                        )
                    ),
                    # Status
                    html.div(
                        {"style": {"marginBottom": "1rem"}},
                        html.div(
                            {"style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "color": "var(--success)", "fontSize": "0.875rem", "fontWeight": "700"}},
                            icon_check(16, "var(--success)"), " Eligible to Sit for Recruitment"
                        ) if c["is_eligible"] else html.div(
                            html.div({"style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "color": "var(--danger)", "fontSize": "0.875rem", "fontWeight": "700", "marginBottom": "0.25rem"}}, icon_alert(16, "var(--danger)"), " Recruitment Criteria Unmet"),
                            html.div(reason_items)
                        )
                    ),
                    html.div(
                        {"style": {"fontSize": "0.8rem", "color": "var(--text-secondary)", "padding": "0.75rem 1rem", "backgroundColor": "#FFFDF9", "borderRadius": "var(--radius-sm)", "border": "1px solid var(--border-subtle)"}},
                        html.strong({"style": {"color": "var(--brand-navy)"}}, "Key Preparation Focus: "), c["required_skills"]
                    )
                ),
                html.div(
                    {"style": {"marginTop": "1.25rem", "paddingTop": "1rem", "borderTop": "1.5px solid var(--border-subtle)"}},
                    html.span(
                        {"className": "badge badge-success" if c["is_eligible"] else "badge badge-vermillion", "style": {"width": "100%", "justifyContent": "center", "padding": "0.55rem", "fontSize": "0.8rem"}},
                        "✓ Fully Qualified" if c["is_eligible"] else "⚠️ CGPA/Arrear Gap"
                    )
                )
            )
        )

    # Placement Readiness Score Progress Meter Card
    readiness = data.get("placement_readiness") or {}
    score = readiness.get("score", 0) if isinstance(readiness, dict) else int(readiness or 0)
    tip = readiness.get("tip", "") if isinstance(readiness, dict) else ""
    cgpa_part = readiness.get("cgpa_part", 0) if isinstance(readiness, dict) else 0
    backlog_part = readiness.get("backlog_part", 0) if isinstance(readiness, dict) else 0
    company_part = readiness.get("company_part", 0) if isinstance(readiness, dict) else 0
    meter_color = "var(--danger)" if score < 40 else ("var(--brand-vermillion)" if score < 70 else "var(--success)")

    readiness_meter_card = html.div(
        {"className": "card", "style": {"marginBottom": "2rem", "borderLeft": f"4px solid {meter_color}"}},
        html.div(
            {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1rem", "flexWrap": "wrap", "gap": "1rem"}},
            html.div(
                html.h3({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)"}}, "Institutional Placement Readiness Meter"),
                html.p({"style": {"fontSize": "0.85rem", "color": "var(--text-secondary)", "marginTop": "0.2rem"}}, "Automated weighting: 50% CGPA • 30% Backlogs Clearance • 20% Company Cutoff Coverage")
            ),
            html.div(
                {"style": {"display": "flex", "alignItems": "baseline", "gap": "0.35rem"}},
                html.span({"style": {"fontFamily": "var(--font-display)", "fontSize": "2.25rem", "color": meter_color, "lineHeight": "1"}}, str(score)),
                html.span({"style": {"color": "var(--text-muted)", "fontSize": "1rem", "fontWeight": "700"}}, "/ 100")
            )
        ),
        # Progress Bar Meter
        html.div(
            {"style": {"height": "12px", "width": "100%", "backgroundColor": "var(--border-subtle)", "borderRadius": "6px", "overflow": "hidden", "marginBottom": "1rem"}},
            html.div({"style": {"width": f"{score}%", "height": "100%", "backgroundColor": meter_color, "transition": "width 0.4s ease"}})
        ),
        # Component Breakdown Badges
        html.div(
            {"style": {"display": "flex", "gap": "0.75rem", "marginBottom": "1rem", "flexWrap": "wrap"}},
            html.span({"className": "badge badge-cyan"}, f"CGPA Weight: {cgpa_part:.1f} / 50"),
            html.span({"className": "badge badge-success" if backlog_part == 30 else "badge badge-warning"}, f"Zero-Arrears Weight: {backlog_part:.1f} / 30"),
            html.span({"className": "badge badge-vermillion"}, f"Company Criteria: {company_part:.1f} / 20")
        ),
        # Improvement Priority Tip
        html.div(
            {"style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "fontSize": "0.875rem", "fontWeight": "600", "backgroundColor": "var(--bg-surface-elevated)", "padding": "0.75rem 1rem", "borderRadius": "var(--radius-sm)", "border": "1px solid var(--border-subtle)"}},
            html.span({"style": {"color": meter_color, "fontWeight": "800"}}, "💡 Improvement Priority:"),
            html.span({"style": {"color": "var(--brand-navy)"}}, tip)
        )
    )

    return html.div(
        # Header & Filter
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
                    "Corporate Recruitment & Placement Matrix"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, f"Instant criteria audit for {student_name} (CGPA {current_cgpa:.2f}, {backlogs_count} standing arrears)")
            ),
            html.div(
                {"style": {"display": "flex", "gap": "0.5rem", "backgroundColor": "var(--bg-surface-elevated)", "border": "1px solid var(--border-subtle)", "padding": "0.3rem", "borderRadius": "var(--radius-full)"}},
                html.button(
                    {"className": "btn", "style": {"padding": "0.4rem 1rem", "fontSize": "0.8rem", "backgroundColor": "var(--brand-vermillion)" if filter_mode == "all" else "transparent", "color": "#FFFFFF" if filter_mode == "all" else "var(--text-primary)"}, "on_click": lambda e: set_filter_mode("all")},
                    f"All ({len(companies)})"
                ),
                html.button(
                    {"className": "btn", "style": {"padding": "0.4rem 1rem", "fontSize": "0.8rem", "backgroundColor": "var(--brand-vermillion)" if filter_mode == "eligible" else "transparent", "color": "#FFFFFF" if filter_mode == "eligible" else "var(--text-primary)"}, "on_click": lambda e: set_filter_mode("eligible")},
                    f"Eligible ({eligible_count})"
                ),
                html.button(
                    {"className": "btn", "style": {"padding": "0.4rem 1rem", "fontSize": "0.8rem", "backgroundColor": "var(--brand-vermillion)" if filter_mode == "ineligible" else "transparent", "color": "#FFFFFF" if filter_mode == "ineligible" else "var(--text-primary)"}, "on_click": lambda e: set_filter_mode("ineligible")},
                    f"Ineligible ({ineligible_count})"
                )
            )
        ),

        # Top Summary KPIs
        html.div(
            {"className": "stat-grid", "style": {"marginBottom": "2rem"}},
            StatCard(
                label="Total Companies Audited",
                value=str(len(companies)),
                subtitle="Tier-1 Tech & MNC recruitments",
                icon=icon_briefcase(26, "var(--brand-navy)")
            ),
            StatCard(
                label="Eligible Opportunities",
                value=str(eligible_count),
                subtitle=f"Qualification rate: {int(eligible_count / (len(companies) or 1) * 100)}%",
                icon=icon_check(26, "var(--brand-vermillion)"),
                value_color="var(--brand-vermillion)"
            ),
            StatCard(
                label="Top Package Reached",
                value=f"{max([c['package_lpa'] for c in companies if c['is_eligible']] or [0]):.1f} LPA",
                subtitle="Highest qualifying annual package",
                icon=icon_shield_check(26, "#10B981")
            )
        ),

        # Placement Readiness Score Progress Meter
        readiness_meter_card,

        # Company Cards Grid
        html.div(
            {"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "1.75rem"}},
            company_cards if company_cards else [
                EmptyStateCard(
                    title="No companies have been added yet.",
                    description="Placement coordinators have not published corporate recruitment criteria yet."
                )
            ]
        )
    )
