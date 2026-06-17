from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import raise_not_found
from app.core.database import get_db
from app.schemas import AddCartItemRequest, Cart, UpdateCartItemRequest
from app.services import cart as cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=Cart)
def get_cart(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return cart_service.list_cart(db, current_user.id)


@router.post("/items", response_model=Cart, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: AddCartItemRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return cart_service.add_cart_item(db, current_user.id, payload.productId, payload.quantity)
    except ValueError:
        raise_not_found("Товар не найден")


@router.patch("/items/{itemId}", response_model=Cart)
def update_cart_item(
    itemId: str,
    payload: UpdateCartItemRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = cart_service.update_cart_item(db, current_user.id, itemId, payload.quantity)
    if result is None:
        raise_not_found("Позиция корзины не найдена")
    return result


@router.delete("/items/{itemId}", response_model=Cart)
def delete_cart_item(
    itemId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = cart_service.delete_cart_item(db, current_user.id, itemId)
    if result is None:
        raise_not_found("Позиция корзины не найдена")
    return result
