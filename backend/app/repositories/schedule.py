from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def doctor_schedule_detail_options() -> tuple:
    return (
        selectinload(models.DoctorSchedule.specialist).selectinload(models.Specialist.services),
    )


def list_admin_doctor_schedule(
    db: Session,
    specialist_id: str | None,
    schedule_date,
    is_available: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.DoctorSchedule], dict]:
    statement = (
        select(models.DoctorSchedule)
        .join(models.Specialist, models.DoctorSchedule.specialist_id == models.Specialist.id)
        .options(*doctor_schedule_detail_options())
        .where(models.Specialist.is_active.is_(True))
        .order_by(
            models.DoctorSchedule.schedule_date.desc(),
            models.DoctorSchedule.start_time.asc(),
        )
    )

    if specialist_id:
        statement = statement.where(models.DoctorSchedule.specialist_id == specialist_id)

    if schedule_date:
        statement = statement.where(models.DoctorSchedule.schedule_date == schedule_date)

    if is_available is not None:
        statement = statement.where(models.DoctorSchedule.is_available.is_(is_available))

    return paginated(db, statement, page, limit)


def list_doctor_schedule(db: Session, specialist_id: str, date_from: str | None = None, date_to: str | None = None) -> list[models.DoctorSchedule]:
    statement = (
        select(models.DoctorSchedule)
        .options(*doctor_schedule_detail_options())
        .where(models.DoctorSchedule.specialist_id == specialist_id)
        .order_by(models.DoctorSchedule.schedule_date, models.DoctorSchedule.start_time)
    )
    if date_from:
        from datetime import date as d
        statement = statement.where(models.DoctorSchedule.schedule_date >= d.fromisoformat(date_from))
    if date_to:
        from datetime import date as d
        statement = statement.where(models.DoctorSchedule.schedule_date <= d.fromisoformat(date_to))
    return db.scalars(statement).all()


def get_admin_doctor_schedule_item(
    db: Session,
    schedule_id: str,
) -> models.DoctorSchedule | None:
    return db.scalar(
        select(models.DoctorSchedule)
        .options(*doctor_schedule_detail_options())
        .where(models.DoctorSchedule.id == schedule_id)
    )


def create_admin_doctor_schedule_item(db: Session, payload) -> models.DoctorSchedule:
    schedule_item = models.DoctorSchedule(
        specialist_id=payload.specialistId,
        schedule_date=payload.parsed_date,
        start_time=payload.parsed_start_time,
        end_time=payload.parsed_end_time,
        is_available=payload.isAvailable,
    )
    db.add(schedule_item)
    db.commit()
    return get_admin_doctor_schedule_item(db, schedule_item.id)


def update_admin_doctor_schedule_item(
    db: Session,
    schedule_id: str,
    payload,
) -> models.DoctorSchedule | None:
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return None

    if "specialistId" in payload.model_fields_set and payload.specialistId is not None:
        schedule_item.specialist_id = payload.specialistId
    if "date" in payload.model_fields_set and payload.date is not None:
        schedule_item.schedule_date = payload.parsed_date
    if "startTime" in payload.model_fields_set and payload.startTime is not None:
        schedule_item.start_time = payload.parsed_start_time
    if "endTime" in payload.model_fields_set and payload.endTime is not None:
        schedule_item.end_time = payload.parsed_end_time
    if "isAvailable" in payload.model_fields_set and payload.isAvailable is not None:
        schedule_item.is_available = payload.isAvailable

    if schedule_item.start_time >= schedule_item.end_time:
        raise ValueError("startTime must be earlier than endTime")

    db.add(schedule_item)
    db.commit()
    return get_admin_doctor_schedule_item(db, schedule_id)


def deactivate_admin_doctor_schedule_item(db: Session, schedule_id: str) -> bool:
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return False

    schedule_item.is_available = False
    db.add(schedule_item)
    db.commit()
    return True


def delete_admin_doctor_schedule_item(db: Session, schedule_id: str) -> bool:
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return False

    db.delete(schedule_item)
    db.commit()
    return True


def list_schedule_items(
    db: Session,
    specialist_id: str,
    schedule_date,
) -> list[models.DoctorSchedule]:
    return db.scalars(
        select(models.DoctorSchedule)
        .join(models.Specialist, models.DoctorSchedule.specialist_id == models.Specialist.id)
        .where(
            models.DoctorSchedule.specialist_id == specialist_id,
            models.DoctorSchedule.schedule_date == schedule_date,
            models.DoctorSchedule.is_available.is_(True),
            models.Specialist.is_active.is_(True),
        )
        .order_by(models.DoctorSchedule.start_time)
    ).all()
