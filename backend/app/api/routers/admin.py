import csv
import io
import os
import time
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import repositories
from app.api.deps import require_admin
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models import User as UserModel
from app.schemas import (
    AdminCreateOrderRequest,
    AdminProduct,
    AdminProductListResponse,
    AdminSettingsResponse,
    AdminUpdateUserRequest,
    AdminService,
    AdminServiceListResponse,
    AdminSpecialist,
    AdminSpecialistListResponse,
    AdminCreateRecommendationRequest,
    Appointment,
    AppointmentListResponse,
    ClinicInfo,
    CreateDoctorScheduleRequest,
    CreateProductCategoryRequest,
    CreateProductRequest,
    CreateReviewRequest,
    CreateServiceCategoryRequest,
    CreateServiceRequest,
    CreateSpecialistRequest,
    CreateUserRequest,
    DoctorSchedule,
    DoctorScheduleListResponse,
    Order,
    OrderListResponse,
    OrderStatus,
    PaymentStatus,
    ProductCategory,
    Recommendation,
    RecommendationListResponse,
    RescheduleAppointmentRequest,
    Review,
    ReviewListResponse,
    ServiceCategory,
    UpdateAppointmentStatusRequest,
    UpdateAppointmentContactRequest,
    UpdateClinicInfoRequest,
    UpdateDoctorScheduleRequest,
    UpdateOrderStatusRequest,
    UpdateAdminSettingsRequest,
    UpdateProductRequest,
    UpdateRecommendationRequest,
    UpdateReviewRequest,
    UpdateServiceCategoryRequest,
    UpdateServiceRequest,
    UpdateSpecialistRequest,
    User as UserSchema,
    UserListResponse,
    UserRole,
)
from app.serializers import (
    admin_product_to_api,
    admin_service_to_api,
    admin_specialist_to_api,
    appointment_to_api,
    clinic_info_to_api,
    doctor_schedule_to_api,
    order_to_api,
    product_category_to_api,
    recommendation_to_api,
    review_to_api,
    service_category_to_api,
    user_to_api,
)

AppointmentStatusFilter = Literal["pending", "confirmed", "completed", "cancelled"]

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.patch("/clinic-info", response_model=ClinicInfo)
def update_admin_clinic_info(
    payload: UpdateClinicInfoRequest,
    db: Session = Depends(get_db),
) -> dict:
    info = repositories.update_clinic_info(db, payload)
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic info not found",
        )

    return clinic_info_to_api(info)


@router.get("/settings", response_model=AdminSettingsResponse)
def get_admin_settings(db: Session = Depends(get_db)) -> dict:
    return {"settings": repositories.get_settings_map(db)}


@router.put("/settings", response_model=AdminSettingsResponse)
def update_admin_settings(
    payload: UpdateAdminSettingsRequest,
    db: Session = Depends(get_db),
) -> dict:
    return {"settings": repositories.replace_settings(db, payload.settings)}


LICENSE_DIR = Path("uploads/legal")
LICENSE_FILENAME = "license.pdf"
LICENSE_MAX_BYTES = 10 * 1024 * 1024  # 10 МБ — достаточно для скана лицензии
LICENSE_SETTING_KEY = "licenseFileUrl"


@router.post("/settings/license", response_model=AdminSettingsResponse)
async def upload_license_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    """Загружает PDF лицензии медцентра. Старый файл перезаписывается."""
    if (file.content_type or "").lower() != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допускаются только PDF-файлы",
        )

    contents = await file.read()
    if len(contents) > LICENSE_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл больше {LICENSE_MAX_BYTES // (1024 * 1024)} МБ",
        )
    # %PDF в первых байтах — отсекаем подделку content-type без чтения всего файла.
    if not contents.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не является корректным PDF",
        )

    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    (LICENSE_DIR / LICENSE_FILENAME).write_bytes(contents)

    # ?v=<ts> ломает кэш браузера, чтобы после замены файла открылся свежий
    public_url = f"/uploads/legal/{LICENSE_FILENAME}?v={int(time.time())}"
    repositories.upsert_setting(db, LICENSE_SETTING_KEY, public_url)
    return {"settings": repositories.get_settings_map(db)}


