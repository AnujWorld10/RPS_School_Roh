"""Align audit_logs table with AuditLog ORM.

Revision ID: 006_audit_logs
Revises: 005_inquiry_history
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_audit_logs"
down_revision: Union[str, None] = "005_inquiry_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("audit_logs"):
        return

    columns = {c["name"] for c in inspector.get_columns("audit_logs")}

    if "user_id" in columns and "actor_user_id" not in columns:
        op.execute(
            "ALTER TABLE audit_logs CHANGE COLUMN user_id actor_user_id BIGINT NULL"
        )
        columns.discard("user_id")
        columns.add("actor_user_id")

    if "actor_user_id" not in columns:
        op.add_column("audit_logs", sa.Column("actor_user_id", sa.BigInteger(), nullable=True))
        op.create_foreign_key(
            "fk_audit_logs_actor_user_id",
            "audit_logs",
            "users",
            ["actor_user_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if "old_values" not in columns:
        op.add_column("audit_logs", sa.Column("old_values", sa.JSON(), nullable=True))
    if "new_values" not in columns:
        op.add_column("audit_logs", sa.Column("new_values", sa.JSON(), nullable=True))
    if "request_id" not in columns:
        op.add_column("audit_logs", sa.Column("request_id", sa.String(100), nullable=True))

    op.execute("UPDATE audit_logs SET request_id = '' WHERE request_id IS NULL")
    op.alter_column(
        "audit_logs",
        "request_id",
        existing_type=sa.String(100),
        nullable=False,
    )

    if "changes" in columns:
        op.drop_column("audit_logs", "changes")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("audit_logs"):
        return
    columns = {c["name"] for c in inspector.get_columns("audit_logs")}
    if "changes" not in columns:
        op.add_column("audit_logs", sa.Column("changes", sa.JSON(), nullable=True))
    if "request_id" in columns:
        op.alter_column("audit_logs", "request_id", existing_type=sa.String(100), nullable=True)
    if "new_values" in columns:
        op.drop_column("audit_logs", "new_values")
    if "old_values" in columns:
        op.drop_column("audit_logs", "old_values")
    if "actor_user_id" in columns and "user_id" not in columns:
        op.execute(
            "ALTER TABLE audit_logs CHANGE COLUMN actor_user_id user_id BIGINT NULL"
        )
