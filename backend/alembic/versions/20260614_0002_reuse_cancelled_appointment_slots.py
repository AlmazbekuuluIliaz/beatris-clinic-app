"""Allow cancelled appointment slots to be reused.

Revision ID: 20260614_0002
Revises: 20260614_0001
Create Date: 2026-06-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from alembic.migration_guards import has_column, has_unique_constraint

revision: str = "20260614_0002"
down_revision: str | None = "20260614_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OLD_CONSTRAINT = "uq_appointments_specialist_slot"
NEW_CONSTRAINT = "uq_appointments_active_specialist_slot"


def upgrade() -> None:
    if has_unique_constraint("appointments", OLD_CONSTRAINT):
        op.drop_constraint(OLD_CONSTRAINT, "appointments", type_="unique")

    if not has_column("appointments", "active_slot_marker"):
        op.add_column(
            "appointments",
            sa.Column(
                "active_slot_marker",
                sa.Integer(),
                sa.Computed(
                    "CASE WHEN status = 'cancelled' THEN NULL ELSE 1 END",
                    persisted=True,
                ),
                nullable=True,
            ),
        )

    if not has_unique_constraint("appointments", NEW_CONSTRAINT):
        op.create_unique_constraint(
            NEW_CONSTRAINT,
            "appointments",
            ["specialist_id", "appointment_date", "appointment_time", "active_slot_marker"],
        )


def downgrade() -> None:
    if has_unique_constraint("appointments", NEW_CONSTRAINT):
        op.drop_constraint(NEW_CONSTRAINT, "appointments", type_="unique")

    if has_column("appointments", "active_slot_marker"):
        op.drop_column("appointments", "active_slot_marker")

    if not has_unique_constraint("appointments", OLD_CONSTRAINT):
        op.create_unique_constraint(
            OLD_CONSTRAINT,
            "appointments",
            ["specialist_id", "appointment_date", "appointment_time"],
        )
