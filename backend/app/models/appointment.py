from __future__ import annotations

import enum
from datetime import date, datetime, time

from sqlalchemy import (
    CHAR, CheckConstraint, Computed, Date, DateTime, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class AppointmentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentContactStatus(str, enum.Enum):
    NOT_CONTACTED = "not_contacted"
    CONTACTED = "contacted"
    AGREED = "agreed"
    DECLINED = "declined"


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("specialist_id", "appointment_date", "appointment_time", "active_slot_marker", name="uq_appointments_active_specialist_slot"),
        Index("ix_appointments_patient_id", "patient_id"),
        Index("ix_appointments_specialist_date", "specialist_id", "appointment_date"),
        CheckConstraint("patient_contact_status IN ('not_contacted', 'contacted', 'agreed', 'declined')", name="chk_appointments_patient_contact_status"),
    )

    appointment_number: Mapped[str | None] = mapped_column(String(30), unique=True)
    patient_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="SET NULL"))
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    service_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("services.id"), nullable=False)
    specialist_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("specialists.id"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(nullable=False)
    requested_date: Mapped[date | None] = mapped_column(Date)
    requested_time: Mapped[time | None] = mapped_column()
    status: Mapped[AppointmentStatus] = mapped_column(
        __import__("sqlalchemy", fromlist=["Enum"]).Enum(AppointmentStatus, values_callable=enum_values, native_enum=True, validate_strings=True),
        nullable=False, default=AppointmentStatus.PENDING, server_default=AppointmentStatus.PENDING.value,
    )
    active_slot_marker: Mapped[int | None] = mapped_column(
        Integer, Computed("CASE WHEN status = 'cancelled' THEN NULL ELSE 1 END", persisted=True)
    )
    comment: Mapped[str | None] = mapped_column(Text)
    patient_contact_status: Mapped[str] = mapped_column(
        String(20), nullable=False,
        default=AppointmentContactStatus.NOT_CONTACTED.value,
        server_default=AppointmentContactStatus.NOT_CONTACTED.value,
    )
    patient_contacted_at: Mapped[datetime | None] = mapped_column(DateTime)
    patient_contact_comment: Mapped[str | None] = mapped_column(Text)

    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    service = relationship("Service", back_populates="appointments")
    specialist = relationship("Specialist", back_populates="appointments")
    recommendations = relationship("Recommendation", back_populates="appointment")
    status_history = relationship("AppointmentStatusHistory", back_populates="appointment", order_by="AppointmentStatusHistory.created_at.desc()")


class AppointmentStatusHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "appointment_status_history"
    __table_args__ = (
        Index("ix_appointment_status_history_appointment_id", "appointment_id"),
        Index("ix_appointment_status_history_admin_id", "admin_id"),
    )

    appointment_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    admin_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="SET NULL"))
    previous_status: Mapped[AppointmentStatus] = mapped_column(
        __import__("sqlalchemy", fromlist=["Enum"]).Enum(AppointmentStatus, values_callable=enum_values, native_enum=True, validate_strings=True),
        nullable=False,
    )
    new_status: Mapped[AppointmentStatus] = mapped_column(
        __import__("sqlalchemy", fromlist=["Enum"]).Enum(AppointmentStatus, values_callable=enum_values, native_enum=True, validate_strings=True),
        nullable=False,
    )
    created_at = mapped_column(DateTime, nullable=False, server_default=__import__("sqlalchemy", fromlist=["func"]).func.current_timestamp())

    appointment: Mapped[Appointment] = relationship(back_populates="status_history")
    admin = relationship("User")
