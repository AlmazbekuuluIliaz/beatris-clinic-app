from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ClinicInfo(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clinic_info"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    whatsapp: Mapped[str | None] = mapped_column(String(20))
    instagram: Mapped[str | None] = mapped_column(String(255))
    working_hours: Mapped[str] = mapped_column(String(255), nullable=False)
    map_url: Mapped[str | None] = mapped_column(String(500))


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
