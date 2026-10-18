"""Reconcile legacy tables and create missing teacher domain tables.

Revision ID: 009_reconcile_orm_schema
Revises: 008_inquiry_duplicate_key
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "009_reconcile_orm_schema"
down_revision: str | None = "008_inquiry_duplicate_key"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _inspector():
    return sa.inspect(op.get_bind())


def _columns(table: str) -> set[str]:
    return {column["name"] for column in _inspector().get_columns(table)}


def _ensure_column(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def _ensure_index(table: str, name: str, columns: list[str], *, unique: bool = False) -> None:
    indexes = {index["name"] for index in _inspector().get_indexes(table)}
    constraints = {
        constraint["name"]
        for constraint in _inspector().get_unique_constraints(table)
        if constraint.get("name")
    }
    if name not in indexes and name not in constraints:
        op.create_index(name, table, columns, unique=unique)


def _ensure_unique_constraint(table: str, name: str, columns: list[str]) -> None:
    constraints = {
        constraint["name"]
        for constraint in _inspector().get_unique_constraints(table)
        if constraint.get("name")
    }
    indexes = {index["name"] for index in _inspector().get_indexes(table)}
    if name not in constraints and name not in indexes:
        with op.batch_alter_table(table) as batch_op:
            batch_op.create_unique_constraint(name, columns)


def _ensure_foreign_key(
    table: str,
    name: str,
    columns: list[str],
    referred_table: str,
    referred_columns: list[str],
    *,
    ondelete: str | None = None,
) -> None:
    foreign_keys = {foreign_key.get("name") for foreign_key in _inspector().get_foreign_keys(table)}
    if name not in foreign_keys:
        with op.batch_alter_table(table) as batch_op:
            batch_op.create_foreign_key(
                name,
                referred_table,
                columns,
                referred_columns,
                ondelete=ondelete,
            )


def _ensure_check(table: str, name: str, expression: str) -> None:
    checks = {constraint.get("name") for constraint in _inspector().get_check_constraints(table)}
    if name not in checks:
        with op.batch_alter_table(table) as batch_op:
            batch_op.create_check_constraint(name, expression)


def _make_nullable(table: str, column: str, column_type: sa.types.TypeEngine) -> None:
    metadata = {item["name"]: item for item in _inspector().get_columns(table)}
    if column in metadata and not metadata[column]["nullable"]:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(
                column,
                existing_type=column_type,
                nullable=True,
            )


def _make_required(table: str, column: str, column_type: sa.types.TypeEngine) -> None:
    metadata = {item["name"]: item for item in _inspector().get_columns(table)}
    if column in metadata and metadata[column]["nullable"]:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(
                column,
                existing_type=column_type,
                nullable=False,
            )


def _legacy_text_id(prefix: str, identifier: sa.Column) -> sa.ColumnElement:
    return sa.literal(prefix) + sa.cast(identifier, sa.String(20))


def _reconcile_students() -> None:
    if not _inspector().has_table("students"):
        raise RuntimeError("Migration 009 requires the students table from the base schema")

    student_columns = {
        "admission_no": sa.Column("admission_no", sa.String(50), nullable=True),
        "first_name": sa.Column("first_name", sa.String(100), nullable=True),
        "last_name": sa.Column("last_name", sa.String(100), nullable=True),
        "current_class_id": sa.Column("current_class_id", sa.BigInteger(), nullable=True),
        "academic_year": sa.Column("academic_year", sa.String(20), nullable=True),
        "roll_number": sa.Column("roll_number", sa.Integer(), nullable=True),
        "status": sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
    }
    for column in student_columns.values():
        _ensure_column("students", column)

    students = sa.table(
        "students",
        sa.column("id", sa.BigInteger),
        sa.column("user_id", sa.BigInteger),
        sa.column("student_code", sa.String(20)),
        sa.column("first_name", sa.String(100)),
        sa.column("last_name", sa.String(100)),
        sa.column("status", sa.String(50)),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.BigInteger),
        sa.column("first_name", sa.String(100)),
        sa.column("last_name", sa.String(100)),
    )
    bind = op.get_bind()
    first_name = (
        sa.select(users.c.first_name)
        .where(users.c.id == students.c.user_id)
        .scalar_subquery()
    )
    last_name = (
        sa.select(users.c.last_name)
        .where(users.c.id == students.c.user_id)
        .scalar_subquery()
    )
    bind.execute(
        students.update()
        .where(students.c.first_name.is_(None))
        .values(first_name=first_name)
    )
    bind.execute(
        students.update()
        .where(students.c.last_name.is_(None))
        .values(last_name=last_name)
    )
    bind.execute(
        students.update()
        .where(students.c.student_code.is_(None))
        .values(student_code=_legacy_text_id("STU", students.c.id))
    )
    bind.execute(
        students.update()
        .where(
            students.c.status.in_(
                ["ACTIVE", "INACTIVE", "PROSPECTIVE", "GRADUATED", "TRANSFERRED"]
            )
        )
        .values(status=sa.func.lower(students.c.status))
    )

    _make_nullable("students", "user_id", sa.BigInteger())
    _make_nullable("students", "enrollment_number", sa.String(50))
    _make_required("students", "student_code", sa.String(20))
    _make_required("students", "first_name", sa.String(100))
    _make_required("students", "last_name", sa.String(100))
    _make_required("students", "status", sa.String(50))

    _ensure_unique_constraint("students", "uq_student_code", ["student_code"])
    _ensure_unique_constraint("students", "uq_students_admission_no", ["admission_no"])
    _ensure_unique_constraint("students", "uq_students_inquiry_id", ["inquiry_id"])
    _ensure_unique_constraint(
        "students",
        "uq_student_roll_per_class_year",
        ["class_id", "academic_year", "roll_number"],
    )
    _ensure_foreign_key(
        "students",
        "fk_students_current_class_id_classes",
        ["current_class_id"],
        "classes",
        ["id"],
    )
    _ensure_index("students", "ix_students_current_class_id", ["current_class_id"])


def _reconcile_teachers() -> None:
    if not _inspector().has_table("teachers"):
        raise RuntimeError("Migration 009 requires the teachers table from the base schema")

    teacher_columns = {
        "employee_no": sa.Column("employee_no", sa.String(50), nullable=True),
        "first_name": sa.Column("first_name", sa.String(100), nullable=True),
        "last_name": sa.Column("last_name", sa.String(100), nullable=True),
        "email": sa.Column("email", sa.String(255), nullable=True),
        "phone": sa.Column("phone", sa.String(30), nullable=True),
        "joining_date": sa.Column("joining_date", sa.Date(), nullable=True),
        "status": sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
    }
    for column in teacher_columns.values():
        _ensure_column("teachers", column)

    teachers = sa.table(
        "teachers",
        sa.column("id", sa.BigInteger),
        sa.column("user_id", sa.BigInteger),
        sa.column("employee_id", sa.String(50)),
        sa.column("employee_no", sa.String(50)),
        sa.column("first_name", sa.String(100)),
        sa.column("last_name", sa.String(100)),
        sa.column("email", sa.String(255)),
        sa.column("phone", sa.String(30)),
        sa.column("joining_date", sa.Date),
        sa.column("status", sa.String(50)),
    )
    users = sa.table(
        "users",
        sa.column("id", sa.BigInteger),
        sa.column("first_name", sa.String(100)),
        sa.column("last_name", sa.String(100)),
        sa.column("email", sa.String(255)),
        sa.column("phone", sa.String(30)),
    )
    bind = op.get_bind()
    def user_value(field: str):
        return (
            sa.select(getattr(users.c, field))
            .where(users.c.id == teachers.c.user_id)
            .scalar_subquery()
        )
    bind.execute(
        teachers.update()
        .where(teachers.c.employee_no.is_(None))
        .values(
            employee_no=sa.func.coalesce(
                teachers.c.employee_id,
                _legacy_text_id("LEGACY-", teachers.c.id),
            )
        )
    )
    for field in ("first_name", "last_name", "email", "phone"):
        bind.execute(
            teachers.update()
            .where(getattr(teachers.c, field).is_(None))
            .values(**{field: user_value(field)})
        )
    bind.execute(
        teachers.update()
        .where(teachers.c.status.in_(["ACTIVE", "INACTIVE", "RESIGNED"]))
        .values(status=sa.func.lower(teachers.c.status))
    )

    _make_nullable("teachers", "user_id", sa.BigInteger())
    _make_nullable("teachers", "employee_id", sa.String(50))
    for column, column_type in (
        ("employee_no", sa.String(50)),
        ("first_name", sa.String(100)),
        ("last_name", sa.String(100)),
        ("email", sa.String(255)),
        ("status", sa.String(50)),
    ):
        _make_required("teachers", column, column_type)

    _ensure_unique_constraint("teachers", "uq_teachers_user_id", ["user_id"])
    _ensure_unique_constraint("teachers", "uq_teachers_employee_no", ["employee_no"])
    _ensure_unique_constraint("teachers", "uq_teachers_email", ["email"])
    _ensure_unique_constraint("teachers", "uq_teachers_phone", ["phone"])
    _ensure_index("teachers", "ix_teachers_status", ["status"])


def _create_teacher_tables() -> None:
    if not _inspector().has_table("teacher_subjects"):
        op.create_table(
            "teacher_subjects",
            sa.Column("teacher_id", sa.BigInteger(), nullable=False),
            sa.Column("subject_id", sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("teacher_id", "subject_id"),
            sa.UniqueConstraint("teacher_id", "subject_id", name="uq_teacher_subject"),
        )

    if not _inspector().has_table("teacher_classes"):
        op.create_table(
            "teacher_classes",
            sa.Column("teacher_id", sa.BigInteger(), nullable=False),
            sa.Column("class_id", sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("teacher_id", "class_id"),
            sa.UniqueConstraint("teacher_id", "class_id", name="uq_teacher_class"),
        )

    if not _inspector().has_table("teacher_attendance"):
        op.create_table(
            "teacher_attendance",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("teacher_id", sa.BigInteger(), nullable=False),
            sa.Column("attendance_date", sa.Date(), nullable=False),
            sa.Column("status", sa.String(50), nullable=False),
            sa.Column("remarks", sa.String(255), nullable=True),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "teacher_id",
                "attendance_date",
                name="uq_teacher_attendance_date",
            ),
            sa.CheckConstraint(
                "status IN ('present', 'absent', 'leave', 'half_day')",
                name="ck_teacher_attendance_attendance_status",
            ),
        )
    _ensure_index(
        "teacher_attendance",
        "ix_teacher_attendance_teacher_id",
        ["teacher_id"],
    )

    if not _inspector().has_table("teacher_salary"):
        op.create_table(
            "teacher_salary",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("teacher_id", sa.BigInteger(), nullable=False),
            sa.Column("base_salary", sa.Numeric(12, 2), nullable=False),
            sa.Column("allowance", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("deduction", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("effective_from", sa.Date(), nullable=False),
            sa.Column("status", sa.String(50), nullable=False, server_default="active"),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("teacher_id", name="uq_teacher_salary_teacher_id"),
            sa.CheckConstraint("base_salary >= 0", name="ck_teacher_salary_base_nonnegative"),
            sa.CheckConstraint("allowance >= 0", name="ck_teacher_salary_allowance_nonnegative"),
            sa.CheckConstraint("deduction >= 0", name="ck_teacher_salary_deduction_nonnegative"),
            sa.CheckConstraint(
                "status IN ('active', 'inactive')",
                name="ck_teacher_salary_salary_status",
            ),
        )

    if not _inspector().has_table("teacher_salary_payments"):
        op.create_table(
            "teacher_salary_payments",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("teacher_id", sa.BigInteger(), nullable=False),
            sa.Column("salary_id", sa.BigInteger(), nullable=False),
            sa.Column("payment_month", sa.String(7), nullable=False),
            sa.Column("gross_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column(
                "deduction_amount",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column("net_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
            sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
            sa.ForeignKeyConstraint(["salary_id"], ["teacher_salary.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "teacher_id",
                "payment_month",
                name="uq_teacher_payment_month",
            ),
            sa.CheckConstraint(
                "gross_amount >= 0",
                name="ck_teacher_payment_gross_nonnegative",
            ),
            sa.CheckConstraint(
                "deduction_amount >= 0 AND deduction_amount <= gross_amount",
                name="ck_teacher_payment_deduction_range",
            ),
            sa.CheckConstraint(
                "net_amount >= 0 AND net_amount = gross_amount - deduction_amount",
                name="ck_teacher_payment_net_calculation",
            ),
            sa.CheckConstraint(
                "status IN ('pending', 'paid', 'failed')",
                name="ck_teacher_payment_payment_status",
            ),
        )
    _ensure_index(
        "teacher_salary_payments",
        "ix_teacher_salary_payments_teacher_id",
        ["teacher_id"],
    )

    if not _inspector().has_table("student_admissions"):
        op.create_table(
            "student_admissions",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("student_id", sa.BigInteger(), nullable=False),
            sa.Column("class_id", sa.BigInteger(), nullable=False),
            sa.Column("academic_year", sa.String(20), nullable=False),
            sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
            sa.Column("rejection_reason", sa.Text(), nullable=True),
            sa.Column("approved_by", sa.BigInteger(), nullable=True),
            sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
            sa.ForeignKeyConstraint(["class_id"], ["classes.id"]),
            sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "student_id",
                "academic_year",
                name="uq_student_admission_year",
            ),
        )
    _ensure_index("student_admissions", "ix_student_admissions_student_id", ["student_id"])
    _ensure_index("student_admissions", "ix_student_admissions_status", ["status"])


def upgrade() -> None:
    if not _inspector().has_table("classes"):
        raise RuntimeError("Migration 009 requires the classes table from the base schema")

    _reconcile_students()
    _reconcile_teachers()
    _create_teacher_tables()

    class_table = sa.table(
        "classes",
        sa.column("status", sa.String(50)),
    )
    op.get_bind().execute(
        class_table.update()
        .where(class_table.c.status.in_(["ACTIVE", "INACTIVE"]))
        .values(status=sa.func.lower(class_table.c.status))
    )
    for table, uppercase_statuses in (
        ("teacher_attendance", ("PRESENT", "ABSENT", "LEAVE", "HALF_DAY")),
        ("teacher_salary", ("ACTIVE", "INACTIVE")),
        ("teacher_salary_payments", ("PENDING", "PAID", "FAILED")),
    ):
        status_table = sa.table(table, sa.column("status", sa.String(50)))
        op.get_bind().execute(
            status_table.update()
            .where(status_table.c.status.in_(uppercase_statuses))
            .values(status=sa.func.lower(status_table.c.status))
        )
    _ensure_check("classes", "ck_classes_class_status", "status IN ('active', 'inactive')")
    _ensure_check(
        "teachers",
        "ck_teachers_teacher_status",
        "status IN ('active', 'inactive', 'resigned')",
    )
    _ensure_check(
        "teacher_attendance",
        "ck_teacher_attendance_attendance_status",
        "status IN ('present', 'absent', 'leave', 'half_day')",
    )
    _ensure_check(
        "teacher_salary",
        "ck_teacher_salary_base_nonnegative",
        "base_salary >= 0",
    )
    _ensure_check(
        "teacher_salary",
        "ck_teacher_salary_allowance_nonnegative",
        "allowance >= 0",
    )
    _ensure_check(
        "teacher_salary",
        "ck_teacher_salary_deduction_nonnegative",
        "deduction >= 0",
    )
    _ensure_check(
        "teacher_salary",
        "ck_teacher_salary_salary_status",
        "status IN ('active', 'inactive')",
    )
    _ensure_check(
        "teacher_salary_payments",
        "ck_teacher_payment_gross_nonnegative",
        "gross_amount >= 0",
    )
    _ensure_check(
        "teacher_salary_payments",
        "ck_teacher_payment_deduction_range",
        "deduction_amount >= 0 AND deduction_amount <= gross_amount",
    )
    _ensure_check(
        "teacher_salary_payments",
        "ck_teacher_payment_net_calculation",
        "net_amount >= 0 AND net_amount = gross_amount - deduction_amount",
    )
    _ensure_check(
        "teacher_salary_payments",
        "ck_teacher_payment_payment_status",
        "status IN ('pending', 'paid', 'failed')",
    )


def downgrade() -> None:
    raise RuntimeError(
        "Revision 009 is not safely reversible after application data is written. "
        "Restore a database backup taken before this revision instead."
    )
