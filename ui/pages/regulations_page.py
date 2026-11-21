"""
Academic Regulations & Curriculum Component for EduGrade AI ReactPy Frontend.
Editorial Consultancy Design (Anton, Newsreader, Vermillion, Navy).
"""

from reactpy import component, html
from ui.components.icons import icon_award, icon_layers, icon_book_open, icon_check

@component
def RegulationsPage():
    semester_curriculum = [
        {
            "sem": 1,
            "credits": 20,
            "courses": [
                "HS8151 Communicative English (3 Cr)",
                "MA8151 Engineering Mathematics - I (4 Cr)",
                "PH8151 Engineering Physics (3 Cr)",
                "CY8151 Engineering Chemistry (3 Cr)",
                "GE8151 Problem Solving & Python (3 Cr)",
                "GE8161 Python Programming Lab (2 Cr)",
                "BS8161 Physics & Chemistry Lab (2 Cr)",
            ],
        },
        {
            "sem": 2,
            "credits": 20,
            "courses": [
                "HS8251 Technical English (3 Cr)",
                "MA8251 Engineering Mathematics - II (4 Cr)",
                "PH8252 Physics for Information Science (3 Cr)",
                "BE8255 Basic Electrical & Electronics (3 Cr)",
                "GE8292 Engineering Graphics (4 Cr)",
                "CS8261 C Programming Lab (2 Cr)",
            ],
        },
        {
            "sem": 3,
            "credits": 19,
            "courses": [
                "MA8351 Discrete Mathematics (4 Cr)",
                "CS8351 Digital Principles & System Design (4 Cr)",
                "CS8391 Data Structures (3 Cr)",
                "CS8392 Object Oriented Programming (3 Cr)",
                "EC8395 Communication Engineering (3 Cr)",
                "CS8381 Data Structures Lab (2 Cr)",
            ],
        },
        {
            "sem": 4,
            "credits": 21,
            "courses": [
                "MA8402 Probability & Queueing Theory (4 Cr)",
                "CS8491 Design & Analysis of Algorithms (4 Cr)",
                "CS8492 Database Management Systems (3 Cr)",
                "CS8451 Operating Systems (3 Cr)",
                "CS8461 Operating Systems Lab (2 Cr)",
                "CS8481 DBMS Laboratory (2 Cr)",
                "GE8291 Environmental Science (3 Cr)",
            ],
        },
        {
            "sem": 5,
            "credits": 18,
            "courses": [
                "CS8501 Theory of Computation (3 Cr)",
                "CS8591 Computer Networks (3 Cr)",
                "EC8691 Microprocessors & Microcontrollers (3 Cr)",
                "CS8502 Object Oriented Analysis & Design (3 Cr)",
                "CS8511 Networks Laboratory (2 Cr)",
                "CS8512 Microprocessors Lab (2 Cr)",
                "HS8581 Professional Communication (2 Cr)",
            ],
        },
    ]

    sem_cards = []
    for s in semester_curriculum:
        course_lis = [
            html.li(
                {"key": c, "style": {"display": "flex", "alignItems": "center", "gap": "0.5rem", "fontSize": "0.85rem", "color": "var(--text-secondary)"}},
                icon_check(14, "var(--brand-vermillion)"),
                html.span(c)
            ) for c in s["courses"]
        ]
        sem_cards.append(
            html.div(
                {"key": str(s["sem"]), "className": "card"},
                html.div(
                    {"style": {"display": "flex", "justifyContent": "space-between", "alignItems": "center", "borderBottom": "1.5px solid var(--border-subtle)", "paddingBottom": "0.75rem", "marginBottom": "0.75rem"}},
                    html.div({"style": {"fontFamily": "var(--font-serif)", "fontSize": "1.3rem", "fontWeight": "700", "color": "var(--brand-navy)"}}, f"Semester {s['sem']} Curriculum"),
                    html.span({"className": "badge badge-vermillion"}, f"{s['credits']} Total Credits")
                ),
                html.ul({"style": {"listStyle": "none", "display": "flex", "flexDirection": "column", "gap": "0.5rem", "marginTop": "0.75rem"}}, course_lis)
            )
        )

    return html.div(
        html.div(
            {"style": {"marginBottom": "2.25rem"}},
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
                "Academic Regulations & Curriculum Framework"
            ),
            html.p({"style": {"color": "var(--text-secondary)", "marginTop": "0.25rem"}}, "AICTE & University Choice Based Credit System (CBCS) 160-Credit Degree Framework.")
        ),
        html.div(
            {"className": "stat-grid", "style": {"marginBottom": "2rem"}},
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Graduation Requirement"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, "160"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, "Minimum earned credits across 8 Semesters")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_award(26, "var(--brand-vermillion)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "Grading Scale"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-vermillion)"}}, "10.0"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, "O (10), A+ (9), A (8), B+ (7), B (6), RA (0)")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_layers(26, "var(--brand-navy)"))
            ),
            html.div(
                {"className": "stat-card"},
                html.div(
                    html.div({"className": "stat-label"}, "First Class Benchmark"),
                    html.div({"className": "stat-value", "style": {"color": "var(--brand-navy)"}}, "6.50"),
                    html.small({"style": {"color": "var(--text-muted)", "fontWeight": "600"}}, "8.50+ CGPA required for First Class Distinction")
                ),
                html.div({"style": {"alignSelf": "flex-end"}}, icon_book_open(26, "#10B981"))
            )
        ),
        html.div({"style": {"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))", "gap": "1.75rem"}}, sem_cards)
    )
