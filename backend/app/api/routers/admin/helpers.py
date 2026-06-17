from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.errors import raise_bad_request
from app.services import users as users_service
from app.services import services as services_service
from app.services import specialists as specialists_service
from app.services import products as products_service
from app.services import appointments as appointments_service

_CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

_IMAGE_MAGIC = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"RIFF", "webp"),
)

IMAGE_UPLOAD_FOLDERS = {"services", "categories", "products", "specialists"}
IMAGE_MAX_BYTES = 5 * 1024 * 1024


def validate_specialist_user(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return
    user = users_service.get_user(db, user_id)
    if user is None:
        raise_bad_request("Пользователь для специалиста не найден")
    if user.role.value != "doctor":
        raise_bad_request("Пользователь должен иметь роль врача")


def validate_service_ids(db: Session, service_ids: list[str]) -> None:
    unique_service_ids = list(dict.fromkeys(service_ids))
    services = services_service.list_services_by_ids(db, unique_service_ids)
    found_service_ids = {s.id for s in services}
    missing = [sid for sid in unique_service_ids if sid not in found_service_ids]
    if missing:
        raise_bad_request({"message": "Некоторые услуги не найдены", "serviceIds": missing})


def validate_schedule_specialist(db: Session, specialist_id: str) -> None:
    if specialists_service.get_specialist_by_id(db, specialist_id) is None:
        raise_bad_request("Специалист не найден")


def parse_schedule_date_filter(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Дата должна быть в формате YYYY-MM-DD")


def validate_recommendation_user(db: Session, user_id: str, expected_role: str, not_found_detail: str) -> None:
    user = users_service.get_user(db, user_id)
    if user is None:
        raise_bad_request(not_found_detail)
    if user.role.value != expected_role:
        raise_bad_request(f"Пользователь должен иметь роль {expected_role}")


def validate_recommendation_appointment(db: Session, appointment_id: str | None) -> None:
    if appointment_id is None:
        return
    if appointments_service.get_appointment(db, appointment_id) is None:
        raise_bad_request("Запись на приём не найдена")


def validate_recommendation_product_ids(db: Session, product_ids: list[str]) -> None:
    unique_ids = list(dict.fromkeys(product_ids))
    products = products_service.list_products_by_ids(db, unique_ids)
    found = {p.id for p in products}
    missing = [pid for pid in unique_ids if pid not in found]
    if missing:
        raise_bad_request({"message": "Некоторые товары не найдены", "productIds": missing})


def validate_product_category(db: Session, category_id: str | None) -> None:
    if category_id is None:
        raise_bad_request("Категория товара обязательна")
    if products_service.get_product_category(db, category_id) is None:
        raise_bad_request("Категория товара не найдена")


def sanitize_image_basename(original: str) -> str:
    import re
    name = (original or "").rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    if "." in name:
        name = name.rsplit(".", 1)[0]
    name = name.lower()
    name = "".join(_CYRILLIC_TO_LATIN.get(ch, ch) for ch in name)
    name = re.sub(r"[^a-z0-9_-]+", "-", name).strip("-")
    return name


def unique_filename(target_dir: Path, basename: str, ext: str) -> str:
    candidate = f"{basename}.{ext}"
    if not (target_dir / candidate).exists():
        return candidate
    i = 1
    while True:
        candidate = f"{basename}-{i}.{ext}"
        if not (target_dir / candidate).exists():
            return candidate
        i += 1


def detect_image_extension(payload: bytes, content_type: str) -> str | None:
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


def csv_response(filename: str, header: list[str], rows: list[list]) -> StreamingResponse:
    buf = io.StringIO()
    buf.write("\ufeff")
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def format_money_for_excel(value) -> str:
    return f"{float(value):.2f}".replace(".", ",")
