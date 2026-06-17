from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.errors import raise_not_found
from app.core.database import get_db
from app.schemas import (
    CreateReviewRequest,
    Review,
    ReviewListResponse,
    UpdateReviewRequest,
)
from app.services import reviews as reviews_service

router = APIRouter()


@router.get("/reviews", response_model=ReviewListResponse)
def get_admin_reviews(
    search: str | None = None,
    isPublished: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = reviews_service.list_admin_reviews(db, search, isPublished, page, limit)
    return {"items": items, "meta": meta}


@router.post("/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_admin_review(payload: CreateReviewRequest, db: Session = Depends(get_db)) -> dict:
    return reviews_service.create_admin_review(db, payload)


@router.get("/reviews/{id}", response_model=Review)
def get_admin_review(id: str, db: Session = Depends(get_db)) -> dict:
    result = reviews_service.get_admin_review(db, id)
    if result is None:
        raise_not_found("Отзыв не найден")
    return result


@router.patch("/reviews/{id}", response_model=Review)
def update_admin_review(id: str, payload: UpdateReviewRequest, db: Session = Depends(get_db)) -> dict:
    result = reviews_service.update_admin_review(db, id, payload)
    if result is None:
        raise_not_found("Отзыв не найден")
    return result


@router.delete("/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_review(id: str, db: Session = Depends(get_db)) -> Response:
    if not reviews_service.delete_admin_review(db, id):
        raise_not_found("Отзыв не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
