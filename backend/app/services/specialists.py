from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories


def _serialize_specialist(s) -> dict:
    return {
        "id": s.id,
        "fullName": s.full_name,
        "position": s.position,
        "specialization": s.specialization,
        "experienceYears": s.experience_years,
        "photoUrl": s.photo_url,
        "serviceIds": [svc.id for svc in s.services],
    }


def _serialize_admin_specialist(s) -> dict:
    data = _serialize_specialist(s)
    data["userId"] = s.user_id
    data["isActive"] = s.is_active
    return data


def _serialize_schedule(s) -> dict:
    sp = s.specialist
    sp_data = {
        "id": sp.id,
        "fullName": sp.full_name,
        "position": sp.position,
        "specialization": sp.specialization,
        "experienceYears": sp.experience_years,
        "photoUrl": sp.photo_url,
        "serviceIds": [svc.id for svc in sp.services],
    } if sp else None
    return {
        "id": s.id,
        "specialist": sp_data,
        "date": s.schedule_date.isoformat(),
        "startTime": s.start_time.strftime("%H:%M"),
        "endTime": s.end_time.strftime("%H:%M"),
        "isAvailable": s.is_available,
        "createdAt": s.created_at,
        "updatedAt": s.updated_at,
    }


def list_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_specialists(db, search, service_id, page, limit)
    return [_serialize_specialist(s) for s in items], meta


def get_specialist(db: Session, specialist_id: str) -> dict | None:
    specialist = repositories.get_specialist(db, specialist_id)
    if specialist is None:
        return None
    return _serialize_specialist(specialist)


def list_admin_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_specialists(db, search, service_id, is_active, page, limit)
    return [_serialize_admin_specialist(s) for s in items], meta


def get_admin_specialist(db: Session, specialist_id: str) -> dict | None:
    specialist = repositories.get_admin_specialist(db, specialist_id)
    if specialist is None:
        return None
    return _serialize_admin_specialist(specialist)


def create_admin_specialist(db: Session, payload) -> dict:
    specialist = repositories.create_admin_specialist(db, payload)
    return _serialize_admin_specialist(specialist)


def update_admin_specialist(db: Session, specialist_id: str, payload) -> dict | None:
    specialist = repositories.update_admin_specialist(db, specialist_id, payload)
    if specialist is None:
        return None
    return _serialize_admin_specialist(specialist)


def delete_admin_specialist(db: Session, specialist_id: str) -> str:
    return repositories.delete_admin_specialist(db, specialist_id)


def list_admin_doctor_schedule(
    db: Session,
    specialist_id: str | None,
    schedule_date,
    is_available: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_doctor_schedule(db, specialist_id, schedule_date, is_available, page, limit)
    return [_serialize_schedule(s) for s in items], meta


def get_admin_doctor_schedule_item(db: Session, schedule_id: str) -> dict | None:
    item = repositories.get_admin_doctor_schedule_item(db, schedule_id)
    if item is None:
        return None
    return _serialize_schedule(item)


def create_admin_doctor_schedule_item(db: Session, payload) -> dict:
    item = repositories.create_admin_doctor_schedule_item(db, payload)
    return _serialize_schedule(item)


def update_admin_doctor_schedule_item(db: Session, schedule_id: str, payload) -> dict | None:
    item = repositories.update_admin_doctor_schedule_item(db, schedule_id, payload)
    if item is None:
        return None
    return _serialize_schedule(item)


def delete_admin_doctor_schedule_item(db: Session, schedule_id: str) -> bool:
    return repositories.delete_admin_doctor_schedule_item(db, schedule_id)


def list_doctor_schedule(db: Session, specialist_id: str) -> list[dict]:
    items = repositories.list_doctor_schedule(db, specialist_id)
    return [_serialize_schedule(s) for s in items]


def deactivate_specialist(db: Session, specialist_id: str) -> bool:
    return repositories.deactivate_admin_specialist(db, specialist_id)


def deactivate_schedule_item(db: Session, schedule_id: str) -> bool:
    return repositories.deactivate_admin_doctor_schedule_item(db, schedule_id)


def delete_schedule_item(db: Session, schedule_id: str) -> bool:
    return repositories.delete_admin_doctor_schedule_item(db, schedule_id)


def get_specialist_by_id(db: Session, specialist_id: str):
    return repositories.get_admin_specialist(db, specialist_id)
