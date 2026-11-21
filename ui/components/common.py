"""
Reusable common UI helper components for EduGrade AI ReactPy Frontend.
"""
from reactpy import component, html

@component
def EmptyStateCard(title: str, description: str):
    """Clean empty-state card rendered when lists or datasets are empty."""
    return html.div(
        {"className": "card", "style": {"textAlign": "center", "padding": "3rem 1.5rem"}},
        html.h3(
            {"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.35rem", "color": "var(--brand-navy)", "marginBottom": "0.5rem"}},
            title
        ),
        html.p(
            {"style": {"color": "var(--text-secondary)", "fontSize": "0.95rem"}},
            description
        )
    )

@component
def StatCard(label: str, value: str, subtitle: str, icon=None, value_color="var(--brand-navy)"):
    """Standard metric card displaying title, formatted value, subtitle, and optional right-aligned icon."""
    return html.div(
        {"className": "stat-card"},
        html.div(
            html.div({"className": "stat-label"}, label),
            html.div({"className": "stat-value", "style": {"color": value_color}}, value),
            html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, subtitle)
        ),
        html.div({"style": {"alignSelf": "flex-end"}}, icon) if icon else html.div()
    )

@component
def AlertBanner(message: str, is_error: bool = True):
    """Status feedback alert banner for form submissions and notifications."""
    bg = "rgba(225, 29, 72, 0.08)" if is_error else "rgba(16, 185, 129, 0.08)"
    border = "rgba(225, 29, 72, 0.25)" if is_error else "rgba(16, 185, 129, 0.25)"
    color = "var(--danger)" if is_error else "var(--success)"
    return html.div(
        {
            "style": {
                "padding": "0.85rem 1.15rem",
                "borderRadius": "var(--radius-sm)",
                "backgroundColor": bg,
                "border": f"1px solid {border}",
                "color": color,
                "fontSize": "0.9rem",
                "fontWeight": "600",
                "marginBottom": "1.25rem"
            }
        },
        message
    )
