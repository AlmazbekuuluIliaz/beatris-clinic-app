from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models


def list_wishlist_items(db: Session, user_id: str) -> list[models.WishlistItem]:
    return db.scalars(
        select(models.WishlistItem)
        .options(selectinload(models.WishlistItem.product).selectinload(models.Product.category))
        .where(models.WishlistItem.user_id == user_id)
        .order_by(models.WishlistItem.created_at.desc())
    ).all()


def add_wishlist_item(db: Session, user_id: str, product_id: str) -> models.WishlistItem:
    item = db.scalar(
        select(models.WishlistItem).where(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.product_id == product_id,
        )
    )
    if item is None:
        item = models.WishlistItem(user_id=user_id, product_id=product_id)
        db.add(item)
        db.commit()
    return db.scalar(
        select(models.WishlistItem)
        .options(selectinload(models.WishlistItem.product).selectinload(models.Product.category))
        .where(models.WishlistItem.id == item.id)
    )


def delete_wishlist_item(db: Session, user_id: str, product_id: str) -> bool:
    item = db.scalar(
        select(models.WishlistItem).where(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.product_id == product_id,
        )
    )
    if item is None:
        return False

    db.delete(item)
    db.commit()
    return True
