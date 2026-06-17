from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models


def list_cart_items(db: Session, user_id: str) -> list[models.CartItem]:
    return db.scalars(
        select(models.CartItem)
        .options(selectinload(models.CartItem.product).selectinload(models.Product.category))
        .where(models.CartItem.user_id == user_id)
        .order_by(models.CartItem.created_at)
    ).all()


def add_cart_item(
    db: Session,
    user_id: str,
    product: models.Product,
    quantity: int,
) -> list[models.CartItem]:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.user_id == user_id,
            models.CartItem.product_id == product.id,
        )
    )
    if item is None:
        item = models.CartItem(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
        )
    else:
        item.quantity += quantity
        item.price = product.price

    db.add(item)
    db.commit()
    return list_cart_items(db, user_id)


def update_cart_item(db: Session, user_id: str, item_id: str, quantity: int) -> list[models.CartItem] | None:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user_id,
        )
    )
    if item is None:
        return None

    item.quantity = quantity
    db.add(item)
    db.commit()
    return list_cart_items(db, user_id)


def delete_cart_item(db: Session, user_id: str, item_id: str) -> list[models.CartItem] | None:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user_id,
        )
    )
    if item is None:
        return None

    db.delete(item)
    db.commit()
    return list_cart_items(db, user_id)
