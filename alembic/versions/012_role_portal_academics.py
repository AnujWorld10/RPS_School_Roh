"""Add role-portal academic workflows and permissions.

Revision ID: 012_role_portal_academics
Revises: 011_student_contact_fields
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "012_role_portal_academics"
down_revision: str | None = "011_student_contact_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_NEW_PERMISSIONS = (
    ("teaching_assignments.manage", "teaching_assignments", "manage"),
    ("assignments.create", "assignments", "create"),
    ("assignments.read", "assignments", "read"),
    ("assignments.update", "assignments", "update"),
    ("assignments.publish", "assignments", "publish"),
    ("timetable.create", "timetable", "create"),
    ("timetable.read", "timetable", "read"),
    ("timetable.update", "timetable", "update"),
    ("assessments.create", "assessments", "create"),
    ("assessments.read", "assessments", "read"),
    ("assessments.update", "assessments", "update"),
    ("assessments.publish", "assessments", "publish"),
    ("events.create", "events", "create"),
    ("events.read", "events", "read"),
    ("events.update", "events", "update"),
    ("events.review", "events", "review"),
)

_ROLE_GRANTS = {
    "SUPER_ADMIN": {item[0] for item in _NEW_PERMISSIONS},
    "ADMIN": {item[0] for item in _NEW_PERMISSIONS},
    "TEACHER": {
        "subjects.create",
        "subjects.read",
        "subjects.update",
        "students.create",
        "students.read",
        "students.update",
        "inquiries.read",
        "inquiries.review",
        "interviews.read",
        "admissions.read",
        "admissions.approve",
        "teaching_assignments.manage",
        "assignments.create",
        "assignments.read",
        "assignments.update",
        "assignments.publish",
        "timetable.create",
        "timetable.read",
        "timetable.update",
        "assessments.create",
        "assessments.read",
        "assessments.update",
        "assessments.publish",
        "events.create",
        "events.read",
        "events.update",
    },
    "STUDENT": {
        "assignments.read",
        "timetable.read",
        "assessments.read",
        "events.read",
    },
    "PARENT": {
        "assignments.read",
        "timetable.read",
        "assessments.read",
        "events.read",
    },
}


def upgrade() -> None:
    op.create_table(
        "assignments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("assigned_teacher_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "assigned_date",
            sa.Date(),
            server_default=sa.text("(CURRENT_DATE)"),
            nullable=False,
        ),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'published', 'closed')",
            name="ck_assignments_status",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_assignments_class_subject",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_assignments_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assignments_class_id", "assignments", ["class_id"])
    op.create_index("ix_assignments_assigned_teacher_id", "assignments", ["assigned_teacher_id"])

    op.create_table(
        "assignment_attachments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("assignment_id", sa.BigInteger(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("uploaded_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_path", name="uq_assignment_attachments_file_path"),
    )
    op.create_index(
        "ix_assignment_attachments_assignment_id",
        "assignment_attachments",
        ["assignment_id"],
    )

    op.create_table(
        "timetable_entries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("teacher_id", sa.BigInteger(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("room", sa.String(length=100), nullable=True),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("day_of_week BETWEEN 0 AND 6", name="ck_timetable_day_of_week"),
        sa.CheckConstraint("start_time < end_time", name="ck_timetable_time_order"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_timetable_class_subject",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_timetable_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_timetable_entries_class_id", "timetable_entries", ["class_id"])
    op.create_index("ix_timetable_entries_teacher_id", "timetable_entries", ["teacher_id"])
    op.create_index("ix_timetable_entries_academic_year", "timetable_entries", ["academic_year"])

    op.create_table(
        "assessments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("assessment_type", sa.String(length=30), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("teacher_id", sa.BigInteger(), nullable=False),
        sa.Column("assessment_date", sa.Date(), nullable=False),
        sa.Column("max_score", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "assessment_type IN ('unit_test', 'periodic_test', 'mid_term', 'final_exam', "
            "'assignment', 'quiz', 'practical', 'oral')",
            name="ck_assessments_type",
        ),
        sa.CheckConstraint("max_score > 0", name="ck_assessments_max_score_positive"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_assessments_class_subject",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id", "class_id", "subject_id"],
            [
                "teacher_class_subjects.teacher_id",
                "teacher_class_subjects.class_id",
                "teacher_class_subjects.subject_id",
            ],
            name="fk_assessments_teacher_class_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessments_class_id", "assessments", ["class_id"])
    op.create_index("ix_assessments_teacher_id", "assessments", ["teacher_id"])

    op.create_table(
        "assessment_results",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.BigInteger(), nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("result_status", sa.String(length=10), server_default="present", nullable=False),
        sa.Column("remarks", sa.String(length=500), nullable=True),
        sa.Column("entered_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "result_status IN ('present', 'absent')",
            name="ck_assessment_result_status",
        ),
        sa.CheckConstraint("score IS NULL OR score >= 0", name="ck_assessment_result_nonnegative"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assessment_id", "student_id", name="uq_assessment_result_student"),
    )
    op.create_index("ix_assessment_results_assessment_id", "assessment_results", ["assessment_id"])
    op.create_index("ix_assessment_results_student_id", "assessment_results", ["student_id"])

    op.create_table(
        "school_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(length=200), nullable=True),
        sa.Column("audience", sa.String(length=20), server_default="all", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending_review", nullable=False),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("reviewed_by", sa.BigInteger(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("starts_at < ends_at", name="ck_school_events_time_order"),
        sa.CheckConstraint(
            "audience IN ('public', 'students', 'parents', 'all')",
            name="ck_school_events_audience",
        ),
        sa.CheckConstraint(
            "status IN ('pending_review', 'published', 'rejected')",
            name="ck_school_events_status",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_school_events_starts_at", "school_events", ["starts_at"])

    _seed_role_portal_permissions()


def _seed_role_portal_permissions() -> None:
    bind = op.get_bind()
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String()),
        sa.column("module", sa.String()),
        sa.column("action", sa.String()),
    )
    roles = sa.table("roles", sa.column("id", sa.BigInteger()), sa.column("code", sa.String()))
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.BigInteger()),
        sa.column("permission_id", sa.BigInteger()),
    )

    permission_ids: dict[str, int] = {}
    for code, module, action in _NEW_PERMISSIONS:
        permission_id = bind.scalar(sa.select(permissions.c.id).where(permissions.c.code == code))
        if permission_id is None:
            bind.execute(permissions.insert().values(code=code, module=module, action=action))
            permission_id = bind.scalar(
                sa.select(permissions.c.id).where(permissions.c.code == code)
            )
            if permission_id is None:
                raise RuntimeError(f"Failed to create permission: {code}")
        permission_ids[code] = int(permission_id)

    for code in set().union(*_ROLE_GRANTS.values()).difference(permission_ids):
        permission_id = bind.scalar(sa.select(permissions.c.id).where(permissions.c.code == code))
        if permission_id is not None:
            permission_ids[code] = int(permission_id)

    for role_code, permission_codes in _ROLE_GRANTS.items():
        role_id = bind.scalar(sa.select(roles.c.id).where(roles.c.code == role_code))
        if role_id is None:
            continue
        for permission_code in permission_codes:
            if permission_code not in permission_ids:
                continue
            permission_id = permission_ids[permission_code]
            exists = bind.scalar(
                sa.select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.permission_id == permission_id,
                )
            )
            if exists is None:
                bind.execute(
                    role_permissions.insert().values(
                        role_id=role_id,
                        permission_id=permission_id,
                    )
                )


def downgrade() -> None:
    bind = op.get_bind()
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String()),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.BigInteger()),
        sa.column("permission_id", sa.BigInteger()),
    )
    permission_ids = bind.scalars(
        sa.select(permissions.c.id).where(
            permissions.c.code.in_([item[0] for item in _NEW_PERMISSIONS])
        )
    ).all()
    if permission_ids:
        bind.execute(
            role_permissions.delete().where(
                role_permissions.c.permission_id.in_(permission_ids)
            )
        )
        bind.execute(permissions.delete().where(permissions.c.id.in_(permission_ids)))

    op.drop_index("ix_school_events_starts_at", table_name="school_events")
    op.drop_table("school_events")
    op.drop_index("ix_assessment_results_student_id", table_name="assessment_results")
    op.drop_index("ix_assessment_results_assessment_id", table_name="assessment_results")
    op.drop_table("assessment_results")
    op.drop_index("ix_assessments_teacher_id", table_name="assessments")
    op.drop_index("ix_assessments_class_id", table_name="assessments")
    op.drop_table("assessments")
    op.drop_index("ix_timetable_entries_academic_year", table_name="timetable_entries")
    op.drop_index("ix_timetable_entries_teacher_id", table_name="timetable_entries")
    op.drop_index("ix_timetable_entries_class_id", table_name="timetable_entries")
    op.drop_table("timetable_entries")
    op.drop_index("ix_assignment_attachments_assignment_id", table_name="assignment_attachments")
    op.drop_table("assignment_attachments")
    op.drop_index("ix_assignments_assigned_teacher_id", table_name="assignments")
    op.drop_index("ix_assignments_class_id", table_name="assignments")
    op.drop_table("assignments")
