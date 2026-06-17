from __future__ import annotations

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
