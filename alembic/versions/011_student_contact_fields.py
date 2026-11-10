"""Add missing optional student contact fields.

Revision ID: 011_student_contact_fields
Revises: 010_subject_academic_map
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "011_student_contact_fields"
down_revision: str | None = "010_subject_academic_map"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns("students")}


def upgrade() -> None:
    columns = _column_names()
    if "email" not in columns:
        op.add_column("students", sa.Column("email", sa.String(length=255), nullable=True))
    if "phone" not in columns:
        op.add_column("students", sa.Column("phone", sa.String(length=30), nullable=True))


def downgrade() -> None:
    columns = _column_names()
    if "phone" in columns:
        op.drop_column("students", "phone")
    if "email" in columns:
        op.drop_column("students", "email")
