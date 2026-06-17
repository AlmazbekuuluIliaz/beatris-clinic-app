"""Add reviews table.

Revision ID: 20260607_0001
Revises: 20260606_0001
Create Date: 2026-06-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from alembic.migration_guards import has_index, has_table

revision: str = "20260607_0001"
down_revision: str | None = "20260606_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if not has_table("reviews"):
        op.create_table(
            "reviews",
            sa.Column("id", sa.CHAR(length=36), server_default=sa.text("(UUID())"), nullable=False),
            sa.Column("author_name", sa.String(length=255), nullable=False),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("source", sa.String(length=50), server_default="2gis", nullable=False),
            sa.Column("source_url", sa.String(length=1000), nullable=True),
            sa.Column("is_published", sa.Boolean(), server_default=sa.text("1"), nullable=False),
            sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
            sa.Column("published_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=False),
            sa.CheckConstraint("rating >= 1 AND rating <= 5", name="chk_reviews_rating"),
            sa.CheckConstraint("sort_order >= 0", name="chk_reviews_sort_order"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not has_index("reviews", "ix_reviews_published_sort"):
        op.create_index("ix_reviews_published_sort", "reviews", ["is_published", "sort_order"])


def downgrade() -> None:
    op.drop_index("ix_reviews_published_sort", table_name="reviews")
    op.drop_table("reviews")
