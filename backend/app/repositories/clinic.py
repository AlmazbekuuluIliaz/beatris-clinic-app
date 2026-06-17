from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models


def get_clinic_info(db: Session) -> models.ClinicInfo | None:
    return db.scalar(select(models.ClinicInfo).order_by(models.ClinicInfo.created_at).limit(1))


def update_clinic_info(db: Session, payload) -> models.ClinicInfo | None:
    info = get_clinic_info(db)
    if info is None:
        return None

    if "name" in payload.model_fields_set and payload.name is not None:
        info.name = payload.name
    if "description" in payload.model_fields_set and payload.description is not None:
        info.description = payload.description
    if "address" in payload.model_fields_set and payload.address is not None:
        info.address = payload.address
    if "phone" in payload.model_fields_set and payload.phone is not None:
        info.phone = payload.phone
    if "whatsapp" in payload.model_fields_set:
        info.whatsapp = payload.whatsapp
    if "instagram" in payload.model_fields_set:
        info.instagram = payload.instagram
    if "workingHours" in payload.model_fields_set and payload.workingHours is not None:
        info.working_hours = payload.workingHours
    if "mapUrl" in payload.model_fields_set:
        info.map_url = payload.mapUrl

    db.add(info)
    db.commit()
    db.refresh(info)
    return info
