from __future__ import annotations

from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class Recommendation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_patient_id", "patient_id"),
        Index("ix_recommendations_doctor_id", "doctor_id"),
    )

    patient_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id"))
    doctor_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("appointments.id", ondelete="SET NULL"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())

    patient = relationship("User", back_populates="patient_recommendations", foreign_keys=[patient_id])
    doctor = relationship("User", back_populates="doctor_recommendations", foreign_keys=[doctor_id])
    appointment = relationship("Appointment", back_populates="recommendations")
    product_links: Mapped[list[RecommendationProduct]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")
    products = relationship("Product", secondary="recommendation_products", back_populates="recommendations", viewonly=True)


class RecommendationProduct(Base):
    __tablename__ = "recommendation_products"

    recommendation_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("recommendations.id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)

    recommendation: Mapped[Recommendation] = relationship(back_populates="product_links")
    product = relationship("Product", back_populates="recommendation_links")
