"""
PDF Transcript Generation Service for EduGrade AI Platform.
Produces professional, editorial-styled official academic transcripts using ReportLab.
"""

import io
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds 'Page X of Y' and official system footer to every page."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer divider line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(40, 40, letter[0] - 40, 40)

        # Footer text
        footer_left = "EduGrade AI Academic Intelligence Platform • CBCS Regulations • Computer-Generated Transcript"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(40, 28, footer_left)
        self.drawRightString(letter[0] - 40, 28, footer_right)
        self.restoreState()


def generate_transcript_pdf(student_profile, semester_filter=None):
    """
    Generates a PDF byte stream containing the student's official academic transcript.
    """
    from core.models import SemesterRecord, CourseResult

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Brand Colors: Navy (#0F172A), Vermillion (#EA580C), Slate (#475569)
    navy = colors.HexColor("#0F172A")
    vermillion = colors.HexColor("#EA580C")
    light_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=navy,
        spaceBefore=10,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=navy
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=navy
    )
    cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("EduGrade AI — Official Academic Transcript", title_style))
    story.append(Paragraph("Choice Based Credit System (CBCS) • Autonomous Academic Performance Record", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=vermillion, spaceBefore=0, spaceAfter=14))

    # 2. Student Info Table
    user = student_profile.user
    full_name = f"{user.first_name} {user.last_name}".strip() or user.username
    now_str = timezone.now().strftime("%B %d, %Y — %H:%M")

    info_data = [
        [
            Paragraph("<b>Student Name:</b>", cell_style),
            Paragraph(full_name, cell_bold),
            Paragraph("<b>Roll Number:</b>", cell_style),
            Paragraph(student_profile.roll_number or "N/A", cell_bold)
        ],
        [
            Paragraph("<b>Department:</b>", cell_style),
            Paragraph(student_profile.department or "General Engineering", cell_style),
            Paragraph("<b>Current Semester:</b>", cell_style),
            Paragraph(f"Semester {student_profile.current_semester}", cell_style)
        ],
        [
            Paragraph("<b>Regulation:</b>", cell_style),
            Paragraph("2026 CBCS Autonomous", cell_style),
            Paragraph("<b>Date Generated:</b>", cell_style),
            Paragraph(now_str, cell_style)
        ]
    ]

    info_table = Table(info_data, colWidths=[100, 160, 100, 172])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    # 3. Semester Course Tables
    sem_qs = SemesterRecord.objects.filter(student=student_profile).order_by('semester_number')
    if semester_filter:
        sem_qs = sem_qs.filter(semester_number=semester_filter)

    semesters = list(sem_qs)

    if not semesters and not CourseResult.objects.filter(student=student_profile).exists():
        story.append(Paragraph("<b>No academic records available for this student.</b>", cell_style))
    else:
        for sem in semesters:
            courses = CourseResult.objects.filter(
                student=student_profile,
                semester_number=sem.semester_number
            ).order_by('course_code')

            sem_title = f"Semester {sem.semester_number} Course Results & Credits (SGPA: {float(sem.sgpa):.2f})"
            story.append(Paragraph(sem_title, section_heading))

            table_data = [
                [
                    Paragraph("Course Code", cell_header),
                    Paragraph("Course Title", cell_header),
                    Paragraph("Credits", cell_header),
                    Paragraph("Grade", cell_header),
                    Paragraph("Grade Point", cell_header)
                ]
            ]

            for c in courses:
                grade_display = c.grade
                if c.arrear_cleared and c.previous_grade:
                    grade_display = f"{c.grade} (Passed Arrear)"
                table_data.append([
                    Paragraph(c.course_code, cell_bold),
                    Paragraph(c.course_name, cell_style),
                    Paragraph(str(c.credits), cell_style),
                    Paragraph(grade_display, cell_bold if c.grade not in ['U', 'RA', 'SA', 'W'] else cell_style),
                    Paragraph(f"{float(c.grade_point):.1f}", cell_style)
                ])

            course_table = Table(table_data, colWidths=[90, 242, 60, 70, 70])
            course_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), navy),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
            ]))
            story.append(course_table)
            story.append(Spacer(1, 10))

    # 4. Cumulative Summary Box
    story.append(Spacer(1, 6))
    story.append(Paragraph("Cumulative Academic Standing & Placement Eligibility", section_heading))

    standing = "Placement Eligible (0 Backlogs)" if student_profile.is_placement_eligible else "Arrears / Criteria Pending"
    standing_color = colors.HexColor("#166534") if student_profile.is_placement_eligible else vermillion

    summary_data = [
        [
            Paragraph("<b>Cumulative CGPA:</b>", cell_style),
            Paragraph(f"<b>{float(student_profile.current_cgpa):.2f} / 10.00</b>", cell_bold),
            Paragraph("<b>Degree Credits Earned:</b>", cell_style),
            Paragraph(f"<b>{student_profile.credits_earned}</b>", cell_bold)
        ],
        [
            Paragraph("<b>Active Standing Arrears:</b>", cell_style),
            Paragraph(f"<b>{student_profile.backlogs_count}</b>", cell_bold),
            Paragraph("<b>Institutional Standing:</b>", cell_style),
            Paragraph(f"<b>{standing}</b>", ParagraphStyle('Standing', parent=cell_bold, textColor=standing_color))
        ]
    ]

    summary_table = Table(summary_data, colWidths=[140, 120, 140, 132])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), light_bg),
        ('BOX', (0, 0), (-1, -1), 1, vermillion),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
