"""Unit tests for inquiry business identifier generation."""

from app.utils.inquiry_ids import INQUIRY_CODE_PREFIX


def test_inquiry_code_prefix():
    """Inquiry codes must use the INQ prefix per FRD."""
    assert INQUIRY_CODE_PREFIX == "INQ"
