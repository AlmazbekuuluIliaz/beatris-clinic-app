from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import raise_bad_request, raise_conflict, raise_not_found
from app.core.database import get_db
from app.schemas import (
    AdminSpecialist,
    AdminSpecialistListResponse,
    CreateDoctorScheduleRequest,
    CreateSpecialistRequest,
    DoctorSchedule,
    DoctorScheduleListResponse,
    UpdateDoctorScheduleRequest,
    UpdateSpecialistRequest,
)
from app.services import specialists as specialists_service
from app.api.routers.admin.helpers import (
    validate_schedule_specialist,
    validate_service_ids,
    validate_specialist_user,
    parse_schedule_date_filter,
)

router = APIRouter()


@router.get("/specialists", response_model=AdminSpecialistListResponse)
def get_admin_specialists(
    search: str | None = None,
    serviceId: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = specialists_service.list_admin_specialists(db, search, serviceId, isActive, page, limit)
    return {"items": items, "meta": meta}


@router.post("/specialists", response_model=AdminSpecialist, status_code=status.HTTP_201_CREATED)
def create_admin_specialist(
    payload: CreateSpecialistRequest,
    db: Session = Depends(get_db),
) -> dict:
    validate_specialist_user(db, payload.userId)
    validate_service_ids(db, payload.serviceIds)
    try:
        return specialists_service.create_admin_specialist(db, payload)
    except IntegrityError:
        raise_bad_request("Специалист с такими данными уже существует")


@router.get("/specialists/{id}", response_model=AdminSpecialist)
def get_admin_specialist(id: str, db: Session = Depends(get_db)) -> dict:
    result = specialists_service.get_admin_specialist(db, id)
    if result is None:
        raise_not_found("Специалист не найден")
    return result


@router.patch("/specialists/{id}", response_model=AdminSpecialist)
def update_admin_specialist(
    id: str,
    payload: UpdateSpecialistRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "userId" in payload.model_fields_set:
        validate_specialist_user(db, payload.userId)
    if "serviceIds" in payload.model_fields_set and payload.serviceIds is not None:
        validate_service_ids(db, payload.serviceIds)
    try:
        result = specialists_service.update_admin_specialist(db, id, payload)
    except IntegrityError:
        raise_bad_request("Специалист с такими данными уже существует")
    if result is None:
        raise_not_found("Специалист не найден")
    return result


@router.delete("/specialists/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_specialist(id: str, db: Session = Depends(get_db)) -> Response:
    if not specialists_service.deactivate_specialist(db, id):
        raise_not_found("Специалист не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/specialists/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_specialist(id: str, db: Session = Depends(get_db)) -> Response:
    result = specialists_service.delete_admin_specialist(db, id)
    if result == "not_found":
        raise_not_found("Специалист не найден")
    if result == "has_appointments":
        raise_conflict("Невозможно удалить специалиста: на него есть записи на приём. Сначала скройте его.")
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
    parsed_date = parse_schedule_date_filter(scheduleDate)
    items, meta = specialists_service.list_admin_doctor_schedule(db, specialistId, parsed_date, isAvailable, page, limit)
    return {"items": items, "meta": meta}


@router.post("/doctor-schedule", response_model=DoctorSchedule, status_code=status.HTTP_201_CREATED)
def create_admin_doctor_schedule_item(
    payload: CreateDoctorScheduleRequest,
    db: Session = Depends(get_db),
) -> dict:
    validate_schedule_specialist(db, payload.specialistId)
    try:
        return specialists_service.create_admin_doctor_schedule_item(db, payload)
    except IntegrityError:
        raise_bad_request("Расписание специалиста с такими данными уже существует")


@router.get("/doctor-schedule/{id}", response_model=DoctorSchedule)
def get_admin_doctor_schedule_item(id: str, db: Session = Depends(get_db)) -> dict:
    result = specialists_service.get_admin_doctor_schedule_item(db, id)
    if result is None:
        raise_not_found("Запись расписания не найдена")
    return result


@router.patch("/doctor-schedule/{id}", response_model=DoctorSchedule)
def update_admin_doctor_schedule_item(
    id: str,
    payload: UpdateDoctorScheduleRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "specialistId" in payload.model_fields_set and payload.specialistId is not None:
        validate_schedule_specialist(db, payload.specialistId)
    try:
        result = specialists_service.update_admin_doctor_schedule_item(db, id, payload)
    except ValueError as exc:
        raise_bad_request(str(exc))
    except IntegrityError:
        raise_bad_request("Расписание специалиста с такими данными уже существует")
    if result is None:
        raise_not_found("Запись расписания не найдена")
    return result


@router.delete("/doctor-schedule/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_doctor_schedule_item(id: str, db: Session = Depends(get_db)) -> Response:
    if not specialists_service.deactivate_schedule_item(db, id):
        raise_not_found("Запись расписания не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/doctor-schedule/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_doctor_schedule_item(id: str, db: Session = Depends(get_db)) -> Response:
    if not specialists_service.delete_schedule_item(db, id):
        raise_not_found("Запись расписания не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
