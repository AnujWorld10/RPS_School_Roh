"""Phase 2: interviews, inquiry admissions, documents, student enrollment fields.

Revision ID: 002_phase2
Revises: 001_student_inquiry
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_phase2"
down_revision: Union[str, None] = "001_student_inquiry"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "interview_schedules",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("inquiry_id", sa.BigInteger(), nullable=False),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.Column("schedule_time", sa.Time(), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("interviewer_teacher_id", sa.BigInteger(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["inquiry_id"], ["student_inquiries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interviewer_teacher_id"], ["teachers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interview_schedules_inquiry_id", "interview_schedules", ["inquiry_id"])

    op.create_table(
        "inquiry_admissions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("admission_code", sa.String(20), nullable=False),
        sa.Column("inquiry_id", sa.BigInteger(), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("section", sa.String(20), nullable=True),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("permanent_address", sa.Text(), nullable=True),
        sa.Column("temporary_address", sa.Text(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("disability", sa.String(255), nullable=True),
        sa.Column("blood_group", sa.String(10), nullable=True),
        sa.Column("reason_for_school_change", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("student_id", sa.BigInteger(), nullable=True),
        sa.Column("approved_by", sa.BigInteger(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["inquiry_id"], ["student_inquiries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("inquiry_id", name="uq_inquiry_admission_inquiry"),
        sa.UniqueConstraint("admission_code", name="uq_inquiry_admission_code"),
        sa.UniqueConstraint("student_id", name="uq_inquiry_admission_student"),
    )

    op.create_table(
        "admission_documents",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("admission_id", sa.BigInteger(), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("verification_status", sa.String(20), nullable=False),
        sa.Column("verified_by", sa.BigInteger(), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["admission_id"], ["inquiry_admissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("admission_id", "document_type", name="uq_admission_document_type"),
    )

    # Extend students table for enrollment (skip if columns already exist)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    student_cols = {c["name"] for c in inspector.get_columns("students")} if inspector.has_table("students") else set()

    if "students" in inspector.get_table_names():
        if "student_code" not in student_cols:
            op.add_column("students", sa.Column("student_code", sa.String(20), nullable=True))
            op.execute("UPDATE students SET student_code = CONCAT('STU', id) WHERE student_code IS NULL")
            # op.alter_column("students", "student_code", nullable=False)
            op.alter_column('students', 'student_code', type_=sa.String(20), existing_type=sa.String(20), nullable=False)

            op.create_unique_constraint("uq_student_code", "students", ["student_code"])
        if "inquiry_id" not in student_cols:
            op.add_column("students", sa.Column("inquiry_id", sa.BigInteger(), nullable=True))
            op.create_foreign_key(
                "fk_students_inquiry_id",
                "students",
                "student_inquiries",
                ["inquiry_id"],
                ["id"],
                ondelete="SET NULL",
            )
            op.create_unique_constraint("uq_students_inquiry_id", "students", ["inquiry_id"])
        if "class_id" not in student_cols:
            op.add_column("students", sa.Column("class_id", sa.BigInteger(), nullable=True))
            op.create_foreign_key(
                "fk_students_class_id",
                "students",
                "classes",
                ["class_id"],
                ["id"],
            )
        if "academic_year" not in student_cols:
            op.add_column("students", sa.Column("academic_year", sa.String(20), nullable=True))
        if "roll_number" not in student_cols:
            op.add_column("students", sa.Column("roll_number", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_table("admission_documents")
    op.drop_table("inquiry_admissions")
    op.drop_table("interview_schedules")
