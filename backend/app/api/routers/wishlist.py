from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import raise_not_found
from app.core.database import get_db
from app.schemas import AddWishlistItemRequest, WishlistItem
from app.services import wishlist as wishlist_service

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=list[WishlistItem])
def get_wishlist(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return wishlist_service.list_wishlist(db, current_user.id)


@router.post("/items", response_model=WishlistItem, status_code=status.HTTP_201_CREATED)
def add_wishlist_item(
    payload: AddWishlistItemRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return wishlist_service.add_wishlist_item(db, current_user.id, payload.productId)
    except ValueError:
        raise_not_found("Товар не найден")


@router.delete("/items/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wishlist_item(
    productId: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not wishlist_service.delete_wishlist_item(db, current_user.id, productId):
        raise_not_found("Товар не найден в избранном")
