"""Add admission and recurring fee structures.

Revision ID: 013_fee_structures
Revises: 012_role_portal_academics
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "013_fee_structures"
down_revision: str | None = "012_role_portal_academics"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_NEW_PERMISSIONS = (
    ("fees.create", "fees", "create"),
    ("fees.read", "fees", "read"),
    ("fees.update", "fees", "update"),
    ("fees.delete", "fees", "delete"),
)
_BIGINT_PK = sa.BigInteger().with_variant(sa.Integer(), "sqlite")

_ROLE_PERMISSIONS = {
    "SUPER_ADMIN": {item[0] for item in _NEW_PERMISSIONS},
    "ADMIN": {item[0] for item in _NEW_PERMISSIONS},
    "ACCOUNTANT": {"fees.create", "fees.read", "fees.update"},
}


def _seed_fee_permissions() -> None:
    bind = op.get_bind()
    permissions = sa.table(
        "permissions",
        sa.column("id", sa.BigInteger()),
        sa.column("code", sa.String(100)),
        sa.column("module", sa.String(100)),
        sa.column("action", sa.String(50)),
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

    for code, module, action in _NEW_PERMISSIONS:
        permission_id = bind.scalar(sa.select(permissions.c.id).where(permissions.c.code == code))
        if permission_id is None:
            bind.execute(sa.insert(permissions).values(code=code, module=module, action=action))

    permission_ids = {
        code: bind.scalar(sa.select(permissions.c.id).where(permissions.c.code == code))
        for code, _, _ in _NEW_PERMISSIONS
    }
    for role_code, permission_codes in _ROLE_PERMISSIONS.items():
        role_id = bind.scalar(sa.select(roles.c.id).where(roles.c.code == role_code))
        if role_id is None:
            continue
        for permission_code in permission_codes:
            permission_id = permission_ids[permission_code]
            exists = bind.scalar(
                sa.select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == role_id,
                    role_permissions.c.permission_id == permission_id,
                )
            )
            if not exists:
                bind.execute(
                    sa.insert(role_permissions).values(
                        role_id=role_id,
                        permission_id=permission_id,
                    )
                )


def upgrade() -> None:
    op.create_table(
        "admission_fee_structures",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("structure_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name="fk_admission_fee_structures_class",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("academic_year", "class_id", name="uq_admission_fee_year_class"),
    )
    op.create_index(
        "ix_admission_fee_structures_academic_year",
        "admission_fee_structures",
        ["academic_year"],
    )
    op.create_index(
        "ix_admission_fee_structures_class_id",
        "admission_fee_structures",
        ["class_id"],
    )

    op.create_table(
        "admission_fee_components",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("structure_id", sa.BigInteger(), nullable=False),
        sa.Column("fee_name", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_refundable", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_optional", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount >= 0", name="ck_admission_fee_component_nonnegative"),
        sa.ForeignKeyConstraint(
            ["structure_id"],
            ["admission_fee_structures.id"],
            name="fk_admission_fee_components_structure",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "structure_id",
            "fee_name",
            name="uq_admission_fee_component_name",
        ),
    )
    op.create_index(
        "ix_admission_fee_components_structure_id",
        "admission_fee_components",
        ["structure_id"],
    )

    op.create_table(
        "monthly_fee_structures",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("class_id", sa.BigInteger(), nullable=False),
        sa.Column("structure_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name="fk_monthly_fee_structures_class",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("academic_year", "class_id", name="uq_monthly_fee_year_class"),
    )
    op.create_index(
        "ix_monthly_fee_structures_academic_year",
        "monthly_fee_structures",
        ["academic_year"],
    )
    op.create_index(
        "ix_monthly_fee_structures_class_id",
        "monthly_fee_structures",
        ["class_id"],
    )

    op.create_table(
        "monthly_fee_components",
        sa.Column("id", _BIGINT_PK, autoincrement=True, nullable=False),
        sa.Column("structure_id", sa.BigInteger(), nullable=False),
        sa.Column("fee_name", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("billing_frequency", sa.String(length=20), nullable=False),
        sa.Column("is_optional", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("amount >= 0", name="ck_monthly_fee_component_nonnegative"),
        sa.CheckConstraint(
            "billing_frequency IN ('MONTHLY', 'QUARTERLY', 'ANNUALLY', 'ONE_TIME')",
            name="ck_monthly_fee_component_frequency",
        ),
        sa.ForeignKeyConstraint(
            ["structure_id"],
            ["monthly_fee_structures.id"],
            name="fk_monthly_fee_components_structure",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "structure_id",
            "fee_name",
            name="uq_monthly_fee_component_name",
        ),
    )
    op.create_index(
        "ix_monthly_fee_components_structure_id",
        "monthly_fee_components",
        ["structure_id"],
    )
    _seed_fee_permissions()


def downgrade() -> None:
    bind = op.get_bind()
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
    permission_ids = sa.select(permissions.c.id).where(
        permissions.c.code.in_([item[0] for item in _NEW_PERMISSIONS])
    )
    bind.execute(
        sa.delete(role_permissions).where(role_permissions.c.permission_id.in_(permission_ids))
    )
    bind.execute(
        sa.delete(permissions).where(permissions.c.code.in_([item[0] for item in _NEW_PERMISSIONS]))
    )

    op.drop_index("ix_monthly_fee_components_structure_id", table_name="monthly_fee_components")
    op.drop_table("monthly_fee_components")
    op.drop_index("ix_monthly_fee_structures_class_id", table_name="monthly_fee_structures")
    op.drop_index(
        "ix_monthly_fee_structures_academic_year",
        table_name="monthly_fee_structures",
    )
    op.drop_table("monthly_fee_structures")
    op.drop_index(
        "ix_admission_fee_components_structure_id",
        table_name="admission_fee_components",
    )
    op.drop_table("admission_fee_components")
    op.drop_index(
        "ix_admission_fee_structures_class_id",
        table_name="admission_fee_structures",
    )
    op.drop_index(
        "ix_admission_fee_structures_academic_year",
        table_name="admission_fee_structures",
    )
    op.drop_table("admission_fee_structures")
