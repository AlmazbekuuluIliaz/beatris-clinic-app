from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.wishlist import WishlistItem


def list_wishlist(db: Session, user_id: str) -> list[dict]:
    items = repositories.list_wishlist_items(db, user_id)
    return [WishlistItem.model_validate(i).model_dump() for i in items]


def add_wishlist_item(db: Session, user_id: str, product_id: str) -> dict:
    item = repositories.add_wishlist_item(db, user_id, product_id)
    return WishlistItem.model_validate(item).model_dump()


def delete_wishlist_item(db: Session, user_id: str, product_id: str) -> bool:
    return repositories.delete_wishlist_item(db, user_id, product_id)
