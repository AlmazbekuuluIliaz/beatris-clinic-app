from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import Review, ReviewListResponse
from app.services import reviews as reviews_service

router = APIRouter(tags=["Reviews"])


@router.get("/reviews", response_model=ReviewListResponse)
def get_reviews(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> dict:
    items, meta = reviews_service.list_reviews(db, page, limit)
    return {"items": items, "meta": meta}
