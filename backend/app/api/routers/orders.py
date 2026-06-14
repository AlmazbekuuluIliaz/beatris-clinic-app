from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import CreateOrderRequest, Order, PaymentCreateResponse
from app.serializers import order_to_api, payment_create_to_api

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CreateOrderRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    cart_items = repositories.list_cart_items(db, current_user.id)
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty",
        )

    order = repositories.create_order_from_cart(db, current_user.id, payload, cart_items)
    return order_to_api(order)


@router.get("/my", response_model=list[Order])
def get_my_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    orders = repositories.list_user_orders(db, current_user.id)
    return [order_to_api(order) for order in orders]


@router.get("/{id}", response_model=Order)
def get_order_by_id(
    id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = repositories.get_user_order(db, current_user.id, id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_to_api(order)


@router.post("/{id}/payment", response_model=PaymentCreateResponse)
def create_order_payment(
    id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = repositories.get_user_order(db, current_user.id, id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    payment = repositories.create_order_payment(db, order)
    return payment_create_to_api(payment)
