"""Data access for inquiry_admissions and admission_documents."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.pagination import PaginatedResult, PaginationParams
from app.models.admission import AdmissionDocument, InquiryAdmission
from app.repositories.base import BaseRepository


class InquiryAdmissionRepository(BaseRepository[InquiryAdmission]):
    """CRUD for inquiry-linked admissions."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, InquiryAdmission)

    def get_by_inquiry_id(self, inquiry_id: int) -> InquiryAdmission | None:
        stmt = select(InquiryAdmission).where(InquiryAdmission.inquiry_id == inquiry_id)
        return self.session.scalar(stmt)

    def get_with_documents(self, admission_id: int) -> InquiryAdmission | None:
        stmt = (
            select(InquiryAdmission)
            .where(InquiryAdmission.id == admission_id)
            .options(
                selectinload(InquiryAdmission.documents),
                selectinload(InquiryAdmission.inquiry),
                selectinload(InquiryAdmission.school_class),
            )
        )
        return self.session.scalar(stmt)

    def list_filtered(
        self,
        params: PaginationParams,
        status: str | None = None,
        academic_year: str | None = None,
    ) -> PaginatedResult:
        stmt = select(InquiryAdmission)
        if status:
            stmt = stmt.where(InquiryAdmission.status == status)
        if academic_year:
            stmt = stmt.where(InquiryAdmission.academic_year == academic_year)
        return self.paginate(stmt, params)


class AdmissionDocumentRepository(BaseRepository[AdmissionDocument]):
    """CRUD for admission document rows."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, AdmissionDocument)

    def get_by_admission_and_type(
        self,
        admission_id: int,
        document_type: str,
    ) -> AdmissionDocument | None:
        stmt = select(AdmissionDocument).where(
            AdmissionDocument.admission_id == admission_id,
            AdmissionDocument.document_type == document_type,
        )
        return self.session.scalar(stmt)

    def list_for_admission(self, admission_id: int) -> list[AdmissionDocument]:
        stmt = select(AdmissionDocument).where(AdmissionDocument.admission_id == admission_id)
        return list(self.session.scalars(stmt).all())
