"""SQLAlchemy ORM models — import all models for Alembic autogenerate."""

from app.models.admission import AdmissionDocument, InquiryAdmission, StudentAdmission
from app.models.audit_log import AuditLog
from app.models.business_id_sequence import BusinessIDSequence
from app.models.class_model import Class
from app.models.fees import (
    AdmissionFeeComponent,
    AdmissionFeeStructure,
    MonthlyFeeComponent,
    MonthlyFeeStructure,
)
from app.models.interview import InterviewSchedule
from app.models.permission import Permission, RolePermission
from app.models.refresh_token import RefreshToken
from app.models.role import Role, UserRole
from app.models.role_portal import (
    Assessment,
    AssessmentResult,
    Assignment,
    AssignmentAttachment,
    SchoolEvent,
    TimetableEntry,
)
from app.models.student import Student
from app.models.student_inquiry import InquiryStatusHistory, StudentInquiry
from app.models.subject import ClassSubject, Subject, TeacherClassSubject, TeacherSubject
from app.models.teacher import (
    Teacher,
    TeacherAttendance,
    TeacherClass,
    TeacherSalary,
    TeacherSalaryPayment,
)
from app.models.user import User

__all__ = [
    "User",
    "Role",
    "UserRole",
    "Permission",
    "RolePermission",
    "Class",
    "AdmissionFeeStructure",
    "AdmissionFeeComponent",
    "MonthlyFeeStructure",
    "MonthlyFeeComponent",
    "Student",
    "StudentAdmission",
    "InquiryAdmission",
    "AdmissionDocument",
    "StudentInquiry",
    "InquiryStatusHistory",
    "InterviewSchedule",
    "Teacher",
    "Subject",
    "ClassSubject",
    "TeacherSubject",
    "TeacherClassSubject",
    "TeacherClass",
    "TeacherAttendance",
    "TeacherSalary",
    "TeacherSalaryPayment",
    "RefreshToken",
    "AuditLog",
    "BusinessIDSequence",
    "Assignment",
    "AssignmentAttachment",
    "TimetableEntry",
    "Assessment",
    "AssessmentResult",
    "SchoolEvent",
]
