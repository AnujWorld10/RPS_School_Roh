from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.class_model import Class
from app.models.enums import AttendanceStatus, ClassStatus, PaymentStatus, TeacherStatus
from app.models.teacher import Teacher, TeacherAttendance, TeacherSalaryPayment
from app.schemas.classes import ClassUpdateRequest
from app.schemas.teachers import (
    AttendanceCreateRequest,
    SalaryPaymentCreateRequest,
    TeacherUpdateRequest,
)


def test_salary_payment_requires_exact_net_calculation():
    payment = SalaryPaymentCreateRequest(
        payment_month="2026-10",
        gross_amount=Decimal("1000.00"),
        deduction_amount=Decimal("125.00"),
        net_amount=Decimal("875.00"),
    )

    assert payment.net_amount == Decimal("875.00")
    assert payment.status is PaymentStatus.PAID


@pytest.mark.parametrize(
    ("gross", "deduction", "net"),
    [
        ("1000.00", "125.00", "874.99"),
        ("100.00", "101.00", "0.00"),
        ("100.001", "0.00", "100.001"),
    ],
)
def test_salary_payment_rejects_invalid_amounts(gross, deduction, net):
    with pytest.raises(ValidationError):
        SalaryPaymentCreateRequest(
            payment_month="2026-10",
            gross_amount=Decimal(gross),
            deduction_amount=Decimal(deduction),
            net_amount=Decimal(net),
        )


def test_attendance_request_rejects_unknown_state():
    with pytest.raises(ValidationError):
        AttendanceCreateRequest(
            attendance_date="2026-10-18",
            status="working-from-home",
        )


def test_state_schemas_use_domain_enums():
    with pytest.raises(ValidationError):
        ClassUpdateRequest(status="open")
    with pytest.raises(ValidationError):
        TeacherUpdateRequest(status="enabled")

    assert TeacherStatus.ACTIVE.value == "active"
    assert ClassStatus.INACTIVE.value == "inactive"
    assert AttendanceStatus.HALF_DAY.value == "half_day"


@pytest.mark.parametrize(
    ("table", "constraint_name"),
    [
        (Class.__table__, "ck_classes_class_status"),
        (Teacher.__table__, "ck_teachers_teacher_status"),
        (TeacherAttendance.__table__, "ck_teacher_attendance_attendance_status"),
        (TeacherSalaryPayment.__table__, "ck_teacher_payment_net_calculation"),
    ],
)
def test_orm_metadata_declares_database_domain_constraints(table, constraint_name):
    assert any(
        constraint.name == constraint_name for constraint in table.constraints
    )
