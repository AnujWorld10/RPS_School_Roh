"""
Admission application and document verification (inquiry-driven flow).
"""

from datetime import UTC, datetime

from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from app.core.pagination import PaginatedResult, PaginationParams
from app.core.transactions import transaction
from app.models.admission import AdmissionDocument, InquiryAdmission
from app.models.enums import (
    REQUIRED_ADMISSION_DOCUMENTS,
    AdmissionStatus,
    ClassStatus,
    DocumentVerificationStatus,
    InquiryStatus,
)
from app.repositories.classes import ClassRepository
from app.repositories.inquiries import StudentInquiryRepository
from app.repositories.inquiry_admissions import (
    AdmissionDocumentRepository,
    InquiryAdmissionRepository,
)
from app.schemas.admissions import InquiryAdmissionCreateRequest, InquiryAdmissionUpdateRequest
from app.services.audit import AuditService
from app.services.inquiries import InquiryService
from app.utils.business_ids import generate_admission_code
from app.utils.file_storage import save_upload_file


class InquiryAdmissionService:
    """Manage admission forms, uploads, and document verification."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = InquiryAdmissionRepository(session)
        self.documents = AdmissionDocumentRepository(session)
        self.inquiries = StudentInquiryRepository(session)
        self.classes = ClassRepository(session)
        self.inquiry_service = InquiryService(session)
        self.audit = AuditService(session)

    def create_from_inquiry(
        self,
        inquiry_id: int,
        payload: InquiryAdmissionCreateRequest,
        actor_id: int | None,
        request: Request,
    ) -> InquiryAdmission:
        """
        Open an admission application for an inquiry that passed the interview.

        Moves inquiry to DOCUMENT_PENDING when submitted.
        """
        inquiry = self.inquiries.get_by_id(inquiry_id)
        if not inquiry:
            raise NotFoundException("Inquiry not found")
        if inquiry.status != InquiryStatus.INTERVIEW_PASS.value:
            raise BusinessRuleException("Admission requires inquiry status INTERVIEW_PASS")
        if self.repo.get_by_inquiry_id(inquiry_id):
            raise ConflictException("Admission already exists for this inquiry")

        school_class = self.classes.get_active(payload.class_id)
        if not school_class or school_class.status != ClassStatus.ACTIVE.value:
            raise NotFoundException("Class not found")

        with transaction(self.session):
            admission = self.repo.create(
                InquiryAdmission(
                    admission_code=generate_admission_code(self.session),
                    inquiry_id=inquiry_id,
                    class_id=payload.class_id,
                    section=payload.section or school_class.section,
                    academic_year=payload.academic_year,
                    status=AdmissionStatus.SUBMITTED.value,
                    permanent_address=payload.permanent_address or inquiry.address,
                    temporary_address=payload.temporary_address,
                    nationality=payload.nationality,
                    disability=payload.disability,
                    blood_group=payload.blood_group,
                    reason_for_school_change=payload.reason_for_school_change,
                    notes=payload.notes,
                )
            )
            self.inquiry_service.transition_status(
                inquiry_id,
                InquiryStatus.DOCUMENT_PENDING.value,
                actor_id,
                request,
                change_reason="Admission application submitted",
                manage_transaction=False,
            )
            self.audit.log(
                action="admission.create",
                entity_type="inquiry_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def get_admission(self, admission_id: int) -> InquiryAdmission:
        admission = self.repo.get_with_documents(admission_id)
        if not admission:
            raise NotFoundException("Admission not found")
        return admission

    def list_admissions(
        self,
        params: PaginationParams,
        status: str | None = None,
        academic_year: str | None = None,
    ) -> PaginatedResult:
        return self.repo.list_filtered(params, status, academic_year)

    def update_admission(
        self,
        admission_id: int,
        payload: InquiryAdmissionUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> InquiryAdmission:
        admission = self.get_admission(admission_id)
        if admission.status in (AdmissionStatus.APPROVED.value, AdmissionStatus.REJECTED.value):
            raise BusinessRuleException("Cannot update closed admission")
        with transaction(self.session):
            for field in (
                "class_id",
                "section",
                "academic_year",
                "permanent_address",
                "temporary_address",
                "nationality",
                "disability",
                "blood_group",
                "reason_for_school_change",
                "notes",
            ):
                value = getattr(payload, field)
                if value is not None:
                    setattr(admission, field, value)
            admission = self.repo.update(admission)
            self.audit.log(
                action="admission.update",
                entity_type="inquiry_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def upload_document(
        self,
        admission_id: int,
        document_type: str,
        file: UploadFile,
        request: Request,
    ) -> AdmissionDocument:
        """Upload or replace one required document type."""
        if document_type not in REQUIRED_ADMISSION_DOCUMENTS:
            raise BusinessRuleException(f"Invalid document type: {document_type}")

        admission = self.get_admission(admission_id)
        if admission.status == AdmissionStatus.REJECTED.value:
            raise BusinessRuleException("Cannot upload documents for rejected admission")

        relative_path, original_name = save_upload_file(
            file,
            f"admissions/{admission_id}",
        )

        with transaction(self.session):
            existing = self.documents.get_by_admission_and_type(admission_id, document_type)
            if existing:
                existing.file_name = original_name
                existing.file_path = relative_path
                existing.verification_status = DocumentVerificationStatus.PENDING.value
                existing.rejection_reason = None
                doc = self.documents.update(existing)
            else:
                doc = self.documents.create(
                    AdmissionDocument(
                        admission_id=admission_id,
                        document_type=document_type,
                        file_name=original_name,
                        file_path=relative_path,
                        mime_type=file.content_type,
                    )
                )
            self.audit.log(
                action="admission.document.upload",
                entity_type="admission_document",
                entity_id=doc.id,
                request=request,
            )
            return doc

    def verify_document(
        self,
        document_id: int,
        verified: bool,
        actor_id: int,
        request: Request,
        rejection_reason: str | None = None,
    ) -> AdmissionDocument:
        """Mark a document VERIFIED or REJECTED; may advance admission to document verification."""
        doc = self.documents.get_by_id(document_id)
        if not doc:
            raise NotFoundException("Document not found")
        if not verified and not rejection_reason:
            raise BusinessRuleException("Rejection reason is required when rejecting a document")

        with transaction(self.session):
            if verified:
                doc.verification_status = DocumentVerificationStatus.VERIFIED.value
                doc.verified_by = actor_id
                doc.verified_at = datetime.now(UTC)
                doc.rejection_reason = None
            else:
                doc.verification_status = DocumentVerificationStatus.REJECTED.value
                doc.rejection_reason = rejection_reason
                doc.verified_by = actor_id
                doc.verified_at = datetime.now(UTC)
            doc = self.documents.update(doc)
            self._sync_admission_document_status(doc.admission_id, actor_id, request)
            return doc

    def _sync_admission_document_status(
        self,
        admission_id: int,
        actor_id: int,
        request: Request,
    ) -> None:
        """When all required docs are verified, move admission and inquiry forward."""
        admission = self.get_admission(admission_id)
        docs = self.documents.list_for_admission(admission_id)
        uploaded_types = {d.document_type for d in docs}
        if not REQUIRED_ADMISSION_DOCUMENTS.issubset(uploaded_types):
            return

        if any(d.verification_status == DocumentVerificationStatus.REJECTED.value for d in docs):
            return

        if all(d.verification_status == DocumentVerificationStatus.VERIFIED.value for d in docs):
            admission.status = AdmissionStatus.DOCUMENT_VERIFICATION.value
            self.repo.update(admission)
            self.inquiry_service.transition_status(
                admission.inquiry_id,
                InquiryStatus.DOCUMENT_VERIFICATION.value,
                actor_id,
                request,
                change_reason="All documents verified",
                manage_transaction=False,
            )

    def submit_for_enrollment(
        self,
        admission_id: int,
        actor_id: int,
        request: Request,
    ) -> InquiryAdmission:
        """
        Mark admission approved and ready for enrollment (all docs verified).

        Inquiry must be in DOCUMENT_VERIFICATION.
        """
        admission = self.get_admission(admission_id)
        docs = self.documents.list_for_admission(admission_id)
        uploaded = {d.document_type for d in docs}
        if not REQUIRED_ADMISSION_DOCUMENTS.issubset(uploaded):
            raise BusinessRuleException("All required documents must be uploaded")
        if not all(
            d.verification_status == DocumentVerificationStatus.VERIFIED.value for d in docs
        ):
            raise BusinessRuleException("All documents must be verified before approval")

        with transaction(self.session):
            admission.status = AdmissionStatus.APPROVED.value
            admission.approved_by = actor_id
            admission.approved_at = datetime.now(UTC)
            admission = self.repo.update(admission)
            self.audit.log(
                action="admission.approve",
                entity_type="inquiry_admission",
                entity_id=admission.id,
                actor_user_id=actor_id,
                request=request,
            )
            return admission

    def reject_admission(
        self,
        admission_id: int,
        rejection_reason: str,
        actor_id: int,
        request: Request,
    ) -> InquiryAdmission:
        admission = self.get_admission(admission_id)
        with transaction(self.session):
            admission.status = AdmissionStatus.REJECTED.value
            admission.rejection_reason = rejection_reason
            admission = self.repo.update(admission)
            self.inquiry_service.transition_status(
                admission.inquiry_id,
                InquiryStatus.REJECTED.value,
                actor_id,
                request,
                rejection_reason=rejection_reason,
                manage_transaction=False,
            )
            return admission
