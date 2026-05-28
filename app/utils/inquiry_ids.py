"""
Business identifier generation for student inquiries.

Format: ``INQ{YYYY}{5-digit-serial}`` e.g. ``INQ202600001``.
"""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.student_inquiry import StudentInquiry

INQUIRY_CODE_PREFIX = "INQ"


def generate_inquiry_identifiers(session: Session) -> tuple[str, int]:
    """
    Allocate the next inquiry_code and serial_number for the current calendar year.

    Args:
        session: Active SQLAlchemy session (caller owns transaction).

    Returns:
        Tuple of (inquiry_code, serial_number).

    Example:
        >>> code, serial = generate_inquiry_identifiers(session)
        >>> code
        'INQ202600001'
    """
    year = datetime.now(UTC).year
    # Serial is scoped per year so codes remain readable and sortable.
    max_serial = session.scalar(
        select(func.coalesce(func.max(StudentInquiry.serial_number), 0)).where(
            StudentInquiry.inquiry_code.like(f"{INQUIRY_CODE_PREFIX}{year}%")
        )
    )
    serial_number = int(max_serial or 0) + 1
    inquiry_code = f"{INQUIRY_CODE_PREFIX}{year}{serial_number:05d}"
    return inquiry_code, serial_number
