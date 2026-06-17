from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def get_specialist_by_user_id(db: Session, user_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.user_id == user_id, models.Specialist.is_active.is_(True))
    )


def list_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Specialist], dict]:
    from sqlalchemy import or_

    statement = (
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.is_active.is_(True))
        .order_by(models.Specialist.full_name)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Specialist.full_name.ilike(needle),
                models.Specialist.position.ilike(needle),
                models.Specialist.specialization.ilike(needle),
            )
        )

    if service_id:
        statement = statement.join(models.Specialist.services).where(models.Service.id == service_id)

    return paginated(db, statement, page, limit)


def get_specialist(db: Session, specialist_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.id == specialist_id, models.Specialist.is_active.is_(True))
    )


def list_admin_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Specialist], dict]:
    from sqlalchemy import or_

    statement = (
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .order_by(models.Specialist.full_name)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Specialist.full_name.ilike(needle),
                models.Specialist.position.ilike(needle),
                models.Specialist.specialization.ilike(needle),
            )
        )

    if service_id:
        statement = statement.join(models.Specialist.services).where(models.Service.id == service_id)

    if is_active is not None:
        statement = statement.where(models.Specialist.is_active.is_(is_active))

    return paginated(db, statement, page, limit)


def get_admin_specialist(db: Session, specialist_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.id == specialist_id)
    )


def create_admin_specialist(db: Session, payload) -> models.Specialist:
    specialist = models.Specialist(
        user_id=payload.userId,
        full_name=payload.fullName,
        position=payload.position,
        specialization=payload.specialization,
        experience_years=payload.experienceYears,
        photo_url=payload.photoUrl,
        is_active=payload.isActive,
    )
    db.add(specialist)
    db.flush()
    replace_specialist_services(db, specialist.id, payload.serviceIds)
    db.commit()
    return get_admin_specialist(db, specialist.id)


def update_admin_specialist(db: Session, specialist_id: str, payload) -> models.Specialist | None:
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return None

    if "userId" in payload.model_fields_set:
        specialist.user_id = payload.userId
    if "fullName" in payload.model_fields_set and payload.fullName is not None:
        specialist.full_name = payload.fullName
    if "position" in payload.model_fields_set and payload.position is not None:
        specialist.position = payload.position
    if "specialization" in payload.model_fields_set and payload.specialization is not None:
        specialist.specialization = payload.specialization
    if "experienceYears" in payload.model_fields_set:
        specialist.experience_years = payload.experienceYears
    if "photoUrl" in payload.model_fields_set:
        specialist.photo_url = payload.photoUrl
    if "isActive" in payload.model_fields_set and payload.isActive is not None:
        specialist.is_active = payload.isActive

    db.add(specialist)
    if "serviceIds" in payload.model_fields_set and payload.serviceIds is not None:
        replace_specialist_services(db, specialist_id, payload.serviceIds)

    db.commit()
    return get_admin_specialist(db, specialist_id)


def deactivate_admin_specialist(db: Session, specialist_id: str) -> bool:
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return False

    specialist.is_active = False
    db.add(specialist)
    db.commit()
    return True


def delete_admin_specialist(db: Session, specialist_id: str) -> str:
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return "not_found"

    appointment_count = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.specialist_id == specialist_id)
    )
    if appointment_count:
        return "has_appointments"

    db.delete(specialist)
    db.commit()
    return "deleted"


def replace_specialist_services(db: Session, specialist_id: str, service_ids: list[str]) -> None:
    db.execute(
        delete(models.SpecialistService).where(
            models.SpecialistService.specialist_id == specialist_id,
        )
    )
    for service_id in dict.fromkeys(service_ids):
        db.add(models.SpecialistService(specialist_id=specialist_id, service_id=service_id))
