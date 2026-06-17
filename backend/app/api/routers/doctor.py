from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_doctor
from app.core.database import get_db
from app.schemas import Appointment, AppointmentListResponse, DoctorSchedule
from app.services import appointments as appointments_service
from app.services import schedule as schedule_service

router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.get("/schedule", response_model=list[DoctorSchedule])
def get_doctor_schedule(
    dateFrom: str | None = None,
    dateTo: str | None = None,
    current_user=Depends(require_doctor),
    db: Session = Depends(get_db),
) -> list[dict]:
    specialist = schedule_service.get_specialist_by_user_id(db, current_user.id)
    if specialist is None:
        return []
    return schedule_service.list_doctor_schedule(db, specialist.id, dateFrom, dateTo)


@router.get("/appointments", response_model=AppointmentListResponse)
def get_doctor_appointments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    dateFrom: str | None = None,
    dateTo: str | None = None,
    current_user=Depends(require_doctor),
    db: Session = Depends(get_db),
) -> dict:
    specialist = schedule_service.get_specialist_by_user_id(db, current_user.id)
    if specialist is None:
        return {"items": [], "meta": {"page": page, "limit": limit, "total": 0}}
    items, meta = appointments_service.list_doctor_appointments_paginated(db, specialist.id, page, limit, dateFrom, dateTo)
    return {"items": items, "meta": meta}
