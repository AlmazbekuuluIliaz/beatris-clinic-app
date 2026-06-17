from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.orders import PaymentStatus


class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    paymentUrl: str = Field(validation_alias=AliasChoices("payment_url", "paymentUrl"))
    providerPaymentId: Optional[str] = Field(default=None, validation_alias=AliasChoices("provider_payment_id", "providerPaymentId"))
    status: PaymentStatus
    expiresAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("expires_at", "expiresAt"))
    createdAt: datetime = Field(validation_alias=AliasChoices("created_at", "createdAt"))


class PaymentCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    paymentId: str = Field(validation_alias=AliasChoices("id", "paymentId"))
    paymentUrl: str = Field(validation_alias=AliasChoices("payment_url", "paymentUrl"))
    expiresAt: datetime = Field(validation_alias=AliasChoices("expires_at", "expiresAt"))
