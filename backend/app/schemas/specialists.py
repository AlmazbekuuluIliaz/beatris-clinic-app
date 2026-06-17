from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.base import PaginationMeta


class Specialist(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    fullName: str = Field(validation_alias=AliasChoices("full_name", "fullName"))
    position: str
    specialization: str
    experienceYears: Optional[int] = Field(default=None, validation_alias=AliasChoices("experience_years", "experienceYears"))
    photoUrl: Optional[str] = Field(default=None, validation_alias=AliasChoices("photo_url", "photoUrl"))
    serviceIds: list[str] = Field(default_factory=list)


class SpecialistListResponse(BaseModel):
    items: list[Specialist]
    meta: PaginationMeta


class AdminSpecialist(Specialist):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    userId: Optional[str] = Field(default=None, validation_alias=AliasChoices("user_id", "userId"))
    isActive: bool = Field(validation_alias=AliasChoices("is_active", "isActive"))


class AdminSpecialistListResponse(BaseModel):
    items: list[AdminSpecialist]
    meta: PaginationMeta


class CreateSpecialistRequest(BaseModel):
    userId: Optional[str] = Field(default=None, min_length=1)
    fullName: str = Field(min_length=1, max_length=255)
    position: str = Field(min_length=1, max_length=255)
    specialization: str = Field(min_length=1, max_length=255)
    experienceYears: Optional[int] = Field(default=None, ge=0)
    photoUrl: Optional[str] = Field(default=None, max_length=500)
    serviceIds: list[str] = Field(default_factory=list)
    isActive: bool = True


class UpdateSpecialistRequest(BaseModel):
    userId: Optional[str] = Field(default=None, min_length=1)
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    position: Optional[str] = Field(default=None, min_length=1, max_length=255)
    specialization: Optional[str] = Field(default=None, min_length=1, max_length=255)
    experienceYears: Optional[int] = Field(default=None, ge=0)
    photoUrl: Optional[str] = Field(default=None, max_length=500)
    serviceIds: Optional[list[str]] = None
    isActive: Optional[bool] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class DoctorSchedule(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    specialist: Specialist
    date: str = Field(validation_alias=AliasChoices("schedule_date", "date"))
    startTime: str = Field(validation_alias=AliasChoices("start_time", "startTime"))
    endTime: str = Field(validation_alias=AliasChoices("end_time", "endTime"))
    isAvailable: bool = Field(validation_alias=AliasChoices("is_available", "isAvailable"))
    createdAt: datetime = Field(validation_alias=AliasChoices("created_at", "createdAt"))
    updatedAt: datetime = Field(validation_alias=AliasChoices("updated_at", "updatedAt"))


class DoctorScheduleListResponse(BaseModel):
    items: list[DoctorSchedule]
    meta: PaginationMeta


class DoctorScheduleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    date: str = Field(validation_alias=AliasChoices("schedule_date", "date"))
    startTime: str = Field(validation_alias=AliasChoices("start_time", "startTime"))
    endTime: str = Field(validation_alias=AliasChoices("end_time", "endTime"))
    isAvailable: bool = Field(validation_alias=AliasChoices("is_available", "isAvailable"))


class CreateDoctorScheduleRequest(BaseModel):
    specialistId: str
    date: str
    startTime: str
    endTime: str
    isAvailable: bool = True

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        date.fromisoformat(value)
        return value

    @field_validator("startTime", "endTime")
    @classmethod
    def validate_time(cls, value: str) -> str:
        datetime.strptime(value, "%H:%M")
        return value

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.parsed_start_time >= self.parsed_end_time:
            raise ValueError("startTime must be earlier than endTime")
        return self

    @property
    def parsed_date(self) -> date:
        return date.fromisoformat(self.date)

    @property
    def parsed_start_time(self) -> time:
        return datetime.strptime(self.startTime, "%H:%M").time()

    @property
    def parsed_end_time(self) -> time:
        return datetime.strptime(self.endTime, "%H:%M").time()


class UpdateDoctorScheduleRequest(BaseModel):
    specialistId: Optional[str] = None
    date: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    isAvailable: Optional[bool] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            date.fromisoformat(value)
        return value

    @field_validator("startTime", "endTime")
    @classmethod
    def validate_time(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            datetime.strptime(value, "%H:%M")
        return value

    @model_validator(mode="after")
    def validate_has_changes(self):
        values = [
            self.specialistId,
            self.date,
            self.startTime,
            self.endTime,
            self.isAvailable,
        ]
        if not self.model_fields_set or all(value is None for value in values):
            raise ValueError("At least one field must be provided")
        if self.startTime is not None and self.endTime is not None:
            if self.parsed_start_time >= self.parsed_end_time:
                raise ValueError("startTime must be earlier than endTime")
        return self

    @property
    def parsed_date(self) -> date | None:
        return date.fromisoformat(self.date) if self.date is not None else None

    @property
    def parsed_start_time(self) -> time | None:
        return datetime.strptime(self.startTime, "%H:%M").time() if self.startTime is not None else None

    @property
    def parsed_end_time(self) -> time | None:
        return datetime.strptime(self.endTime, "%H:%M").time() if self.endTime is not None else None
