"""Generate parent-downloadable admission confirmation letters."""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.admission import InquiryAdmission


def create_admission_letter(admission: InquiryAdmission) -> bytes:
    """Create an admission letter without including either Aadhaar number."""
    inquiry = admission.inquiry
    student = admission.student
    school_class = admission.school_class
    if not inquiry or not student or not school_class:
        raise ValueError("Admission is missing information required for its letter.")

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"Admission confirmation - {student.student_code}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AdmissionTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#123c55"),
        spaceAfter=12,
    )
    body_style = styles["BodyText"]
    body_style.leading = 16
    student_name = " ".join(
        part
        for part in (student.first_name, inquiry.middle_name, student.last_name)
        if part
    )
    data = [
        ("Student ID", student.student_code),
        ("Student name", student_name),
        ("Date of birth", student.date_of_birth.strftime("%d %B %Y")),
        ("Gender", student.gender.title()),
        ("Class", school_class.name),
        ("Section", admission.section or school_class.section or "To be assigned"),
        ("Academic year", admission.academic_year),
        ("Roll number", str(student.roll_number or "To be assigned")),
        ("Previous school", inquiry.last_school or "Not provided"),
        (
            "Previous-school marks",
            str(admission.last_school_marks)
            if admission.last_school_marks is not None
            else "Not provided",
        ),
        (
            "Previous-school percentage",
            f"{admission.last_school_percentage}%"
            if admission.last_school_percentage is not None
            else "Not provided",
        ),
        (
            "Previous-school ID / roll number",
            admission.last_school_id_or_roll_number or "Not provided",
        ),
        ("Parent / guardian", inquiry.father_name),
        ("Parent email", inquiry.email),
        ("Parent mobile", inquiry.parent_mobile),
        ("Address", admission.permanent_address or inquiry.address or "Not provided"),
        ("Admission reference", admission.admission_code),
        ("Enrolled on", student.created_at.strftime("%d %B %Y")),
    ]
    rows = [
        [
            Paragraph(f"<b>{escape(label)}</b>", body_style),
            Paragraph(escape(value), body_style),
        ]
        for label, value in data
    ]
    table = Table(rows, colWidths=[55 * mm, 105 * mm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef4f7")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    document.build(
        [
            Paragraph("Admission Confirmation", title_style),
            Paragraph(
                f"Dear {escape(inquiry.father_name)},",
                body_style,
            ),
            Spacer(1, 8),
            Paragraph(
                f"We are pleased to confirm that {escape(student_name)} has been admitted to "
                f"{escape(school_class.name)} for the {escape(admission.academic_year)} "
                "academic year. Please keep this letter for your records.",
                body_style,
            ),
            Spacer(1, 14),
            table,
            Spacer(1, 20),
            Paragraph("Regards,<br/><b>School Administration</b>", body_style),
        ]
    )
    return buffer.getvalue()
