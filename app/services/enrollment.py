"""
Student enrollment: create student record, roll number, and complete inquiry pipeline.
"""

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, NotFoundException
from app.core.transactions import transaction
from app.models.enums import AdmissionStatus, ClassStatus, InquiryStatus, StudentStatus
from app.models.student import Student
from app.repositories.classes import ClassRepository
from app.repositories.inquiry_admissions import InquiryAdmissionRepository
from app.repositories.students import StudentRepository
from app.schemas.enrollment import EnrollmentResponse
from app.services.audit import AuditService
from app.services.inquiries import InquiryService
from app.utils.business_ids import allocate_roll_number, generate_student_code


class EnrollmentService:
    """Finalize admission by creating an enrolled student with roll number."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.admissions = InquiryAdmissionRepository(session)
        self.students = StudentRepository(session)
        self.classes = ClassRepository(session)
        self.inquiry_service = InquiryService(session)
        self.audit = AuditService(session)

    def enroll_student(
        self,
        admission_id: int,
        actor_id: int,
        request: Request,
    ) -> EnrollmentResponse:
        """
        Create ``students`` row from approved admission and set inquiry to ADMISSION_SUCCESS.

        Args:
            admission_id: PK of inquiry_admissions.
            actor_id: Staff user performing enrollment.
            request: FastAPI request for audit metadata.

        Returns:
            EnrollmentResponse with student and roll details.
        """
        admission = self.admissions.get_with_documents(admission_id)
        if not admission:
            raise NotFoundException("Admission not found")
        if admission.status != AdmissionStatus.APPROVED.value:
            raise BusinessRuleException("Admission must be approved before enrollment")
        if admission.student_id:
            raise BusinessRuleException("Student already enrolled for this admission")

        inquiry = admission.inquiry
        if not inquiry:
            raise NotFoundException("Linked inquiry not found")

        school_class = self.classes.get_active(admission.class_id)
        if not school_class or school_class.status != ClassStatus.ACTIVE.value:
            raise BusinessRuleException("Target class is not active")

        enrolled = self.classes.count_active_students(admission.class_id)
        if enrolled >= school_class.capacity:
            raise BusinessRuleException("Class capacity exceeded")

        with transaction(self.session):
            roll_number = allocate_roll_number(
                self.session,
                admission.class_id,
                admission.academic_year,
            )
            student_code = generate_student_code(self.session)
            student = self.students.create(
                Student(
                    student_code=student_code,
                    inquiry_id=inquiry.id,
                    first_name=inquiry.first_name,
                    last_name=inquiry.last_name,
                    date_of_birth=inquiry.date_of_birth,
                    gender=inquiry.gender,
                    email=inquiry.email,
                    phone=inquiry.student_mobile or inquiry.parent_mobile,
                    class_id=admission.class_id,
                    current_class_id=admission.class_id,
                    academic_year=admission.academic_year,
                    roll_number=roll_number,
                    status=StudentStatus.ACTIVE.value,
                )
            )
            admission.student_id = student.id
            self.admissions.update(admission)

            self.inquiry_service.transition_status(
                inquiry.id,
                InquiryStatus.ADMISSION_SUCCESS.value,
                actor_id,
                request,
                change_reason=f"Enrolled as {student_code}, roll {roll_number}",
                manage_transaction=False,
            )

            self.audit.log(
                action="student.enroll",
                entity_type="student",
                entity_id=student.id,
                actor_user_id=actor_id,
                new_values={
                    "student_code": student_code,
                    "roll_number": roll_number,
                    "admission_id": admission_id,
                },
                request=request,
            )

            return EnrollmentResponse(
                student_id=student.id,
                student_code=student_code,
                admission_id=admission.id,
                admission_code=admission.admission_code,
                inquiry_code=inquiry.inquiry_code,
                class_id=admission.class_id,
                section=admission.section,
                academic_year=admission.academic_year,
                roll_number=roll_number,
            )
