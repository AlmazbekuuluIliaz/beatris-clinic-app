from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.payments import PaymentCreateResponse


def _product_snapshot(item) -> dict:
    if item.product is not None:
        return {
            "id": item.product.id,
            "title": item.product.title,
            "slug": item.product.slug,
            "description": item.product.description,
            "price": float(item.product.price),
            "imageUrl": item.product.image_url,
            "stock": item.product.stock,
            "category": {
                "id": item.product.category.id,
                "title": item.product.category.title,
                "slug": item.product.category.slug,
            },
        }
    return {
        "id": item.product_id or "",
        "title": item.product_title,
        "slug": item.product_slug,
        "description": "",
        "price": float(item.price),
        "imageUrl": None,
        "stock": 0,
        "category": {"id": "", "title": "", "slug": ""},
    }


def _serialize(order) -> dict:
    return {
        "id": order.id,
        "orderNumber": order.order_number,
        "userId": order.user_id,
        "items": [
            {
                "product": _product_snapshot(item),
                "quantity": item.quantity,
                "price": float(item.price),
                "subtotal": float(item.subtotal),
            }
            for item in order.items
        ],
        "totalPrice": float(order.total_price),
        "paymentStatus": order.payment_status.value,
        "orderStatus": order.order_status.value,
        "paymentMethod": order.payment_method.value,
        "deliveryMethod": order.delivery_method.value,
        "deliveryAddress": order.delivery_address,
        "recipientName": order.recipient_name,
        "recipientPhone": order.recipient_phone,
        "createdAt": order.created_at,
    }


def create_order(db: Session, user_id: str, payload) -> dict:
    cart_items = repositories.list_cart_items(db, user_id)
    if not cart_items:
        raise ValueError("cart_empty")

    order = repositories.create_order_from_cart(db, user_id, payload, cart_items)
    return _serialize(order)


def list_user_orders(db: Session, user_id: str) -> list[dict]:
    orders = repositories.list_user_orders(db, user_id)
    return [_serialize(o) for o in orders]


def get_user_order(db: Session, user_id: str, order_id: str) -> dict | None:
    order = repositories.get_user_order(db, user_id, order_id)
    if order is None:
        return None
    return _serialize(order)


def create_order_payment(db: Session, user_id: str, order_id: str) -> dict:
    order = repositories.get_user_order(db, user_id, order_id)
    if order is None:
        raise ValueError("order_not_found")

    payment = repositories.create_order_payment(db, order)
    return PaymentCreateResponse(
        paymentId=payment.id,
        paymentUrl=payment.payment_url,
        expiresAt=payment.expires_at,
    ).model_dump()


def list_admin_orders(
    db: Session,
    order_status: str | None,
    payment_status: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_orders(db, order_status, payment_status, search, page, limit)
    return [_serialize(o) for o in items], meta


def get_admin_order(db: Session, order_id: str) -> dict | None:
    order = repositories.get_admin_order(db, order_id)
    if order is None:
        return None
    return _serialize(order)


def update_admin_order_status(db: Session, order_id: str, payload) -> dict | None:
    order = repositories.update_admin_order_status(db, order_id, payload)
    if order is None:
        return None
    return _serialize(order)


def create_admin_order(db: Session, payload) -> dict:
    user = repositories.get_user(db, payload.userId)
    if user is None:
        raise ValueError("user_not_found")

    for item in payload.items:
        product = repositories.get_product(db, item.productId)
        if product is None or not product.is_active:
            raise ValueError("product_not_found")

    order = repositories.create_admin_order(db, payload)
    if order is None:
        raise ValueError("could_not_create_order")

    return _serialize(order)


def list_orders_for_export(
    db: Session,
    order_status,
    payment_status,
    search,
    date_from,
    date_to,
):
    return repositories.list_admin_orders_all(db, order_status, payment_status, search, date_from, date_to)
