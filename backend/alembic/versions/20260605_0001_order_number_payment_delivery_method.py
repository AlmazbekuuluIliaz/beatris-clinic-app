"""Add order_number, payment_method, delivery_method to orders.

Gives each order a human-readable number (BT-YYMMDD-NNN) alongside its UUID,
plus the payment method (card online / cash on delivery) and delivery method
(courier / pickup). Existing rows are backfilled: order_number is generated per
day in created_at order, methods get sensible defaults.

Revision ID: 20260605_0001
Revises: 20260604_0001
Create Date: 2026-06-05 00:00:00.000000
"""

from collections.abc import Sequence
from datetime import datetime

import sqlalchemy as sa
from alembic import op

from alembic.migration_guards import has_column, has_unique_constraint

revision: str = "20260605_0001"
down_revision: str | None = "20260604_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if not has_column("orders", "payment_method"):
        op.add_column(
            "orders",
            sa.Column(
                "payment_method",
                sa.Enum("card_online", "cash_on_delivery", name="payment_method"),
                nullable=False,
                server_default="card_online",
            ),
        )
    if not has_column("orders", "delivery_method"):
        op.add_column(
            "orders",
            sa.Column(
                "delivery_method",
                sa.Enum("courier", "pickup", name="delivery_method"),
                nullable=False,
                server_default="courier",
            ),
        )

    # order_number is only backfilled/constrained when it is freshly added.
    # On a database where the schema already ships it (e.g. built from the full
    # SQL snapshot) the column is already populated, NOT NULL and unique.
    if not has_column("orders", "order_number"):
        op.add_column(
            "orders",
            sa.Column("order_number", sa.String(length=30), nullable=True),
        )

        # Backfill order_number for existing rows: per-day counter in created_at order.
        conn = op.get_bind()
        rows = conn.execute(
            sa.text("SELECT id, created_at FROM orders ORDER BY created_at, id")
        ).fetchall()
        counters: dict[str, int] = {}
        for row in rows:
            created = row.created_at
            day = (created or datetime.now()).strftime("%y%m%d")
            counters[day] = counters.get(day, 0) + 1
            number = f"BT-{day}-{counters[day]:03d}"
            conn.execute(
                sa.text("UPDATE orders SET order_number = :number WHERE id = :id"),
                {"number": number, "id": row.id},
            )

        op.alter_column(
            "orders",
            "order_number",
            existing_type=sa.String(length=30),
            nullable=False,
        )

    if not has_unique_constraint("orders", "uq_orders_order_number"):
        op.create_unique_constraint("uq_orders_order_number", "orders", ["order_number"])


def downgrade() -> None:
    op.drop_constraint("uq_orders_order_number", "orders", type_="unique")
    op.drop_column("orders", "order_number")
    op.drop_column("orders", "delivery_method")
    op.drop_column("orders", "payment_method")
