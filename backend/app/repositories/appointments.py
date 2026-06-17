from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models

ALLOWED_APPOINTMENT_STATUS_TRANSITIONS = {
    models.AppointmentStatus.PENDING: {
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.CANCELLED,
    },
    models.AppointmentStatus.CONFIRMED: {
        models.AppointmentStatus.COMPLETED,
        models.AppointmentStatus.CANCELLED,
        models.AppointmentStatus.PENDING,
    },
    models.AppointmentStatus.COMPLETED: {
        models.AppointmentStatus.PENDING,
    },
    models.AppointmentStatus.CANCELLED: {
        models.AppointmentStatus.PENDING,
    },
}


def appointment_detail_options() -> tuple:
    return (
        selectinload(models.Appointment.service).selectinload(models.Service.category),
        selectinload(models.Appointment.specialist).selectinload(models.Specialist.services),
        selectinload(models.Appointment.status_history).selectinload(models.AppointmentStatusHistory.admin),
    )


def is_appointment_status_transition_allowed(
    current_status: models.AppointmentStatus,
    next_status: models.AppointmentStatus | str,
) -> bool:
    next_status = models.AppointmentStatus(next_status)
    if current_status == next_status:
        return True
    return next_status in ALLOWED_APPOINTMENT_STATUS_TRANSITIONS[current_status]


def list_admin_appointments(
    db: Session,
    appointment_status: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Appointment], dict]:
    from app.repositories.base import paginated

    statement = (
        select(models.Appointment)
        .options(*appointment_detail_options())
        .order_by(
            models.Appointment.appointment_date.desc(),
            models.Appointment.appointment_time.asc(),
        )
    )

    if appointment_status:
        statement = statement.where(models.Appointment.status == models.AppointmentStatus(appointment_status))

    return paginated(db, statement, page, limit)


def count_pending_appointments(db: Session) -> int:
    return db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.status == models.AppointmentStatus.PENDING)
    ) or 0


def list_user_appointments_paginated(
    db: Session, user_id: str, page: int, limit: int
) -> tuple[list[models.Appointment], dict]:
    from app.repositories.base import paginated

    statement = (
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.patient_id == user_id)
        .order_by(models.Appointment.appointment_date.desc(), models.Appointment.appointment_time.desc())
    )
    return paginated(db, statement, page, limit)


def list_doctor_appointments_paginated(
    db: Session, specialist_id: str, page: int, limit: int, date_from: str | None = None, date_to: str | None = None
) -> tuple[list[models.Appointment], dict]:
    from app.repositories.base import paginated

    statement = (
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.specialist_id == specialist_id)
        .order_by(models.Appointment.appointment_date.desc(), models.Appointment.appointment_time.desc())
    )
    if date_from:
        from datetime import date as d
        statement = statement.where(models.Appointment.appointment_date >= d.fromisoformat(date_from))
    if date_to:
        from datetime import date as d
        statement = statement.where(models.Appointment.appointment_date <= d.fromisoformat(date_to))
    return paginated(db, statement, page, limit)


def get_appointment(db: Session, appointment_id: str) -> models.Appointment | None:
    return db.scalar(
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.id == appointment_id)
    )


