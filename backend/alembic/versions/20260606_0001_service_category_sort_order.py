"""Add sort_order to service_categories.

Lets admins control the order in which service directions (categories) appear
on the public site instead of relying on alphabetical title ordering. Existing
rows are backfilled sequentially by current title order so the column is never
all-zero on upgrade.

Revision ID: 20260606_0001
Revises: 20260605_0001
Create Date: 2026-06-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260606_0001"
down_revision: str | None = "20260605_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "service_categories",
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    # Backfill existing rows with a stable order based on current title sort,
    # so upgrades preserve a deterministic ordering instead of all zeros.
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id FROM service_categories ORDER BY title")
    ).fetchall()
    for position, row in enumerate(rows, start=1):
        conn.execute(
            sa.text(
                "UPDATE service_categories SET sort_order = :pos WHERE id = :id"
            ),
            {"pos": position, "id": row.id},
        )


def downgrade() -> None:
    op.drop_column("service_categories", "sort_order")
