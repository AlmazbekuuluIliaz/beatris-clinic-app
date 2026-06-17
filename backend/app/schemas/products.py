from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta


class ProductCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    slug: str


class CreateProductCategoryRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)


class UpdateProductCategoryRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    slug: str
    description: str
    price: float = Field(ge=0)
    imageUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("image_url", "imageUrl"))
    stock: int = Field(ge=0)
    category: ProductCategory


class ProductListResponse(BaseModel):
    items: list[Product]
    meta: PaginationMeta


class AdminProduct(Product):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    isActive: bool = Field(validation_alias=AliasChoices("is_active", "isActive"))
    createdAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("created_at", "createdAt"))


class AdminProductListResponse(BaseModel):
    items: list[AdminProduct]
    meta: PaginationMeta


class CreateProductRequest(BaseModel):
    categoryId: str
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    stock: int = Field(ge=0)
    isActive: bool = True


class UpdateProductRequest(BaseModel):
    categoryId: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    stock: Optional[int] = Field(default=None, ge=0)
    isActive: Optional[bool] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
