from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import AddCartItemRequest, Cart, UpdateCartItemRequest
from app.serializers import cart_to_api

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=Cart)
def get_cart(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items = repositories.list_cart_items(db, current_user.id)
    return cart_to_api(items)


@router.post("/items", response_model=Cart, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: AddCartItemRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    product = repositories.get_product(db, payload.productId)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found",
        )

    items = repositories.add_cart_item(db, current_user.id, product, payload.quantity)
    return cart_to_api(items)


@router.patch("/items/{itemId}", response_model=Cart)
def update_cart_item(
    itemId: str,
    payload: UpdateCartItemRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items = repositories.update_cart_item(db, current_user.id, itemId, payload.quantity)
    if items is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    return cart_to_api(items)


@router.delete("/items/{itemId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(
    itemId: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    repositories.delete_cart_item(db, current_user.id, itemId)
    return None
