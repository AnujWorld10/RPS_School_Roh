"""Domain enumerations used across ORM models and Pydantic schemas."""

import enum


class UserStatus(str, enum.Enum):
    """Lifecycle state of a platform user account."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class ClassStatus(str, enum.Enum):
    """Whether a school class record is open for admissions."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class StudentStatus(str, enum.Enum):
    """Enrollment lifecycle for a registered student."""

    PROSPECTIVE = "prospective"
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"


class AdmissionStatus(str, enum.Enum):
    """Workflow state of an inquiry-linked admission application."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    DOCUMENT_PENDING = "document_pending"
    DOCUMENT_VERIFICATION = "document_verification"
    APPROVED = "approved"
    REJECTED = "rejected"


class Gender(str, enum.Enum):
    """Student gender values accepted on public inquiry forms."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class InquiryStatus(str, enum.Enum):
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
        InquiryStatus.ADMISSION_SUCCESS.value,
        InquiryStatus.REJECTED.value,
    },
}


class InterviewMode(str, enum.Enum):
    """How the interview or test is conducted."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class InterviewResult(str, enum.Enum):
    """Outcome of a scheduled interview (null until completed)."""

    SCHEDULED = "SCHEDULED"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ABSENT = "ABSENT"


class InterviewResultUpdate(str, enum.Enum):
    """Allowed values when staff records interview outcome."""

    PASSED = "PASSED"
    FAILED = "FAILED"
    ABSENT = "ABSENT"


class DocumentType(str, enum.Enum):
    """Required admission document types per FRD."""

    PROGRESS_REPORT = "progress_report"
    TRANSFER_CERTIFICATE = "transfer_certificate"
    MIGRATION_CERTIFICATE = "migration_certificate"
    CHARACTER_CERTIFICATE = "character_certificate"
    STUDENT_AADHAR = "student_aadhar"
    PARENT_AADHAR = "parent_aadhar"


REQUIRED_ADMISSION_DOCUMENTS: frozenset[str] = frozenset(d.value for d in DocumentType)


class DocumentVerificationStatus(str, enum.Enum):
    """Staff verification state for an uploaded document."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class TeacherStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    RESIGNED = "resigned"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    HALF_DAY = "half_day"


class SalaryStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
