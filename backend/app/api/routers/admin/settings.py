from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import AdminSettingsResponse, UpdateAdminSettingsRequest
from app.services import admin as admin_service
from app.api.routers.admin.helpers import (
    IMAGE_MAX_BYTES,
    IMAGE_UPLOAD_FOLDERS,
    detect_image_extension,
    sanitize_image_basename,
    unique_filename,
)

router = APIRouter()

LICENSE_DIR = Path("uploads/legal")
LICENSE_FILENAME = "license.pdf"
LICENSE_MAX_BYTES = 10 * 1024 * 1024
LICENSE_SETTING_KEY = "licenseFileUrl"


@router.get("/settings", response_model=AdminSettingsResponse)
def get_admin_settings(db: Session = Depends(get_db)) -> dict:
    return {"settings": admin_service.get_settings(db)}


@router.put("/settings", response_model=AdminSettingsResponse)
def update_admin_settings(
    payload: UpdateAdminSettingsRequest,
    db: Session = Depends(get_db),
) -> dict:
    return {"settings": admin_service.update_settings(db, payload.settings)}


@router.post("/settings/license", response_model=AdminSettingsResponse)
async def upload_license_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    if (file.content_type or "").lower() != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Допускаются только PDF-файлы")

    contents = await file.read()
    if len(contents) > LICENSE_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Файл больше {LICENSE_MAX_BYTES // (1024 * 1024)} МБ")
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл не является корректным PDF")

    LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    (LICENSE_DIR / LICENSE_FILENAME).write_bytes(contents)

    public_url = f"/uploads/legal/{LICENSE_FILENAME}?v={int(time.time())}"
    admin_service.upsert_setting(db, LICENSE_SETTING_KEY, public_url)
    return {"settings": admin_service.get_settings(db)}


@router.delete("/settings/license", response_model=AdminSettingsResponse)
def delete_license_pdf(db: Session = Depends(get_db)) -> dict:
    file_path = LICENSE_DIR / LICENSE_FILENAME
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
    admin_service.upsert_setting(db, LICENSE_SETTING_KEY, None)
    return {"settings": admin_service.get_settings(db)}


@router.post("/uploads/image")
async def upload_admin_image(
    folder: str = Query(...),
    file: UploadFile = File(...),
) -> dict:
    if folder not in IMAGE_UPLOAD_FOLDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Папка должна быть одной из: {sorted(IMAGE_UPLOAD_FOLDERS)}")

    contents = await file.read()
    if len(contents) > IMAGE_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Файл больше {IMAGE_MAX_BYTES // (1024 * 1024)} МБ")

    ext = detect_image_extension(contents, file.content_type or "")
    if ext is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Поддерживаются только JPG, PNG и WebP")

    target_dir = Path("uploads") / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    basename = sanitize_image_basename(file.filename or "")
    if not basename:
        import uuid
        basename = uuid.uuid4().hex
    filename = unique_filename(target_dir, basename, ext)
    (target_dir / filename).write_bytes(contents)

    return {"url": f"/uploads/{folder}/{filename}"}
