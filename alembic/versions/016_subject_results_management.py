"""Add elective selections and centrally managed examination results.

Revision ID: 016_subject_results_management
Revises: 015_admission_details
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

_BIGINT_PK = sa.BigInteger().with_variant(sa.Integer(), "sqlite")

revision: str = "016_subject_results_management"
down_revision: str | None = "015_admission_details"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _ensure_column(table_name: str, column: sa.Column) -> None:
    if column.name not in _column_names(table_name):
        op.add_column(table_name, column)


def _ensure_check(table_name: str, name: str, expression: str) -> None:
    check_names = {
        constraint.get("name")
        for constraint in sa.inspect(op.get_bind()).get_check_constraints(table_name)
    }
    if name not in check_names:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.create_check_constraint(name, expression)


def upgrade() -> None:
    _ensure_column("subjects", sa.Column("category", sa.String(100), nullable=True))
    _ensure_column(
        "subjects",
        sa.Column(
            "subject_type",
            sa.String(20),
            nullable=False,
            server_default="mandatory",
        ),
    )
    _ensure_column("subjects", sa.Column("max_marks", sa.Numeric(8, 2), nullable=True))
    _ensure_column("subjects", sa.Column("passing_marks", sa.Numeric(8, 2), nullable=True))
    _ensure_check(
        "subjects",
        "ck_subjects_subject_type",
        "subject_type IN ('mandatory', 'elective', 'optional')",
    )

    _ensure_column(
        "class_subjects",
        sa.Column(
            "subject_type",
            sa.String(20),
            nullable=False,
            server_default="mandatory",
        ),
    )
    _ensure_column("class_subjects", sa.Column("stream", sa.String(30), nullable=True))
    _ensure_column(
        "class_subjects",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    _ensure_check(
        "class_subjects",
        "ck_class_subjects_subject_type",
        "subject_type IN ('mandatory', 'elective', 'optional')",
    )

    _ensure_column(
        "teacher_class_subjects",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "student_subject_selections",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("selected_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["selected_by"], ["users.id"]),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_student_subject_selection_offering",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id", "class_id", "subject_id", name="uq_student_subject_selection"
        ),
    )
    op.create_index(
        "ix_student_subject_selections_student_id",
        "student_subject_selections",
        ["student_id"],
    )
    op.create_index(
        "ix_student_subject_selections_class_id",
        "student_subject_selections",
        ["class_id"],
    )

    op.create_table(
        "examinations",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("examination_type", sa.String(40), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'scheduled', 'published', 'locked')",
            name="ck_examinations_status",
        ),
        sa.CheckConstraint(
            "examination_type IN ('unit_test', 'periodic_test', 'term', 'mid_term', "
            "'final_exam', 'practical', 'oral')",
            name="ck_examinations_type",
        ),
        sa.CheckConstraint("start_date <= end_date", name="ck_examinations_date_range"),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("class_id", "name", name="uq_examinations_class_name"),
    )
    op.create_index("ix_examinations_class_id", "examinations", ["class_id"])

    op.create_table(
        "examination_subjects",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("examination_id", sa.BigInteger(), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("subject_id", sa.BigInteger(), nullable=False),
        sa.Column("teacher_id", sa.BigInteger(), nullable=True),
        sa.Column("max_marks", sa.Numeric(8, 2), nullable=False),
        sa.Column("passing_marks", sa.Numeric(8, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("max_marks > 0", name="ck_examination_subject_max_positive"),
        sa.CheckConstraint(
            "passing_marks >= 0 AND passing_marks <= max_marks",
            name="ck_examination_subject_pass_range",
        ),
        sa.ForeignKeyConstraint(["examination_id"], ["examinations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["class_id", "subject_id"],
            ["class_subjects.class_id", "class_subjects.subject_id"],
            name="fk_examination_subject_offering",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("examination_id", "subject_id", name="uq_examination_subject"),
    )
    op.create_index(
        "ix_examination_subjects_examination_id",
        "examination_subjects",
        ["examination_id"],
    )
    op.create_index("ix_examination_subjects_class_id", "examination_subjects", ["class_id"])
    op.create_index("ix_examination_subjects_subject_id", "examination_subjects", ["subject_id"])

    op.create_table(
        "examination_components",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("examination_subject_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("component_type", sa.String(20), nullable=False),
        sa.Column("max_marks", sa.Numeric(8, 2), nullable=False),
        sa.Column("passing_marks", sa.Numeric(8, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "component_type IN ('theory', 'practical', 'internal', 'combined')",
            name="ck_examination_component_type",
        ),
        sa.CheckConstraint("max_marks > 0", name="ck_examination_component_max_positive"),
        sa.CheckConstraint(
            "passing_marks >= 0 AND passing_marks <= max_marks",
            name="ck_examination_component_pass_range",
        ),
        sa.ForeignKeyConstraint(
            ["examination_subject_id"], ["examination_subjects.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("examination_subject_id", "name", name="uq_examination_component_name"),
    )
    op.create_index(
        "ix_examination_components_examination_subject_id",
        "examination_components",
        ["examination_subject_id"],
    )

    op.create_table(
        "student_marks",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("component_id", sa.BigInteger(), nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("obtained_marks", sa.Numeric(8, 2), nullable=True),
        sa.Column("result_status", sa.String(10), nullable=False),
        sa.Column("remarks", sa.String(500), nullable=True),
        sa.Column("entered_by", sa.BigInteger(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("grade", sa.String(10), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "result_status IN ('PASS', 'FAIL', 'ABSENT', 'EXEMPTED')",
            name="ck_student_marks_result_status",
        ),
        sa.CheckConstraint(
            "obtained_marks IS NULL OR obtained_marks >= 0",
            name="ck_student_marks_nonnegative",
        ),
        sa.ForeignKeyConstraint(
            ["component_id"], ["examination_components.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entered_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("component_id", "student_id", name="uq_student_mark_component_student"),
    )
    op.create_index("ix_student_marks_student_id", "student_marks", ["student_id"])

    op.create_table(
        "grading_rules",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("scale_code", sa.String(50), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("minimum_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("maximum_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("description", sa.String(200), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "minimum_percentage >= 0 AND maximum_percentage <= 100 "
            "AND minimum_percentage <= maximum_percentage",
            name="ck_grading_rule_percentage_range",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scale_code", "grade", name="uq_grading_rule_scale_grade"),
    )
    op.create_index("ix_grading_rules_scale_code", "grading_rules", ["scale_code"])

    op.create_table(
        "examination_results",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("examination_id", sa.BigInteger(), nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("total_max_marks", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_obtained_marks", sa.Numeric(10, 2), nullable=False),
        sa.Column("percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("grade", sa.String(10), nullable=False),
        sa.Column("result_status", sa.String(10), nullable=False),
        sa.Column(
            "calculated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "result_status IN ('PASS', 'FAIL')",
            name="ck_examination_results_status",
        ),
        sa.ForeignKeyConstraint(["examination_id"], ["examinations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("examination_id", "student_id", name="uq_examination_result_student"),
    )
    op.create_index(
        "ix_examination_results_examination_id",
        "examination_results",
        ["examination_id"],
    )
    op.create_index("ix_examination_results_student_id", "examination_results", ["student_id"])

    grades = (
        ("F", 0, 32.99, "Needs improvement"),
        ("D", 33, 39.99, "Basic"),
        ("C", 40, 49.99, "Satisfactory"),
        ("B", 50, 59.99, "Good"),
        ("A", 60, 74.99, "Very good"),
        ("A+", 75, 89.99, "Excellent"),
        ("O", 90, 100, "Outstanding"),
    )
    op.bulk_insert(
        sa.table(
            "grading_rules",
            sa.column("scale_code", sa.String(50)),
            sa.column("grade", sa.String(10)),
            sa.column("minimum_percentage", sa.Numeric(5, 2)),
            sa.column("maximum_percentage", sa.Numeric(5, 2)),
            sa.column("description", sa.String(200)),
        ),
        [
            {
                "scale_code": "DEFAULT",
                "grade": grade,
                "minimum_percentage": minimum,
                "maximum_percentage": maximum,
                "description": description,
            }
            for grade, minimum, maximum, description in grades
        ],
    )
    _seed_academic_permissions()


def _seed_academic_permissions() -> None:
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
    grants = {
        "SUPER_ADMIN": {
            "academics.subjects.manage",
            "academics.examinations.manage",
            "academics.marks.manage",
            "academics.marks.correct",
            "academics.results.read",
            "academics.grading.manage",
            "academics.electives.manage",
        },
        "ADMIN": {
            "academics.subjects.manage",
            "academics.examinations.manage",
            "academics.marks.manage",
            "academics.marks.correct",
            "academics.results.read",
            "academics.grading.manage",
            "academics.electives.manage",
        },
        "STUDENT": {"academics.results.read"},
    }
    connection = op.get_bind()
    for code, action in (
        ("academics.subjects.manage", "subjects.manage"),
        ("academics.examinations.manage", "examinations.manage"),
        ("academics.marks.manage", "marks.manage"),
        ("academics.marks.correct", "marks.correct"),
        ("academics.results.read", "results.read"),
        ("academics.grading.manage", "grading.manage"),
        ("academics.electives.manage", "electives.manage"),
    ):
        permission_id = connection.execute(
            sa.select(permissions.c.id).where(permissions.c.code == code)
        ).scalar_one_or_none()
        if permission_id is None:
            connection.execute(
                permissions.insert().values(
                    code=code,
                    module="academics",
                    action=action,
                )
            )
            permission_id = connection.execute(
                sa.select(permissions.c.id).where(permissions.c.code == code)
            ).scalar_one()
        for role_code, permission_codes in grants.items():
            if code not in permission_codes:
                continue
            role_id = connection.execute(
                sa.select(roles.c.id).where(roles.c.code == role_code)
            ).scalar_one_or_none()
            if role_id is None:
                continue
            exists = connection.execute(
                sa.select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.permission_id == permission_id,
                )
            ).first()
            if exists is None:
                connection.execute(
                    role_permissions.insert().values(
                        role_id=role_id,
                        permission_id=permission_id,
                    )
                )
    teacher_role_id = connection.execute(
        sa.select(roles.c.id).where(roles.c.code == "TEACHER")
    ).scalar_one_or_none()
    if teacher_role_id is not None:
        for code in (
            "subjects.create",
            "subjects.update",
            "teaching_assignments.manage",
        ):
            permission_id = connection.execute(
                sa.select(permissions.c.id).where(permissions.c.code == code)
            ).scalar_one_or_none()
            if permission_id is not None:
                connection.execute(
                    role_permissions.delete().where(
                        role_permissions.c.role_id == teacher_role_id,
                        role_permissions.c.permission_id == permission_id,
                    )
                )


def downgrade() -> None:
    op.drop_index("ix_examination_results_student_id", table_name="examination_results")
    op.drop_index("ix_examination_results_examination_id", table_name="examination_results")
    op.drop_table("examination_results")
    op.drop_index("ix_grading_rules_scale_code", table_name="grading_rules")
    op.drop_table("grading_rules")
    op.drop_index("ix_student_marks_student_id", table_name="student_marks")
    op.drop_table("student_marks")
    op.drop_index(
        "ix_examination_components_examination_subject_id",
        table_name="examination_components",
    )
    op.drop_table("examination_components")
    op.drop_index("ix_examination_subjects_subject_id", table_name="examination_subjects")
    op.drop_index("ix_examination_subjects_class_id", table_name="examination_subjects")
    op.drop_index(
        "ix_examination_subjects_examination_id",
        table_name="examination_subjects",
    )
    op.drop_table("examination_subjects")
    op.drop_index("ix_examinations_class_id", table_name="examinations")
    op.drop_table("examinations")
    op.drop_index(
        "ix_student_subject_selections_class_id",
        table_name="student_subject_selections",
    )
    op.drop_index(
        "ix_student_subject_selections_student_id",
        table_name="student_subject_selections",
    )
    op.drop_table("student_subject_selections")

    with op.batch_alter_table("teacher_class_subjects") as batch_op:
        batch_op.drop_column("is_active")
    with op.batch_alter_table("class_subjects") as batch_op:
        batch_op.drop_constraint("ck_class_subjects_subject_type", type_="check")
        batch_op.drop_column("is_active")
        batch_op.drop_column("stream")
        batch_op.drop_column("subject_type")
    with op.batch_alter_table("subjects") as batch_op:
        batch_op.drop_constraint("ck_subjects_subject_type", type_="check")
        batch_op.drop_column("passing_marks")
        batch_op.drop_column("max_marks")
        batch_op.drop_column("subject_type")
    _drop_academic_permissions()


def _drop_academic_permissions() -> None:
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(100)),
    )
    role_permissions = sa.table(
        "role_permissions",
        sa.column("role_id", sa.BigInteger()),
        sa.column("permission_id", sa.BigInteger()),
    )
    roles = sa.table(
        "roles",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(50)),
    )
    connection = op.get_bind()
    for code in (
        "academics.subjects.manage",
        "academics.examinations.manage",
        "academics.marks.manage",
        "academics.marks.correct",
        "academics.results.read",
        "academics.grading.manage",
        "academics.electives.manage",
    ):
        permission_id = connection.execute(
            sa.select(permissions.c.id).where(permissions.c.code == code)
        ).scalar_one_or_none()
        if permission_id is not None:
            connection.execute(
                role_permissions.delete().where(role_permissions.c.permission_id == permission_id)
            )
            connection.execute(permissions.delete().where(permissions.c.id == permission_id))
    teacher_role_id = connection.execute(
        sa.select(roles.c.id).where(roles.c.code == "TEACHER")
    ).scalar_one_or_none()
    if teacher_role_id is not None:
        for code in (
            "subjects.create",
            "subjects.update",
            "teaching_assignments.manage",
        ):
            permission_id = connection.execute(
                sa.select(permissions.c.id).where(permissions.c.code == code)
            ).scalar_one_or_none()
            if permission_id is None:
                continue
            exists = connection.execute(
                sa.select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == teacher_role_id,
                    role_permissions.c.permission_id == permission_id,
                )
            ).first()
            if exists is None:
                connection.execute(
                    role_permissions.insert().values(
                        role_id=teacher_role_id,
                        permission_id=permission_id,
                    )
                )
