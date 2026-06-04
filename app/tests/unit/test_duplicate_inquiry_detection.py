"""
Unit tests for duplicate student inquiry detection.

Tests the find_duplicate_inquiry() method and integration with create_public_inquiry().
"""

from datetime import date, datetime
import itertools
from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException
from app.models.enums import Gender, InquiryStatus
from app.repositories.inquiries import StudentInquiryRepository
from app.schemas.inquiries import PublicInquiryCreateRequest
from app.services.inquiries import InquiryService


def make_unique_name():
    """Generate a unique name using UUID to avoid test collisions."""
    return str(uuid4())[:8]


def make_unique_inquiry_identifier():
    """Create a unique inquiry code and serial number for tests."""
    current_year = datetime.now().year
    serial_number = uuid4().int % 100000000
    inquiry_code = f"INQ{current_year}{serial_number:08d}"
    return inquiry_code, serial_number


def create_test_inquiry(repo, inquiry_code, serial_number, first_name, last_name, father_name, dob, status=InquiryStatus.PENDING.value, student_mobile=None, parent_mobile=None, email=None):
    """Create a test StudentInquiry using auto-increment IDs in SQLite."""
    from app.models.student_inquiry import StudentInquiry

    inquiry = StudentInquiry(
        inquiry_code=inquiry_code,
        serial_number=serial_number,
        first_name=first_name,
        middle_name=None,
        last_name=last_name,
        gender=Gender.MALE.value,
        father_name=father_name,
        date_of_birth=dob,
        student_mobile=student_mobile or "03001234567",
        parent_mobile=parent_mobile or "03009876543",
        email=email or f"{first_name.lower()}.{last_name.lower()}@example.com",
        address="123 Main Street",
        last_school="ABC School",
        current_class="Class 5",
        admission_for_class="Class 6",
        status=status,
    )
    return repo.create(inquiry)


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

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        inquiry1 = create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
        )

        # Check for duplicate
        duplicate = repo.find_duplicate_inquiry(
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            date_of_birth=dob,
        )

        assert duplicate is not None
        assert duplicate.id == inquiry1.id
        assert duplicate.inquiry_code == inquiry_code

    def test_find_duplicate_case_insensitive(self, db_session: Session):
        """Test that duplicate detection is case-insensitive."""
        repo = StudentInquiryRepository(db_session)

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        inquiry1 = create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
        )
        db_session.commit()

        # Check with different case
        duplicate = repo.find_duplicate_inquiry(
            first_name=unique_first.upper(),
            last_name=unique_last.lower(),
            father_name=unique_father.upper(),
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is not None
        assert duplicate.id == inquiry1.id

    def test_no_duplicate_different_names(self, db_session: Session):
        """Test that different names are not considered duplicates."""
        repo = StudentInquiryRepository(db_session)

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
        )
        db_session.commit()

        # Check with different first name
        duplicate = repo.find_duplicate_inquiry(
            first_name="Ali",
            last_name=unique_last,
            father_name=unique_father,
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_no_duplicate_different_dob(self, db_session: Session):
        """Test that different DOB is not considered a duplicate."""
        repo = StudentInquiryRepository(db_session)

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
        )
        db_session.commit()

        # Check with different DOB (sibling with different DOB)
        duplicate = repo.find_duplicate_inquiry(
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            date_of_birth=date(2016, 3, 20),  # Different DOB
        )

        assert duplicate is None

    def test_excluded_rejected_status(self, db_session: Session):
        """Test that REJECTED inquiries are excluded from duplicate detection."""
        repo = StudentInquiryRepository(db_session)

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
            status=InquiryStatus.REJECTED.value,
        )
        db_session.commit()

        # Check for duplicate - should NOT find it because it's REJECTED
        duplicate = repo.find_duplicate_inquiry(
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_excluded_interview_fail_status(self, db_session: Session):
        """Test that INTERVIEW_FAIL inquiries are excluded from duplicate detection."""
        repo = StudentInquiryRepository(db_session)

        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
            status=InquiryStatus.INTERVIEW_FAIL.value,
        )
        db_session.commit()

        # Check for duplicate - should NOT find it because it's INTERVIEW_FAIL
        duplicate = repo.find_duplicate_inquiry(
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            date_of_birth=date(2015, 6, 15),
        )

        assert duplicate is None

    def test_service_raises_conflict_on_duplicate(self, db_session: Session, sample_inquiry_data):
        """Test that InquiryService raises ConflictException on duplicate."""
        from unittest.mock import MagicMock

        repo = StudentInquiryRepository(db_session)

        # Create first inquiry with unique data
        unique_first = make_unique_name()
        unique_last = make_unique_name()
        unique_father = make_unique_name()
        dob = date(2015, 6, 15)
        inquiry_code, serial_number = make_unique_inquiry_identifier()

        create_test_inquiry(
            repo=repo,
            inquiry_code=inquiry_code,
            serial_number=serial_number,
            first_name=unique_first,
            last_name=unique_last,
            father_name=unique_father,
            dob=dob,
        )
        db_session.commit()

        # Create service and attempt to create duplicate
        service = InquiryService(db_session)
        request_mock = MagicMock()
        
        # Update sample_inquiry_data to match our created inquiry
        duplicate_request = PublicInquiryCreateRequest(
            first_name=unique_first,
            middle_name="Test",
            last_name=unique_last,
            gender="male",
            father_name=unique_father,
            dob="2015-06-15",
            student_mobile="03001234567",
            parent_mobile="03009876543",
            email="test@example.com",
            address="123 Main Street",
            last_school="ABC School",
            current_class="Class 5",
            admission_for_class="Class 6",
        )

        with pytest.raises(ConflictException) as exc_info:
            service.create_public_inquiry(duplicate_request, request_mock)

        assert "Student inquiry already exists" in str(exc_info.value.message)
