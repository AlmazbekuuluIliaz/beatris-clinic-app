from __future__ import annotations

from decimal import Decimal
from sqlalchemy.orm import Session

from app import repositories
from app.schemas.cart import Cart, CartItem


def _build_cart(items: list) -> dict:
    validated = [CartItem.model_validate(i).model_dump() for i in items]
    total = sum(item["subtotal"] for item in validated)
    return {"items": validated, "totalPrice": total}


def list_cart(db: Session, user_id: str) -> dict:
    items = repositories.list_cart_items(db, user_id)
    return _build_cart(items)


def add_cart_item(db: Session, user_id: str, product_id: str, quantity: int) -> dict:
    product = repositories.get_product(db, product_id)
    if product is None:
        raise ValueError("product_not_found")

    items = repositories.add_cart_item(db, user_id, product, quantity)
    return _build_cart(items)


def update_cart_item(db: Session, user_id: str, item_id: str, quantity: int) -> dict | None:
    items = repositories.update_cart_item(db, user_id, item_id, quantity)
    if items is None:
        return None
    return _build_cart(items)


def delete_cart_item(db: Session, user_id: str, item_id: str) -> dict | None:
    items = repositories.delete_cart_item(db, user_id, item_id)
    if items is None:
        return None
    return _build_cart(items)
