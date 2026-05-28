"""Add SoftDeleteMixin columns (deleted_by, is_active) to classes and students.

Revision ID: 004_soft_delete
Revises: 003_align_permissions
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_soft_delete"
down_revision: Union[str, None] = "003_align_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ensure_soft_delete_columns(table: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table):
        return
    columns = {c["name"] for c in inspector.get_columns(table)}
    if "deleted_by" not in columns:
        op.add_column(table, sa.Column("deleted_by", sa.BigInteger(), nullable=True))
    if "is_active" not in columns:
        op.add_column(
            table,
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.alter_column(table, "is_active", server_default=None)


def upgrade() -> None:
    _ensure_soft_delete_columns("classes")
    _ensure_soft_delete_columns("students")

    # Align legacy status values with ClassStatus enum (active / inactive).
    op.execute(
        """
        UPDATE classes
        SET status = LOWER(status)
        WHERE status IN ('ACTIVE', 'INACTIVE')
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for table in ("classes", "students"):
        if not inspector.has_table(table):
            continue
        columns = {c["name"] for c in inspector.get_columns(table)}
        if "deleted_by" in columns:
            op.drop_column(table, "deleted_by")
        if "is_active" in columns:
            op.drop_column(table, "is_active")