def update_appointment_status(
    db: Session,
    appointment_id: str,
    appointment_status: str,
    admin_id: str | None = None,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    previous_status = appointment.status
    next_status = models.AppointmentStatus(appointment_status)
    appointment.status = next_status
    db.add(appointment)
    if previous_status != next_status:
        db.add(
            models.AppointmentStatusHistory(
                appointment_id=appointment_id,
                admin_id=admin_id,
                previous_status=previous_status,
                new_status=next_status,
            )
        )
    db.commit()
    return get_appointment(db, appointment_id)


def reschedule_appointment(
    db: Session,
    appointment_id: str,
    payload,
    admin_id: str | None = None,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    if appointment.status not in (models.AppointmentStatus.PENDING, models.AppointmentStatus.CONFIRMED):
        raise ValueError("cannot_reschedule_status")

    previous_date = appointment.appointment_date
    previous_time = appointment.appointment_time
    previous_specialist_id = appointment.specialist_id

    appointment.specialist_id = payload.specialistId
    appointment.appointment_date = payload.parsed_date
    appointment.appointment_time = payload.parsed_time
    if "comment" in payload.model_fields_set:
        appointment.comment = payload.comment

    db.add(
        models.AppointmentStatusHistory(
            appointment_id=appointment_id,
            admin_id=admin_id,
            previous_status=appointment.status,
            new_status=appointment.status,
        )
    )

    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def update_appointment_contact(
    db: Session,
    appointment_id: str,
    payload,
    admin_id: str | None = None,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    appointment.patient_contact_status = payload.patientContactStatus
    appointment.patient_contact_comment = payload.patientContactComment
    appointment.patient_contacted_at = datetime.utcnow()

    previous_status = appointment.status

    if payload.patientContactStatus == "agreed" and appointment.status == models.AppointmentStatus.PENDING:
        appointment.status = models.AppointmentStatus.CONFIRMED
    elif payload.patientContactStatus == "declined" and appointment.status == models.AppointmentStatus.PENDING:
        appointment.status = models.AppointmentStatus.CANCELLED

    if previous_status != appointment.status:
        db.add(
            models.AppointmentStatusHistory(
                appointment_id=appointment_id,
                admin_id=admin_id,
                previous_status=previous_status,
                new_status=appointment.status,
            )
        )

    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def cancel_user_appointment(db: Session, user_id: str, appointment_id: str) -> models.Appointment | None:
    appointment = db.scalar(
        select(models.Appointment).where(
            models.Appointment.id == appointment_id,
            models.Appointment.patient_id == user_id,
        )
    )
    if appointment is None:
        return None

    previous_status = appointment.status
    appointment.status = models.AppointmentStatus.CANCELLED

    if previous_status != models.AppointmentStatus.CANCELLED:
        db.add(
            models.AppointmentStatusHistory(
                appointment_id=appointment_id,
                admin_id=None,
                previous_status=previous_status,
                new_status=models.AppointmentStatus.CANCELLED,
            )
        )

    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def _next_appointment_number(db: Session) -> str:
    prefix = f"AP-{datetime.now():%y%m%d}-"
    last = db.scalar(
        select(models.Appointment.appointment_number)
        .where(models.Appointment.appointment_number.like(f"{prefix}%"))
        .order_by(models.Appointment.appointment_number.desc())
        .limit(1)
    )
    sequence = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{sequence:03d}"


def create_appointment(
    db: Session,
    payload,
    patient_id: str | None = None,
) -> models.Appointment:
    appointment = models.Appointment(
        appointment_number=_next_appointment_number(db),
        patient_id=patient_id,
        patient_name=payload.patientName,
        patient_phone=payload.patientPhone,
        service_id=payload.serviceId,
        specialist_id=payload.specialistId,
        appointment_date=payload.parsed_date,
        appointment_time=payload.parsed_time,
        requested_date=payload.parsed_date,
        requested_time=payload.parsed_time,
        status=models.AppointmentStatus.PENDING,
        comment=payload.comment,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return db.scalar(
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.id == appointment.id)
    )


def list_busy_appointments(
    db: Session,
    specialist_id: str,
    appointment_date,
    exclude_appointment_id: str | None = None,
) -> list[models.Appointment]:
    statement = (
        select(models.Appointment)
        .options(selectinload(models.Appointment.service))
        .where(
            models.Appointment.specialist_id == specialist_id,
            models.Appointment.appointment_date == appointment_date,
            models.Appointment.status != models.AppointmentStatus.CANCELLED,
        )
    )
    if exclude_appointment_id is not None:
        statement = statement.where(models.Appointment.id != exclude_appointment_id)
    return db.scalars(statement).all()


def is_appointment_slot_available(
    db: Session,
    specialist_id: str,
    service: models.Service,
    appointment_date,
    appointment_time,
    exclude_appointment_id: str | None = None,
) -> bool:
    from app.repositories.schedule import list_schedule_items

    duration = service.duration_minutes or 30
    start = appointment_time.hour * 60 + appointment_time.minute
    candidate = (start, start + duration)

    schedule_match = False
    for schedule_item in list_schedule_items(db, specialist_id, appointment_date):
        schedule_start = schedule_item.start_time.hour * 60 + schedule_item.start_time.minute
        schedule_end = schedule_item.end_time.hour * 60 + schedule_item.end_time.minute
        if schedule_start <= candidate[0] and candidate[1] <= schedule_end:
            schedule_match = True
            break
    if not schedule_match:
        return False

    busy_intervals = []
    for appointment in list_busy_appointments(db, specialist_id, appointment_date, exclude_appointment_id):
        busy_start = appointment.appointment_time.hour * 60 + appointment.appointment_time.minute
        busy_end = busy_start + (appointment.service.duration_minutes or 30)
        busy_intervals.append((busy_start, busy_end))

    return not any(candidate[0] < busy[1] and busy[0] < candidate[1] for busy in busy_intervals)
