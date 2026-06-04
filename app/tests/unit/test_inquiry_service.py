from datetime import date

import pytest
from unittest.mock import MagicMock

from app.models.enums import InquiryStatus
from app.models.student_inquiry import StudentInquiry
from app.services.inquiries import InquiryService
from app.utils.inquiry_ids import generate_inquiry_identifiers


def create_sample_inquiry(repo_session):
    inquiry_code, serial = generate_inquiry_identifiers(repo_session)
    inquiry = StudentInquiry(
        inquiry_code=inquiry_code,
        serial_number=serial,
        first_name="Test",
        last_name="Student",
        father_name="Parent",
        date_of_birth=date(2016, 1, 1),
        gender="male",
        parent_mobile="03001234567",
        email="parent@test.local",
        status=InquiryStatus.PENDING.value,
    )
    from app.repositories.inquiries import StudentInquiryRepository

    repo = StudentInquiryRepository(repo_session)
    created = repo.create(inquiry)
    repo_session.commit()
    return created


def test_valid_transition_pending_to_under_review(db_session):
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    updated = service.transition_status(inquiry.id, InquiryStatus.UNDER_REVIEW.value, actor_id=1, request=request_mock)
    assert updated.status == InquiryStatus.UNDER_REVIEW.value


def test_invalid_transition_raises_business_rule(db_session):
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    # PENDING -> PROCESSING is not allowed directly
    with pytest.raises(Exception) as exc:
        service.transition_status(inquiry.id, InquiryStatus.PROCESSING.value, actor_id=1, request=request_mock)
    assert "Cannot transition" in str(exc.value) or "Cannot transition" in getattr(exc.value, 'message', '')


def test_reject_requires_reason(db_session):
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    with pytest.raises(Exception) as exc:
        service.transition_status(inquiry.id, InquiryStatus.REJECTED.value, actor_id=1, request=request_mock)
    assert "Rejection reason is required" in str(exc.value)


def test_rejecting_terminal_status_raises(db_session):
    inquiry = create_sample_inquiry(db_session)
    # Manually set to terminal
    from app.repositories.inquiries import StudentInquiryRepository

    repo = StudentInquiryRepository(db_session)
    inquiry.status = InquiryStatus.ADMISSION_SUCCESS.value
    repo.update(inquiry)
    db_session.commit()

    service = InquiryService(db_session)
    request_mock = MagicMock()

    with pytest.raises(Exception) as exc:
        service.reject_inquiry(inquiry.id, "Not eligible", actor_id=1, request=request_mock)
    assert "already in a terminal state" in str(exc.value)
