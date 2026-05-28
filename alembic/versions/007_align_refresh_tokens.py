"""Align refresh_tokens with RefreshToken ORM (token_hash, updated_at).

Revision ID: 007_refresh_tokens
Revises: 006_audit_logs
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_refresh_tokens"
down_revision: Union[str, None] = "006_audit_logs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("refresh_tokens"):
        return

    columns = {c["name"] for c in inspector.get_columns("refresh_tokens")}

    if "token_hash" not in columns:
        op.add_column("refresh_tokens", sa.Column("token_hash", sa.String(255), nullable=True))
        columns.add("token_hash")

    if "token" in columns:
        # Legacy column stored the raw token; new code stores SHA-256 hash only.
        op.execute(
            """
            UPDATE refresh_tokens
            SET token_hash = SHA2(token, 256)
            WHERE token_hash IS NULL OR token_hash = ''
            """
        )
        op.drop_index("ix_refresh_tokens_token", table_name="refresh_tokens")
        op.drop_column("refresh_tokens", "token")
        columns.discard("token")

    if "token_hash" in columns:
        op.execute(
            "UPDATE refresh_tokens SET token_hash = '' WHERE token_hash IS NULL"
        )
        op.alter_column(
            "refresh_tokens",
            "token_hash",
            existing_type=sa.String(255),
            nullable=False,
        )
        indexes = {idx["name"] for idx in inspector.get_indexes("refresh_tokens")}
        if "uq_refresh_tokens_token_hash" not in indexes and "token_hash" in {
            c["name"] for c in inspector.get_columns("refresh_tokens")
        }:
            op.create_unique_constraint(
                "uq_refresh_tokens_token_hash",
                "refresh_tokens",
                ["token_hash"],
            )

    if "updated_at" not in columns:
        op.add_column(
            "refresh_tokens",
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("refresh_tokens"):
        return
    columns = {c["name"] for c in inspector.get_columns("refresh_tokens")}

    if "updated_at" in columns:
        op.drop_column("refresh_tokens", "updated_at")
    if "token" not in columns and "token_hash" in columns:
        op.add_column("refresh_tokens", sa.Column("token", sa.String(500), nullable=True))
        op.execute("UPDATE refresh_tokens SET token = token_hash")
        op.alter_column("refresh_tokens", "token", nullable=False)
        op.drop_constraint("uq_refresh_tokens_token_hash", "refresh_tokens", type_="unique")
        op.drop_column("refresh_tokens", "token_hash")
        op.create_index("ix_refresh_tokens_token", "refresh_tokens", ["token"], unique=True)
