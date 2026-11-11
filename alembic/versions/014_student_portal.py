"""Add student portal account links and RPS student ID sequence.

Revision ID: 014_student_portal
Revises: 013_fee_structures
"""

from __future__ import annotations

import re
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "014_student_portal"
down_revision: str | None = "013_fee_structures"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _last_existing_rps_id() -> int:
    bind = op.get_bind()
    students = sa.table(
        "students",
        sa.column("student_code", sa.String(20)),
    )
    admissions = sa.table(
        "inquiry_admissions",
        sa.column("admission_code", sa.String(20)),
    )
    values = [
        *bind.scalars(
            sa.select(students.c.student_code).where(students.c.student_code.like("RPS%"))
        ),
        *bind.scalars(
            sa.select(admissions.c.admission_code).where(admissions.c.admission_code.like("RPS%"))
        ),
    ]
    serials = [
        int(match.group(1)) for value in values if (match := re.fullmatch(r"RPS(\d{5})", value))
    ]
    return max(serials, default=0)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("business_id_sequences"):
        op.create_table(
            "business_id_sequences",
            sa.Column("sequence_name", sa.String(length=50), nullable=False),
            sa.Column("last_value", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("sequence_name"),
        )
    sequences = sa.table(
        "business_id_sequences",
        sa.column("sequence_name", sa.String(50)),
        sa.column("last_value", sa.Integer()),
    )
    if bind.scalar(
        sa.select(sequences.c.sequence_name).where(sequences.c.sequence_name == "student")
    ) is None:
        bind.execute(
            sequences.insert().values(
                sequence_name="student",
                last_value=_last_existing_rps_id(),
            )
        )

    student_columns = {column["name"] for column in inspector.get_columns("students")}
    if "user_id" not in student_columns:
        with op.batch_alter_table("students") as batch_op:
            batch_op.add_column(sa.Column("user_id", sa.BigInteger(), nullable=True))

    user_foreign_keys = [
        foreign_key
        for foreign_key in sa.inspect(bind).get_foreign_keys("students")
        if foreign_key["constrained_columns"] == ["user_id"]
        and foreign_key["referred_table"] == "users"
    ]
    if not any(foreign_key.get("options", {}).get("ondelete") == "SET NULL"
               for foreign_key in user_foreign_keys):
        with op.batch_alter_table("students") as batch_op:
            for foreign_key in user_foreign_keys:
                if not foreign_key.get("name"):
                    raise RuntimeError("Cannot replace the unnamed students.user_id foreign key")
                batch_op.drop_constraint(foreign_key["name"], type_="foreignkey")
            batch_op.create_foreign_key(
                "fk_students_user_id",
                "users",
                ["user_id"],
                ["id"],
                ondelete="SET NULL",
            )

    unique_constraints = sa.inspect(bind).get_unique_constraints("students")
    unique_indexes = sa.inspect(bind).get_indexes("students")
    has_user_unique = any(
        item.get("column_names") == ["user_id"] for item in [*unique_constraints, *unique_indexes]
    )
    if not has_user_unique:
        with op.batch_alter_table("students") as batch_op:
            batch_op.create_unique_constraint("uq_students_user_id", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    unique_constraints = inspector.get_unique_constraints("students")
    if any(item.get("name") == "uq_students_user_id" for item in unique_constraints):
        with op.batch_alter_table("students") as batch_op:
            batch_op.drop_constraint("uq_students_user_id", type_="unique")
    user_foreign_keys = [
        foreign_key
        for foreign_key in sa.inspect(bind).get_foreign_keys("students")
        if foreign_key["constrained_columns"] == ["user_id"]
        and foreign_key["referred_table"] == "users"
    ]
    if any(foreign_key.get("options", {}).get("ondelete") == "SET NULL"
           for foreign_key in user_foreign_keys):
        with op.batch_alter_table("students") as batch_op:
            for foreign_key in user_foreign_keys:
                if foreign_key.get("options", {}).get("ondelete") == "SET NULL":
                    batch_op.drop_constraint(foreign_key["name"], type_="foreignkey")
            batch_op.create_foreign_key(
                "fk_students_user_id_legacy",
                "users",
                ["user_id"],
                ["id"],
                ondelete="CASCADE",
            )
    if inspector.has_table("business_id_sequences"):
        op.drop_table("business_id_sequences")
