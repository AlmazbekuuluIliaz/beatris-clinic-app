from __future__ import annotations

import enum

from sqlalchemy import CHAR, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("phone", name="uq_users_phone"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        __import__("sqlalchemy", fromlist=["Enum"]).Enum(
            UserRole,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=UserRole.PATIENT,
        server_default=UserRole.PATIENT.value,
    )

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    specialist_profile = relationship(
        "Specialist",
        back_populates="user",
        uselist=False,
    )
    appointments = relationship(
        "Appointment",
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
    )
    wishlist_items = relationship(
        "WishlistItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders = relationship("Order", back_populates="user")
    patient_recommendations = relationship(
        "Recommendation",
        back_populates="patient",
        foreign_keys="Recommendation.patient_id",
    )
    doctor_recommendations = relationship(
        "Recommendation",
        back_populates="doctor",
        foreign_keys="Recommendation.doctor_id",
    )


class RefreshToken(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[str] = mapped_column(DateTime, nullable=False)
    revoked_at = mapped_column(DateTime)
    created_at = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    user: Mapped[User] = relationship(back_populates="refresh_tokens")
