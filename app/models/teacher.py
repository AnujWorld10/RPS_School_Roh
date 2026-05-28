from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PaymentStatus, SalaryStatus, TeacherStatus


class Teacher(Base, TimestampMixin):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        unique=True,
        nullable=True,
    )
    employee_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=TeacherStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    salary: Mapped["TeacherSalary | None"] = relationship(back_populates="teacher", uselist=False)
    attendances: Mapped[list["TeacherAttendance"]] = relationship(back_populates="teacher")
    salary_payments: Mapped[list["TeacherSalaryPayment"]] = relationship(back_populates="teacher")


class TeacherClass(Base):
    __tablename__ = "teacher_classes"
    __table_args__ = (UniqueConstraint("teacher_id", "class_id", name="uq_teacher_class"),)

    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    class_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("classes.id", ondelete="CASCADE"),
        primary_key=True,
    )


class TeacherAttendance(Base):
    __tablename__ = "teacher_attendance"
    __table_args__ = (
        UniqueConstraint("teacher_id", "attendance_date", name="uq_teacher_attendance_date"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id"),
        nullable=False,
        index=True,
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)

    teacher: Mapped["Teacher"] = relationship(back_populates="attendances")


class TeacherSalary(Base):
    __tablename__ = "teacher_salary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id"),
        unique=True,
        nullable=False,
    )
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    allowance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    deduction: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=SalaryStatus.ACTIVE.value,
        nullable=False,
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="salary")
    payments: Mapped[list["TeacherSalaryPayment"]] = relationship(back_populates="salary")


class TeacherSalaryPayment(Base):
    __tablename__ = "teacher_salary_payments"
    __table_args__ = (
        UniqueConstraint("teacher_id", "payment_month", name="uq_teacher_payment_month"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teachers.id"),
        nullable=False,
        index=True,
    )
    salary_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("teacher_salary.id"),
        nullable=False,
    )
    payment_month: Mapped[str] = mapped_column(String(7), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deduction_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default=PaymentStatus.PENDING.value,
        nullable=False,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    teacher: Mapped["Teacher"] = relationship(back_populates="salary_payments")
    salary: Mapped["TeacherSalary"] = relationship(back_populates="payments")
