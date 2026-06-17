from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta

UserRole = Literal["patient", "doctor", "admin"]


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    fullName: str = Field(validation_alias=AliasChoices("full_name", "fullName"))
    phone: str
    email: Optional[str] = None
    role: str
    createdAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("created_at", "createdAt"))


class UserListResponse(BaseModel):
    items: list[User]
    meta: PaginationMeta


class CreateUserRequest(BaseModel):
    fullName: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    password: str = Field(min_length=8)
    role: UserRole = "patient"


class UpdateUserRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[UserRole] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class AdminUpdateUserRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class UpdateProfileRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