IMAGE_UPLOAD_FOLDERS = {"services", "categories", "products", "specialists"}
IMAGE_MAX_BYTES = 5 * 1024 * 1024  # 5 МБ — достаточно для миниатюр карточек

_CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def _sanitize_image_basename(original: str) -> str:
    import re
    # Берём только имя файла, без пути
    name = (original or "").rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    # Срезаем расширение — поставим своё (по реальному типу)
    if "." in name:
        name = name.rsplit(".", 1)[0]
    name = name.lower()
    # Транслитерируем кириллицу
    name = "".join(_CYRILLIC_TO_LATIN.get(ch, ch) for ch in name)
    # Оставляем только безопасные для URL/FS символы
    name = re.sub(r"[^a-z0-9_-]+", "-", name).strip("-")
    return name


def _unique_filename(target_dir: Path, basename: str, ext: str) -> str:
    candidate = f"{basename}.{ext}"
    if not (target_dir / candidate).exists():
        return candidate
    i = 1
    while True:
        candidate = f"{basename}-{i}.{ext}"
        if not (target_dir / candidate).exists():
            return candidate
        i += 1

# Magic bytes для отсечения подделок content-type
_IMAGE_MAGIC = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"RIFF", "webp"),  # webp начинается с RIFF...WEBP
)


def _detect_image_extension(payload: bytes, content_type: str) -> str | None:
    for magic, ext in _IMAGE_MAGIC:
        if payload.startswith(magic):
            if ext == "webp" and b"WEBP" not in payload[:16]:
                continue
            return ext
    ct = (content_type or "").lower()
    if ct == "image/jpeg":
        return "jpg"
    if ct == "image/png":
        return "png"
    if ct == "image/webp":
        return "webp"
    return None


@router.post("/uploads/image")
async def upload_admin_image(
    folder: str = Query(...),
    file: UploadFile = File(...),
) -> dict:
    """Загружает картинку в uploads/{folder}/, возвращает публичный URL."""
    if folder not in IMAGE_UPLOAD_FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Папка должна быть одной из: {sorted(IMAGE_UPLOAD_FOLDERS)}",
        )

    contents = await file.read()
    if len(contents) > IMAGE_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл больше {IMAGE_MAX_BYTES // (1024 * 1024)} МБ",
        )

    ext = _detect_image_extension(contents, file.content_type or "")
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поддерживаются только JPG, PNG и WebP",
        )

    target_dir = Path("uploads") / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    basename = _sanitize_image_basename(file.filename or "")
    if not basename:
        import uuid
        basename = uuid.uuid4().hex
    filename = _unique_filename(target_dir, basename, ext)
    (target_dir / filename).write_bytes(contents)

    return {"url": f"/uploads/{folder}/{filename}"}


@router.delete("/settings/license", response_model=AdminSettingsResponse)
def delete_license_pdf(db: Session = Depends(get_db)) -> dict:
    """Удаляет PDF лицензии и стирает соответствующую настройку."""
    file_path = LICENSE_DIR / LICENSE_FILENAME
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    repositories.upsert_setting(db, LICENSE_SETTING_KEY, None)
    return {"settings": repositories.get_settings_map(db)}


@router.get("/users", response_model=UserListResponse)
def get_admin_users(
    search: str | None = None,
    role: UserRole | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    users, meta = repositories.list_admin_users(db, search, role, page, limit)
    return {
        "items": [user_to_api(user) for user in users],
        "meta": meta,
    }


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
) -> dict:
    if repositories.get_user_by_phone(db, payload.phone) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone already exists",
        )

    if payload.email and repositories.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    try:
        user = repositories.create_admin_user(db, payload, get_password_hash(payload.password))
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this data already exists",
        ) from exc

    return user_to_api(user)


