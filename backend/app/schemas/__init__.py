from __future__ import annotations

from app.schemas.base import PaginationMeta

from app.schemas.users import (
    AdminUpdateUserRequest,
    CreateUserRequest,
    UpdateProfileRequest,
    UpdateUserRequest,
    User,
    UserListResponse,
    UserRole,
)

from app.schemas.clinic import (
    ClinicInfo,
    UpdateClinicInfoRequest,
)

from app.schemas.services import (
    AdminService,
    AdminServiceListResponse,
    CreateServiceCategoryRequest,
    CreateServiceRequest,
    Service,
    ServiceCategory,
    ServiceListResponse,
    UpdateServiceCategoryRequest,
    UpdateServiceRequest,
)

from app.schemas.products import (
    AdminProduct,
    AdminProductListResponse,
    CreateProductCategoryRequest,
    CreateProductRequest,
    Product,
    ProductCategory,
    ProductListResponse,
    UpdateProductCategoryRequest,
    UpdateProductRequest,
)

from app.schemas.specialists import (
    AdminSpecialist,
    AdminSpecialistListResponse,
    CreateSpecialistRequest,
    CreateDoctorScheduleRequest,
    DoctorSchedule,
    DoctorScheduleItem,
    DoctorScheduleListResponse,
    Specialist,
    SpecialistListResponse,
    UpdateDoctorScheduleRequest,
    UpdateSpecialistRequest,
)

from app.schemas.appointments import (
    Appointment,
    AppointmentListResponse,
    AppointmentStatusHistoryItem,
    BookAppointmentRequest,
    CreateAppointmentRequest,
    AvailableSlot,
    PendingCountResponse,
    RescheduleAppointmentRequest,
    UpdateAppointmentContactRequest,
    UpdateAppointmentStatusRequest,
)

from app.schemas.wishlist import (
    AddWishlistItemRequest,
    WishlistItem,
)

from app.schemas.cart import (
    AddCartItemRequest,
    Cart,
    CartItem,
    UpdateCartItemRequest,
)

from app.schemas.orders import (
    AdminCreateOrderItem,
    AdminCreateOrderRequest,
    CreateOrderRequest,
    DeliveryMethod,
    Order,
    OrderItem,
    OrderListResponse,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    UpdateOrderStatusRequest,
)

from app.schemas.payments import (
    Payment,
    PaymentCreateResponse,
)

from app.schemas.reviews import (
    CreateReviewRequest,
    Review,
    ReviewListResponse,
    UpdateReviewRequest,
)

from app.schemas.recommendations import (
    AdminCreateRecommendationRequest,
    CreateRecommendationRequest,
    Recommendation,
    RecommendationListResponse,
    UpdateRecommendationRequest,
)

from app.schemas.analytics import (
    SalesAnalyticsResponse,
    SalesPeriodPoint,
    ServicesAnalyticsResponse,
    TopProductPoint,
)

from app.schemas.admin_settings import (
    AdminSettingsResponse,
    UpdateAdminSettingsRequest,
)

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenResponse,
    RegisterRequest,
    SpecialistProfile,
)
