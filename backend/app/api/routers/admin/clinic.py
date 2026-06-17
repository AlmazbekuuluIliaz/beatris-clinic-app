from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.errors import raise_not_found
from app.core.database import get_db
from app.schemas import ClinicInfo, UpdateClinicInfoRequest
from app.services import clinic as clinic_service

router = APIRouter()


@router.patch("/clinic-info", response_model=ClinicInfo)
def update_admin_clinic_info(
    payload: UpdateClinicInfoRequest,
    db: Session = Depends(get_db),
) -> dict:
    result = clinic_service.update_clinic_info(db, payload)
    if result is None:
        raise_not_found("Информация о клинике не найдена")
    return result
