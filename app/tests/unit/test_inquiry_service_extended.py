"""Unit tests for service layer: audit logging, state transitions, error handling."""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AuthenticationException,
    BusinessRuleException,
    NotFoundException,
)
from app.models.enums import InquiryStatus
from app.models.student_inquiry import StudentInquiry
from app.repositories.inquiries import StudentInquiryRepository
from app.services.inquiries import InquiryService
from app.utils.inquiry_ids import generate_inquiry_identifiers


def create_sample_inquiry(repo_session):
    """Helper to create a sample inquiry for testing."""
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
    repo = StudentInquiryRepository(repo_session)
    created = repo.create(inquiry)
    repo_session.commit()
    return created


def test_inquiry_status_history_recorded_on_creation(db_session):
    """Test that status history is recorded when inquiry is created."""
    service = InquiryService(db_session)
    request_mock = MagicMock()

    from app.schemas.inquiries import PublicInquiryCreateRequest
    from app.models.enums import Gender

    payload = PublicInquiryCreateRequest(
        first_name="History",
        middle_name="Test",
        last_name="Student",
        gender=Gender.MALE,
        father_name="Parent",
        dob=date(2016, 1, 1),
        student_mobile="03001234567",
        parent_mobile="03009876543",
        email="history@test.local",
        address="123 St",
        last_school="School",
        current_class="Class 5",
        admission_for_class="Class 6",
        last_school_percentage=None,
        admission_for_class_id=None,
    )

    inquiry = service.create_public_inquiry(payload, request_mock)

    # Verify status history was recorded
    history = service.history.get_by_inquiry_id(inquiry.id)
    assert len(history) >= 1
    assert history[0].to_status == InquiryStatus.PENDING.value


def test_get_public_status_with_invalid_code_raises_not_found(db_session):
    """Test that get_public_status raises NotFoundException for invalid code."""
    service = InquiryService(db_session)
    request_mock = MagicMock()

    with pytest.raises(NotFoundException):
        service.get_public_status("INVALID_CODE")


def test_update_public_inquiry_with_no_changes_succeeds(db_session):
    """Test updating inquiry with no field changes succeeds."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    from app.schemas.inquiries import PublicInquiryUpdateRequest

    payload = PublicInquiryUpdateRequest(
        inquiry_code=inquiry.inquiry_code,
        email=inquiry.email,
        parent_mobile=inquiry.parent_mobile,
        # All other fields None (no changes)
    )

    updated = service.update_public_inquiry(payload, request_mock)
    assert updated.id == inquiry.id
    # No fields changed, so names remain same
    assert updated.first_name == inquiry.first_name


def test_update_inquiry_admin_with_internal_notes(db_session):
    """Test admin update of inquiry with internal notes."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    from app.schemas.inquiries import AdminInquiryUpdateRequest

    payload = AdminInquiryUpdateRequest(
        internal_notes="This student needs special attention",
        admission_for_class_id=None,
    )

    updated = service.update_inquiry_admin(inquiry.id, payload, actor_id=1, request=request_mock)
    assert updated.internal_notes == "This student needs special attention"


def test_start_review_transition_succeeds(db_session):
    """Test start_review transitions PENDING → UNDER_REVIEW."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    updated = service.start_review(inquiry.id, actor_id=1, request=request_mock, notes="Starting review")
    assert updated.status == InquiryStatus.UNDER_REVIEW.value


def test_mark_processing_transition_succeeds(db_session):
    """Test mark_processing transitions UNDER_REVIEW → PROCESSING."""
    inquiry = create_sample_inquiry(db_session)
    # First transition to UNDER_REVIEW
    service = InquiryService(db_session)
    request_mock = MagicMock()

    updated = service.start_review(inquiry.id, actor_id=1, request=request_mock, notes=None)
    assert updated.status == InquiryStatus.UNDER_REVIEW.value

    # Now mark as processing
    processed = service.mark_processing(inquiry.id, actor_id=1, request=request_mock, notes="Processing")
    assert processed.status == InquiryStatus.PROCESSING.value


def test_reject_inquiry_from_pending_succeeds(db_session):
    """Test rejecting inquiry from PENDING status."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    updated = service.reject_inquiry(inquiry.id, "Not eligible", actor_id=1, request=request_mock)
    assert updated.status == InquiryStatus.REJECTED.value
    assert updated.rejection_reason == "Not eligible"