@router.get("/users/{id}", response_model=UserSchema)
def get_admin_user(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    user = repositories.get_user(db, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user_to_api(user)


@router.patch("/users/{id}", response_model=UserSchema)
def update_admin_user(
    id: str,
    payload: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.phone:
        existing_user = repositories.get_user_by_phone(db, payload.phone)
        if existing_user is not None and existing_user.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone already exists",
            )

    if payload.email:
        existing_user = repositories.get_user_by_email(db, payload.email)
        if existing_user is not None and existing_user.id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    try:
        password_hash = get_password_hash(payload.password) if payload.password else None
        user = repositories.update_admin_user(db, id, payload, password_hash)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this data already exists",
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user_to_api(user)


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user(
    id: str,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    if id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current admin user cannot be deleted",
        )

    try:
        deleted = repositories.delete_admin_user(db, id)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User has related records and cannot be deleted",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/specialists", response_model=AdminSpecialistListResponse)
def get_admin_specialists(
    search: str | None = None,
    serviceId: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    specialists, meta = repositories.list_admin_specialists(db, search, serviceId, isActive, page, limit)
    return {
        "items": [admin_specialist_to_api(specialist) for specialist in specialists],
        "meta": meta,
    }


@router.post("/specialists", response_model=AdminSpecialist, status_code=status.HTTP_201_CREATED)
def create_admin_specialist(
    payload: CreateSpecialistRequest,
    db: Session = Depends(get_db),
) -> dict:
    _validate_specialist_user(db, payload.userId)
    _validate_service_ids(db, payload.serviceIds)

    try:
        specialist = repositories.create_admin_specialist(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialist with this data already exists",
        ) from exc

    return admin_specialist_to_api(specialist)


@router.get("/specialists/{id}", response_model=AdminSpecialist)
def get_admin_specialist(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    specialist = repositories.get_admin_specialist(db, id)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found",
        )

    return admin_specialist_to_api(specialist)


@router.patch("/specialists/{id}", response_model=AdminSpecialist)
def update_admin_specialist(
    id: str,
    payload: UpdateSpecialistRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "userId" in payload.model_fields_set:
        _validate_specialist_user(db, payload.userId)
    if "serviceIds" in payload.model_fields_set and payload.serviceIds is not None:
        _validate_service_ids(db, payload.serviceIds)

    try:
        specialist = repositories.update_admin_specialist(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialist with this data already exists",
        ) from exc

    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found",
        )

    return admin_specialist_to_api(specialist)


@router.delete("/specialists/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_specialist(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.deactivate_admin_specialist(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/specialists/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_specialist(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    result = repositories.delete_admin_specialist(db, id)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found",
        )
    if result == "has_appointments":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Невозможно удалить специалиста: на него есть записи на приём. Сначала скройте его.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/doctor-schedule", response_model=DoctorScheduleListResponse)
def get_admin_doctor_schedule(
    specialistId: str | None = None,
    scheduleDate: str | None = Query(default=None, alias="date"),
    isAvailable: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    parsed_date = _parse_schedule_date_filter(scheduleDate)
    schedule_items, meta = repositories.list_admin_doctor_schedule(
        db,
        specialistId,
        parsed_date,
        isAvailable,
        page,
        limit,
    )
    return {
        "items": [doctor_schedule_to_api(schedule_item) for schedule_item in schedule_items],
        "meta": meta,
    }


@router.post("/doctor-schedule", response_model=DoctorSchedule, status_code=status.HTTP_201_CREATED)
def create_admin_doctor_schedule_item(
    payload: CreateDoctorScheduleRequest,
    db: Session = Depends(get_db),
) -> dict:
    _validate_schedule_specialist(db, payload.specialistId)

    try:
        schedule_item = repositories.create_admin_doctor_schedule_item(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor schedule slot with this data already exists",
        ) from exc

    return doctor_schedule_to_api(schedule_item)


@router.get("/doctor-schedule/{id}", response_model=DoctorSchedule)
def get_admin_doctor_schedule_item(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    schedule_item = repositories.get_admin_doctor_schedule_item(db, id)
    if schedule_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule slot not found",
        )

    return doctor_schedule_to_api(schedule_item)


@router.patch("/doctor-schedule/{id}", response_model=DoctorSchedule)
def update_admin_doctor_schedule_item(
    id: str,
    payload: UpdateDoctorScheduleRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "specialistId" in payload.model_fields_set and payload.specialistId is not None:
        _validate_schedule_specialist(db, payload.specialistId)

    try:
        schedule_item = repositories.update_admin_doctor_schedule_item(db, id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor schedule slot with this data already exists",
        ) from exc

    if schedule_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule slot not found",
        )

    return doctor_schedule_to_api(schedule_item)


@router.delete("/doctor-schedule/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_doctor_schedule_item(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.deactivate_admin_doctor_schedule_item(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule slot not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/doctor-schedule/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_doctor_schedule_item(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.delete_admin_doctor_schedule_item(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor schedule slot not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_admin_order(
    payload: AdminCreateOrderRequest,
    db: Session = Depends(get_db),
) -> dict:
    if repositories.get_user(db, payload.userId) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    for item in payload.items:
        product = repositories.get_product(db, item.productId)
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product not found or inactive",
            )

    order = repositories.create_admin_order(db, payload)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create order",
        )

    return order_to_api(order)


@router.get("/orders", response_model=OrderListResponse)
def get_admin_orders(
    orderStatus: OrderStatus | None = None,
    paymentStatus: PaymentStatus | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    orders, meta = repositories.list_admin_orders(db, orderStatus, paymentStatus, search, page, limit)
    return {
        "items": [order_to_api(order) for order in orders],
        "meta": meta,
    }


@router.get("/orders/{id}", response_model=Order)
def get_admin_order(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    order = repositories.get_admin_order(db, id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_to_api(order)


@router.patch("/orders/{id}", response_model=Order)
@router.patch("/orders/{id}/status", response_model=Order)
def update_admin_order_status(
    id: str,
    payload: UpdateOrderStatusRequest,
    db: Session = Depends(get_db),
) -> dict:
    order = repositories.update_admin_order_status(db, id, payload)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order_to_api(order)


@router.get("/reviews", response_model=ReviewListResponse)
def get_admin_reviews(
    search: str | None = None,
    isPublished: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    reviews, meta = repositories.list_admin_reviews(db, search, isPublished, page, limit)
    return {
        "items": [review_to_api(review) for review in reviews],
        "meta": meta,
    }


@router.post("/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_admin_review(
    payload: CreateReviewRequest,
    db: Session = Depends(get_db),
) -> dict:
    review = repositories.create_admin_review(db, payload)
    return review_to_api(review)


@router.get("/reviews/{id}", response_model=Review)
def get_admin_review(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    review = repositories.get_admin_review(db, id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review_to_api(review)


@router.patch("/reviews/{id}", response_model=Review)
def update_admin_review(
    id: str,
    payload: UpdateReviewRequest,
    db: Session = Depends(get_db),
) -> dict:
    review = repositories.update_admin_review(db, id, payload)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review_to_api(review)


@router.delete("/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_review(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.delete_admin_review(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/recommendations", response_model=RecommendationListResponse)
def get_admin_recommendations(
    patientId: str | None = None,
    doctorId: str | None = None,
    appointmentId: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    recommendations, meta = repositories.list_admin_recommendations(
        db,
        patientId,
        doctorId,
        appointmentId,
        search,
        page,
        limit,
    )
    return {
        "items": [recommendation_to_api(recommendation) for recommendation in recommendations],
        "meta": meta,
    }


@router.post("/recommendations", response_model=Recommendation, status_code=status.HTTP_201_CREATED)
def create_admin_recommendation(
    payload: AdminCreateRecommendationRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.patientId is not None:
        _validate_recommendation_user(db, payload.patientId, "patient", "Patient not found")
    _validate_recommendation_user(db, payload.doctorId, "doctor", "Doctor not found")
    _validate_recommendation_appointment(db, payload.appointmentId)
    _validate_recommendation_product_ids(db, payload.productIds)

    try:
        recommendation = repositories.create_admin_recommendation(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation with this data cannot be created",
        ) from exc

    return recommendation_to_api(recommendation)


@router.get("/recommendations/{id}", response_model=Recommendation)
def get_admin_recommendation(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    recommendation = repositories.get_admin_recommendation(db, id)
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation_to_api(recommendation)


@router.patch("/recommendations/{id}", response_model=Recommendation)
def update_admin_recommendation(
    id: str,
    payload: UpdateRecommendationRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "patientId" in payload.model_fields_set and payload.patientId is not None:
        _validate_recommendation_user(db, payload.patientId, "patient", "Patient not found")
    if "doctorId" in payload.model_fields_set and payload.doctorId is not None:
        _validate_recommendation_user(db, payload.doctorId, "doctor", "Doctor not found")
    if "appointmentId" in payload.model_fields_set:
        _validate_recommendation_appointment(db, payload.appointmentId)
    if "productIds" in payload.model_fields_set and payload.productIds is not None:
        _validate_recommendation_product_ids(db, payload.productIds)

    try:
        recommendation = repositories.update_admin_recommendation(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation with this data cannot be updated",
        ) from exc

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return recommendation_to_api(recommendation)


@router.delete("/recommendations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_recommendation(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.delete_admin_recommendation(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/product-categories", response_model=list[ProductCategory])
def get_admin_product_categories(db: Session = Depends(get_db)) -> list[dict]:
    categories = repositories.list_product_categories(db)
    return [product_category_to_api(category) for category in categories]


@router.post(
    "/product-categories",
    response_model=ProductCategory,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_product_category(
    payload: CreateProductCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        category = repositories.create_product_category(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product category with this slug already exists",
        ) from exc

    return product_category_to_api(category)


@router.get("/products", response_model=AdminProductListResponse)
def get_admin_products(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    products, meta = repositories.list_admin_products(db, search, categorySlug, isActive, page, limit)
    return {
        "items": [admin_product_to_api(product) for product in products],
        "meta": meta,
    }


@router.post("/products", response_model=AdminProduct, status_code=status.HTTP_201_CREATED)
def create_admin_product(
    payload: CreateProductRequest,
    db: Session = Depends(get_db),
) -> dict:
    _validate_product_category(db, payload.categoryId)

    try:
        product = repositories.create_admin_product(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this slug or data already exists",
        ) from exc

    return admin_product_to_api(product)


@router.get("/products/{id}", response_model=AdminProduct)
def get_admin_product(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    product = repositories.get_admin_product(db, id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return admin_product_to_api(product)


@router.patch("/products/{id}", response_model=AdminProduct)
def update_admin_product(
    id: str,
    payload: UpdateProductRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "categoryId" in payload.model_fields_set:
        _validate_product_category(db, payload.categoryId)

    try:
        product = repositories.update_admin_product(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this slug or data already exists",
        ) from exc

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return admin_product_to_api(product)


@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_product(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.deactivate_admin_product(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/products/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_product(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    result = repositories.delete_admin_product(db, id)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    if result == "has_carts":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Невозможно удалить товар: он находится в корзине у пользователей. Сначала скройте его.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/service-categories", response_model=list[ServiceCategory])
def get_admin_service_categories(db: Session = Depends(get_db)) -> list[dict]:
    categories = repositories.list_service_categories(db)
    return [service_category_to_api(category) for category in categories]


@router.post(
    "/service-categories",
    response_model=ServiceCategory,
    status_code=status.HTTP_201_CREATED,
)
def create_admin_service_category(
    payload: CreateServiceCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        category = repositories.create_service_category(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service category with this slug already exists",
        ) from exc

    return service_category_to_api(category)


@router.patch("/service-categories/{id}", response_model=ServiceCategory)
def update_admin_service_category(
    id: str,
    payload: UpdateServiceCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        category = repositories.update_service_category(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service category with this slug already exists",
        ) from exc

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found",
        )

    return service_category_to_api(category)


@router.delete("/service-categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_service_category(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    result = repositories.delete_service_category(db, id)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service category not found",
        )
    if result == "has_services":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала удалите или перенесите услуги этой категории",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/services", response_model=AdminServiceListResponse)
def get_admin_services(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    services, meta = repositories.list_admin_services(db, search, categorySlug, isActive, page, limit)
    return {
        "items": [admin_service_to_api(service) for service in services],
        "meta": meta,
    }


@router.post("/services", response_model=AdminService, status_code=status.HTTP_201_CREATED)
def create_admin_service(
    payload: CreateServiceRequest,
    db: Session = Depends(get_db),
) -> dict:
    if repositories.get_service_category(db, payload.categoryId) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service category not found",
        )

    try:
        service = repositories.create_admin_service(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service with this slug or data already exists",
        ) from exc

    return admin_service_to_api(service)


@router.get("/services/{id}", response_model=AdminService)
def get_admin_service(
    id: str,
    db: Session = Depends(get_db),
) -> dict:
    service = repositories.get_admin_service(db, id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return admin_service_to_api(service)


@router.patch("/services/{id}", response_model=AdminService)
def update_admin_service(
    id: str,
    payload: UpdateServiceRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.categoryId and repositories.get_service_category(db, payload.categoryId) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service category not found",
        )

    try:
        service = repositories.update_admin_service(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service with this slug or data already exists",
        ) from exc

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return admin_service_to_api(service)


@router.delete("/services/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_service(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    if not repositories.deactivate_admin_service(db, id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/services/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_service(
    id: str,
    db: Session = Depends(get_db),
) -> Response:
    result = repositories.delete_admin_service(db, id)
    if result == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )
    if result == "has_appointments":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Невозможно удалить услугу: на неё есть записи на приём. Сначала скройте её.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/appointments", response_model=AppointmentListResponse)
def get_admin_appointments(
    statusFilter: AppointmentStatusFilter | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    appointments, meta = repositories.list_admin_appointments(db, statusFilter, page, limit)
    return {
        "items": [appointment_to_api(appointment) for appointment in appointments],
        "meta": meta,
    }


@router.patch("/appointments/{id}", response_model=Appointment)
def update_appointment_status(
    id: str,
    payload: UpdateAppointmentStatusRequest,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    existing_appointment = repositories.get_appointment(db, id)
    if existing_appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )

    next_status = payload.status
    if not repositories.is_appointment_status_transition_allowed(existing_appointment.status, next_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Недопустимый переход статуса: "
                f"{existing_appointment.status.value} -> {next_status}"
            ),
        )

    appointment = repositories.update_appointment_status(db, id, payload.status, current_user.id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )

    return appointment_to_api(appointment)


@router.patch("/appointments/{id}/reschedule", response_model=Appointment)
def reschedule_appointment(
    id: str,
    payload: RescheduleAppointmentRequest,
    db: Session = Depends(get_db),
) -> dict:
    appointment = repositories.get_appointment(db, id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )

    specialist = repositories.get_specialist(db, payload.specialistId)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не найден",
        )

    if appointment.service_id not in {service.id for service in specialist.services}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не оказывает услугу этой записи",
        )

    if not repositories.is_appointment_slot_available(
        db,
        payload.specialistId,
        appointment.service,
        payload.parsed_date,
        payload.parsed_time,
        exclude_appointment_id=id,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранное время недоступно",
        )

    try:
        updated = repositories.reschedule_appointment(db, id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранное время уже занято",
        ) from exc

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )
    return appointment_to_api(updated)


@router.patch("/appointments/{id}/contact", response_model=Appointment)
def update_appointment_contact(
    id: str,
    payload: UpdateAppointmentContactRequest,
    db: Session = Depends(get_db),
) -> dict:
    appointment = repositories.update_appointment_contact(db, id, payload)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена",
        )

    return appointment_to_api(appointment)


def _validate_specialist_user(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return

    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialist user not found",
        )

    if user.role.value != "doctor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialist user must have doctor role",
        )


def _validate_service_ids(db: Session, service_ids: list[str]) -> None:
    unique_service_ids = list(dict.fromkeys(service_ids))
    services = repositories.list_services_by_ids(db, unique_service_ids)
    found_service_ids = {service.id for service in services}
    missing_service_ids = [service_id for service_id in unique_service_ids if service_id not in found_service_ids]

    if missing_service_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Some services were not found", "serviceIds": missing_service_ids},
        )


def _validate_schedule_specialist(db: Session, specialist_id: str) -> None:
    if repositories.get_admin_specialist(db, specialist_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specialist not found",
        )


def _parse_schedule_date_filter(value: str | None) -> date | None:
    if value is None:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date must be in YYYY-MM-DD format",
        ) from exc


def _validate_recommendation_user(
    db: Session,
    user_id: str,
    expected_role: str,
    not_found_detail: str,
) -> None:
    user = repositories.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=not_found_detail,
        )

    if user.role.value != expected_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must have {expected_role} role",
        )


def _validate_recommendation_appointment(db: Session, appointment_id: str | None) -> None:
    if appointment_id is None:
        return

    if repositories.get_appointment(db, appointment_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment not found",
        )


def _validate_recommendation_product_ids(db: Session, product_ids: list[str]) -> None:
    unique_product_ids = list(dict.fromkeys(product_ids))
    products = repositories.list_products_by_ids(db, unique_product_ids)
    found_product_ids = {product.id for product in products}
    missing_product_ids = [product_id for product_id in unique_product_ids if product_id not in found_product_ids]

    if missing_product_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Some products were not found", "productIds": missing_product_ids},
        )


def _validate_product_category(db: Session, category_id: str | None) -> None:
    if category_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product category is required",
        )

    if repositories.get_product_category(db, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product category not found",
        )


ORDER_STATUS_LABELS_RU = {
    "created": "Создан",
    "paid": "Оплачен",
    "processing": "В обработке",
    "delivered": "Доставлен",
    "cancelled": "Отменён",
}
PAYMENT_STATUS_LABELS_RU = {
    "pending": "Ожидает",
    "paid": "Оплачено",
    "failed": "Ошибка",
    "refunded": "Возврат",
}


def _csv_response(filename: str, header: list[str], rows: list[list]) -> StreamingResponse:
    buf = io.StringIO()
    buf.write("﻿")  # UTF-8 BOM so Excel recognises encoding on Windows
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _format_money_for_excel(value) -> str:
    return f"{float(value):.2f}".replace(".", ",")


@router.get("/exports/products.csv")
def export_admin_products(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    products = repositories.list_admin_products_all(db, search, categorySlug, isActive)
    header = ["Название", "Slug", "Категория", "Цена", "Остаток", "Статус", "Описание"]
    rows = [
        [
            p.title,
            p.slug,
            p.category.title if p.category else "",
            _format_money_for_excel(p.price),
            p.stock,
            "Активен" if p.is_active else "Скрыт",
            p.description or "",
        ]
        for p in products
    ]
    return _csv_response("products.csv", header, rows)


@router.get("/exports/orders.csv")
def export_admin_orders(
    orderStatus: OrderStatus | None = None,
    paymentStatus: PaymentStatus | None = None,
    search: str | None = None,
    dateFrom: date | None = None,
    dateTo: date | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    orders = repositories.list_admin_orders_all(
        db, orderStatus, paymentStatus, search, dateFrom, dateTo,
    )
    header = [
        "Номер", "Дата", "Клиент", "Телефон клиента",
        "Получатель", "Телефон получателя", "Адрес",
        "Статус заказа", "Статус оплаты", "Сумма", "Позиций", "Комментарий",
    ]
    rows = []
    for o in orders:
        created = o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else ""
        order_status_value = o.order_status.value if o.order_status else ""
        payment_status_value = o.payment_status.value if o.payment_status else ""
        rows.append([
            o.order_number or "",
            created,
            o.user.full_name if o.user else "",
            o.user.phone if o.user else "",
            o.recipient_name or "",
            o.recipient_phone or "",
            o.delivery_address or "",
            ORDER_STATUS_LABELS_RU.get(order_status_value, order_status_value),
            PAYMENT_STATUS_LABELS_RU.get(payment_status_value, payment_status_value),
            _format_money_for_excel(o.total_price),
            len(o.items or []),
            o.comment or "",
        ])
    return _csv_response("orders.csv", header, rows)
