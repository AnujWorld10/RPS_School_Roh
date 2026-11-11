"""
Generate human-readable business identifiers (INQ, ADM, RPS codes).
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException
from app.models.admission import InquiryAdmission
from app.models.business_id_sequence import BusinessIDSequence
from app.models.student import Student

ADM_PREFIX = "ADM"
STUDENT_PREFIX = "RPS"


def _next_serial(session: Session, model, code_column, prefix: str, year: int) -> int:
    """Return next serial number for codes matching ``{prefix}{year}``."""
    pattern = f"{prefix}{year}%"
    max_serial = session.scalar(
        select(func.count()).select_from(model).where(code_column.like(pattern))
    )
    return int(max_serial or 0) + 1


def generate_admission_code(session: Session) -> str:
    """
    Allocate admission business ID: ADM{YYYY}{5-digit}.

    Args:
        session: Active SQLAlchemy session.

    Returns:
        Admission code string.
    """
    year = datetime.now(UTC).year
    count = session.scalar(
        select(func.count())
        .select_from(InquiryAdmission)
        .where(InquiryAdmission.admission_code.like(f"{ADM_PREFIX}{year}%"))
    )
    serial = int(count or 0) + 1
    return f"{ADM_PREFIX}{year}{serial:05d}"


def generate_student_code(session: Session) -> str:
    """
    Allocate the next school-wide student business ID: RPS{5-digit}.

    Args:
        session: Active SQLAlchemy session.

    Returns:
        Student code string.
    """
    sequence = session.scalar(
        select(BusinessIDSequence)
        .where(BusinessIDSequence.sequence_name == "student")
        .with_for_update()
    )
    if sequence is None:
        raise RuntimeError(
            "The student ID sequence is missing; apply database migrations and seed data."
        )
    if sequence.last_value >= 99_999:
        raise BusinessRuleException("The school has reached the maximum number of student IDs.")
    sequence.last_value += 1
    session.flush()
    return f"{STUDENT_PREFIX}{sequence.last_value:05d}"


def allocate_roll_number(session: Session, class_id: int, academic_year: str) -> int:
    """
    Allocate next roll number for a class in an academic year (transaction-safe best effort).

    Args:
        session: Active SQLAlchemy session.
        class_id: Target class PK.
        academic_year: Academic session label.

    Returns:
        Next available roll number (starting at 1).
    """
    max_roll = session.scalar(
        select(func.coalesce(func.max(Student.roll_number), 0)).where(
            Student.class_id == class_id,
            Student.academic_year == academic_year,
            Student.deleted_at.is_(None),
        )
    )
    return int(max_roll or 0) + 1
