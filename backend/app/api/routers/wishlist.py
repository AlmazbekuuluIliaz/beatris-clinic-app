from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import AddWishlistItemRequest, WishlistItem
from app.serializers import wishlist_item_to_api

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=list[WishlistItem])
def get_wishlist(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    items = repositories.list_wishlist_items(db, current_user.id)
    return [wishlist_item_to_api(item) for item in items]


@router.post("/items", response_model=WishlistItem, status_code=status.HTTP_201_CREATED)
def add_wishlist_item(
    payload: AddWishlistItemRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if repositories.get_product(db, payload.productId) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found",
        )

    try:
        item = repositories.add_wishlist_item(db, current_user.id, payload.productId)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wishlist item cannot be added",
        ) from exc

    return wishlist_item_to_api(item)


@router.delete("/items/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wishlist_item(
    productId: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    repositories.delete_wishlist_item(db, current_user.id, productId)
    return None
