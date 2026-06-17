from __future__ import annotations

import enum
from decimal import Decimal
from datetime import datetime

from sqlalchemy import (
    CHAR, CheckConstraint, DateTime, ForeignKey, Index, Integer,
    Numeric, String, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CARD_ONLINE = "card_online"
    CASH_ON_DELIVERY = "cash_on_delivery"


class DeliveryMethod(str, enum.Enum):
    COURIER = "courier"
    PICKUP = "pickup"


def _sqle(num_cls):
    return __import__("sqlalchemy", fromlist=["Enum"]).Enum(
        num_cls, values_callable=enum_values, native_enum=True, validate_strings=True
    )


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="chk_orders_total_price"),
        Index("ix_orders_user_id", "user_id"),
    )

    order_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        _sqle(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING.value,
    )
    order_status: Mapped[OrderStatus] = mapped_column(
        _sqle(OrderStatus), nullable=False, default=OrderStatus.CREATED, server_default=OrderStatus.CREATED.value,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        _sqle(PaymentMethod), nullable=False, default=PaymentMethod.CARD_ONLINE, server_default=PaymentMethod.CARD_ONLINE.value,
    )
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        _sqle(DeliveryMethod), nullable=False, default=DeliveryMethod.COURIER, server_default=DeliveryMethod.COURIER.value,
    )
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    user = relationship("User", back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(back_populates="order", cascade="all, delete-orphan")
    payments: Mapped[list[Payment]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="chk_order_items_quantity"),
        CheckConstraint("price >= 0", name="chk_order_items_price"),
        CheckConstraint("subtotal >= 0", name="chk_order_items_subtotal"),
    )

    order_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("products.id", ondelete="SET NULL"))
    product_title: Mapped[str] = mapped_column(String(255), nullable=False)
    product_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("provider_payment_id", name="uq_payments_provider_payment_id"),)

    order_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    payment_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[PaymentStatus] = mapped_column(
        _sqle(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING.value,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped[Order] = relationship(back_populates="payments")
