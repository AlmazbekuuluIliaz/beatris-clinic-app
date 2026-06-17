from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta


class ServiceCategory(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    slug: str
    description: Optional[str] = None
    imageUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("image_url", "imageUrl"))
    sortOrder: int = Field(default=0, validation_alias=AliasChoices("sort_order", "sortOrder"))


class CreateServiceCategoryRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    sortOrder: int = Field(default=0, ge=0)


class UpdateServiceCategoryRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    sortOrder: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Service(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    title: str
    slug: str
    description: str
    price: float = Field(ge=0)
    durationMinutes: Optional[int] = Field(default=None, validation_alias=AliasChoices("duration_minutes", "durationMinutes"))
    category: ServiceCategory
    imageUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("image_url", "imageUrl"))
    contraindications: Optional[str] = None


class ServiceListResponse(BaseModel):
    items: list[Service]
    meta: PaginationMeta


class AdminService(Service):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    isActive: bool = Field(validation_alias=AliasChoices("is_active", "isActive"))


class AdminServiceListResponse(BaseModel):
    items: list[AdminService]
    meta: PaginationMeta


class CreateServiceRequest(BaseModel):
    categoryId: str
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    durationMinutes: Optional[int] = Field(default=None, gt=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    contraindications: Optional[str] = None
    isActive: bool = True


class UpdateServiceRequest(BaseModel):
    categoryId: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    durationMinutes: Optional[int] = Field(default=None, gt=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    contraindications: Optional[str] = None
    isActive: Optional[bool] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
