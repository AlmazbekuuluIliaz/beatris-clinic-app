from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta


class Review(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    authorName: str = Field(validation_alias=AliasChoices("author_name", "authorName"))
    rating: int = Field(ge=1, le=5)
    text: str
    source: str
    sourceUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("source_url", "sourceUrl"))
    isPublished: bool = Field(validation_alias=AliasChoices("is_published", "isPublished"))
    sortOrder: int = Field(ge=0, validation_alias=AliasChoices("sort_order", "sortOrder"))
    publishedAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("published_at", "publishedAt"))
    createdAt: datetime = Field(validation_alias=AliasChoices("created_at", "createdAt"))
    updatedAt: datetime = Field(validation_alias=AliasChoices("updated_at", "updatedAt"))


class ReviewListResponse(BaseModel):
    items: list[Review]
    meta: PaginationMeta


class CreateReviewRequest(BaseModel):
    authorName: str = Field(min_length=1, max_length=255)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1)
    source: str = Field(default="2gis", min_length=1, max_length=50)
    sourceUrl: Optional[str] = Field(default=None, max_length=1000)
    isPublished: bool = True
    sortOrder: int = Field(default=0, ge=0)
    publishedAt: Optional[datetime] = None


class UpdateReviewRequest(BaseModel):
    authorName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    text: Optional[str] = Field(default=None, min_length=1)
    source: Optional[str] = Field(default=None, min_length=1, max_length=50)
    sourceUrl: Optional[str] = Field(default=None, max_length=1000)
    isPublished: Optional[bool] = None
    sortOrder: Optional[int] = Field(default=None, ge=0)
    publishedAt: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
