"""Add appointment patient contact tracking.

Revision ID: 20260609_0001
Revises: 20260607_0001
Create Date: 2026-06-09 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260609_0001"
down_revision: str | None = "20260607_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("patient_contact_status", sa.String(length=20), server_default="not_contacted", nullable=False),
    )
    op.add_column("appointments", sa.Column("patient_contacted_at", sa.DateTime(), nullable=True))
    op.add_column("appointments", sa.Column("patient_contact_comment", sa.Text(), nullable=True))
    op.create_check_constraint(
        "chk_appointments_patient_contact_status",
        "appointments",
        "patient_contact_status IN ('not_contacted', 'contacted', 'agreed', 'declined')",
    )


def downgrade() -> None:
    op.drop_constraint("chk_appointments_patient_contact_status", "appointments", type_="check")
    op.drop_column("appointments", "patient_contact_comment")
    op.drop_column("appointments", "patient_contacted_at")
    op.drop_column("appointments", "patient_contact_status")
