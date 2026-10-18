"""Domain enumerations used across ORM models and Pydantic schemas."""

from enum import StrEnum


class UserStatus(StrEnum):
    """Lifecycle state of a platform user account."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class ClassStatus(StrEnum):
    """Whether a school class record is open for admissions."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class StudentStatus(StrEnum):
    """Enrollment lifecycle for a registered student."""

    PROSPECTIVE = "prospective"
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"


class AdmissionStatus(StrEnum):
    """Workflow state of an inquiry-linked admission application."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    DOCUMENT_PENDING = "document_pending"
    DOCUMENT_VERIFICATION = "document_verification"
    APPROVED = "approved"
    REJECTED = "rejected"


class Gender(StrEnum):
    """Student gender values accepted on public inquiry forms."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class InquiryStatus(StrEnum):
    """
    End-to-end pipeline status for a student admission inquiry.

    Transitions are recorded in ``inquiry_status_history``.
    """

    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    PROCESSING = "PROCESSING"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    INTERVIEW_PASS = "INTERVIEW_PASS"
    INTERVIEW_FAIL = "INTERVIEW_FAIL"
    DOCUMENT_PENDING = "DOCUMENT_PENDING"
    DOCUMENT_VERIFICATION = "DOCUMENT_VERIFICATION"
    ADMISSION_SUCCESS = "ADMISSION_SUCCESS"
    REJECTED = "REJECTED"


INQUIRY_LOCKED_STATUSES: frozenset[str] = frozenset(
    {
        InquiryStatus.ADMISSION_SUCCESS.value,
        InquiryStatus.REJECTED.value,
        InquiryStatus.INTERVIEW_FAIL.value,
    }
)

INQUIRY_ADMIN_TRANSITIONS: dict[str, set[str]] = {
    InquiryStatus.PENDING.value: {
        InquiryStatus.UNDER_REVIEW.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.UNDER_REVIEW.value: {
        InquiryStatus.PROCESSING.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.PROCESSING.value: {
        InquiryStatus.INTERVIEW_SCHEDULED.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.INTERVIEW_SCHEDULED.value: {
        InquiryStatus.INTERVIEW_PASS.value,
        InquiryStatus.INTERVIEW_FAIL.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.INTERVIEW_PASS.value: {
        InquiryStatus.DOCUMENT_PENDING.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.DOCUMENT_PENDING.value: {
        InquiryStatus.DOCUMENT_VERIFICATION.value,
        InquiryStatus.REJECTED.value,
    },
    InquiryStatus.DOCUMENT_VERIFICATION.value: {
        InquiryStatus.DOCUMENT_PENDING.value,
        InquiryStatus.ADMISSION_SUCCESS.value,
        InquiryStatus.REJECTED.value,
    },
}


class InterviewMode(StrEnum):
    """How the interview or test is conducted."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class InterviewResult(StrEnum):
    """Outcome of a scheduled interview (null until completed)."""

    SCHEDULED = "SCHEDULED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ABSENT = "ABSENT"


class InterviewResultUpdate(StrEnum):
    """Allowed values when staff records interview outcome."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    ABSENT = "ABSENT"


class DocumentType(StrEnum):
    """Required admission document types per FRD."""

    PROGRESS_REPORT = "progress_report"
    TRANSFER_CERTIFICATE = "transfer_certificate"
    MIGRATION_CERTIFICATE = "migration_certificate"
    CHARACTER_CERTIFICATE = "character_certificate"
    STUDENT_AADHAR = "student_aadhar"
    PARENT_AADHAR = "parent_aadhar"


REQUIRED_ADMISSION_DOCUMENTS: frozenset[str] = frozenset(d.value for d in DocumentType)


class DocumentVerificationStatus(StrEnum):
    """Staff verification state for an uploaded document."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class TeacherStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    HALF_DAY = "half_day"


class SalaryStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
