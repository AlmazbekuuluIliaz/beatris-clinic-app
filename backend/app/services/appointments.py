from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import repositories
from app.services import appointment_slots
from app.schemas.appointments import Appointment


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


def _serialize_service(s) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "slug": s.slug,
        "description": s.description,
        "price": float(s.price),
        "durationMinutes": s.duration_minutes,
        "category": {
            "id": s.category.id,
            "title": s.category.title,
            "slug": s.category.slug,
            "description": s.category.description,
            "imageUrl": s.category.image_url,
            "sortOrder": s.category.sort_order,
        },
        "imageUrl": s.image_url,
        "contraindications": s.contraindications,
    }


def _serialize(appointment) -> dict:
    history = []
    for h in appointment.status_history:
        history.append({
            "id": h.id,
            "adminId": h.admin_id,
            "adminName": h.admin.full_name if h.admin else None,
            "previousStatus": h.previous_status.value,
            "newStatus": h.new_status.value,
            "createdAt": h.created_at,
        })
    return {
        "id": appointment.id,
        "appointmentNumber": appointment.appointment_number,
        "patientId": appointment.patient_id,
        "patientName": appointment.patient_name,
        "patientPhone": appointment.patient_phone,
        "service": _serialize_service(appointment.service),
        "specialist": _serialize_specialist(appointment.specialist),
        "date": appointment.appointment_date.isoformat(),
        "time": appointment.appointment_time.strftime("%H:%M"),
        "requestedDate": appointment.requested_date.isoformat() if appointment.requested_date else None,
        "requestedTime": appointment.requested_time.strftime("%H:%M") if appointment.requested_time else None,
        "status": appointment.status.value,
        "comment": appointment.comment,
        "patientContactStatus": appointment.patient_contact_status,
        "patientContactedAt": appointment.patient_contacted_at,
        "patientContactComment": appointment.patient_contact_comment,
        "statusHistory": history,
        "createdAt": appointment.created_at,
    }


def get_available_slots(
    db: Session,
    specialist_id: str,
    service_id: str,
    date_str: str,
) -> list[dict]:
    service = repositories.get_service(db, service_id)
    if service is None:
        raise ValueError("service_not_found")

    specialist = repositories.get_specialist(db, specialist_id)
    if specialist is None:
        raise ValueError("specialist_not_found")

    if service_id not in {s.id for s in specialist.services}:
        raise ValueError("specialist_does_not_provide_service")

    try:
        schedule_date = appointment_slots.parse_date(date_str)
    except ValueError:
        raise ValueError("invalid_date")

    return appointment_slots.available_slots(db, specialist_id, service, schedule_date)


def create_appointment(db: Session, payload, patient_id: str | None = None) -> dict:
    service = repositories.get_service(db, payload.serviceId)
    if service is None:
        raise ValueError("service_not_found")

    specialist = repositories.get_specialist(db, payload.specialistId)
    if specialist is None:
        raise ValueError("specialist_not_found")

    if payload.serviceId not in {s.id for s in specialist.services}:
        raise ValueError("specialist_does_not_provide_service")

    slots = appointment_slots.available_slots(db, payload.specialistId, service, payload.parsed_date)
    if not any(slot["time"] == payload.time for slot in slots):
        raise ValueError("slot_unavailable")

    try:
        appointment = repositories.create_appointment(db, payload, patient_id)
    except IntegrityError:
        db.rollback()
        raise ValueError("slot_taken")

    return _serialize(appointment)


