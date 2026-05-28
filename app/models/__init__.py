"""SQLAlchemy ORM models — import all models for Alembic autogenerate."""

from app.models.admission import AdmissionDocument, InquiryAdmission, StudentAdmission
from app.models.audit_log import AuditLog
from app.models.class_model import Class
from app.models.interview import InterviewSchedule
from app.models.permission import Permission, RolePermission
from app.models.refresh_token import RefreshToken
from app.models.role import Role, UserRole
from app.models.student import Student
from app.models.student_inquiry import InquiryStatusHistory, StudentInquiry
from app.models.subject import Subject, TeacherSubject
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
    "Student",
    "StudentAdmission",
    "InquiryAdmission",
    "AdmissionDocument",
    "StudentInquiry",
    "InquiryStatusHistory",
    "InterviewSchedule",
    "Teacher",
    "Subject",
    "TeacherSubject",
    "TeacherClass",
    "TeacherAttendance",
    "TeacherSalary",
    "TeacherSalaryPayment",
    "RefreshToken",
    "AuditLog",
]
