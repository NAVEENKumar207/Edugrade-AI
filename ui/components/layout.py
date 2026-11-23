"""
Layout Component for EduGrade AI ReactPy Frontend.
Implements the Swiss-Brutalist 'Industrial Academic Precision' layout from New Ui.
Pairs a persistent 256px architectural left rail with an exposed 1px hairline border top shell.
Includes responsive mobile drawer navigation and accessibility attributes.
"""

from reactpy import component, html, use_state
from ui.components.theme_toggle import ThemeToggle


@component
def AppLayout(user, current_page, set_page, logout_action, children, theme="light", toggle_theme=None):
    mobile_open, set_mobile_open = use_state(False)
    profile = getattr(user, 'profile', None)
    is_admin = profile.is_admin() if profile else False
    cgpa_val = float(profile.current_cgpa) if profile else 0.0
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username if user else "Student"
    
    # Compute 2-letter initials
    initials = "".join([part[0].upper() for part in full_name.split()[:2]]) or "EG"
    roll_no = profile.roll_number if profile and profile.roll_number else (user.email if user else "2026")
    dept = profile.department if profile and profile.department else "Computer Science"
    curr_sem = f"Sem {profile.current_semester}" if profile else "CBCS"

    if is_admin:
        nav_items = [
            {"id": "admin_dashboard", "label": "Cohort Directory", "icon": "groups"},
            {"id": "drives", "label": "Placement Drives", "icon": "business_center"},
            {"id": "regulations", "label": "Regulations", "icon": "menu_book"},
            {"id": "profile", "label": "Profile", "icon": "person"},
        ]
        page_title = "Faculty Oversight"
        page_subtitle = f"{dept.upper()} • AUDIT DIRECTORY"
    else:
        nav_items = [
            {"id": "dashboard", "label": "Dashboard", "icon": "dashboard"},
            {"id": "future_lab", "label": "Future Lab", "icon": "model_training"},
            {"id": "results", "label": "Transcripts", "icon": "receipt_long"},
            {"id": "planner", "label": "CGPA Planner", "icon": "calculate"},
            {"id": "placements", "label": "Placements", "icon": "work"},
            {"id": "journey", "label": "My Journey", "icon": "route"},
            {"id": "advisor", "label": "AI Advisor", "icon": "psychology"},
            {"id": "regulations", "label": "Regulations", "icon": "menu_book"},
            {"id": "profile", "label": "Profile", "icon": "person"},
        ]
        page_title = "Student Dashboard"
        page_subtitle = f"{dept.upper()} • CBCS 2026"

    nav_links = []
    for item in nav_items:
        is_active = (
            (current_page == item["id"])
            or (item["id"] == "dashboard" and current_page in ["dashboard", "student_dashboard"])
            or (item["id"] == "placements" and current_page in ["placements", "placement"])
            or (item["id"] == "advisor" and current_page in ["advisor", "ai_advisor", "ai-advisor"])
            or (item["id"] == "future_lab" and current_page in ["future_lab", "futurelab", "twin"])
            or (item["id"] == "admin_dashboard" and current_page in ["admin_dashboard", "admin", "cohort"])
            or (item["id"] == "drives" and current_page in ["drives", "drive_manager"])
            or (item["id"] == "regulations" and current_page in ["regulations", "syllabus"])
        )
        
        link_class = (
            "flex items-center gap-gutter-sm px-3 py-2.5 bg-light-secondary text-light-on-secondary font-label text-label-lg transition-colors duration-state-change ease-state-change cursor-pointer"
            if is_active else
            "flex items-center gap-gutter-sm px-3 py-2.5 text-light-on-surface-variant hover:bg-light-surface-container-low hover:text-light-on-surface font-label text-label-lg transition-colors duration-state-change ease-state-change cursor-pointer"
        )
        
        nav_links.append(
            html.a(
                {
                    "key": item["id"],
                    "className": link_class,
                    "on_click": lambda e, pid=item["id"]: (set_page(pid), set_mobile_open(False))
                },
                html.span(
                    {
                        "className": "material-symbols-outlined text-[20px]",
                        "style": {"fontVariationSettings": "'FILL' 1" if is_active else "'FILL' 0"}
                    },
                    item["icon"]
                ),
                html.span({"className": "truncate"}, item["label"])
            )
        )

    return html.div(
        {"className": "min-h-screen flex bg-light-surface-container-low font-body antialiased relative"},
        
        # Persistent 256px Desktop Left Sidebar
        html.aside(
            {"className": "hidden md:flex w-64 shrink-0 min-h-screen bg-light-surface-container-lowest border-r border-light-outline-variant flex-col justify-between"},
            html.div(
                {"className": "p-gutter-lg flex flex-col gap-gutter-xl"},
                
                # Brand Logo & Title Header
                html.div(
                    {
                        "className": "flex items-center gap-3 cursor-pointer",
                        "on_click": lambda e: set_page("landing")
                    },
                    html.div(
                        {
                            "className": "w-10 h-10 bg-light-primary flex items-center justify-center font-display font-bold text-white text-lg shrink-0",
                            "style": {"borderRadius": "0px"}
                        },
                        "EG"
                    ),
                    html.div(
                        {"className": "flex flex-col"},
                        html.div(
                            {"className": "font-headline text-lg font-bold uppercase tracking-tight text-light-on-surface"},
                            "EduGrade ",
                            html.span({"className": "text-light-primary"}, "AI")
                        ),
                        html.span(
                            {"className": "font-mono text-[10px] text-light-on-surface-variant uppercase tracking-wider"},
                            "Academic Precision"
                        )
                    )
                ),
                
                # Navigation items
                html.nav(
                    {"aria-label": "Portal Navigation", "className": "flex flex-col gap-1"},
                    nav_links
                )
            ),
            
            # Bottom User Identity & Controls
            html.div(
                {"className": "p-gutter-md border-t border-light-outline-variant flex flex-col gap-2"},
                
                # User profile pill
                html.div(
                    {
                        "className": "flex items-center justify-between gap-gutter-sm cursor-pointer hover:bg-light-surface-container-low p-1.5 transition-colors",
                        "on_click": lambda e: set_page("profile"),
                        "title": "View Profile"
                    },
                    html.div(
                        {"className": "flex items-center gap-gutter-sm min-w-0"},
                        html.div(
                            {"className": "w-9 h-9 bg-light-secondary text-light-on-secondary flex items-center justify-center font-mono text-mono-sm shrink-0 font-bold"},
                            initials
                        ),
                        html.div(
                            {"className": "flex flex-col min-w-0"},
                            html.span({"className": "font-title text-title-md text-light-on-surface truncate font-semibold"}, full_name),
                            html.span({"className": "font-mono text-mono-sm text-light-on-surface-variant truncate"}, f"{roll_no} • {curr_sem}")
                        )
                    )
                ),
                
                # Quick Action Row: Theme toggle + Sign out
                html.div(
                    {"className": "flex items-center justify-between pt-1 border-t border-light-outline-variant/60"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else html.span(),
                    html.button(
                        {
                            "type": "button",
                            "aria-label": "Sign out",
                            "className": "inline-flex items-center gap-1.5 px-3 py-1.5 text-light-on-surface-variant hover:bg-light-surface-container-low hover:text-light-primary font-mono text-mono-sm uppercase transition-colors shrink-0 cursor-pointer",
                            "on_click": lambda e: logout_action()
                        },
                        html.span({"className": "material-symbols-outlined text-[18px]"}, "logout"),
                        html.span("Sign Out")
                    )
                )
            )
        ),

        # Mobile Navigation Drawer (Hidden on Desktop)
        (
            html.div(
                {"className": "fixed inset-0 z-50 md:hidden bg-light-on-surface/50 flex"},
                html.div(
                    {"className": "w-72 max-w-[85vw] bg-light-surface-container-lowest h-full p-4 flex flex-col justify-between shadow-2xl overflow-y-auto border-r border-light-outline-variant"},
                    html.div(
                        {"className": "flex flex-col gap-4"},
                        html.div(
                            {"className": "flex items-center justify-between pb-3 border-b border-light-outline-variant"},
                            html.div(
                                {"className": "flex items-center gap-2 cursor-pointer", "on_click": lambda e: (set_page("landing"), set_mobile_open(False))},
                                html.div({"className": "w-8 h-8 bg-light-primary text-white font-bold flex items-center justify-center font-display text-sm"}, "EG"),
                                html.span({"className": "font-headline font-bold uppercase"}, "EduGrade AI")
                            ),
                            html.button(
                                {
                                    "type": "button",
                                    "aria-label": "Close navigation menu",
                                    "className": "p-1.5 text-light-on-surface hover:text-light-primary cursor-pointer",
                                    "on_click": lambda e: set_mobile_open(False)
                                },
                                html.span({"className": "material-symbols-outlined text-[20px]"}, "close")
                            )
                        ),
                        html.nav({"aria-label": "Mobile Navigation", "className": "flex flex-col gap-1"}, nav_links)
                    ),
                    html.div(
                        {"className": "pt-4 border-t border-light-outline-variant flex flex-col gap-2"},
                        html.div(
                            {"className": "flex items-center justify-between"},
                            ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else html.span(),
                            html.button(
                                {
                                    "type": "button",
                                    "aria-label": "Sign out",
                                    "className": "inline-flex items-center gap-1.5 px-3 py-1.5 text-light-on-surface-variant hover:text-light-primary font-mono text-mono-sm uppercase cursor-pointer",
                                    "on_click": lambda e: (set_mobile_open(False), logout_action())
                                },
                                html.span({"className": "material-symbols-outlined text-[18px]"}, "logout"),
                                html.span("Sign Out")
                            )
                        )
                    )
                ),
                html.div(
                    {"className": "flex-1 cursor-pointer", "on_click": lambda e: set_mobile_open(False)}
                )
            )
            if mobile_open else None
        ),
        
        # Main Workspace Column
        html.div(
            {"className": "flex-1 flex flex-col min-w-0"},
            
            # Top Shell Header
            html.header(
                {"className": "bg-light-surface-container-lowest border-b border-light-outline-variant px-gutter-lg py-gutter-md flex items-center justify-between gap-gutter-md sticky top-0 z-20"},
                html.div(
                    {"className": "flex items-center gap-gutter-md"},
                    html.button(
                        {
                            "type": "button",
                            "aria-label": "Toggle navigation menu",
                            "className": "md:hidden flex items-center justify-center p-1.5 text-light-on-surface border border-light-outline-variant hover:bg-light-surface-container cursor-pointer",
                            "on_click": lambda e: set_mobile_open(not mobile_open)
                        },
                        html.span({"className": "material-symbols-outlined text-[20px]"}, "menu" if not mobile_open else "close")
                    ),
                    html.div(
                        html.h1({"className": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight font-bold"}, page_title),
                        html.p({"className": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, page_subtitle)
                    )
                ),
                
                # Status badges & metrics
                html.div(
                    {"className": "flex items-center gap-gutter-sm"},
                    ThemeToggle(theme=theme, toggle_theme=toggle_theme, compact=True) if toggle_theme else None,
                    (
                        html.span(
                            {"className": "inline-flex items-center gap-gutter-xs px-3 py-1.5 rounded-full bg-light-primary text-white font-mono text-mono-sm uppercase whitespace-nowrap shrink-0 font-bold"},
                            html.span({"className": "material-symbols-outlined text-[15px]"}, "shield_person"),
                            html.span("Faculty / Admin")
                        )
                        if is_admin else
                        html.span(
                            {"className": "inline-flex items-center gap-gutter-xs px-3 py-1.5 rounded-full bg-light-secondary text-light-on-secondary font-mono text-mono-sm uppercase whitespace-nowrap shrink-0"},
                            html.span({"className": "material-symbols-outlined text-[15px]"}, "verified"),
                            html.span(f"CGPA: {cgpa_val:.2f} • {'Placement Eligible' if getattr(profile, 'is_placement_eligible', True) else 'Remediation Needed'}")
                        )
                    )
                )
            ),
            
            # Main Content Canvas
            html.main(
                {"className": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg"},
                children
            )
        )
    )
