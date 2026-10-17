"""Unit tests for inquiry business identifier generation."""

from datetime import UTC, datetime
from unittest.mock import Mock

from app.utils.inquiry_ids import INQUIRY_CODE_PREFIX, generate_inquiry_identifiers


def test_inquiry_code_prefix():
    """Inquiry codes must use the INQ prefix per FRD."""
    assert INQUIRY_CODE_PREFIX == "INQ"


def test_inquiry_serial_remains_unique_across_years():
    session = Mock()
    session.scalar.return_value = 100001

    code, serial = generate_inquiry_identifiers(session)

    assert serial == 100002
    assert code == f"INQ{datetime.now(UTC).year}100002"
    assert "inquiry_code" not in str(session.scalar.call_args.args[0])
