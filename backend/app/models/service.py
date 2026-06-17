from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean, CHAR, CheckConstraint, ForeignKey, Index, Integer, Numeric,
    String, Text, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ServiceCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "service_categories"
    __table_args__ = (UniqueConstraint("slug", name="uq_service_categories_slug"),)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default=text("0"))

    services: Mapped[list[Service]] = relationship(back_populates="category")


class Service(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_services_slug"),
        CheckConstraint("price >= 0", name="chk_services_price"),
        CheckConstraint("duration_minutes IS NULL OR duration_minutes > 0", name="chk_services_duration"),
        Index("ix_services_category_id", "category_id"),
        Index("ix_services_title", "title"),
    )

    category_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("service_categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(500))
    contraindications: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("1"))

    category: Mapped[ServiceCategory] = relationship(back_populates="services")
    specialist_links = relationship("SpecialistService", back_populates="service", cascade="all, delete-orphan")
    specialists = relationship("Specialist", secondary="specialist_services", back_populates="services", viewonly=True)
    appointments = relationship("Appointment", back_populates="service")


class SpecialistService(Base):
    __tablename__ = "specialist_services"

    specialist_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("specialists.id", ondelete="CASCADE"), primary_key=True)
    service_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True)

    specialist = relationship("Specialist", back_populates="service_links")
    service: Mapped[Service] = relationship(back_populates="specialist_links")
