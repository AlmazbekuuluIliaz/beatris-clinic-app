from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import raise_bad_request, raise_not_found
from app.core.database import get_db
from app.schemas import CreateOrderRequest, Order, PaymentCreateResponse
from app.services import orders as orders_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CreateOrderRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return orders_service.create_order(db, current_user.id, payload)
    except ValueError as e:
        if str(e) == "cart_empty":
            raise_bad_request("Корзина пуста")
        raise


@router.get("/my", response_model=list[Order])
def get_my_orders(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return orders_service.list_user_orders(db, current_user.id)


@router.get("/{id}", response_model=Order)
def get_order_by_id(
    id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = orders_service.get_user_order(db, current_user.id, id)
    if result is None:
        raise_not_found("Заказ не найден")
    return result


@router.post("/{id}/payment", response_model=PaymentCreateResponse)
def create_order_payment(
    id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return orders_service.create_order_payment(db, current_user.id, id)
    except ValueError:
        raise_not_found("Заказ не найден")
