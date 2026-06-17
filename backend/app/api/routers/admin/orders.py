from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.errors import ORDER_ERRORS, raise_bad_request, raise_not_found
from app.core.database import get_db
from app.schemas import (
    AdminCreateOrderRequest,
    Order,
    OrderListResponse,
    OrderStatus,
    PaymentStatus,
    SalesAnalyticsResponse,
    ServicesAnalyticsResponse,
    UpdateOrderStatusRequest,
)
from app.services import admin as admin_service
from app.services import orders as orders_service
from app.api.routers.admin.helpers import csv_response, format_money_for_excel

router = APIRouter()


@router.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_admin_order(
    payload: AdminCreateOrderRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return orders_service.create_admin_order(db, payload)
    except ValueError as e:
        raise_bad_request(ORDER_ERRORS.get(str(e), str(e)))


@router.get("/orders", response_model=OrderListResponse)
def get_admin_orders(
    orderStatus: OrderStatus | None = None,
    paymentStatus: PaymentStatus | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = orders_service.list_admin_orders(db, orderStatus, paymentStatus, search, page, limit)
    return {"items": items, "meta": meta}


@router.get("/orders/{id}", response_model=Order)
def get_admin_order(id: str, db: Session = Depends(get_db)) -> dict:
    result = orders_service.get_admin_order(db, id)
    if result is None:
        raise_not_found("Order not found")
    return result


@router.patch("/orders/{id}", response_model=Order)
@router.patch("/orders/{id}/status", response_model=Order)
def update_admin_order_status(
    id: str,
    payload: UpdateOrderStatusRequest,
    db: Session = Depends(get_db),
) -> dict:
    result = orders_service.update_admin_order_status(db, id, payload)
    if result is None:
        raise_not_found("Order not found")
    return result


@router.get("/analytics/sales", response_model=SalesAnalyticsResponse)
def get_admin_sales_analytics(
    dateFrom: date | None = None,
    dateTo: date | None = None,
    db: Session = Depends(get_db),
) -> dict:
    date_to = dateTo or date.today()
    date_from = dateFrom or (date_to - timedelta(days=29))
    if date_from > date_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата начала должна быть раньше или равна дате окончания")
    return admin_service.get_sales_analytics(db, date_from, date_to)


@router.get("/analytics/services", response_model=ServicesAnalyticsResponse)
def get_admin_services_analytics(
    dateFrom: date | None = None,
    dateTo: date | None = None,
    db: Session = Depends(get_db),
) -> dict:
    date_to = dateTo or date.today()
    date_from = dateFrom or (date_to - timedelta(days=29))
    if date_from > date_to:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата начала должна быть раньше или равна дате окончания")
    return admin_service.get_services_analytics(db, date_from, date_to)


ORDER_STATUS_LABELS_RU = {
    "created": "Создан",
    "paid": "Оплачен",
    "processing": "В обработке",
    "delivered": "Доставлен",
    "cancelled": "Отменён",
}
PAYMENT_STATUS_LABELS_RU = {
    "pending": "Ожидает",
    "paid": "Оплачено",
    "failed": "Ошибка",
    "refunded": "Возврат",
}


@router.get("/exports/orders.csv")
def export_admin_orders(
    orderStatus: OrderStatus | None = None,
    paymentStatus: PaymentStatus | None = None,
    search: str | None = None,
    dateFrom: date | None = None,
    dateTo: date | None = None,
    db: Session = Depends(get_db),
):
    orders = orders_service.list_orders_for_export(db, orderStatus, paymentStatus, search, dateFrom, dateTo)
    header = [
        "Номер", "Дата", "Клиент", "Телефон клиента",
        "Получатель", "Телефон получателя", "Адрес",
        "Статус заказа", "Статус оплаты", "Сумма", "Позиций", "Комментарий",
    ]
    rows = []
    for o in orders:
        created = o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else ""
        order_status_value = o.order_status.value if o.order_status else ""
        payment_status_value = o.payment_status.value if o.payment_status else ""
        rows.append([
            o.order_number or "",
            created,
            o.user.full_name if o.user else "",
            o.user.phone if o.user else "",
            o.recipient_name or "",
            o.recipient_phone or "",
            o.delivery_address or "",
            ORDER_STATUS_LABELS_RU.get(order_status_value, order_status_value),
            PAYMENT_STATUS_LABELS_RU.get(payment_status_value, payment_status_value),
            format_money_for_excel(o.total_price),
            len(o.items or []),
            o.comment or "",
        ])
    return csv_response("orders.csv", header, rows)
