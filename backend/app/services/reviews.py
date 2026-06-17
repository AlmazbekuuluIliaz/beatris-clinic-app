from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.reviews import Review


def list_reviews(db: Session, page: int, limit: int) -> tuple[list[dict], dict]:
    items, meta = repositories.list_reviews(db, page, limit)
    return [Review.model_validate(r).model_dump() for r in items], meta


def list_admin_reviews(
    db: Session,
    search: str | None,
    is_published: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_reviews(db, search, is_published, page, limit)
    return [Review.model_validate(r).model_dump() for r in items], meta


def get_admin_review(db: Session, review_id: str) -> dict | None:
    review = repositories.get_admin_review(db, review_id)
    if review is None:
        return None
    return Review.model_validate(review).model_dump()


def create_admin_review(db: Session, payload) -> dict:
    review = repositories.create_admin_review(db, payload)
    return Review.model_validate(review).model_dump()


def update_admin_review(db: Session, review_id: str, payload) -> dict | None:
    review = repositories.update_admin_review(db, review_id, payload)
    if review is None:
        return None
    return Review.model_validate(review).model_dump()


def delete_admin_review(db: Session, review_id: str) -> bool:
    return repositories.delete_admin_review(db, review_id)
