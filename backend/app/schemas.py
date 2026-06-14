from __future__ import annotations

from datetime import date, datetime, time
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int


class User(BaseModel):
    id: str
    fullName: str
    phone: str
    email: Optional[str] = None
    role: str
    createdAt: Optional[datetime] = None


class ClinicInfo(BaseModel):
    id: str
    name: str
    description: str
    address: str
    phone: str
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None
    workingHours: str
    mapUrl: Optional[str] = None


UserRole = Literal["patient", "doctor", "admin"]
OrderStatus = Literal["created", "paid", "processing", "delivered", "cancelled"]
PaymentStatus = Literal["pending", "paid", "failed", "refunded"]
PaymentMethod = Literal["card_online", "cash_on_delivery"]
DeliveryMethod = Literal["courier", "pickup"]


class UserListResponse(BaseModel):
    items: list[User]
    meta: PaginationMeta


class CreateUserRequest(BaseModel):
    fullName: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    password: str = Field(min_length=8)
    role: UserRole = "patient"


class UpdateUserRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[UserRole] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class AdminUpdateUserRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class UpdateProfileRequest(BaseModel):
    fullName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, min_length=1, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


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


class RegisterRequest(BaseModel):
    fullName: str
    phone: str
    email: Optional[str] = None
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    phone: str
    password: str
    remember: bool = True


class AuthResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    user: User


class RefreshTokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int


class ServiceCategory(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str] = None
    imageUrl: Optional[str] = None
    sortOrder: int = 0


class CreateServiceCategoryRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    sortOrder: int = Field(default=0, ge=0)


class UpdateServiceCategoryRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    sortOrder: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Service(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    price: float = Field(ge=0)
    durationMinutes: Optional[int] = None
    category: ServiceCategory
    imageUrl: Optional[str] = None
    contraindications: Optional[str] = None


class ServiceListResponse(BaseModel):
    items: list[Service]
    meta: PaginationMeta


class AdminService(Service):
    isActive: bool


class AdminServiceListResponse(BaseModel):
    items: list[AdminService]
    meta: PaginationMeta


class CreateServiceRequest(BaseModel):
    categoryId: str
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    durationMinutes: Optional[int] = Field(default=None, gt=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    contraindications: Optional[str] = None
    isActive: bool = True


class UpdateServiceRequest(BaseModel):
    categoryId: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    durationMinutes: Optional[int] = Field(default=None, gt=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    contraindications: Optional[str] = None
    isActive: Optional[bool] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class ProductCategory(BaseModel):
    id: str
    title: str
    slug: str


class CreateProductCategoryRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)


class Product(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    price: float = Field(ge=0)
    imageUrl: Optional[str] = None
    stock: int = Field(ge=0)
    category: ProductCategory


class ProductListResponse(BaseModel):
    items: list[Product]
    meta: PaginationMeta


class AdminProduct(Product):
    isActive: bool
    createdAt: Optional[datetime] = None


class AdminProductListResponse(BaseModel):
    items: list[AdminProduct]
    meta: PaginationMeta


class CreateProductRequest(BaseModel):
    categoryId: str
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: float = Field(ge=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    stock: int = Field(ge=0)
    isActive: bool = True


class UpdateProductRequest(BaseModel):
    categoryId: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, ge=0)
    imageUrl: Optional[str] = Field(default=None, max_length=500)
    stock: Optional[int] = Field(default=None, ge=0)
    isActive: Optional[bool] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Specialist(BaseModel):
    id: str
    fullName: str
    position: str
    specialization: str
    experienceYears: Optional[int] = None
    photoUrl: Optional[str] = None
    serviceIds: list[str] = Field(default_factory=list)


class SpecialistListResponse(BaseModel):
    items: list[Specialist]
    meta: PaginationMeta


class AdminSpecialist(Specialist):
    userId: Optional[str] = None
    isActive: bool


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
    id: str
    specialist: Specialist
    date: str
    startTime: str
    endTime: str
    isAvailable: bool
    createdAt: datetime
    updatedAt: datetime


class DoctorScheduleListResponse(BaseModel):
    items: list[DoctorSchedule]
    meta: PaginationMeta


class DoctorScheduleItem(BaseModel):
    date: str
    startTime: str
    endTime: str
    isAvailable: bool


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


class AvailableSlot(BaseModel):
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
        date.fromisoformat(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        datetime.strptime(value, "%H:%M")
        return value

    @property
    def parsed_date(self) -> date:
        return date.fromisoformat(self.date)

    @property
    def parsed_time(self) -> time:
        return datetime.strptime(self.time, "%H:%M").time()


class AppointmentStatusHistoryItem(BaseModel):
    id: str
    adminId: Optional[str] = None
    adminName: Optional[str] = None
    previousStatus: str
    newStatus: str
    createdAt: datetime


class Appointment(BaseModel):
    id: str
    appointmentNumber: Optional[str] = None
    patientId: Optional[str] = None
    patientName: Optional[str] = None
    patientPhone: Optional[str] = None
    service: Service
    specialist: Specialist
    date: str
    time: str
    requestedDate: Optional[str] = None
    requestedTime: Optional[str] = None
    status: str
    comment: Optional[str] = None
    patientContactStatus: str = "not_contacted"
    patientContactedAt: Optional[datetime] = None
    patientContactComment: Optional[str] = None
    statusHistory: list[AppointmentStatusHistoryItem] = []
    createdAt: Optional[datetime] = None


class AppointmentListResponse(BaseModel):
    items: list[Appointment]
    meta: PaginationMeta


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
        date.fromisoformat(value)
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        datetime.strptime(value, "%H:%M")
        return value

    @property
    def parsed_date(self) -> date:
        return date.fromisoformat(self.date)

    @property
    def parsed_time(self) -> time:
        return datetime.strptime(self.time, "%H:%M").time()


class UpdateAppointmentContactRequest(BaseModel):
    patientContactStatus: Literal["not_contacted", "contacted", "agreed", "declined"]
    patientContactComment: Optional[str] = None


class WishlistItem(BaseModel):
    id: str
    product: Product
    createdAt: Optional[datetime] = None


class AddWishlistItemRequest(BaseModel):
    productId: str


class CartItem(BaseModel):
    id: str
    product: Product
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    subtotal: float = Field(ge=0)


class Cart(BaseModel):
    items: list[CartItem]
    totalPrice: float = Field(ge=0)


class AddCartItemRequest(BaseModel):
    productId: str
    quantity: int = Field(ge=1)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(ge=1)


class CreateOrderRequest(BaseModel):
    paymentMethod: PaymentMethod
    deliveryMethod: DeliveryMethod
    deliveryAddress: str = Field(min_length=1, max_length=500)
    recipientName: str = Field(min_length=1, max_length=255)
    recipientPhone: str = Field(min_length=1, max_length=20)
    comment: Optional[str] = None


class AdminCreateOrderItem(BaseModel):
    productId: str = Field(min_length=1)
    quantity: int = Field(ge=1)


class AdminCreateOrderRequest(BaseModel):
    userId: str = Field(min_length=1)
    items: list[AdminCreateOrderItem] = Field(min_length=1)
    paymentMethod: PaymentMethod
    deliveryMethod: DeliveryMethod
    deliveryAddress: str = Field(min_length=1, max_length=500)
    recipientName: str = Field(min_length=1, max_length=255)
    recipientPhone: str = Field(min_length=1, max_length=20)
    comment: Optional[str] = None


class OrderItem(BaseModel):
    product: Product
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)
    subtotal: float = Field(ge=0)


class Payment(BaseModel):
    id: str
    paymentUrl: str
    providerPaymentId: Optional[str] = None
    status: PaymentStatus
    expiresAt: Optional[datetime] = None
    createdAt: datetime


class Order(BaseModel):
    id: str
    orderNumber: str
    userId: Optional[str] = None
    items: list[OrderItem]
    totalPrice: float = Field(ge=0)
    paymentStatus: PaymentStatus
    orderStatus: OrderStatus
    paymentMethod: PaymentMethod
    deliveryMethod: DeliveryMethod
    deliveryAddress: Optional[str] = None
    recipientName: Optional[str] = None
    recipientPhone: Optional[str] = None
    createdAt: Optional[datetime] = None


class OrderListResponse(BaseModel):
    items: list[Order]
    meta: PaginationMeta


class UpdateOrderStatusRequest(BaseModel):
    orderStatus: OrderStatus


class PaymentCreateResponse(BaseModel):
    paymentId: str
    paymentUrl: str
    expiresAt: datetime


class Review(BaseModel):
    id: str
    authorName: str
    rating: int = Field(ge=1, le=5)
    text: str
    source: str
    sourceUrl: Optional[str] = None
    isPublished: bool
    sortOrder: int = Field(ge=0)
    publishedAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


class ReviewListResponse(BaseModel):
    items: list[Review]
    meta: PaginationMeta


class CreateReviewRequest(BaseModel):
    authorName: str = Field(min_length=1, max_length=255)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=1)
    source: str = Field(default="2gis", min_length=1, max_length=50)
    sourceUrl: Optional[str] = Field(default=None, max_length=1000)
    isPublished: bool = True
    sortOrder: int = Field(default=0, ge=0)
    publishedAt: Optional[datetime] = None


class UpdateReviewRequest(BaseModel):
    authorName: Optional[str] = Field(default=None, min_length=1, max_length=255)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    text: Optional[str] = Field(default=None, min_length=1)
    source: Optional[str] = Field(default=None, min_length=1, max_length=50)
    sourceUrl: Optional[str] = Field(default=None, max_length=1000)
    isPublished: Optional[bool] = None
    sortOrder: Optional[int] = Field(default=None, ge=0)
    publishedAt: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class Recommendation(BaseModel):
    id: str
    patientId: Optional[str] = None
    patientName: Optional[str] = None
    patientPhone: Optional[str] = None
    doctorId: str
    appointmentId: Optional[str] = None
    text: str
    productIds: list[str] = Field(default_factory=list)
    createdAt: datetime


class RecommendationListResponse(BaseModel):
    items: list[Recommendation]
    meta: PaginationMeta


class CreateRecommendationRequest(BaseModel):
    patientId: Optional[str] = None
    appointmentId: Optional[str] = None
    text: str = Field(min_length=1)
    productIds: list[str] = Field(default_factory=list)


class AdminCreateRecommendationRequest(CreateRecommendationRequest):
    doctorId: str


class UpdateRecommendationRequest(BaseModel):
    patientId: Optional[str] = None
    doctorId: Optional[str] = None
    appointmentId: Optional[str] = None
    text: Optional[str] = Field(default=None, min_length=1)
    productIds: Optional[list[str]] = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class AdminSettingsResponse(BaseModel):
    settings: dict[str, Any]


class UpdateAdminSettingsRequest(BaseModel):
    settings: dict[str, Any]
