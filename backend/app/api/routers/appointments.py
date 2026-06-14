from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app import appointment_slots, repositories
from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import Appointment, AvailableSlot, CreateAppointmentRequest
from app.serializers import appointment_to_api

router = APIRouter(tags=["Appointments"])


@router.get("/appointments/my", response_model=list[Appointment])
def get_my_appointments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    appointments = repositories.list_user_appointments(db, current_user.id)
    return [appointment_to_api(appointment) for appointment in appointments]


@router.get("/appointments/available-slots", response_model=list[AvailableSlot])
def get_available_slots(
    specialistId: str,
    serviceId: str,
    date: str,
    db: Session = Depends(get_db),
) -> list[dict]:
    service = repositories.get_service(db, serviceId)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга не найдена",
        )

    specialist = repositories.get_specialist(db, specialistId)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не найден",
        )

    if serviceId not in {service.id for service in specialist.services}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не оказывает выбранную услугу",
        )

    try:
        schedule_date = appointment_slots.parse_date(date)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректная дата",
        ) from exc

    return appointment_slots.available_slots(db, specialistId, service, schedule_date)


@router.post("/appointments", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: CreateAppointmentRequest, db: Session = Depends(get_db)) -> dict:
    service = repositories.get_service(db, payload.serviceId)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Услуга не найдена",
        )

    specialist = repositories.get_specialist(db, payload.specialistId)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не найден",
        )

    if payload.serviceId not in {service.id for service in specialist.services}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Специалист не оказывает выбранную услугу",
        )

    slots = appointment_slots.available_slots(db, payload.specialistId, service, payload.parsed_date)
    if not any(slot["time"] == payload.time for slot in slots):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранное время недоступно",
        )

    try:
        appointment = repositories.create_appointment(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Выбранное время уже занято",
        ) from exc

    return appointment_to_api(appointment)


@router.patch("/appointments/{id}/cancel", response_model=Appointment)
def cancel_appointment(
    id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    appointment = repositories.cancel_user_appointment(db, current_user.id, id)
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment_to_api(appointment)
