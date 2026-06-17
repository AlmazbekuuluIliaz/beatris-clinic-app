"""Проверка агрегатов продаж: в выручку идут только оплаченные заказы."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, repositories


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _make_order(
    session: Session,
    user_id: str,
    *,
    number: str,
    total: str,
    created_at: datetime,
    order_status: models.OrderStatus,
    payment_status: models.PaymentStatus,
    items: list[tuple[str, int, str]],
) -> None:
    order = models.Order(
        order_number=number,
        user_id=user_id,
        total_price=Decimal(total),
        order_status=order_status,
        payment_status=payment_status,
        payment_method=models.PaymentMethod.CARD_ONLINE,
        delivery_method=models.DeliveryMethod.PICKUP,
        delivery_address="-",
        recipient_name="-",
        recipient_phone="-",
        created_at=created_at,
    )
    for title, qty, subtotal in items:
        order.items.append(
            models.OrderItem(
                product_title=title,
                product_slug=title.lower(),
                quantity=qty,
                price=Decimal(subtotal) / qty,
                subtotal=Decimal(subtotal),
            )
        )
    session.add(order)


def test_sales_analytics_counts_only_paid_orders(db: Session) -> None:
    user = models.User(
        full_name="Тест",
        phone="+70000000000",
        password_hash="x",
        role=models.UserRole.PATIENT,
    )
    db.add(user)
    db.flush()

    inside = datetime(2026, 6, 10, 12, 0)
    outside = datetime(2026, 1, 1, 12, 0)

    # Учитываются: оплаченный и доставленный
    _make_order(
        db, user.id, number="A", total="1000", created_at=inside,
        order_status=models.OrderStatus.PAID,
        payment_status=models.PaymentStatus.PAID,
        items=[("Cream", 2, "1000")],
    )
    _make_order(
        db, user.id, number="B", total="500", created_at=inside,
        order_status=models.OrderStatus.DELIVERED,
        payment_status=models.PaymentStatus.PENDING,
        items=[("Serum", 1, "500")],
    )
    # Не учитываются: отменённый, неоплаченный (created), вне периода
    _make_order(
        db, user.id, number="C", total="9999", created_at=inside,
        order_status=models.OrderStatus.CANCELLED,
        payment_status=models.PaymentStatus.REFUNDED,
        items=[("Cream", 50, "9999")],
    )
    _make_order(
        db, user.id, number="D", total="7777", created_at=inside,
        order_status=models.OrderStatus.CREATED,
        payment_status=models.PaymentStatus.PENDING,
        items=[("Serum", 50, "7777")],
    )
    _make_order(
        db, user.id, number="E", total="3000", created_at=outside,
        order_status=models.OrderStatus.PAID,
        payment_status=models.PaymentStatus.PAID,
        items=[("Cream", 1, "3000")],
    )
    db.commit()

    result = repositories.get_sales_analytics(db, date(2026, 6, 1), date(2026, 6, 30))

    assert result["revenue"] == 1500.0
    assert result["ordersCount"] == 2
    assert result["averageCheck"] == 750.0

    titles = {p["productTitle"]: p for p in result["topProducts"]}
    assert set(titles) == {"Cream", "Serum"}
    assert titles["Cream"]["revenue"] == 1000.0
    assert titles["Cream"]["quantity"] == 2
    assert titles["Serum"]["revenue"] == 500.0
    # Топ отсортирован по выручке убыванию
    assert [p["productTitle"] for p in result["topProducts"]] == ["Cream", "Serum"]

    # День с продажами присутствует в разбивке по периодам
    assert {"period": "2026-06-10", "revenue": 1500.0, "ordersCount": 2} in result["revenueByPeriod"]


def test_sales_analytics_empty_period_is_safe(db: Session) -> None:
    result = repositories.get_sales_analytics(db, date(2026, 6, 1), date(2026, 6, 30))
    assert result["revenue"] == 0.0
    assert result["ordersCount"] == 0
    assert result["averageCheck"] == 0.0
    assert result["topProducts"] == []
    assert result["revenueByPeriod"] == []
