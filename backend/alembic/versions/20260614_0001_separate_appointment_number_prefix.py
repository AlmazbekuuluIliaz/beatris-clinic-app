"""Use a separate prefix for appointment numbers.

Revision ID: 20260614_0001
Revises: 20260611_0001
Create Date: 2026-06-14 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260614_0001"
down_revision: str | None = "20260611_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _replace_prefix(old_prefix: str, new_prefix: str) -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(
            "SELECT id, appointment_number FROM appointments "
            "WHERE appointment_number LIKE :prefix"
        ),
        {"prefix": f"{old_prefix}%"},
    ).fetchall()

    for appointment_id, appointment_number in rows:
        connection.execute(
            sa.text(
                "UPDATE appointments SET appointment_number = :number WHERE id = :id"
            ),
            {
                "number": f"{new_prefix}{appointment_number[len(old_prefix):]}",
                "id": appointment_id,
            },
        )


def upgrade() -> None:
    _replace_prefix("BT-", "AP-")


def downgrade() -> None:
    _replace_prefix("AP-", "BT-")