def book_appointment(db: Session, payload, current_user) -> dict:
    service = repositories.get_service(db, payload.serviceId)
    if service is None:
        raise ValueError("service_not_found")

    specialist = repositories.get_specialist(db, payload.specialistId)
    if specialist is None:
        raise ValueError("specialist_not_found")

    if payload.serviceId not in {s.id for s in specialist.services}:
        raise ValueError("specialist_does_not_provide_service")

    slots = appointment_slots.available_slots(db, payload.specialistId, service, payload.parsed_date)
    if not any(slot["time"] == payload.time for slot in slots):
        raise ValueError("slot_unavailable")

    from types import SimpleNamespace

    book_payload = SimpleNamespace(
        serviceId=payload.serviceId,
        specialistId=payload.specialistId,
        parsed_date=payload.parsed_date,
        parsed_time=payload.parsed_time,
        patientName=current_user.full_name,
        patientPhone=current_user.phone,
        comment=payload.comment,
    )

    try:
        appointment = repositories.create_appointment(db, book_payload, current_user.id)
    except IntegrityError:
        db.rollback()
        raise ValueError("slot_taken")

    return _serialize(appointment)


def list_user_appointments_paginated(
    db: Session, user_id: str, page: int, limit: int
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_user_appointments_paginated(db, user_id, page, limit)
    return [_serialize(a) for a in items], meta


def list_admin_appointments(
    db: Session,
    appointment_status: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_appointments(db, appointment_status, page, limit)
    return [_serialize(a) for a in items], meta


def count_pending_appointments(db: Session) -> int:
    return repositories.count_pending_appointments(db)


def list_doctor_appointments_paginated(
    db: Session, specialist_id: str, page: int, limit: int, date_from: str | None = None, date_to: str | None = None
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_doctor_appointments_paginated(db, specialist_id, page, limit, date_from, date_to)
    return [_serialize(a) for a in items], meta


def cancel_user_appointment(db: Session, user_id: str, appointment_id: str) -> dict | None:
    appointment = repositories.cancel_user_appointment(db, user_id, appointment_id)
    if appointment is None:
        return None
    return _serialize(appointment)


def update_appointment_status(
    db: Session,
    appointment_id: str,
    new_status: str,
    admin_id: str | None = None,
) -> dict | None:
    existing = repositories.get_appointment(db, appointment_id)
    if existing is None:
        return None

    if not repositories.is_appointment_status_transition_allowed(existing.status, new_status):
        raise ValueError(f"invalid_transition:{existing.status.value}->{new_status}")

    appointment = repositories.update_appointment_status(db, appointment_id, new_status, admin_id)
    if appointment is None:
        return None
    return _serialize(appointment)


def reschedule_appointment(db: Session, appointment_id: str, payload, admin_id: str | None = None) -> dict | None:
    appointment = repositories.get_appointment(db, appointment_id)
    if appointment is None:
        return None

    specialist = repositories.get_specialist(db, payload.specialistId)
    if specialist is None:
        raise ValueError("specialist_not_found")

    if appointment.service_id not in {s.id for s in specialist.services}:
        raise ValueError("specialist_does_not_provide_service")

    if not repositories.is_appointment_slot_available(
        db,
        payload.specialistId,
        appointment.service,
        payload.parsed_date,
        payload.parsed_time,
        exclude_appointment_id=appointment_id,
    ):
        raise ValueError("slot_unavailable")

    try:
        updated = repositories.reschedule_appointment(db, appointment_id, payload, admin_id)
    except IntegrityError:
        db.rollback()
        raise ValueError("slot_taken")

    if updated is None:
        return None
    return _serialize(updated)


def update_appointment_contact(db: Session, appointment_id: str, payload, admin_id: str | None = None) -> dict | None:
    appointment = repositories.update_appointment_contact(db, appointment_id, payload, admin_id)
    if appointment is None:
        return None
    return _serialize(appointment)


def get_appointment(db: Session, appointment_id: str) -> dict | None:
    appointment = repositories.get_appointment(db, appointment_id)
    if appointment is None:
        return None
    return _serialize(appointment)


def get_appointment_status_history(db: Session, appointment_id: str) -> list[dict] | None:
    appointment = repositories.get_appointment(db, appointment_id)
    if appointment is None:
        return None
    history = []
    for h in appointment.status_history:
        history.append({
            "id": h.id,
            "adminId": h.admin_id,
            "adminName": h.admin.full_name if h.admin else None,
            "previousStatus": h.previous_status.value,
            "newStatus": h.new_status.value,
            "createdAt": h.created_at,
        })
    return history
