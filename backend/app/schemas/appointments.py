from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import PaginationMeta
from app.schemas.services import Service
from app.schemas.specialists import Specialist


class AvailableSlot(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    specialistId: str
    date: str
    time: str


class CreateAppointmentRequest(BaseModel):
    serviceId: str
    specialistId: str
    date: str
    time: str
    patientName: str
    patientPhone: str
    comment: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        from datetime import date as d
        d.fromisoformat(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        from datetime import datetime as dt
        dt.strptime(value, "%H:%M")
        return value

    @property
    def parsed_date(self):
        from datetime import date as d
        return d.fromisoformat(self.date)

    @property
    def parsed_time(self):
        from datetime import datetime as dt
        return dt.strptime(self.time, "%H:%M").time()


class BookAppointmentRequest(BaseModel):
    serviceId: str
    specialistId: str
    date: str
    time: str
    comment: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        from datetime import date as d
        d.fromisoformat(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        from datetime import datetime as dt
        dt.strptime(value, "%H:%M")
        return value

    @property
    def parsed_date(self):
        from datetime import date as d
        return d.fromisoformat(self.date)

    @property
    def parsed_time(self):
        from datetime import datetime as dt
        return dt.strptime(self.time, "%H:%M").time()


class AppointmentStatusHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    adminId: Optional[str] = Field(default=None, validation_alias=AliasChoices("admin_id", "adminId"))
    adminName: Optional[str] = None
    previousStatus: str = Field(validation_alias=AliasChoices("previous_status", "previousStatus"))
    newStatus: str = Field(validation_alias=AliasChoices("new_status", "newStatus"))
    createdAt: datetime = Field(validation_alias=AliasChoices("created_at", "createdAt"))


class Appointment(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    appointmentNumber: Optional[str] = Field(default=None, validation_alias=AliasChoices("appointment_number", "appointmentNumber"))
    patientId: Optional[str] = Field(default=None, validation_alias=AliasChoices("patient_id", "patientId"))
    patientName: Optional[str] = Field(default=None, validation_alias=AliasChoices("patient_name", "patientName"))
    patientPhone: Optional[str] = Field(default=None, validation_alias=AliasChoices("patient_phone", "patientPhone"))
    service: Service
    specialist: Specialist
    date: str = Field(validation_alias=AliasChoices("appointment_date", "date"))
    time: str = Field(validation_alias=AliasChoices("appointment_time", "time"))
    requestedDate: Optional[str] = Field(default=None, validation_alias=AliasChoices("requested_date", "requestedDate"))
    requestedTime: Optional[str] = Field(default=None, validation_alias=AliasChoices("requested_time", "requestedTime"))
    status: str
    comment: Optional[str] = None
    patientContactStatus: str = Field(default="not_contacted", validation_alias=AliasChoices("patient_contact_status", "patientContactStatus"))
    patientContactedAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("patient_contacted_at", "patientContactedAt"))
    patientContactComment: Optional[str] = Field(default=None, validation_alias=AliasChoices("patient_contact_comment", "patientContactComment"))
    statusHistory: list[AppointmentStatusHistoryItem] = Field(default_factory=list, validation_alias=AliasChoices("status_history", "statusHistory"))
    createdAt: Optional[datetime] = Field(default=None, validation_alias=AliasChoices("created_at", "createdAt"))


class AppointmentListResponse(BaseModel):
    items: list[Appointment]
    meta: PaginationMeta


class PendingCountResponse(BaseModel):
    count: int


class UpdateAppointmentStatusRequest(BaseModel):
    status: Literal["pending", "confirmed", "completed", "cancelled"]


class RescheduleAppointmentRequest(BaseModel):
    specialistId: str
    date: str
    time: str
    comment: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        from datetime import date as d
        d.fromisoformat(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        from datetime import datetime as dt
        dt.strptime(value, "%H:%M")
        return value

    @property
    def parsed_date(self):
        from datetime import date as d
        return d.fromisoformat(self.date)

    @property
    def parsed_time(self):
        from datetime import datetime as dt
        return dt.strptime(self.time, "%H:%M").time()


class UpdateAppointmentContactRequest(BaseModel):
    patientContactStatus: Literal["not_contacted", "contacted", "agreed", "declined"]
    patientContactComment: Optional[str] = None
