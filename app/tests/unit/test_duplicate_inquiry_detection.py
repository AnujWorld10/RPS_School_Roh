"""
Unit tests for duplicate student inquiry detection.

Tests the find_duplicate_inquiry() method and integration with create_public_inquiry().
"""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException
from app.models.enums import Gender, InquiryStatus
from app.repositories.inquiries import StudentInquiryRepository
from app.schemas.inquiries import PublicInquiryCreateRequest
from app.services.inquiries import InquiryService


class TestDuplicateInquiryDetection:
    """Test duplicate detection using student name, father name, and DOB."""

    @pytest.fixture
    def sample_inquiry_data(self) -> PublicInquiryCreateRequest:
        """Create a sample inquiry request for testing."""
        return PublicInquiryCreateRequest(
            first_name="Ahmed",
            middle_name="Ali",
            last_name="Khan",
            gender=Gender.MALE,
            father_name="Mohammed Khan",
            dob=date(2015, 6, 15),
            student_mobile="03001234567",
            parent_mobile="03009876543",
            email="parent@example.com",
            address="123 Main Street",
            last_school="ABC School",
            current_class="Class 5",
            admission_for_class="Class 6",
            last_school_percentage=None,
            admission_for_class_id=None,
        )

    def test_find_duplicate_with_exact_match(self, db_session: Session, sample_inquiry_data):
        """Test that duplicate is found with exact name and DOB match."""
        repo = StudentInquiryRepository(db_session)

        # Create first inquiry
        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        inquiry1 = repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.PENDING.value,
            )
        )
        db_session.commit()

        # Check for duplicate
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ahmed",
            last_name="Khan",
            father_name="Mohammed Khan",
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is not None
        assert duplicate.id == inquiry1.id
        assert duplicate.inquiry_code == inquiry_code

    def test_find_duplicate_case_insensitive(self, db_session: Session):
        """Test that duplicate detection is case-insensitive."""
        repo = StudentInquiryRepository(db_session)

        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        inquiry1 = repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.PENDING.value,
            )
        )
        db_session.commit()

        # Check with different case
        duplicate = repo.find_duplicate_inquiry(
            first_name="AHMED",
            last_name="khan",
            father_name="mohammed KHAN",
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is not None
        assert duplicate.id == inquiry1.id

    def test_no_duplicate_different_names(self, db_session: Session):
        """Test that different names are not considered duplicates."""
        repo = StudentInquiryRepository(db_session)

        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.PENDING.value,
            )
        )
        db_session.commit()

        # Check with different first name
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ali",
            last_name="Khan",
            father_name="Mohammed Khan",
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_no_duplicate_different_dob(self, db_session: Session):
        """Test that different DOB is not considered a duplicate."""
        repo = StudentInquiryRepository(db_session)

        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.PENDING.value,
            )
        )
        db_session.commit()

        # Check with different DOB (sibling with different DOB)
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ahmed",
            last_name="Khan",
            father_name="Mohammed Khan",
            date_of_birth=date(2016, 3, 20),  # Different DOB
        )

        assert duplicate is None

    def test_excluded_rejected_status(self, db_session: Session):
        """Test that REJECTED inquiries are excluded from duplicate detection."""
        repo = StudentInquiryRepository(db_session)

        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.REJECTED.value,  # REJECTED status
            )
        )
        db_session.commit()

        # Check for duplicate - should NOT find it because it's REJECTED
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ahmed",
            last_name="Khan",
            father_name="Mohammed Khan",
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_excluded_interview_fail_status(self, db_session: Session):
        """Test that INTERVIEW_FAIL inquiries are excluded from duplicate detection."""
        repo = StudentInquiryRepository(db_session)

        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry

        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.INTERVIEW_FAIL.value,  # INTERVIEW_FAIL status
            )
        )
        db_session.commit()

        # Check for duplicate - should NOT find it because it's INTERVIEW_FAIL
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ahmed",
            last_name="Khan",
            father_name="Mohammed Khan",
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_service_raises_conflict_on_duplicate(self, db_session: Session, sample_inquiry_data):
        """Test that InquiryService raises ConflictException on duplicate."""
        from app.utils.inquiry_ids import generate_inquiry_identifiers
        from app.models.student_inquiry import StudentInquiry
        from unittest.mock import MagicMock

        repo = StudentInquiryRepository(db_session)

        # Create first inquiry
        inquiry_code, serial_number = generate_inquiry_identifiers(db_session)
        repo.create(
            StudentInquiry(
                inquiry_code=inquiry_code,
                serial_number=serial_number,
                first_name="Ahmed",
                last_name="Khan",
                father_name="Mohammed Khan",
                date_of_birth=date(2015, 6, 15),
                gender=Gender.MALE.value,
                parent_mobile="03009876543",
                email="parent1@example.com",
                address="123 Main Street",
                last_school="ABC School",
                current_class="Class 5",
                admission_for_class="Class 6",
                status=InquiryStatus.PENDING.value,
            )
        )
        db_session.commit()

        # Create service and attempt to create duplicate
        service = InquiryService(db_session)
        request_mock = MagicMock()

        with pytest.raises(ConflictException) as exc_info:
            service.create_public_inquiry(sample_inquiry_data, request_mock)

        assert "Student inquiry already exists" in str(exc_info.value.message)
