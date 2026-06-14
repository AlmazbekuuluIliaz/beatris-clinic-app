from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import repositories
from app.core.database import get_db
from app.schemas import ReviewListResponse
from app.serializers import review_to_api

router = APIRouter(tags=["Reviews"])


@router.get("/reviews", response_model=ReviewListResponse)
def get_reviews(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    reviews, meta = repositories.list_reviews(db, page, limit)
    return {
        "items": [review_to_api(review) for review in reviews],
        "meta": meta,
    }
