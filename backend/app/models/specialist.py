from __future__ import annotations

from datetime import date, time

from sqlalchemy import (
    Boolean, CHAR, CheckConstraint, Date, ForeignKey, Index, Integer,
    String, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Specialist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "specialists"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_specialists_user"),
        CheckConstraint("experience_years IS NULL OR experience_years >= 0", name="chk_specialists_experience"),
        Index("ix_specialists_full_name", "full_name"),
    )

    user_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="SET NULL"))
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_years: Mapped[int | None] = mapped_column(Integer)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))

    user = relationship("User", back_populates="specialist_profile")
    service_links = relationship("SpecialistService", back_populates="specialist", cascade="all, delete-orphan")
    services = relationship("Service", secondary="specialist_services", back_populates="specialists", viewonly=True)
    appointments = relationship("Appointment", back_populates="specialist")
    schedule_items = relationship("DoctorSchedule", back_populates="specialist", cascade="all, delete-orphan")


class DoctorSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "doctor_schedule"
    __table_args__ = (
        UniqueConstraint("specialist_id", "schedule_date", "start_time", "end_time", name="uq_doctor_schedule_slot"),
        CheckConstraint("start_time < end_time", name="chk_doctor_schedule_time"),
    )

    specialist_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("specialists.id", ondelete="CASCADE"), nullable=False)
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))

    specialist: Mapped[Specialist] = relationship(back_populates="schedule_items")
