from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.products import Product


class WishlistItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    product: Product
    createdAt: Optional[datetime] = None


class AddWishlistItemRequest(BaseModel):
    productId: str
