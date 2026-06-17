from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def pagination_meta(page: int, limit: int, total: int) -> dict:
    return {"page": page, "limit": limit, "total": total}


def paginated(db: Session, statement: Select, page: int, limit: int) -> tuple[list, dict]:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = db.scalar(total_statement) or 0
    items = db.scalars(statement.offset((page - 1) * limit).limit(limit)).all()
    return items, pagination_meta(page, limit, total)
