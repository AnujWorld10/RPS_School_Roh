"""
Business identifier generation for student inquiries.

Format: ``INQ{YYYY}{5-digit-serial}`` e.g. ``INQ202600001``.
"""

import json
from datetime import UTC, date, datetime
from hashlib import sha256

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.student_inquiry import StudentInquiry

INQUIRY_CODE_PREFIX = "INQ"


def inquiry_identity_key(
    first_name: str,
    last_name: str,
    father_name: str,
    date_of_birth: date,
) -> str:
    """Build a stable key for active inquiries belonging to the same applicant."""
    identity = [
        " ".join(value.split()).casefold()
        for value in (first_name, last_name, father_name)
    ]
    identity.append(date_of_birth.isoformat())
    canonical = json.dumps(identity, ensure_ascii=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def generate_inquiry_identifiers(session: Session) -> tuple[str, int]:
    """
    Allocate the next globally unique serial and include the current year in its code.

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
    max_serial = session.scalar(
        select(func.coalesce(func.max(StudentInquiry.serial_number), 0))
    )
    serial_number = int(max_serial or 0) + 1
    inquiry_code = f"{INQUIRY_CODE_PREFIX}{year}{serial_number:05d}"
    return inquiry_code, serial_number
