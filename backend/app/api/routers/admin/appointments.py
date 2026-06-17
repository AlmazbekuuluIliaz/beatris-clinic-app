from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.errors import APPOINTMENT_RESCHEDULE_ERRORS, raise_bad_request, raise_not_found
from app.core.database import get_db
from app.models import User as UserModel
from app.schemas import (
    Appointment,
    AppointmentListResponse,
    AppointmentStatusHistoryItem,
    PendingCountResponse,
    RescheduleAppointmentRequest,
    UpdateAppointmentContactRequest,
    UpdateAppointmentStatusRequest,
)
from app.services import appointments as appointments_service

AppointmentStatusFilter = Literal["pending", "confirmed", "completed", "cancelled"]

router = APIRouter()


@router.get("/appointments", response_model=AppointmentListResponse)
def get_admin_appointments(
    statusFilter: AppointmentStatusFilter | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = appointments_service.list_admin_appointments(db, statusFilter, page, limit)
    return {"items": items, "meta": meta}


@router.get("/appointments/pending-count", response_model=PendingCountResponse)
def get_pending_appointments_count(db: Session = Depends(get_db)) -> dict:
    return {"count": appointments_service.count_pending_appointments(db)}


@router.get("/appointments/{id}/status-history", response_model=list[AppointmentStatusHistoryItem])
def get_appointment_status_history(
    id: str,
    db: Session = Depends(get_db),
) -> list[dict]:
    result = appointments_service.get_appointment_status_history(db, id)
    if result is None:
        raise_not_found("Запись не найдена")
    return result


@router.patch("/appointments/{id}", response_model=Appointment)
def update_appointment_status(
    id: str,
    payload: UpdateAppointmentStatusRequest,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = appointments_service.update_appointment_status(db, id, payload.status, current_user.id)
    except ValueError as e:
        if str(e).startswith("invalid_transition"):
            raise_bad_request(f"Недопустимый переход статуса: {e}")
        raise
    if result is None:
        raise_not_found("Запись не найдена")
    return result


@router.patch("/appointments/{id}/reschedule", response_model=Appointment)
def reschedule_appointment(
    id: str,
    payload: RescheduleAppointmentRequest,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = appointments_service.reschedule_appointment(db, id, payload, current_user.id)
    except ValueError as e:
        error_msg = APPOINTMENT_RESCHEDULE_ERRORS.get(str(e), str(e))
        if str(e) == "cannot_reschedule_status":
            error_msg = "Невозможно перенести запись в текущем статусе"
        raise_bad_request(error_msg)
    if result is None:
        raise_not_found("Запись не найдена")
    return result


@router.patch("/appointments/{id}/contact", response_model=Appointment)
def update_appointment_contact(
    id: str,
    payload: UpdateAppointmentContactRequest,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    result = appointments_service.update_appointment_contact(db, id, payload, current_user.id)
    if result is None:
        raise_not_found("Запись не найдена")
    return result
