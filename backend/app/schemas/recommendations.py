from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.schemas.base import PaginationMeta


class Recommendation(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    patientId: Optional[str] = Field(default=None, validation_alias=AliasChoices("patient_id", "patientId"))
    patientName: Optional[str] = None
    patientPhone: Optional[str] = None
    doctorId: str = Field(validation_alias=AliasChoices("doctor_id", "doctorId"))
    appointmentId: Optional[str] = Field(default=None, validation_alias=AliasChoices("appointment_id", "appointmentId"))
    text: str
    productIds: list[str] = Field(default_factory=list)
    createdAt: datetime = Field(validation_alias=AliasChoices("created_at", "createdAt"))


class RecommendationListResponse(BaseModel):
    items: list[Recommendation]
    meta: PaginationMeta


class CreateRecommendationRequest(BaseModel):
    patientId: Optional[str] = None
    appointmentId: Optional[str] = None
    text: str = Field(min_length=1)
    productIds: list[str] = Field(default_factory=list)


class AdminCreateRecommendationRequest(CreateRecommendationRequest):
    doctorId: str


class UpdateRecommendationRequest(BaseModel):
    patientId: Optional[str] = None
    doctorId: Optional[str] = None
    appointmentId: Optional[str] = None
    text: Optional[str] = Field(default=None, min_length=1)
    productIds: Optional[list[str]] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
