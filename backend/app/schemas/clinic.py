from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class ClinicInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    description: str
    address: str
    phone: str
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None
    workingHours: str = Field(validation_alias=AliasChoices("working_hours", "workingHours"))
    mapUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("map_url", "mapUrl"))


class UpdateClinicInfoRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    address: Optional[str] = Field(default=None, min_length=1, max_length=500)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    whatsapp: Optional[str] = Field(default=None, max_length=20)
    instagram: Optional[str] = Field(default=None, max_length=255)
    workingHours: Optional[str] = Field(default=None, min_length=1, max_length=255)
    mapUrl: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self
