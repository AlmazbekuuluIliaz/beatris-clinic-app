"""Add appointment status history.

Revision ID: 20260609_0002
Revises: 20260609_0001
Create Date: 2026-06-09 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260609_0002"
down_revision: str | None = "20260609_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "appointment_status_history",
        sa.Column("id", sa.CHAR(length=36), server_default=sa.text("(UUID())"), nullable=False),
        sa.Column("appointment_id", sa.CHAR(length=36), nullable=False),
        sa.Column("admin_id", sa.CHAR(length=36), nullable=True),
        sa.Column(
            "previous_status",
            sa.Enum("pending", "confirmed", "completed", "cancelled", name="appointmentstatus"),
            nullable=False,
        ),
        sa.Column(
            "new_status",
            sa.Enum("pending", "confirmed", "completed", "cancelled", name="appointmentstatus"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_appointment_status_history_admin_id",
        "appointment_status_history",
        ["admin_id"],
    )
    op.create_index(
        "ix_appointment_status_history_appointment_id",
        "appointment_status_history",
        ["appointment_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_appointment_status_history_appointment_id", table_name="appointment_status_history")
    op.drop_index("ix_appointment_status_history_admin_id", table_name="appointment_status_history")
    op.drop_table("appointment_status_history")
