"""
AI Academic Advisor Chat Component for EduGrade AI ReactPy Frontend.
Industrial Academic Precision Design (Space Grotesk, IBM Plex Mono, Inter, Vermilion, Espresso).
Matches New Ui/ai_academic_advisor/code.html.
"""

import time
from reactpy import component, html, use_state
from ui.services.data_service import (
    get_advisor_messages, send_advisor_chat_message, clear_advisor_chat_history,
    get_student_dashboard_data, get_placement_matrix_data
)

@component
def AiAdvisorPage(user):
    def get_initial_messages():
        msgs = get_advisor_messages(user)
        if msgs:
            return [{"sender": m.sender, "message": m.message} for m in msgs]
        return [{
            "sender": "ai",
            "message": "Hello! I am your EduGrade AI Academic Mentor. I am grounded with your live transcript, historical SGPA trajectory, and placement eligibility. How can I assist you with your academic goals or placement preparations today?"
        }]

    messages, set_messages = use_state(get_initial_messages)
    input_text, set_input_text = use_state("")
    loading, set_loading = use_state(False)
    confirm_clear_until, set_confirm_clear_until = use_state(0.0)

    # Fetch context data for sidebar
    data = get_student_dashboard_data(user)
    student = data.get("student", {}) if data else {}
    recent_courses = data.get("recent_courses", []) if data else []
    placement_data = get_placement_matrix_data(user)
    comp_list = placement_data.get("companies", []) if placement_data else []
    eligible_count = sum(1 for c in comp_list if c.get("is_eligible", False))
    total_companies = len(comp_list)

    weak_courses = [c.course_code for c in recent_courses if c.grade in ['B+', 'B', 'C', 'U', 'RA']][:2]
    weak_str = ", ".join(weak_courses) if weak_courses else "None (All Cleared)"

    def handle_clear_chat(e=None):
        now = time.time()
        if now < confirm_clear_until:
            clear_advisor_chat_history(user)
            set_messages([{
                "sender": "ai",
                "message": "Chat history has been cleared. How can I assist your academic trajectory today?"
            }])
            set_confirm_clear_until(0.0)
        else:
            set_confirm_clear_until(now + 4.0)

    def handle_send(text_to_send):
        clean_text = text_to_send.strip()
        if not clean_text or loading:
            return

        new_msgs = messages + [{"sender": "user", "message": clean_text}]
        set_messages(new_msgs)
        set_input_text("")
        set_loading(True)

        try:
            res = send_advisor_chat_message(user, clean_text)
            reply = res.get('reply', '') if isinstance(res, dict) else str(res)
            source = res.get('source', 'grounded') if isinstance(res, dict) else 'grounded'
            set_messages(new_msgs + [{"sender": "ai", "message": reply, "source": source}])
        except Exception as exc:
            set_messages(new_msgs + [{
                "sender": "ai",
                "message": f"Unable to generate response at this time. Please try again. ({exc})"
            }])
        finally:
            set_loading(False)

    def on_form_submit(e):
        handle_send(input_text)

    is_confirming = time.time() < confirm_clear_until

    # Render message items
    rendered_messages = []
    for idx, msg in enumerate(messages):
        is_user = msg.get("sender") == "user"
        text = msg.get("message", "")
        source = msg.get("source")

        if is_user:
            rendered_messages.append(
                html.div(
                    {"key": str(idx), "class_name": "self-end max-w-xl bg-light-primary text-light-on-primary p-gutter-md"},
                    html.p({"class_name": "font-body text-body-md whitespace-pre-wrap"}, text)
                )
            )
        else:
            source_badge = html.span(
                {"class_name": "inline-flex items-center gap-1 font-mono text-[11px] text-light-primary uppercase font-bold mt-1"},
                html.span({"class_name": "material-symbols-outlined text-[13px]"}, "verified"),
                f"Grounded by EduGrade Engine ({source})" if source else "Grounded by Academic History"
            )
            rendered_messages.append(
                html.div(
                    {"key": str(idx), "class_name": "self-start max-w-2xl bg-light-surface-container-low border border-light-outline-variant p-gutter-md flex flex-col gap-gutter-sm"},
                    html.p({"class_name": "font-body text-body-md text-light-on-surface whitespace-pre-wrap ai-reply-text"}, text),
                    source_badge
                )
            )

    if loading:
        rendered_messages.append(
            html.div(
                {"key": "loading", "class_name": "self-start max-w-2xl bg-light-surface-container-low border border-light-outline-variant p-gutter-md flex items-center gap-2"},
                html.span({"class_name": "material-symbols-outlined text-[18px] text-light-primary animate-spin"}, "progress_activity"),
                html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant"}, "Analyzing transcript and synthesizing advice...")
            )
        )

    # Prompt chips
    prompts = [
        "How do I reach 8.80 CGPA before graduation?",
        "Audit Google 9.00 CGPA gap",
        "தமிழில் எனது placement தகுதி பற்றி சொல்லுங்கள்",
        "Build Sem VII weekly study schedule"
    ]

    return html.div(
        {"class_name": "flex-1 p-gutter-lg max-w-[1440px] w-full mx-auto flex flex-col gap-gutter-lg overflow-y-auto"},
        
        # Header
        html.div(
            {"class_name": "flex flex-wrap items-center justify-between gap-gutter-md pb-gutter-md border-b border-light-outline-variant"},
            html.div(
                html.h1({"class_name": "font-headline text-headline-md text-light-on-surface uppercase tracking-tight"}, "AI Academic Advisor"),
                html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, "Grounded Bilingual Academic Guidance • English & தமிழ்")
            ),
            html.div(
                {"class_name": "flex items-center gap-gutter-sm"},
                html.span({"class_name": "px-3 py-1.5 rounded-full bg-light-primary-container text-light-on-primary-container font-mono text-mono-sm uppercase whitespace-nowrap font-bold"}, "EN / தமிழ் Active")
            )
        ),

        # Main Workspace Grid
        html.main(
            {"class_name": "grid grid-cols-1 xl:grid-cols-12 gap-gutter-lg items-start"},
            
            # Left: Chat Window (8 cols)
            html.section(
                {"class_name": "xl:col-span-8 bg-light-surface-container-lowest border border-light-outline-variant flex flex-col min-h-[640px]"},
                
                # Chat Header
                html.header(
                    {"class_name": "px-gutter-lg py-gutter-md border-b border-light-outline-variant flex items-center justify-between gap-gutter-sm flex-wrap"},
                    html.div(
                        {"class_name": "flex items-center gap-gutter-sm"},
                        html.div(
                            {"class_name": "w-9 h-9 bg-light-primary-container text-light-on-primary-container flex items-center justify-center shrink-0"},
                            html.span({"class_name": "material-symbols-outlined text-[18px]"}, "psychology")
                        ),
                        html.div(
                            html.h2({"class_name": "font-headline text-title-md text-light-on-surface uppercase font-bold"}, "EduGrade Mentor"),
                            html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant uppercase"}, f"Synced • Sem {student.get('current_semester', 6)} ({student.get('current_cgpa', 8.64):.2f} CGPA)")
                        )
                    ),
                    html.div(
                        {"class_name": "flex items-center gap-gutter-sm"},
                        html.span({"class_name": "px-2.5 py-1 rounded-full bg-light-secondary-container text-light-on-secondary-container font-mono text-mono-sm whitespace-nowrap shrink-0 font-bold"}, "Grounded Mode"),
                        html.button(
                            {
                                "type": "button",
                                "on_click": handle_clear_chat,
                                "class_name": f"inline-flex items-center justify-center gap-gutter-xs px-gutter-md py-2 border font-mono text-mono-sm uppercase transition-colors duration-state-change whitespace-nowrap shrink-0 cursor-pointer {'bg-light-primary text-light-on-primary border-light-primary font-bold' if is_confirming else 'bg-light-surface text-light-on-surface border-light-outline-variant hover:bg-light-surface-container-low'}"
                            },
                            html.span({"class_name": "material-symbols-outlined text-[16px]"}, "refresh"),
                            html.span("Confirm Reset?" if is_confirming else "New Chat")
                        )
                    )
                ),

                # Message Thread
                html.div(
                    {"class_name": "flex-1 p-gutter-lg flex flex-col gap-gutter-md overflow-y-auto max-h-[460px]"},
                    rendered_messages
                ),

                # Footer with Recommendation Chips and Input
                html.footer(
                    {"class_name": "p-gutter-md border-t border-light-outline-variant flex flex-col gap-gutter-sm bg-light-surface-container-lowest"},
                    
                    # Prompt recommendation chips
                    html.div(
                        {"class_name": "flex flex-wrap gap-gutter-xs"},
                        [
                            html.button(
                                {
                                    "key": p_text,
                                    "type": "button",
                                    "on_click": lambda e, pt=p_text: handle_send(pt),
                                    "class_name": "px-3 py-1.5 rounded-full bg-light-surface-container-low border border-light-outline-variant font-mono text-label-sm text-light-on-surface hover:bg-light-surface-container hover:border-light-primary transition-colors duration-state-change whitespace-nowrap cursor-pointer"
                                },
                                p_text
                            ) for p_text in prompts
                        ]
                    ),

                    # Input form with Tamil/English Voice Mode
                    html.div(
                        {"class_name": "flex items-center gap-2 mb-1 flex-wrap"},
                        html.div(
                            {"class_name": "flex items-center gap-1 border border-light-outline-variant rounded-radius-sm p-0.5 bg-light-surface-container-low"},
                            html.button(
                                {
                                    "type": "button",
                                    "data-voice-lang": "ta-IN",
                                    "aria-label": "Set Tamil Language",
                                    "on_click": lambda e: None,
                                    "onclick": "window.setVoiceLang('ta-IN')",
                                    "class_name": "px-2 py-0.5 font-mono text-[11px] font-bold text-light-on-surface hover:text-light-primary cursor-pointer"
                                },
                                "தமிழ்"
                            ),
                            html.span({"class_name": "text-light-outline-variant"}, "|"),
                            html.button(
                                {
                                    "type": "button",
                                    "data-voice-lang": "en-IN",
                                    "aria-label": "Set English Language",
                                    "on_click": lambda e: None,
                                    "onclick": "window.setVoiceLang('en-IN')",
                                    "class_name": "px-2 py-0.5 font-mono text-[11px] font-bold text-light-on-surface hover:text-light-primary cursor-pointer"
                                },
                                "English"
                            )
                        ),
                        html.button(
                            {
                                "id": "voice-mic-btn",
                                "type": "button",
                                "on_click": lambda e: None,
                                "onclick": "window.startVoiceInput()",
                                "title": "Speak query using microphone",
                                "class_name": "inline-flex items-center gap-1 px-2.5 py-1 border border-light-outline-variant bg-light-surface-container-low font-mono text-label-xs text-light-on-surface hover:border-light-primary transition-colors cursor-pointer"
                            },
                            html.span({"class_name": "material-symbols-outlined text-[15px]"}, "mic"),
                            html.span("Voice Input")
                        ),
                        html.button(
                            {
                                "id": "voice-speak-btn",
                                "type": "button",
                                "on_click": lambda e: None,
                                "onclick": "window.readLatestReplyAloud()",
                                "title": "Read latest advisor reply aloud",
                                "class_name": "inline-flex items-center gap-1 px-2.5 py-1 border border-light-outline-variant bg-light-surface-container-low font-mono text-label-xs text-light-on-surface hover:border-light-primary transition-colors cursor-pointer"
                            },
                            html.span({"class_name": "material-symbols-outlined text-[15px]"}, "volume_up"),
                            html.span("Read Aloud")
                        ),
                        html.span(
                            {"id": "voice-lang-label", "class_name": "text-[10px] font-mono text-light-on-surface-variant ml-auto"},
                            "தமிழ் (ta-IN)"
                        )
                    ),
                    html.div(
                        {"class_name": "flex items-center gap-gutter-sm"},
                        html.input(
                            {
                                "id": "ai-advisor-input",
                                "type": "text",
                                "placeholder": "Ask about CGPA targets, weak subjects, or placement prep (EN / தமிழ்)...",
                                "value": input_text,
                                "on_change": lambda e: set_input_text(e.get("target", {}).get("value", "")),
                                "on_key_down": lambda e: handle_send(input_text) if e.get("key") == "Enter" else None,
                                "disabled": loading,
                                "class_name": "flex-1 border border-light-outline-variant bg-light-surface-container-lowest px-3 py-2.5 font-body text-body-md text-light-on-surface focus:border-light-primary focus:ring-1 focus:ring-light-primary focus:outline-none"
                            }
                        ),
                        html.button(
                            {
                                "type": "button",
                                "on_click": on_form_submit,
                                "disabled": loading or not input_text.strip(),
                                "class_name": "inline-flex items-center justify-center gap-gutter-xs px-gutter-md py-2.5 bg-light-primary text-light-on-primary font-mono text-mono-md uppercase hover:bg-light-primary-container hover:text-light-on-primary-container transition-colors duration-state-change whitespace-nowrap shrink-0 disabled:opacity-50 cursor-pointer"
                            },
                            html.span("Send"),
                            html.span({"class_name": "material-symbols-outlined text-[18px]"}, "send")
                        )
                    ),
                    html.div(
                        {"class_name": "text-[10px] font-mono text-light-on-surface-variant mt-0.5"},
                        "Voice uses your browser's speech service."
                    )
                )
            ),

            # Right: Grounded Context Sidebar (4 cols)
            html.aside(
                {"class_name": "xl:col-span-4 flex flex-col gap-gutter-lg"},
                
                # Context Snapshot Card
                html.article(
                    {"class_name": "bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
                    html.div(
                        {"class_name": "flex items-center gap-gutter-sm border-b border-light-outline-variant pb-gutter-sm"},
                        html.div(
                            {"class_name": "w-8 h-8 bg-light-primary/10 text-light-primary flex items-center justify-center shrink-0"},
                            html.span({"class_name": "material-symbols-outlined text-[20px]"}, "analytics")
                        ),
                        html.h3({"class_name": "font-headline text-title-md text-light-on-surface uppercase font-bold"}, "Context Snapshot")
                    ),
                    html.div(
                        {"class_name": "flex flex-col gap-gutter-sm font-mono text-mono-sm"},
                        html.div(
                            {"class_name": "flex items-center justify-between py-1 border-b border-light-outline-variant/40"},
                            html.span({"class_name": "text-light-on-surface-variant uppercase"}, "Current CGPA"),
                            html.span({"class_name": "text-light-on-surface font-bold tabular-nums"}, f"{student.get('current_cgpa', 8.64):.2f}")
                        ),
                        html.div(
                            {"class_name": "flex items-center justify-between py-1 border-b border-light-outline-variant/40"},
                            html.span({"class_name": "text-light-on-surface-variant uppercase"}, "Active Arrears"),
                            html.span({"class_name": "text-light-secondary font-bold tabular-nums"}, str(student.get("backlogs_count", 0)))
                        ),
                        html.div(
                            {"class_name": "flex items-center justify-between py-1 border-b border-light-outline-variant/40"},
                            html.span({"class_name": "text-light-on-surface-variant uppercase"}, "Weakest Courses"),
                            html.span({"class_name": "text-light-primary font-bold"}, weak_str)
                        ),
                        html.div(
                            {"class_name": "flex items-center justify-between py-1"},
                            html.span({"class_name": "text-light-on-surface-variant uppercase"}, "Eligible Drives"),
                            html.span({"class_name": "text-light-secondary font-bold tabular-nums"}, f"{eligible_count} / {total_companies}")
                        )
                    )
                ),

                # Weekly Study Plan Card
                html.article(
                    {"class_name": "bg-light-surface-container-lowest border border-light-outline-variant p-gutter-lg flex flex-col gap-gutter-md"},
                    html.div(
                        {"class_name": "flex items-center gap-gutter-sm border-b border-light-outline-variant pb-gutter-sm"},
                        html.div(
                            {"class_name": "w-8 h-8 bg-light-secondary text-light-on-secondary flex items-center justify-center shrink-0"},
                            html.span({"class_name": "material-symbols-outlined text-[18px]"}, "event_note")
                        ),
                        html.div(
                            html.h3({"class_name": "font-headline text-title-md text-light-on-surface uppercase font-bold"}, "Weekly Study Plan"),
                            html.p({"class_name": "font-mono text-mono-sm text-light-on-surface-variant"}, "Recommended 12 hrs/wk focus")
                        )
                    ),
                    html.div(
                        {"class_name": "flex flex-col divide-y divide-light-outline-variant font-body text-body-sm"},
                        html.div(
                            {"class_name": "py-2.5 flex items-center justify-between gap-gutter-sm"},
                            html.div(
                                html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold"}, "DSA & System Design"),
                                html.p({"class_name": "text-light-on-surface-variant text-body-sm"}, "Placement prep • Mon, Wed, Fri")
                            ),
                            html.span({"class_name": "font-mono text-mono-sm text-light-primary font-bold whitespace-nowrap"}, "6 hrs/wk")
                        ),
                        html.div(
                            {"class_name": "py-2.5 flex items-center justify-between gap-gutter-sm"},
                            html.div(
                                html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold"}, "Core Subject Remediation"),
                                html.p({"class_name": "text-light-on-surface-variant text-body-sm"}, "Foundational concepts • Tue, Thu")
                            ),
                            html.span({"class_name": "font-mono text-mono-sm text-light-secondary font-bold whitespace-nowrap"}, "4 hrs/wk")
                        ),
                        html.div(
                            {"class_name": "py-2.5 flex items-center justify-between gap-gutter-sm"},
                            html.div(
                                html.p({"class_name": "font-title text-title-md text-light-on-surface font-semibold"}, "Upcoming Semester Preview"),
                                html.p({"class_name": "text-light-on-surface-variant text-body-sm"}, "Advanced electives preview • Saturday")
                            ),
                            html.span({"class_name": "font-mono text-mono-sm text-light-on-surface-variant font-bold whitespace-nowrap"}, "2 hrs/wk")
                        )
                    )
                )
            )
        )
    )
