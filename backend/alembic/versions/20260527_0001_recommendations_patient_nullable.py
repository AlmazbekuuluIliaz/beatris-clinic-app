"""Make recommendations.patient_id nullable.

Allows recording a doctor recommendation for a walk-in (first-time) patient who
has no account — the patient identity is then taken from the linked appointment
(patient_name / patient_phone).

Revision ID: 20260527_0001
Revises: 20260511_0001
Create Date: 2026-05-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260527_0001"
down_revision: str | None = "20260511_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "recommendations",
        "patient_id",
        existing_type=sa.CHAR(length=36),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "recommendations",
        "patient_id",
        existing_type=sa.CHAR(length=36),
        nullable=False,
    )
