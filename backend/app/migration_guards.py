from __future__ import annotations

import sqlalchemy as sa
from alembic import op


def has_column(table: str, column: str) -> bool:
    return any(c["name"] == column for c in sa.inspect(op.get_bind()).get_columns(table))


def has_table(table: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(table)


def has_index(table: str, name: str) -> bool:
    return any(ix["name"] == name for ix in sa.inspect(op.get_bind()).get_indexes(table))


def has_unique_constraint(table: str, name: str) -> bool:
    return any(
        uc["name"] == name
        for uc in sa.inspect(op.get_bind()).get_unique_constraints(table)
    )


def has_check_constraint(table: str, name: str) -> bool:
    try:
        return any(
            cc["name"] == name
            for cc in sa.inspect(op.get_bind()).get_check_constraints(table)
        )
    except NotImplementedError:
        return False
