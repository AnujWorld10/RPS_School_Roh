"""Align permissions table with ORM (module, action columns).

Revision ID: 003_align_permissions
Revises: 002_phase2
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_align_permissions"
down_revision: Union[str, None] = "002_phase2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("permissions"):
        return

    columns = {col["name"] for col in inspector.get_columns("permissions")}

    if "module" not in columns:
        op.add_column("permissions", sa.Column("module", sa.String(100), nullable=True))
    if "action" not in columns:
        op.add_column("permissions", sa.Column("action", sa.String(50), nullable=True))

    # Table was created by an older migration with name/description only.
    if "name" in columns:
        op.execute(
            """
            UPDATE permissions
            SET module = SUBSTRING_INDEX(code, '.', 1),
                action = SUBSTRING_INDEX(code, '.', -1)
            WHERE module IS NULL OR action IS NULL
            """
        )

    op.execute(
        """
        UPDATE permissions
        SET module = COALESCE(module, 'general'),
            action = COALESCE(action, 'access')
        WHERE module IS NULL OR action IS NULL
        """
    )

    op.alter_column("permissions", "module", existing_type=sa.String(100), nullable=False)
    op.alter_column("permissions", "action", existing_type=sa.String(50), nullable=False)

    for legacy_col in ("name", "description", "is_active", "created_at", "updated_at"):
        if legacy_col in columns:
            op.drop_column("permissions", legacy_col)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("permissions"):
        return
    columns = {col["name"] for col in inspector.get_columns("permissions")}

    if "name" not in columns:
        op.add_column("permissions", sa.Column("name", sa.String(100), nullable=True))
        op.execute("UPDATE permissions SET name = code WHERE name IS NULL")
        op.alter_column("permissions", "name", nullable=False)

    if "module" in columns:
        op.drop_column("permissions", "module")
    if "action" in columns:
        op.drop_column("permissions", "action")
