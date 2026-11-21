"""
SVG Icons for EduGrade AI ReactPy Components.
Provides crisp, accessible vector icons styled for the academic navy theme.
"""

from reactpy import svg

def svg_icon(paths: list, size=20, color="currentColor"):
    return svg.svg(
        {
            "width": str(size),
            "height": str(size),
            "viewBox": "0 0 24 24",
            "fill": "none",
            "stroke": color,
            "strokeWidth": "2",
            "strokeLinecap": "round",
            "strokeLinejoin": "round",
            "style": {"verticalAlign": "middle", "flexShrink": "0"}
        },
        [svg.path({"key": f"p-{i}", "d": p}) for i, p in enumerate(paths)]
    )

def icon_sparkles(size=20, color="currentColor"):
    return svg_icon([
        "m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z",
        "M5 3v4", "M19 17v4", "M3 5h4", "M17 19h4"
    ], size, color)

def icon_award(size=20, color="currentColor"):
    return svg_icon([
        "m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526",
        "M12 14a6 6 0 1 0 0-12 6 6 0 0 0 0 12Z"
    ], size, color)

def icon_trending_up(size=20, color="currentColor"):
    return svg_icon([
        "m22 7-8.5 8.5-5-5L2 17",
        "M16 7h6v6"
    ], size, color)

def icon_book_open(size=20, color="currentColor"):
    return svg_icon([
        "M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z",
        "M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"
    ], size, color)

def icon_briefcase(size=20, color="currentColor"):
    return svg_icon([
        "M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16",
        "M2 7h20v13a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7z"
    ], size, color)

def icon_calculator(size=20, color="currentColor"):
    return svg_icon([
        "M4 2h16a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z",
        "M8 6h8", "M16 14v4", "M16 10h.01", "M12 10h.01", "M8 10h.01",
        "M12 14h.01", "M8 14h.01", "M12 18h.01", "M8 18h.01"
    ], size, color)

def icon_bot(size=20, color="currentColor"):
    return svg_icon([
        "M12 8V4H8",
        "M4 10a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8z",
        "M2 14h2", "M20 14h2",
        "M15 13v2", "M9 13v2"
    ], size, color)

def icon_user(size=20, color="currentColor"):
    return svg_icon([
        "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2",
        "M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"
    ], size, color)

def icon_users(size=20, color="currentColor"):
    return svg_icon([
        "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2",
        "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
        "M22 21v-2a4 4 0 0 0-3-3.87",
        "M16 3.13a4 4 0 0 1 0 7.75"
    ], size, color)

def icon_shield_check(size=20, color="currentColor"):
    return svg_icon([
        "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10",
        "m9 12 2 2 4-4"
    ], size, color)

def icon_layers(size=20, color="currentColor"):
    return svg_icon([
        "m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z",
        "m22 12.5-9.4 4.3a2 2 0 0 1-1.6 0L2 12.5",
        "m22 17.5-9.4 4.3a2 2 0 0 1-1.6 0L2 17.5"
    ], size, color)

def icon_logout(size=20, color="currentColor"):
    return svg_icon([
        "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",
        "M16 17l5-5-5-5",
        "M21 12H9"
    ], size, color)

def icon_check(size=16, color="currentColor"):
    return svg_icon(["M20 6 9 17l-5-5"], size, color)

def icon_alert(size=16, color="currentColor"):
    return svg_icon([
        "M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z",
        "M12 8v4",
        "M12 16h.01"
    ], size, color)

def icon_sun(size=18, color="currentColor"):
    return svg_icon([
        "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",
        "M12 2v2",
        "M12 20v2",
        "m4.93 4.93 1.41 1.41",
        "m17.66 17.66 1.41 1.41",
        "M2 12h2",
        "M20 12h2",
        "m6.34 17.66-1.41 1.41",
        "m19.07 4.93-1.41 1.41"
    ], size, color)

def icon_moon(size=18, color="currentColor"):
    return svg_icon([
        "M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"
    ], size, color)

