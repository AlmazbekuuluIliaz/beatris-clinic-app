from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def order_detail_options() -> tuple:
    return (
        selectinload(models.Order.user),
        selectinload(models.Order.items).selectinload(models.OrderItem.product).selectinload(models.Product.category),
        selectinload(models.Order.payments),
    )


def _admin_orders_statement(
    order_status: str | None,
    payment_status: str | None,
    search: str | None,
    date_from=None,
    date_to=None,
):
    from sqlalchemy import func

    statement = (
        select(models.Order)
        .join(models.Order.user)
        .options(*order_detail_options())
        .order_by(models.Order.created_at.desc())
    )

    if order_status:
        statement = statement.where(models.Order.order_status == models.OrderStatus(order_status))

    if payment_status:
        statement = statement.where(models.Order.payment_status == models.PaymentStatus(payment_status))

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Order.order_number.ilike(needle),
                models.Order.recipient_name.ilike(needle),
                models.Order.recipient_phone.ilike(needle),
                models.User.full_name.ilike(needle),
                models.User.phone.ilike(needle),
            )
        )

    if date_from is not None:
        statement = statement.where(func.date(models.Order.created_at) >= date_from)

    if date_to is not None:
        statement = statement.where(func.date(models.Order.created_at) <= date_to)

    return statement


def list_admin_orders(
    db: Session,
    order_status: str | None,
    payment_status: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Order], dict]:
    return paginated(
        db,
        _admin_orders_statement(order_status, payment_status, search),
        page,
        limit,
    )


def list_admin_orders_all(
    db: Session,
    order_status: str | None = None,
    payment_status: str | None = None,
    search: str | None = None,
    date_from=None,
    date_to=None,
) -> list[models.Order]:
    return list(
        db.scalars(
            _admin_orders_statement(order_status, payment_status, search, date_from, date_to)
        ).all()
    )


def get_admin_order(db: Session, order_id: str) -> models.Order | None:
    return db.scalar(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.id == order_id)
    )


ORDER_TO_PAYMENT_STATUS = {
    models.OrderStatus.CREATED: models.PaymentStatus.PENDING,
    models.OrderStatus.PAID: models.PaymentStatus.PAID,
    models.OrderStatus.PROCESSING: models.PaymentStatus.PAID,
    models.OrderStatus.DELIVERED: models.PaymentStatus.PAID,
}


def _payment_status_for_order(new_order_status, current_payment_status):
    if new_order_status == models.OrderStatus.CANCELLED:
        if current_payment_status in (models.PaymentStatus.PAID, models.PaymentStatus.REFUNDED):
            return models.PaymentStatus.REFUNDED
        return models.PaymentStatus.FAILED
    return ORDER_TO_PAYMENT_STATUS[new_order_status]


def update_admin_order_status(db: Session, order_id: str, payload) -> models.Order | None:
    order = db.get(models.Order, order_id)
    if order is None:
        return None

    if "orderStatus" in payload.model_fields_set and payload.orderStatus is not None:
        new_status = models.OrderStatus(payload.orderStatus)
        order.order_status = new_status
        order.payment_status = _payment_status_for_order(new_status, order.payment_status)

    db.add(order)
    db.commit()
    return get_admin_order(db, order_id)


def _next_order_number(db: Session) -> str:
    prefix = f"BT-{datetime.now():%y%m%d}-"
    last = db.scalar(
        select(models.Order.order_number)
        .where(models.Order.order_number.like(f"{prefix}%"))
        .order_by(models.Order.order_number.desc())
        .limit(1)
    )
    sequence = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{sequence:03d}"


def create_order_from_cart(db: Session, user_id: str, payload, cart_items: list[models.CartItem]) -> models.Order:
    total_price = sum((item.price * item.quantity for item in cart_items), Decimal("0.00"))
    order = models.Order(
        order_number=_next_order_number(db),
        user_id=user_id,
        total_price=total_price,
        payment_status=models.PaymentStatus.PENDING,
        order_status=models.OrderStatus.CREATED,
        payment_method=models.PaymentMethod(payload.paymentMethod),
        delivery_method=models.DeliveryMethod(payload.deliveryMethod),
        delivery_address=payload.deliveryAddress,
        recipient_name=payload.recipientName,
        recipient_phone=payload.recipientPhone,
        comment=payload.comment,
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_title=item.product.title,
                product_slug=item.product.slug,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.price * item.quantity,
            )
        )
        db.delete(item)

    db.commit()
    return get_user_order(db, user_id, order.id)


def create_admin_order(db: Session, payload) -> models.Order | None:
    from app.repositories.products import get_product

    line_items: list[tuple[models.Product, int, Decimal]] = []
    total_price = Decimal("0.00")
    for item in payload.items:
        product = get_product(db, item.productId)
        if product is None or not product.is_active:
            return None
        subtotal = product.price * item.quantity
        total_price += subtotal
        line_items.append((product, item.quantity, subtotal))

    order = models.Order(
        order_number=_next_order_number(db),
        user_id=payload.userId,
        total_price=total_price,
        payment_status=models.PaymentStatus.PENDING,
        order_status=models.OrderStatus.CREATED,
        payment_method=models.PaymentMethod(payload.paymentMethod),
        delivery_method=models.DeliveryMethod(payload.deliveryMethod),
        delivery_address=payload.deliveryAddress,
        recipient_name=payload.recipientName,
        recipient_phone=payload.recipientPhone,
        comment=payload.comment,
    )
    db.add(order)
    db.flush()

    for product, quantity, subtotal in line_items:
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_title=product.title,
                product_slug=product.slug,
                quantity=quantity,
                price=product.price,
                subtotal=subtotal,
            )
        )

    db.commit()
    return get_admin_order(db, order.id)


def list_user_orders(db: Session, user_id: str) -> list[models.Order]:
    return db.scalars(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.user_id == user_id)
        .order_by(models.Order.created_at.desc())
    ).all()


def get_user_order(db: Session, user_id: str, order_id: str) -> models.Order | None:
    return db.scalar(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.id == order_id, models.Order.user_id == user_id)
    )


def create_order_payment(db: Session, order: models.Order) -> models.Payment:
    payment = models.Payment(
        order_id=order.id,
        payment_url=f"https://payments.example.test/orders/{order.id}",
        provider_payment_id=None,
        status=models.PaymentStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
