"""
Theme Toggle Component for EduGrade AI ReactPy Frontend.
Provides an interactive, animated light/dark mode switch with rich micro-interactions.
Supports dual-icon DOM embedding for instant zero-latency CSS-driven transitions.
"""

from reactpy import component, html
from ui.components.icons import icon_sun, icon_moon

@component
def ThemeToggle(theme="light", toggle_theme=None, compact=True, style=None):
    base_style = {
        "alignItems": "center",
        "justifyContent": "center",
        "cursor": "pointer",
        "transition": "all 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
        "userSelect": "none",
    }
    if style:
        base_style.update(style)

    def handle_click(e):
        if toggle_theme:
            toggle_theme()

    if compact:
        return html.button(
            {
                "type": "button",
                "className": "theme-toggle-btn compact",
                "title": "Switch Light / Dark Theme",
                "aria-label": "Switch Light / Dark Theme",
                "data-theme-toggle": "true",
                "style": base_style,
                "on_click": handle_click,
            },
            html.span(
                {
                    "className": "theme-icon-wrapper theme-icon-sun",
                    "style": {
                        "alignItems": "center",
                        "justifyContent": "center",
                        "transition": "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
                    }
                },
                icon_sun(18, "#F59E0B")
            ),
            html.span(
                {
                    "className": "theme-icon-wrapper theme-icon-moon",
                    "style": {
                        "alignItems": "center",
                        "justifyContent": "center",
                        "transition": "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)",
                    }
                },
                icon_moon(18, "#6366F1")
            )
        )

    # Expanded / Pill Toggle
    return html.button(
        {
            "type": "button",
            "className": "theme-toggle-btn pill",
            "title": "Switch Light / Dark Theme",
            "aria-label": "Switch Light / Dark Theme",
            "data-theme-toggle": "true",
            "style": base_style,
            "on_click": handle_click,
        },
        html.span(
            {
                "className": "theme-toggle-icon theme-icon-sun",
                "style": {"alignItems": "center", "marginRight": "0.45rem"}
            },
            icon_sun(16, "#F59E0B")
        ),
        html.span(
            {
                "className": "theme-toggle-icon theme-icon-moon",
                "style": {"alignItems": "center", "marginRight": "0.45rem"}
            },
            icon_moon(16, "#6366F1")
        ),
        html.span(
            {
                "className": "theme-toggle-text theme-text-light",
                "style": {
                    "fontSize": "0.8rem",
                    "fontWeight": "600",
                    "letterSpacing": "0.02em"
                }
            },
            "Light Mode"
        ),
        html.span(
            {
                "className": "theme-toggle-text theme-text-dark",
                "style": {
                    "fontSize": "0.8rem",
                    "fontWeight": "600",
                    "letterSpacing": "0.02em"
                }
            },
            "Dark Mode"
        )
    )
