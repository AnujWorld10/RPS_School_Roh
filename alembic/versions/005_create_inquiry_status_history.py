"""Create inquiry_status_history if missing (partial migration recovery).

Revision ID: 005_inquiry_history
Revises: 004_soft_delete
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_inquiry_history"
down_revision: Union[str, None] = "004_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("inquiry_status_history"):
        return

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
