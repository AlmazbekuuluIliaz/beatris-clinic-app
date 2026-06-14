"""Initial Beatris simple schema.

Revision ID: 20260511_0001
Revises:
Create Date: 2026-05-11 20:30:00.000000
"""

from collections.abc import Sequence
from pathlib import Path
import re

from alembic import op

revision: str = "20260511_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = [
    "recommendation_products",
    "recommendations",
    "payments",
    "order_items",
    "orders",
    "cart_items",
    "wishlist_items",
    "products",
    "product_categories",
    "doctor_schedule",
    "appointments",
    "specialist_services",
    "specialists",
    "services",
    "service_categories",
    "refresh_tokens",
    "users",
    "clinic_info",
]


def _schema_statements() -> list[str]:
    schema_path = Path(__file__).resolve().parents[2] / "SQL_Beatrice_simple.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    statements: list[str] = []
    current: list[str] = []

    for line in schema_sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue

        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current).rstrip().removesuffix(";"))
            current = []

    if current:
        statements.append("\n".join(current).rstrip())

    return statements


def upgrade() -> None:
    for statement in _schema_statements():
        if _index_exists(statement):
            continue
        op.execute(statement)


def downgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table}")
    op.execute("SET FOREIGN_KEY_CHECKS = 1")


def _index_exists(statement: str) -> bool:
    match = re.match(r"CREATE\s+INDEX\s+([a-zA-Z0-9_]+)\s+ON\s+([a-zA-Z0-9_]+)", statement)
    if match is None:
        return False

    index_name, table_name = match.groups()
    result = op.get_bind().exec_driver_sql(
        """
        SELECT COUNT(*)
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
        """,
        (table_name, index_name),
    )
    return bool(result.scalar())
