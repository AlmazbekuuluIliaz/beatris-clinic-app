"""Add description and image_url to service_categories.

Lets admins enrich service-category cards with a short description and a
preview image (URL string) shown in the admin UI and on the public site.

Revision ID: 20260604_0001
Revises: 20260527_0001
Create Date: 2026-06-04 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.migration_guards import has_column

revision: str = "20260604_0001"
down_revision: str | None = "20260527_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if not has_column("service_categories", "description"):
        op.add_column(
            "service_categories",
            sa.Column("description", sa.Text(), nullable=True),
        )
    if not has_column("service_categories", "image_url"):
        op.add_column(
            "service_categories",
            sa.Column("image_url", sa.String(length=500), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("service_categories", "image_url")
    op.drop_column("service_categories", "description")
