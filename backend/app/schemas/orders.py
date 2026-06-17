from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta
from app.schemas.products import Product


OrderStatus = Literal["created", "paid", "processing", "delivered", "cancelled"]
PaymentStatus = Literal["pending", "paid", "failed", "refunded"]
PaymentMethod = Literal["card_online", "cash_on_delivery"]
DeliveryMethod = Literal["courier", "pickup"]


class CreateOrderRequest(BaseModel):
    paymentMethod: PaymentMethod
    deliveryMethod: DeliveryMethod
    deliveryAddress: str = Field(min_length=1, max_length=500)
    recipientName: str = Field(min_length=1, max_length=255)
    recipientPhone: str = Field(min_length=1, max_length=20)
    comment: Optional[str] = None


class AdminCreateOrderItem(BaseModel):
    productId: str = Field(min_length=1)
    quantity: int = Field(ge=1)


class AdminCreateOrderRequest(BaseModel):
    userId: str = Field(min_length=1)
    items: list[AdminCreateOrderItem] = Field(min_length=1)
    paymentMethod: PaymentMethod
    deliveryMethod: DeliveryMethod
    deliveryAddress: str = Field(min_length=1, max_length=500)
    recipientName: str = Field(min_length=1, max_length=255)
    recipientPhone: str = Field(min_length=1, max_length=20)
    comment: Optional[str] = None


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    product: Product
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    subtotal: float = Field(ge=0)


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    orderNumber: str = Field(validation_alias=AliasChoices("order_number", "orderNumber"))
    userId: Optional[str] = Field(default=None, validation_alias=AliasChoices("user_id", "userId"))
    items: list[OrderItem]
    totalPrice: float = Field(ge=0, validation_alias=AliasChoices("total_price", "totalPrice"))
    paymentStatus: PaymentStatus = Field(validation_alias=AliasChoices("payment_status", "paymentStatus"))
    orderStatus: OrderStatus = Field(validation_alias=AliasChoices("order_status", "orderStatus"))
    paymentMethod: PaymentMethod = Field(validation_alias=AliasChoices("payment_method", "paymentMethod"))
    deliveryMethod: DeliveryMethod = Field(validation_alias=AliasChoices("delivery_method", "deliveryMethod"))
    deliveryAddress: Optional[str] = Field(default=None, validation_alias=AliasChoices("delivery_address", "deliveryAddress"))
    recipientName: Optional[str] = Field(default=None, validation_alias=AliasChoices("recipient_name", "recipientName"))
    recipientPhone: Optional[str] = Field(default=None, validation_alias=AliasChoices("recipient_phone", "recipientPhone"))
    createdAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("created_at", "createdAt"))


class OrderListResponse(BaseModel):
    items: list[Order]
    meta: PaginationMeta


class UpdateOrderStatusRequest(BaseModel):
    orderStatus: OrderStatus
