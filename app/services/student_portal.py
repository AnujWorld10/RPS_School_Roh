from fastapi import Request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import AuthenticationException, ConflictException, NotFoundException
from app.core.security import hash_password, validate_password_strength
from app.core.transactions import transaction
from app.models.admission import InquiryAdmission
from app.models.enums import AdmissionStatus, StudentStatus
from app.models.fees import AdmissionFeeStructure, MonthlyFeeStructure
from app.models.role import Role
from app.models.student import Student
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.fees import AdmissionFeeStructureResponse, MonthlyFeeStructureResponse
from app.schemas.student_portal import (
    StudentPortalFeeDetailsResponse,
    StudentPortalProfileResponse,
    StudentPortalRegistrationRequest,
    StudentPortalRegistrationResponse,
)
from app.services.audit import AuditService
from app.services.auth import AuthService

_INVALID_REGISTRATION = "Admission ID, email, or admission status is invalid."
_DUPLICATE_REGISTRATION = "A student portal account cannot be created for these details."
_FEES_UNAVAILABLE_MESSAGE = (
    "Fee schedules are shown below when configured. The school has not enabled fee invoices "
    "or payment collection, so paid amounts, balances, due dates, and payment status "
    "are unavailable."
)


class StudentPortalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.audit = AuditService(session)

    def register(
        self,
        payload: StudentPortalRegistrationRequest,
        request: Request,
    ) -> StudentPortalRegistrationResponse:
        validate_password_strength(payload.password)
        admission_id = payload.admission_id.strip().upper()
        email = payload.email.strip().casefold()
        try:
            with transaction(self.session):
                admission = self.session.scalar(
                    select(InquiryAdmission)
                    .where(InquiryAdmission.admission_code == admission_id)
                    .options(
                        joinedload(InquiryAdmission.student),
                        joinedload(InquiryAdmission.inquiry),
                    )
                    .with_for_update()
                )
                student = admission.student if admission else None
                if (
                    admission is None
                    or admission.status != AdmissionStatus.APPROVED.value
                    or student is None
                    or student.deleted_at is not None
                    or student.status != StudentStatus.ACTIVE.value
                    or student.student_code != admission.admission_code
                    or student.email is None
                    or student.email.strip().casefold() != email
                ):
                    raise AuthenticationException(_INVALID_REGISTRATION)
                if student.user_id is not None or self.users.email_exists(email):
                    raise ConflictException(_DUPLICATE_REGISTRATION)

                role = self.session.scalar(
                    select(Role).where(Role.code == "STUDENT", Role.is_active.is_(True))
                )
                if role is None:
                    raise RuntimeError("The STUDENT role is missing; seed the role catalog.")

                user = User(
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=email,
                    password_hash=hash_password(payload.password),
                )
                user.roles.append(role)
                self.session.add(user)
                self.session.flush()
                student.user_id = user.id
                self.session.flush()

                self.audit.log(
                    action="student.portal.register",
                    entity_type="student",
                    entity_id=student.id,
                    actor_user_id=user.id,
                    new_values={"user_id": user.id, "student_id": student.student_code},
                    request=request,
                )
                return StudentPortalRegistrationResponse(
                    student_id=student.student_code,
                    email=user.email,
                )
        except IntegrityError as exc:
            raise ConflictException(_DUPLICATE_REGISTRATION) from exc

    def login(self, student_id: str, password: str, request: Request) -> dict:
        student = self.session.scalar(
            select(Student)
            .where(
                Student.student_code == student_id.strip().upper(),
                Student.deleted_at.is_(None),
                Student.status == StudentStatus.ACTIVE.value,
            )
            .options(
                joinedload(Student.portal_user)
                .selectinload(User.roles)
                .selectinload(Role.permissions)
            )
        )
        if student is None or student.portal_user is None:
            raise AuthenticationException("Invalid student ID or password.")
        return AuthService(self.session).login(
            LoginRequest(
                email=student.portal_user.email,
                password=password,
                portal="student",
            ),
            request,
        )

    def get_profile(self, user_id: int) -> StudentPortalProfileResponse:
        student = self._get_student(user_id)
        portal_user = student.portal_user
        if portal_user is None:
            raise NotFoundException("Student profile not found.")
        admission = student.inquiry_admission
        inquiry = admission.inquiry if admission else None
        school_class = student.current_class
        return StudentPortalProfileResponse(
            student_id=student.student_code,
            admission_id=admission.admission_code
            if admission
            else student.admission_no or student.student_code,
            first_name=student.first_name,
            middle_name=inquiry.middle_name if inquiry else None,
            last_name=student.last_name,
            father_name=inquiry.father_name if inquiry else None,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            class_name=school_class.name if school_class else None,
            section=admission.section
            if admission
            else school_class.section
            if school_class
            else None,
            academic_year=student.academic_year,
            email=portal_user.email,
            phone=student.phone,
            address=admission.permanent_address
            if admission
            else inquiry.address
            if inquiry
            else None,
            admission_date=admission.approved_at if admission else None,
            status=student.status,
        )

    def get_fee_details(self, user_id: int) -> StudentPortalFeeDetailsResponse:
        student = self._get_student(user_id)
        admission_structure = None
        monthly_structure = None
        if student.class_id is not None and student.academic_year is not None:
            admission_structure = self.session.scalar(
                select(AdmissionFeeStructure)
                .where(
                    AdmissionFeeStructure.class_id == student.class_id,
                    AdmissionFeeStructure.academic_year == student.academic_year,
                    AdmissionFeeStructure.is_active.is_(True),
                )
                .options(
                    joinedload(AdmissionFeeStructure.school_class),
                    selectinload(AdmissionFeeStructure.components),
                )
            )
            monthly_structure = self.session.scalar(
                select(MonthlyFeeStructure)
                .where(
                    MonthlyFeeStructure.class_id == student.class_id,
                    MonthlyFeeStructure.academic_year == student.academic_year,
                    MonthlyFeeStructure.is_active.is_(True),
                )
                .options(
                    joinedload(MonthlyFeeStructure.school_class),
                    selectinload(MonthlyFeeStructure.components),
                )
            )
        return StudentPortalFeeDetailsResponse(
            student_id=student.student_code,
            class_id=student.class_id,
            academic_year=student.academic_year,
            admission_fee_structure=(
                AdmissionFeeStructureResponse.model_validate(admission_structure)
                if admission_structure
                else None
            ),
            monthly_fee_structure=(
                MonthlyFeeStructureResponse.model_validate(monthly_structure)
                if monthly_structure
                else None
            ),
            billing_message=_FEES_UNAVAILABLE_MESSAGE,
        )

    def _get_student(self, user_id: int) -> Student:
        student = self.session.scalar(
            select(Student)
            .where(
                Student.user_id == user_id,
                Student.deleted_at.is_(None),
                Student.status == StudentStatus.ACTIVE.value,
            )
            .options(
                joinedload(Student.portal_user),
                joinedload(Student.current_class),
                joinedload(Student.inquiry_admission).joinedload(InquiryAdmission.inquiry),
            )
        )
        if student is None or student.portal_user is None:
            raise NotFoundException("Student profile not found.")
        return student
