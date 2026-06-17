from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models
from app.repositories.base import paginated


def list_reviews(db: Session, page: int, limit: int) -> tuple[list[models.Review], dict]:
    statement = (
        select(models.Review)
        .where(models.Review.is_published.is_(True))
        .order_by(
            models.Review.sort_order,
            models.Review.published_at.desc(),
            models.Review.created_at.desc(),
        )
    )
    return paginated(db, statement, page, limit)


def list_admin_reviews(
    db: Session,
    search: str | None,
    is_published: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Review], dict]:
    statement = select(models.Review).order_by(
        models.Review.sort_order,
        models.Review.created_at.desc(),
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Review.author_name.ilike(needle),
                models.Review.text.ilike(needle),
                models.Review.source.ilike(needle),
            )
        )

    if is_published is not None:
        statement = statement.where(models.Review.is_published.is_(is_published))

    return paginated(db, statement, page, limit)


def get_admin_review(db: Session, review_id: str) -> models.Review | None:
    return db.get(models.Review, review_id)


def create_admin_review(db: Session, payload) -> models.Review:
    review = models.Review(
        author_name=payload.authorName,
        rating=payload.rating,
        text=payload.text,
        source=payload.source,
        source_url=payload.sourceUrl,
        is_published=payload.isPublished,
        sort_order=payload.sortOrder,
        published_at=payload.publishedAt,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_admin_review(db: Session, review_id: str, payload) -> models.Review | None:
    review = db.get(models.Review, review_id)
    if review is None:
        return None

    if "authorName" in payload.model_fields_set and payload.authorName is not None:
        review.author_name = payload.authorName
    if "rating" in payload.model_fields_set and payload.rating is not None:
        review.rating = payload.rating
    if "text" in payload.model_fields_set and payload.text is not None:
        review.text = payload.text
    if "source" in payload.model_fields_set and payload.source is not None:
        review.source = payload.source
    if "sourceUrl" in payload.model_fields_set:
        review.source_url = payload.sourceUrl
    if "isPublished" in payload.model_fields_set and payload.isPublished is not None:
        review.is_published = payload.isPublished
    if "sortOrder" in payload.model_fields_set and payload.sortOrder is not None:
        review.sort_order = payload.sortOrder
    if "publishedAt" in payload.model_fields_set:
        review.published_at = payload.publishedAt

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_admin_review(db: Session, review_id: str) -> bool:
    review = db.get(models.Review, review_id)
    if review is None:
        return False

    db.delete(review)
    db.commit()
    return True
