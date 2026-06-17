from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.errors import APPOINTMENT_ERRORS, raise_bad_request, raise_not_found
from app.core.database import get_db
from app.schemas import Appointment, AppointmentListResponse, AvailableSlot, BookAppointmentRequest, CreateAppointmentRequest
from app.services import appointments as appointments_service

router = APIRouter(tags=["Appointments"])


@router.get("/appointments/my", response_model=AppointmentListResponse)
def get_my_appointments(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = appointments_service.list_user_appointments_paginated(db, current_user.id, page, limit)
    return {"items": items, "meta": meta}


@router.get("/appointments/available-slots", response_model=list[AvailableSlot])
def get_available_slots(
    specialistId: str,
    serviceId: str,
    date: str,
    db: Session = Depends(get_db),
) -> list[dict]:
    try:
        return appointments_service.get_available_slots(db, specialistId, serviceId, date)
    except ValueError as e:
        raise_bad_request(APPOINTMENT_ERRORS.get(str(e), str(e)))


@router.post("/appointments/book", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def book_appointment(
    payload: BookAppointmentRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return appointments_service.book_appointment(db, payload, current_user)
    except ValueError as e:
        raise_bad_request(APPOINTMENT_ERRORS.get(str(e), str(e)))


@router.post("/appointments", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: CreateAppointmentRequest, db: Session = Depends(get_db)) -> dict:
    try:
        return appointments_service.create_appointment(db, payload)
    except ValueError as e:
        raise_bad_request(APPOINTMENT_ERRORS.get(str(e), str(e)))


@router.patch("/appointments/{id}/cancel", response_model=Appointment)
def cancel_appointment(
    id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = appointments_service.cancel_user_appointment(db, current_user.id, id)
    if result is None:
        raise_not_found("Appointment not found")
    return result
