"""Add appointment_number, requested_date, requested_time + backfill.

Revision ID: 20260611_0001
Revises: 20260610_0001
Create Date: 2026-06-11 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_0001"
down_revision: str | None = "20260610_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("appointment_number", sa.String(length=30), nullable=True),
    )
    op.add_column("appointments", sa.Column("requested_date", sa.Date(), nullable=True))
    op.add_column("appointments", sa.Column("requested_time", sa.Time(), nullable=True))
    op.create_unique_constraint(
        "uq_appointments_appointment_number",
        "appointments",
        ["appointment_number"],
    )

    # Backfill requested_date/time from current appointment_date/time
    op.execute(
        """
        UPDATE appointments
        SET requested_date = appointment_date,
            requested_time = appointment_time
        WHERE requested_date IS NULL
        """
    )

    # Backfill appointment_number per day, sequence by created_at.
    # Format the day in Python to avoid sa.text() interpreting % as paramstyle.
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            "SELECT id, created_at FROM appointments "
            "WHERE appointment_number IS NULL "
            "ORDER BY created_at, id"
        )
    ).fetchall()
    counters: dict[str, int] = {}
    for row_id, created_at in rows:
        day = created_at.strftime("%y%m%d")
        counters[day] = counters.get(day, 0) + 1
        number = f"BT-{day}-{counters[day]:03d}"
        connection.execute(
            sa.text(
                "UPDATE appointments SET appointment_number = :num WHERE id = :id"
            ),
            {"num": number, "id": row_id},
        )


def downgrade() -> None:
    op.drop_constraint(
        "uq_appointments_appointment_number",
        "appointments",
        type_="unique",
    )
    op.drop_column("appointments", "requested_time")
    op.drop_column("appointments", "requested_date")
    op.drop_column("appointments", "appointment_number")
