from __future__ import annotations

import enum
from datetime import date, datetime, time
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    Computed,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def uuid_str() -> str:
    return str(uuid4())


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [item.value for item in enum_cls]


class Base(DeclarativeBase):
    pass


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


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


class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CARD_ONLINE = "card_online"
    CASH_ON_DELIVERY = "cash_on_delivery"


class DeliveryMethod(str, enum.Enum):
    COURIER = "courier"
    PICKUP = "pickup"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=uuid_str,
        server_default=text("(UUID())"),
    )


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
    """Настройки админ-панели: пара «ключ → JSON-значение».

    Хранятся серверно (а не в localStorage браузера), чтобы быть одинаковыми
    во всех браузерах и переживать перезапуск. Значение сериализуется в JSON,
    что позволяет хранить строки, числа, булевы значения и списки.
    """

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_reviews_rating"),
        CheckConstraint("sort_order >= 0", name="chk_reviews_sort_order"),
        Index("ix_reviews_published_sort", "is_published", "sort_order"),
    )

    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="2gis",
        server_default="2gis",
    )
    source_url: Mapped[str | None] = mapped_column(String(1000))
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime)


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
        SQLEnum(
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
    specialist_profile: Mapped[Specialist | None] = relationship(
        back_populates="user",
        uselist=False,
    )
    appointments: Mapped[list[Appointment]] = relationship(
        back_populates="patient",
        foreign_keys="Appointment.patient_id",
    )
    wishlist_items: Mapped[list[WishlistItem]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    cart_items: Mapped[list[CartItem]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list[Order]] = relationship(back_populates="user")
    patient_recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="patient",
        foreign_keys="Recommendation.patient_id",
    )
    doctor_recommendations: Mapped[list[Recommendation]] = relationship(
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
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    user: Mapped[User] = relationship(back_populates="refresh_tokens")


class ServiceCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "service_categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_service_categories_slug"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )

    services: Mapped[list[Service]] = relationship(back_populates="category")


class Service(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "services"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_services_slug"),
        CheckConstraint("price >= 0", name="chk_services_price"),
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes > 0",
            name="chk_services_duration",
        ),
        Index("ix_services_category_id", "category_id"),
        Index("ix_services_title", "title"),
    )

    category_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("service_categories.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(500))
    contraindications: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    category: Mapped[ServiceCategory] = relationship(back_populates="services")
    specialist_links: Mapped[list[SpecialistService]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
    specialists: Mapped[list[Specialist]] = relationship(
        secondary="specialist_services",
        back_populates="services",
        viewonly=True,
    )
    appointments: Mapped[list[Appointment]] = relationship(back_populates="service")


class Specialist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "specialists"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_specialists_user"),
        CheckConstraint(
            "experience_years IS NULL OR experience_years >= 0",
            name="chk_specialists_experience",
        ),
        Index("ix_specialists_full_name", "full_name"),
    )

    user_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    experience_years: Mapped[int | None] = mapped_column(Integer)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    user: Mapped[User | None] = relationship(back_populates="specialist_profile")
    service_links: Mapped[list[SpecialistService]] = relationship(
        back_populates="specialist",
        cascade="all, delete-orphan",
    )
    services: Mapped[list[Service]] = relationship(
        secondary="specialist_services",
        back_populates="specialists",
        viewonly=True,
    )
    appointments: Mapped[list[Appointment]] = relationship(back_populates="specialist")
    schedule_items: Mapped[list[DoctorSchedule]] = relationship(
        back_populates="specialist",
        cascade="all, delete-orphan",
    )


class SpecialistService(Base):
    __tablename__ = "specialist_services"

    specialist_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("specialists.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )

    specialist: Mapped[Specialist] = relationship(back_populates="service_links")
    service: Mapped[Service] = relationship(back_populates="specialist_links")


class Appointment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint(
            "specialist_id",
            "appointment_date",
            "appointment_time",
            name="uq_appointments_specialist_slot",
        ),
        Index("ix_appointments_patient_id", "patient_id"),
        Index("ix_appointments_specialist_date", "specialist_id", "appointment_date"),
        CheckConstraint(
            "patient_contact_status IN ('not_contacted', 'contacted', 'agreed', 'declined')",
            name="chk_appointments_patient_contact_status",
        ),
    )

    appointment_number: Mapped[str | None] = mapped_column(String(30), unique=True)
    patient_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    service_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("services.id"),
        nullable=False,
    )
    specialist_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("specialists.id"),
        nullable=False,
    )
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(nullable=False)
    requested_date: Mapped[date | None] = mapped_column(Date)
    requested_time: Mapped[time | None] = mapped_column()
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(
            AppointmentStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=AppointmentStatus.PENDING,
        server_default=AppointmentStatus.PENDING.value,
    )
    comment: Mapped[str | None] = mapped_column(Text)
    patient_contact_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AppointmentContactStatus.NOT_CONTACTED.value,
        server_default=AppointmentContactStatus.NOT_CONTACTED.value,
    )
    patient_contacted_at: Mapped[datetime | None] = mapped_column(DateTime)
    patient_contact_comment: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[User | None] = relationship(
        back_populates="appointments",
        foreign_keys=[patient_id],
    )
    service: Mapped[Service] = relationship(back_populates="appointments")
    specialist: Mapped[Specialist] = relationship(back_populates="appointments")
    recommendations: Mapped[list[Recommendation]] = relationship(
        back_populates="appointment",
    )
    status_history: Mapped[list[AppointmentStatusHistory]] = relationship(
        back_populates="appointment",
        order_by="AppointmentStatusHistory.created_at.desc()",
    )


class AppointmentStatusHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "appointment_status_history"
    __table_args__ = (
        Index("ix_appointment_status_history_appointment_id", "appointment_id"),
        Index("ix_appointment_status_history_admin_id", "admin_id"),
    )

    appointment_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
    )
    admin_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    previous_status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(
            AppointmentStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    new_status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(
            AppointmentStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    appointment: Mapped[Appointment] = relationship(back_populates="status_history")
    admin: Mapped[User | None] = relationship()


class DoctorSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "doctor_schedule"
    __table_args__ = (
        UniqueConstraint(
            "specialist_id",
            "schedule_date",
            "start_time",
            "end_time",
            name="uq_doctor_schedule_slot",
        ),
        CheckConstraint("start_time < end_time", name="chk_doctor_schedule_time"),
    )

    specialist_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("specialists.id", ondelete="CASCADE"),
        nullable=False,
    )
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    specialist: Mapped[Specialist] = relationship(back_populates="schedule_items")


class ProductCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_product_categories_slug"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_products_slug"),
        CheckConstraint("price >= 0", name="chk_products_price"),
        CheckConstraint("stock >= 0", name="chk_products_stock"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_title", "title"),
    )

    category_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("product_categories.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500))
    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0"),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("1"),
    )

    category: Mapped[ProductCategory] = relationship(back_populates="products")
    wishlist_items: Mapped[list[WishlistItem]] = relationship(back_populates="product")
    cart_items: Mapped[list[CartItem]] = relationship(back_populates="product")
    order_items: Mapped[list[OrderItem]] = relationship(back_populates="product")
    recommendation_links: Mapped[list[RecommendationProduct]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    recommendations: Mapped[list[Recommendation]] = relationship(
        secondary="recommendation_products",
        back_populates="products",
        viewonly=True,
    )


class WishlistItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_items_user_product"),
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    user: Mapped[User] = relationship(back_populates="wishlist_items")
    product: Mapped[Product] = relationship(back_populates="wishlist_items")


class CartItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_items_user_product"),
        CheckConstraint("quantity >= 1", name="chk_cart_items_quantity"),
        CheckConstraint("price >= 0", name="chk_cart_items_price"),
    )

    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        Computed("quantity * price", persisted=True),
    )

    user: Mapped[User] = relationship(back_populates="cart_items")
    product: Mapped[Product] = relationship(back_populates="cart_items")


class Order(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="chk_orders_total_price"),
        Index("ix_orders_user_id", "user_id"),
    )

    order_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    user_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(
            PaymentStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )
    order_status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(
            OrderStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=OrderStatus.CREATED,
        server_default=OrderStatus.CREATED.value,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(
            PaymentMethod,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=PaymentMethod.CARD_ONLINE,
        server_default=PaymentMethod.CARD_ONLINE.value,
    )
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        SQLEnum(
            DeliveryMethod,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=DeliveryMethod.COURIER,
        server_default=DeliveryMethod.COURIER.value,
    )
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list[Payment]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity >= 1", name="chk_order_items_quantity"),
        CheckConstraint("price >= 0", name="chk_order_items_price"),
        CheckConstraint("subtotal >= 0", name="chk_order_items_subtotal"),
    )

    order_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("products.id", ondelete="SET NULL"),
    )
    product_title: Mapped[str] = mapped_column(String(255), nullable=False)
    product_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product | None] = relationship(back_populates="order_items")


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("provider_payment_id", name="uq_payments_provider_payment_id"),
    )

    order_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    payment_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(
            PaymentStatus,
            values_callable=enum_values,
            native_enum=True,
            validate_strings=True,
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)

    order: Mapped[Order] = relationship(back_populates="payments")


class Recommendation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_patient_id", "patient_id"),
        Index("ix_recommendations_doctor_id", "doctor_id"),
    )

    patient_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("users.id"),
    )
    doctor_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("users.id"),
        nullable=False,
    )
    appointment_id: Mapped[str | None] = mapped_column(
        CHAR(36),
        ForeignKey("appointments.id", ondelete="SET NULL"),
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    patient: Mapped[User | None] = relationship(
        back_populates="patient_recommendations",
        foreign_keys=[patient_id],
    )
    doctor: Mapped[User] = relationship(
        back_populates="doctor_recommendations",
        foreign_keys=[doctor_id],
    )
    appointment: Mapped[Appointment | None] = relationship(
        back_populates="recommendations",
    )
    product_links: Mapped[list[RecommendationProduct]] = relationship(
        back_populates="recommendation",
        cascade="all, delete-orphan",
    )
    products: Mapped[list[Product]] = relationship(
        secondary="recommendation_products",
        back_populates="recommendations",
        viewonly=True,
    )


class RecommendationProduct(Base):
    __tablename__ = "recommendation_products"

    recommendation_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    product_id: Mapped[str] = mapped_column(
        CHAR(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
    )

    recommendation: Mapped[Recommendation] = relationship(back_populates="product_links")
    product: Mapped[Product] = relationship(back_populates="recommendation_links")
