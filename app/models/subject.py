from sqlalchemy import BigInteger, Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BigInt


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(BigInt, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


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
