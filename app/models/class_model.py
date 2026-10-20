from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BIGINT_PK, Base, SoftDeleteMixin, TimestampMixin
from app.models.enums import ClassStatus


class Class(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint("name", "section", "academic_year", name="uq_class_name_section_year"),
        UniqueConstraint("class_teacher_id", name="uq_classes_class_teacher"),
        CheckConstraint(
            "status IN ('active', 'inactive')",
            name="ck_classes_class_status",
        ),
    )

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    class_teacher_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "teachers.id",
            ondelete="SET NULL",
            name="fk_classes_class_teacher",
        ),
        nullable=True,
        comment="Designated class teacher; one class per teacher.",
    )
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
    class_teacher: Mapped["Teacher | None"] = relationship(  # noqa: F821
        foreign_keys=[class_teacher_id],
        back_populates="homeroom_class",
    )
    subject_assignments: Mapped[list["ClassSubject"]] = relationship(  # noqa: F821
        back_populates="school_class",
        cascade="all, delete-orphan",
    )