def test_reject_inquiry_with_empty_reason_fails(db_session):
    """Test rejecting inquiry with empty reason raises error."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    with pytest.raises(BusinessRuleException):
        service.reject_inquiry(inquiry.id, "", actor_id=1, request=request_mock)


def test_audit_log_called_on_inquiry_create(db_session):
    """Test that audit log is created when inquiry is created."""
    service = InquiryService(db_session)
    request_mock = MagicMock()

    from app.schemas.inquiries import PublicInquiryCreateRequest
    from app.models.enums import Gender

    payload = PublicInquiryCreateRequest(
        first_name="Audit",
        middle_name="Test",
        last_name="Student",
        gender=Gender.MALE,
        father_name="Parent",
        dob=date(2016, 6, 15),
        student_mobile="03001234567",
        parent_mobile="03009876543",
        email="audit@test.local",
        address="123 St",
        last_school="School",
        current_class="Class 5",
        admission_for_class="Class 6",
        last_school_percentage=None,
        admission_for_class_id=None,
    )

    # Mock audit service to verify it was called
    with patch.object(service.audit, "log") as mock_log:
        inquiry = service.create_public_inquiry(payload, request_mock)
        mock_log.assert_called_once()
        call_kwargs = mock_log.call_args[1]
        assert call_kwargs["action"] == "inquiry.create.public"
        assert call_kwargs["entity_type"] == "student_inquiry"
        assert call_kwargs["entity_id"] == inquiry.id


def test_audit_log_called_on_status_transition(db_session):
    """Test that audit log is created on status transition."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    # Mock audit service
    with patch.object(service.audit, "log") as mock_log:
        service.start_review(inquiry.id, actor_id=1, request=request_mock, notes="Testing audit")
        # Should have been called for the transition
        assert mock_log.called


def test_list_inquiries_with_pagination(db_session):
    """Test listing inquiries with pagination."""
    # Create a few inquiries
    for i in range(3):
        inquiry_code, serial = generate_inquiry_identifiers(db_session)
        inquiry = StudentInquiry(
            inquiry_code=inquiry_code,
            serial_number=serial,
            first_name=f"Student{i}",
            last_name="Test",
            father_name=f"Parent{i}",
            date_of_birth=date(2016, 1, 1),
            gender="male",
            parent_mobile=f"0300123456{i}",
            email=f"test{i}@test.local",
            status=InquiryStatus.PENDING.value,
        )
        repo = StudentInquiryRepository(db_session)
        repo.create(inquiry)
    db_session.commit()

    service = InquiryService(db_session)
    from app.core.pagination import PaginationParams

    params = PaginationParams(page=1, limit=2)
    result = service.list_inquiries(params)

    assert len(result.items) <= 2
    assert result.total >= 3


def test_list_inquiries_filter_by_status(db_session):
    """Test listing inquiries filtered by status."""
    # Create inquiries with different statuses
    inquiry1_code, serial1 = generate_inquiry_identifiers(db_session)
    inquiry1 = StudentInquiry(
        inquiry_code=inquiry1_code,
        serial_number=serial1,
        first_name="Student1",
        last_name="Test",
        father_name="Parent",
        date_of_birth=date(2016, 1, 1),
        gender="male",
        parent_mobile="03001234567",
        email="test1@test.local",
        status=InquiryStatus.PENDING.value,
    )
    repo = StudentInquiryRepository(db_session)
    repo.create(inquiry1)

    inquiry2_code, serial2 = generate_inquiry_identifiers(db_session)
    inquiry2 = StudentInquiry(
        inquiry_code=inquiry2_code,
        serial_number=serial2,
        first_name="Student2",
        last_name="Test",
        father_name="Parent2",
        date_of_birth=date(2016, 2, 1),
        gender="female",
        parent_mobile="03009876543",
        email="test2@test.local",
        status=InquiryStatus.UNDER_REVIEW.value,
    )
    repo.create(inquiry2)
    db_session.commit()

    service = InquiryService(db_session)
    from app.core.pagination import PaginationParams

    params = PaginationParams(page=1, limit=10)
    result = service.list_inquiries(params, status=InquiryStatus.PENDING.value)

    # Should only return PENDING inquiries
    assert all(item.status == InquiryStatus.PENDING.value for item in result.items)


def test_get_inquiry_with_invalid_id_raises_not_found(db_session):
    """Test get_inquiry raises NotFoundException for invalid ID."""
    service = InquiryService(db_session)

    with pytest.raises(NotFoundException):
        service.get_inquiry(99999)


def test_transition_status_without_transaction_management(db_session):
    """Test transition_status can be called with manage_transaction=False."""
    inquiry = create_sample_inquiry(db_session)
    service = InquiryService(db_session)
    request_mock = MagicMock()

    # Call with manage_transaction=False
    updated = service.transition_status(
        inquiry.id,
        InquiryStatus.UNDER_REVIEW.value,
        actor_id=1,
        request=request_mock,
        manage_transaction=False,
    )
    assert updated.status == InquiryStatus.UNDER_REVIEW.value
