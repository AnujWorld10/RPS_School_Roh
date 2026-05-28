from sqlalchemy import BigInteger, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.enums import ClassStatus


class Class(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("name", "section", "academic_year", name="uq_class_name_section_year"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    section: Mapped[str | None] = mapped_column(String(20), nullable=True)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=ClassStatus.ACTIVE.value,
        nullable=False,
    )

    students: Mapped[list["Student"]] = relationship(  # noqa: F821
        back_populates="current_class",
        foreign_keys="Student.class_id",
    )
    inquiries: Mapped[list["StudentInquiry"]] = relationship(  # noqa: F821
        back_populates="target_class",
        foreign_keys="StudentInquiry.admission_for_class_id",
    )
