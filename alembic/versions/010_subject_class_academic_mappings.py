"""Add subject offerings, class teachers, and class-scoped teacher assignments.

Revision ID: 010_subject_class_academic_mappings
Revises: 009_reconcile_orm_schema
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "010_subject_academic_map"
down_revision: str | None = "009_reconcile_orm_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("classes") as batch_op:
        batch_op.add_column(sa.Column("class_teacher_id", sa.BigInteger(), nullable=True))
        batch_op.create_unique_constraint("uq_classes_class_teacher", ["class_teacher_id"])
        batch_op.create_foreign_key(
            "fk_classes_class_teacher",
            "teachers",
            ["class_teacher_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "class_subjects",
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name="fk_class_subjects_class",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name="fk_class_subjects_subject",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("class_id", "subject_id", name="pk_class_subjects"),
        comment="Subjects offered to each class",
    )

    op.create_table(
        "teacher_class_subjects",
        sa.Column("teacher_id", sa.BigInteger(), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["teachers.id"],
            name="fk_teacher_class_subjects_teacher",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_teacher_class_subject_offering",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name="fk_teacher_class_subjects_subject",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "teacher_id",
            "class_id",
            "subject_id",
            name="pk_teacher_class_subjects",
        ),
        comment="Teacher assignments to class subject offerings",
    )
    op.create_index(
        "ix_teacher_class_subject_offering",
        "teacher_class_subjects",
        ["class_id", "subject_id"],
    )

    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(100)),
        sa.column("module", sa.String(100)),
        sa.column("action", sa.String(100)),
    )
    roles = sa.table(
        "roles",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(50)),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.BigInteger()),
        sa.column("permission_id", sa.BigInteger()),
    )
    connection = op.get_bind()
    for code, action in (
        ("subjects.create", "create"),
        ("subjects.read", "read"),
        ("subjects.update", "update"),
        ("subjects.delete", "delete"),
    ):
        existing_id = connection.execute(
            sa.select(permissions.c.id).where(permissions.c.code == code)
        ).scalar_one_or_none()
        if existing_id is None:
            connection.execute(
                permissions.insert().values(code=code, module="subjects", action=action)
            )
            existing_id = connection.execute(
                sa.select(permissions.c.id).where(permissions.c.code == code)
            ).scalar_one()
        admin_role_ids = connection.execute(
            sa.select(roles.c.id).where(roles.c.code.in_(("SUPER_ADMIN", "ADMIN")))
        ).scalars()
        for role_id in admin_role_ids:
            exists = connection.execute(
                sa.select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.permission_id == existing_id,
                )
            ).first()
            if not exists:
                connection.execute(
                    role_permissions.insert().values(
                        role_id=role_id,
                        permission_id=existing_id,
                    )
                )


def downgrade() -> None:
    op.drop_index("ix_teacher_class_subject_offering", table_name="teacher_class_subjects")
    op.drop_table("teacher_class_subjects")
    op.drop_table("class_subjects")

    with op.batch_alter_table("classes") as batch_op:
        batch_op.drop_constraint("fk_classes_class_teacher", type_="foreignkey")
        batch_op.drop_constraint("uq_classes_class_teacher", type_="unique")
        batch_op.drop_column("class_teacher_id")

    connection = op.get_bind()
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(100)),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("permission_id", sa.BigInteger()),
    )
    for code in ("subjects.create", "subjects.read", "subjects.update", "subjects.delete"):
        permission_id = connection.execute(
            sa.select(permissions.c.id).where(permissions.c.code == code)
        ).scalar_one_or_none()
        if permission_id is not None:
            connection.execute(
                role_permissions.delete().where(role_permissions.c.permission_id == permission_id)
            )
            connection.execute(permissions.delete().where(permissions.c.id == permission_id))
