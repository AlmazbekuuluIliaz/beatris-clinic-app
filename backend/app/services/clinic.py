from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.clinic import ClinicInfo


def get_clinic_info(db: Session) -> dict | None:
    info = repositories.get_clinic_info(db)
    if info is None:
        return None
    return ClinicInfo.model_validate(info).model_dump()


def update_clinic_info(db: Session, payload) -> dict | None:
    info = repositories.update_clinic_info(db, payload)
    if info is None:
        return None
    return ClinicInfo.model_validate(info).model_dump()
