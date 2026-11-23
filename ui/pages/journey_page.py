"""
My Journey & Milestone Badges Component for EduGrade AI ReactPy Frontend.
Displays vertical timeline evolution of semesters and gamified career readiness badge shelf.
"""

from reactpy import component, html
from ui.services.data_service import get_journey_and_badges

@component
def JourneyPage(user):
    data = get_journey_and_badges(user)
    journey = data.get("journey", [])
    badges_data = data.get("badges", {})
    all_badges = badges_data.get("all_badges", [])
    earned_count = len(badges_data.get("earned_badges", []))

    # Empty state check
    if not journey:
        return html.div(
            {"className": "p-gutter-xl max-w-5xl mx-auto flex flex-col gap-gutter-xl animate-fade-in"},
            html.div(
                {"className": "border-b border-light-outline-variant pb-gutter-md"},
                html.h1({"className": "text-display-sm font-headline font-bold text-light-on-surface"}, "My Academic Journey"),
                html.p({"className": "text-body-md text-light-on-surface-variant mt-1"}, "Chronological performance timeline and career milestone badges.")
            ),
            html.div(
                {"className": "p-gutter-xl text-center border border-dashed border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest"},
                html.span({"className": "material-symbols-outlined text-light-on-surface-variant text-[48px]"}, "timeline"),
                html.h3({"className": "text-title-md font-headline font-bold text-light-on-surface mt-2"}, "Your journey starts when your first results are published."),
                html.p({"className": "text-body-sm text-light-on-surface-variant max-w-md mx-auto mt-1"}, "Semester milestones and achievement badges will automatically activate once examinations are completed and published.")
            )
        )

    return html.div(
        {"className": "p-gutter-xl max-w-5xl mx-auto flex flex-col gap-gutter-xl animate-fade-in"},

        # Header Title
        html.div(
            {"className": "border-b border-light-outline-variant pb-gutter-md flex justify-between items-end"},
            html.div(
                html.h1({"className": "text-headline-md font-headline font-bold text-light-on-surface uppercase"}, "My Journey"),
                html.p({"className": "text-mono-sm font-mono text-light-on-surface-variant uppercase mt-1"}, "Semester timeline and achievement badges.")
            ),
            html.div(
                {"className": "badge badge-primary text-label-sm font-mono px-3 py-1.5"},
                f"{earned_count} / {len(all_badges)} Badges"
            )
        ),

        # ==============================================================
        # BADGE SHELF
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-md"},
            html.div(
                {"className": "flex items-center justify-between border-b border-light-outline-variant pb-gutter-xs"},
                html.div(
                    {"className": "flex items-center gap-2"},
                    html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "military_tech"),
                    html.h2({"className": "text-title-md font-headline font-bold text-light-on-surface uppercase"}, "Badges")
                ),
                html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, "Career Milestones")
            ),
            html.div(
                {"className": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter-sm"},
                [
                    html.div(
                        {
                            "key": b["id"],
                            "className": (
                                "p-3 rounded-radius-md border transition-all flex flex-col justify-between "
                                + ("border-light-primary bg-light-surface-container shadow-sm" if b["earned"] else "border-light-outline-variant bg-light-surface-container-low opacity-60")
                            )
                        },
                        html.div(
                            {"className": "flex items-start justify-between gap-2"},
                            html.div(
                                html.strong(
                                    {"className": "text-body-sm font-headline font-bold text-light-on-surface block"},
                                    b["name"]
                                ),
                                html.p({"className": "text-label-xs text-light-on-surface-variant mt-1"}, b["rule"])
                            ),
                            html.span(
                                {
                                    "className": (
                                        "badge font-mono text-label-xs shrink-0 "
                                        + (b.get("badge_class", "badge-primary") if b["earned"] else "bg-light-outline-variant text-light-on-surface-variant")
                                    )
                                },
                                "UNLOCKED" if b["earned"] else "LOCKED"
                            )
                        )
                    )
                    for b in all_badges
                ]
            )
        ),

        # ==============================================================
        # VERTICAL TIMELINE
        # ==============================================================
        html.div(
            {"className": "card p-gutter-lg border border-light-outline-variant rounded-radius-lg bg-light-surface-container-lowest shadow-sm flex flex-col gap-gutter-lg"},
            html.div(
                {"className": "flex items-center gap-2 border-b border-light-outline-variant pb-gutter-xs"},
                html.span({"className": "material-symbols-outlined text-light-primary text-[22px]"}, "timeline"),
                html.h2({"className": "text-title-md font-headline font-bold text-light-on-surface"}, "Chronological Semester Timeline")
            ),

            html.div(
                {"className": "relative pl-6 border-l-2 border-light-outline-variant flex flex-col gap-gutter-xl ml-2"},
                [
                    html.div(
                        {
                            "key": s["semester_number"],
                            "className": "relative flex flex-col gap-2"
                        },
                        # Node circle on the timeline
                        html.div({
                            "className": (
                                "absolute -left-[31px] top-1 w-4 h-4 rounded-radius-full border-2 border-light-surface-container-lowest "
                                + ("bg-light-emerald" if s["change"] == "up" else "bg-light-danger" if s["change"] == "down" else "bg-light-primary")
                            )
                        }),

                        # Semester Title & SGPA badge
                        html.div(
                            {"className": "flex items-center justify-between"},
                            html.div(
                                {"className": "flex items-center gap-2"},
                                html.span({"className": "text-title-sm font-headline font-bold text-light-on-surface"}, f"Semester {s['semester_number']}"),
                                html.span(
                                    {
                                        "className": (
                                            "badge font-mono text-label-xs "
                                            + ("badge-emerald" if s["change"] == "up" else "badge-danger" if s["change"] == "down" else "badge-primary")
                                        )
                                    },
                                    f"SGPA: {s['sgpa']:.2f}"
                                ),
                                html.span(
                                    {"className": "text-label-xs font-mono text-light-on-surface-variant"},
                                    f"(+{s['diff']:.2f})" if s["diff"] > 0 else f"({s['diff']:.2f})" if s["diff"] < 0 else "(=)"
                                )
                            ),
                            html.span({"className": "text-label-xs font-mono text-light-on-surface-variant"}, f"{s['credits_earned']} Credits")
                        ),

                        # Highlight Box
                        html.div(
                            {"className": "p-3 rounded-radius-md bg-light-surface-container-low border border-light-outline-variant text-body-sm"},
                            html.p({"className": "text-light-on-surface font-medium"}, s["highlight"]),
                            html.div(
                                {"className": "grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-2 border-t border-light-outline-variant text-label-xs font-mono text-light-on-surface-variant"},
                                html.div(
                                    "🌟 Top Course: ",
                                    html.strong({"className": "text-light-on-surface"}, f"{s['best_course']['name']} ({s['best_course']['grade']})") if s.get("best_course") else "None"
                                ),
                                html.div(
                                    "⚡ Challenging: ",
                                    html.strong({"className": "text-light-on-surface"}, f"{s['hardest_course']['name']} ({s['hardest_course']['grade']})") if s.get("hardest_course") else "None"
                                )
                            )
                        )
                    )
                    for s in journey
                ]
            )
        )
    )
