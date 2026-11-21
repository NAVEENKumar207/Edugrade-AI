"""
AI Academic Advisor Chat Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

import time
from reactpy import component, html, use_state
from ui.components.icons import icon_bot, icon_sparkles, icon_users
from ui.services.data_service import (
    get_advisor_messages, send_advisor_chat_message, clear_advisor_chat_history
)

@component
def AiAdvisorPage(user):
    def get_initial_messages():
        msgs = get_advisor_messages(user)
        if msgs:
            return [{"sender": m.sender, "message": m.message} for m in msgs]
        return [{
            "sender": "ai",
            "message": "Hello! I am your EduGrade AI Academic Mentor. I have analyzed your course credits, historical SGPA, and subject performance. How can I help you optimize your academic trajectory or placement readiness today?"
        }]

    messages, set_messages = use_state(get_initial_messages)
    input_text, set_input_text = use_state("")
    loading, set_loading = use_state(False)
    confirm_clear_until, set_confirm_clear_until = use_state(0.0)

    def handle_clear_chat(e=None):
        now = time.time()
        if now < confirm_clear_until:
            clear_advisor_chat_history(user)
            set_messages([{
                "sender": "ai",
                "message": "Chat history has been cleared. How can I assist you with your academic goals today?"
            }])
            set_confirm_clear_until(0.0)
        else:
            set_confirm_clear_until(now + 4.0)

    def handle_send(text_to_send):
        clean_text = text_to_send.strip()
        if not clean_text or loading:
            return

        # Append user message
        new_msgs = messages + [{"sender": "user", "message": clean_text}]
        set_messages(new_msgs)
        set_input_text("")
        set_loading(True)

        try:
            res = send_advisor_chat_message(user, clean_text)
            if isinstance(res, dict):
                reply = res.get('reply', '')
                source = res.get('source', 'rule_based')
            else:
                reply = str(res)
                source = 'rule_based'
            set_messages(new_msgs + [{"sender": "ai", "message": reply, "source": source}])
        except Exception as err:
            set_messages(new_msgs + [{"sender": "ai", "message": f"Mentor response error: {str(err)}", "source": "rule_based"}])
        finally:
            set_loading(False)

    suggested = [
        "Make a study plan for my weakest subject",
        "How can I raise my CGPA to 9.0 in remaining semesters?",
        "Which subjects should I focus on to clear arrears or improve grades?",
        "Can you give me a weekly study schedule for Operating Systems & DBMS?",
        "What companies can I apply for with my current CGPA?",
        "எனது பலவீனமான பாடத்திற்கு ஒரு படிப்புத் திட்டம் உருவாக்கவும் (Tamil)"
    ]

    chat_elements = []
    for idx, m in enumerate(messages):
        is_user = m["sender"] == "user"
        chat_elements.append(
            html.div(
                {
                    "key": str(idx),
                    "style": {
                        "display": "flex",
                        "justifyContent": "flex-end" if is_user else "flex-start",
                        "marginBottom": "1.25rem"
                    }
                },
                html.div(
                    {
                        "style": {
                            "maxWidth": "78%",
                            "padding": "1.1rem 1.4rem",
                            "borderRadius": "20px 20px 4px 20px" if is_user else "20px 20px 20px 4px",
                            "backgroundColor": "linear-gradient(135deg, #0284C7, #4F46E5)" if is_user else "var(--bg-surface-elevated)",
                            "color": "#FFFFFF" if is_user else "var(--text-primary)",
                            "border": "none" if is_user else "1px solid var(--border-medium)",
                            "boxShadow": "var(--shadow-sm)",
                            "fontSize": "0.925rem",
                            "lineHeight": "1.6"
                        }
                    },
                    html.div(
                        {
                            "style": {
                                "display": "flex",
                                "alignItems": "center",
                                "gap": "0.5rem",
                                "fontSize": "0.75rem",
                                "fontWeight": "700",
                                "marginBottom": "0.4rem",
                                "color": "#BAE6FD" if is_user else "var(--primary)"
                            }
                        },
                        icon_users(14) if is_user else icon_bot(14),
                        "You" if is_user else "EduGrade AI Mentor"
                    ),
                    html.div({"style": {"whiteSpace": "pre-wrap"}}, m["message"]),
                    html.div(
                        {
                            "style": {
                                "fontSize": "0.72rem",
                                "opacity": "0.6",
                                "marginTop": "0.4rem",
                                "fontStyle": "italic"
                            }
                        },
                        "Powered by Groq" if m.get("source") == "groq" else "Built-in advisor"
                    ) if not is_user and m.get("source") else None
                )
            )
        )

    is_confirming = time.time() < confirm_clear_until

    return html.div(
        # Header
        html.div(
            {
                "style": {
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                    "marginBottom": "2rem",
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
                    "AI Academic Mentor & Trajectory Advisory"
                ),
                html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, "Bilingual English & Tamil advisory grounded in your official credit weights, course history, and target milestones.")
            ),
            html.button(
                {
                    "className": "btn btn-danger" if is_confirming else "btn btn-secondary",
                    "style": {
                        "backgroundColor": "var(--danger)" if is_confirming else "transparent",
                        "color": "#FFFFFF" if is_confirming else "var(--danger)",
                        "borderColor": "var(--danger)",
                        "fontSize": "0.85rem",
                        "padding": "0.5rem 1rem",
                        "display": "inline-flex",
                        "alignItems": "center",
                        "gap": "0.4rem",
                        "transition": "all 0.2s ease"
                    },
                    "on_click": handle_clear_chat
                },
                "⚠️ Click to Confirm Clear (4s)" if is_confirming else "🗑️ Clear Chat"
            )
        ),

        # Suggested Prompt Chips
        html.div(
            {"style": {"marginBottom": "1.5rem"}},
            html.div({"style": {"fontSize": "0.8rem", "fontWeight": "700", "color": "var(--text-primary)", "marginBottom": "0.5rem", "textTransform": "uppercase", "letterSpacing": "0.05em"}}, "Quick Guidance Inquiries:"),
            html.div(
                {"style": {"display": "flex", "flexWrap": "wrap", "gap": "0.5rem"}},
                [
                    html.button(
                        {
                            "key": p,
                            "style": {
                                "backgroundColor": "var(--danger-subtle)",
                                "color": "var(--danger)",
                                "border": "1px solid var(--border-subtle)",
                                "borderRadius": "var(--radius-full)",
                                "padding": "0.4rem 1rem",
                                "fontSize": "0.8rem",
                                "fontWeight": "600",
                                "cursor": "pointer",
                                "transition": "all 0.15s ease"
                            },
                            "on_click": lambda e, prompt_text=p: handle_send(prompt_text)
                        },
                        p
                    )
                    for p in suggested
                ]
            )
        ),

        # Chat Window Card
        html.div(
            {
                "className": "card",
                "style": {
                    "minHeight": "480px",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "space-between",
                    "padding": "1.75rem",
                    "borderRadius": "var(--radius-xl)"
                }
            },
            # Messages Box
            html.div(
                {
                    "style": {
                        "flex": "1",
                        "overflowY": "auto",
                        "maxHeight": "520px",
                        "paddingRight": "0.5rem",
                        "marginBottom": "1.5rem"
                    }
                },
                chat_elements,
                html.div(
                    {"style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "color": "var(--brand-vermillion)", "fontSize": "0.85rem", "fontStyle": "italic"}},
                    icon_sparkles(16, "var(--brand-vermillion)"), " Analyzing student academic records and synthesizing advice..."
                ) if loading else None
            ),

            # Input Form Bar
            html.div(
                {
                    "style": {
                        "display": "flex",
                        "gap": "0.75rem",
                        "borderTop": "1.5px solid var(--border-subtle)",
                        "paddingTop": "1.25rem"
                    }
                },
                html.input({
                    "type": "text",
                    "className": "input",
                    "style": {"borderRadius": "var(--radius-full)", "padding": "0.85rem 1.5rem"},
                    "placeholder": "Ask in English or தமிழ் (e.g. How do I clear backlogs and reach 8.0 CGPA?)...",
                    "value": input_text,
                    "on_change": lambda e: set_input_text(e.get("target", {}).get("value", "") if isinstance(e, dict) else str(e)),
                    "on_keydown": lambda e: handle_send(input_text) if e.get("key") == "Enter" else None
                }),
                html.button(
                    {
                        "className": "btn btn-primary",
                        "style": {"padding": "0.85rem 1.75rem", "borderRadius": "var(--radius-full)"},
                        "disabled": loading or not input_text.strip(),
                        "on_click": lambda e: handle_send(input_text)
                    },
                    "Send Message →"
                )
            )
        )
    )
