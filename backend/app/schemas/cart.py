from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.schemas.products import Product


class CartItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    product: Product
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    subtotal: float = Field(ge=0)


class Cart(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: list[CartItem]
    totalPrice: float = Field(ge=0)


class AddCartItemRequest(BaseModel):
    productId: str
    quantity: int = Field(ge=1)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(ge=1)
