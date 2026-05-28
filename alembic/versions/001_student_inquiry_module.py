"""Student inquiry module: student_inquiries and inquiry_status_history.

Revision ID: 001_student_inquiry
Revises:
Create Date: 2026-05-26

Replaces legacy ``inquiries`` table with FRD-aligned ``student_inquiries``.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_student_inquiry"
down_revision: Union[str, None] = "000_base"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop legacy simplified inquiries table if present from earlier scaffold.
    op.execute("DROP TABLE IF EXISTS inquiries")

    op.create_table(
        "student_inquiries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="Internal surrogate primary key"),
        sa.Column("inquiry_code", sa.String(length=20), nullable=False, comment="Human-readable inquiry ID, e.g. INQ20260001"),
        sa.Column("serial_number", sa.Integer(), nullable=False, comment="Serial used when generating inquiry_code"),
        sa.Column("first_name", sa.String(length=100), nullable=False, comment="Student given name"),
        sa.Column("middle_name", sa.String(length=100), nullable=True, comment="Student middle name"),
        sa.Column("last_name", sa.String(length=100), nullable=False, comment="Student family name"),
        sa.Column("gender", sa.String(length=20), nullable=False, comment="Student gender"),
        sa.Column("father_name", sa.String(length=200), nullable=False, comment="Father or guardian name"),
        sa.Column("date_of_birth", sa.Date(), nullable=False, comment="Student date of birth"),
        sa.Column("student_mobile", sa.String(length=30), nullable=True, comment="Student mobile"),
        sa.Column("parent_mobile", sa.String(length=30), nullable=False, comment="Parent mobile for verification"),
        sa.Column("email", sa.String(length=255), nullable=False, comment="Contact email"),
        sa.Column("address", sa.Text(), nullable=False, comment="Residential address"),
        sa.Column("last_school", sa.String(length=255), nullable=False, comment="Previous school name"),
        sa.Column("current_class", sa.String(length=100), nullable=False, comment="Current class label from applicant"),
        sa.Column("admission_for_class", sa.String(length=100), nullable=False, comment="Target admission class label"),
        sa.Column("last_school_percentage", sa.Numeric(5, 2), nullable=True, comment="Previous school percentage"),
        sa.Column(
            "admission_for_class_id",
            sa.BigInteger(),
            sa.ForeignKey("classes.id", ondelete="SET NULL"),
            nullable=True,
            comment="Optional FK to classes catalog",
        ),
        sa.Column("status", sa.String(length=50), nullable=False, comment="Current pipeline status"),
        sa.Column("rejection_reason", sa.Text(), nullable=True, comment="Parent-visible rejection reason"),
        sa.Column("internal_notes", sa.Text(), nullable=True, comment="Staff-only notes"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inquiry_code", name="uq_student_inquiry_code"),
        sa.UniqueConstraint("serial_number", name="uq_student_inquiry_serial"),
        comment="Public student admission inquiries",
    )
    op.create_index("ix_student_inquiry_status", "student_inquiries", ["status"])
    op.create_index("ix_student_inquiry_parent_mobile", "student_inquiries", ["parent_mobile"])
    op.create_index("ix_student_inquiry_email", "student_inquiries", ["email"])
    op.create_index(
        op.f("ix_student_inquiries_admission_for_class_id"),
        "student_inquiries",
        ["admission_for_class_id"],
    )

    op.create_table(
        "inquiry_status_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False, comment="History row PK"),
        sa.Column(
            "inquiry_id",
            sa.BigInteger(),
            sa.ForeignKey("student_inquiries.id", ondelete="CASCADE"),
            nullable=False,
            comment="FK to student_inquiries.id",
        ),
        sa.Column("from_status", sa.String(length=50), nullable=True, comment="Previous status"),
        sa.Column("to_status", sa.String(length=50), nullable=False, comment="New status"),
        sa.Column(
            "changed_by",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            comment="Staff user id if applicable",
        ),
        sa.Column("change_reason", sa.Text(), nullable=True, comment="Reason or note for transition"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="When transition occurred",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Append-only inquiry status change log",
    )
    op.create_index(
        "ix_inquiry_status_history_inquiry_id",
        "inquiry_status_history",
        ["inquiry_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_inquiry_status_history_inquiry_id", table_name="inquiry_status_history")
    op.drop_table("inquiry_status_history")
    op.drop_index(op.f("ix_student_inquiries_admission_for_class_id"), table_name="student_inquiries")
    op.drop_index("ix_student_inquiry_email", table_name="student_inquiries")
    op.drop_index("ix_student_inquiry_parent_mobile", table_name="student_inquiries")
    op.drop_index("ix_student_inquiry_status", table_name="student_inquiries")
    op.drop_table("student_inquiries")
