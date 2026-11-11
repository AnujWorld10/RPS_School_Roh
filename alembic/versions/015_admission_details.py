"""Add secure Aadhaar and previous-school details to admissions.

Revision ID: 015_admission_details
Revises: 014_student_portal
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "015_admission_details"
down_revision: str | None = "014_student_portal"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("inquiry_admissions") as batch_op:
        batch_op.add_column(sa.Column("student_aadhaar_encrypted", sa.String(512), nullable=True))
        batch_op.add_column(sa.Column("student_aadhaar_last4", sa.String(4), nullable=True))
        batch_op.add_column(sa.Column("parent_aadhaar_encrypted", sa.String(512), nullable=True))
        batch_op.add_column(sa.Column("parent_aadhaar_last4", sa.String(4), nullable=True))
        batch_op.add_column(sa.Column("last_school_marks", sa.Numeric(8, 2), nullable=True))
        batch_op.add_column(sa.Column("last_school_percentage", sa.Numeric(5, 2), nullable=True))
        batch_op.add_column(
            sa.Column("last_school_id_or_roll_number", sa.String(100), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("inquiry_admissions") as batch_op:
        batch_op.drop_column("last_school_id_or_roll_number")
        batch_op.drop_column("last_school_percentage")
        batch_op.drop_column("last_school_marks")
        batch_op.drop_column("parent_aadhaar_last4")
        batch_op.drop_column("parent_aadhaar_encrypted")
        batch_op.drop_column("student_aadhaar_last4")
        batch_op.drop_column("student_aadhaar_encrypted")
