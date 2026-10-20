from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BIGINT_PK, Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = {"comment": "School subject catalog"}

    id: Mapped[int] = mapped_column(BIGINT_PK, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    class_assignments: Mapped[list["ClassSubject"]] = relationship(back_populates="subject")


class ClassSubject(Base):
    __tablename__ = "class_subjects"
    __table_args__ = {"comment": "Subjects offered to each class"}

    class_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="CASCADE", name="fk_class_subjects_class"),
        primary_key=True,
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE", name="fk_class_subjects_subject"),
        primary_key=True,
    )

    school_class: Mapped["Class"] = relationship(back_populates="subject_assignments")  # noqa: F821
    subject: Mapped[Subject] = relationship(back_populates="class_assignments")


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"
    __table_args__ = (UniqueConstraint("teacher_id", "subject_id", name="uq_teacher_subject"),)

    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    subject_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("subjects.id", ondelete="CASCADE"),
        primary_key=True,
    )


class TeacherClassSubject(Base):
    __tablename__ = "teacher_class_subjects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            ondelete="CASCADE",
            name="fk_teacher_class_subject_offering",
        ),
        {"comment": "Teacher assignments to class subject offerings"},
    )

    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "teachers.id",
            ondelete="CASCADE",
            name="fk_teacher_class_subjects_teacher",
        ),
        primary_key=True,
    )
    class_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "subjects.id",
            ondelete="CASCADE",
            name="fk_teacher_class_subjects_subject",
        ),
        primary_key=True,
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="class_subject_assignments")  # noqa: F821
