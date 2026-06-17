from __future__ import annotations

from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def list_service_categories(db: Session) -> list[models.ServiceCategory]:
    return db.scalars(
        select(models.ServiceCategory).order_by(
            models.ServiceCategory.sort_order,
            models.ServiceCategory.title,
        )
    ).all()


def get_service_category(db: Session, category_id: str) -> models.ServiceCategory | None:
    return db.get(models.ServiceCategory, category_id)


def create_service_category(db: Session, payload) -> models.ServiceCategory:
    category = models.ServiceCategory(
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        image_url=payload.imageUrl,
        sort_order=payload.sortOrder,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_service_category(db: Session, category_id: str, payload) -> models.ServiceCategory | None:
    category = db.get(models.ServiceCategory, category_id)
    if category is None:
        return None

    if "title" in payload.model_fields_set:
        category.title = payload.title
    if "slug" in payload.model_fields_set:
        category.slug = payload.slug
    if "description" in payload.model_fields_set:
        category.description = payload.description
    if "imageUrl" in payload.model_fields_set:
        category.image_url = payload.imageUrl
    if "sortOrder" in payload.model_fields_set:
        category.sort_order = payload.sortOrder

    db.commit()
    db.refresh(category)
    return category


def delete_service_category(db: Session, category_id: str) -> str:
    category = db.get(models.ServiceCategory, category_id)
    if category is None:
        return "not_found"

    service_count = db.scalar(
        select(func.count())
        .select_from(models.Service)
        .where(models.Service.category_id == category_id)
    )
    if service_count:
        return "has_services"

    db.delete(category)
    db.commit()
    return "deleted"


def list_services(
    db: Session,
    search: str | None,
    category_slug: str | None,
    min_price: float | None,
    max_price: float | None,
    page: int,
    limit: int,
) -> tuple[list[models.Service], dict]:
    statement = (
        select(models.Service)
        .join(models.Service.category)
        .options(selectinload(models.Service.category))
        .where(models.Service.is_active.is_(True))
        .order_by(models.Service.title)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Service.title.ilike(needle),
                models.Service.description.ilike(needle),
            )
        )

    if category_slug:
        statement = statement.where(models.ServiceCategory.slug == category_slug)

    if min_price is not None:
        statement = statement.where(models.Service.price >= Decimal(str(min_price)))

    if max_price is not None:
        statement = statement.where(models.Service.price <= Decimal(str(max_price)))

    return paginated(db, statement, page, limit)


def get_service(db: Session, service_id: str) -> models.Service | None:
    return db.scalar(
        select(models.Service)
        .options(selectinload(models.Service.category))
        .where(models.Service.id == service_id, models.Service.is_active.is_(True))
    )


def get_service_by_slug(db: Session, slug: str) -> models.Service | None:
    return db.scalar(
        select(models.Service)
        .options(selectinload(models.Service.category))
        .where(models.Service.slug == slug, models.Service.is_active.is_(True))
    )


def list_admin_services(
    db: Session,
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Service], dict]:
    statement = (
        select(models.Service)
        .join(models.Service.category)
        .options(selectinload(models.Service.category))
        .order_by(models.Service.title)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Service.title.ilike(needle),
                models.Service.description.ilike(needle),
            )
        )

    if category_slug:
        statement = statement.where(models.ServiceCategory.slug == category_slug)

    if is_active is not None:
        statement = statement.where(models.Service.is_active.is_(is_active))

    return paginated(db, statement, page, limit)


def get_admin_service(db: Session, service_id: str) -> models.Service | None:
    return db.scalar(
        select(models.Service)
        .options(selectinload(models.Service.category))
        .where(models.Service.id == service_id)
    )


def list_services_by_ids(db: Session, service_ids: list[str]) -> list[models.Service]:
    if not service_ids:
        return []

    unique_service_ids = list(dict.fromkeys(service_ids))
    return db.scalars(select(models.Service).where(models.Service.id.in_(unique_service_ids))).all()


def create_admin_service(db: Session, payload) -> models.Service:
    service = models.Service(
        category_id=payload.categoryId,
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        price=Decimal(str(payload.price)),
        duration_minutes=payload.durationMinutes,
        image_url=payload.imageUrl,
        contraindications=payload.contraindications,
        is_active=payload.isActive,
    )
    db.add(service)
    db.commit()
    return get_admin_service(db, service.id)


def update_admin_service(db: Session, service_id: str, payload) -> models.Service | None:
    service = db.get(models.Service, service_id)
    if service is None:
        return None

    if "categoryId" in payload.model_fields_set:
        service.category_id = payload.categoryId
    if "title" in payload.model_fields_set:
        service.title = payload.title
    if "slug" in payload.model_fields_set:
        service.slug = payload.slug
    if "description" in payload.model_fields_set:
        service.description = payload.description
    if "price" in payload.model_fields_set:
        service.price = Decimal(str(payload.price))
    if "durationMinutes" in payload.model_fields_set:
        service.duration_minutes = payload.durationMinutes
    if "imageUrl" in payload.model_fields_set:
        service.image_url = payload.imageUrl
    if "contraindications" in payload.model_fields_set:
        service.contraindications = payload.contraindications
    if "isActive" in payload.model_fields_set:
        service.is_active = payload.isActive

    db.add(service)
    db.commit()
    return get_admin_service(db, service_id)


def deactivate_admin_service(db: Session, service_id: str) -> bool:
    service = db.get(models.Service, service_id)
    if service is None:
        return False

    service.is_active = False
    db.add(service)
    db.commit()
    return True


def delete_admin_service(db: Session, service_id: str) -> str:
    service = db.get(models.Service, service_id)
    if service is None:
        return "not_found"

    appointment_count = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.service_id == service_id)
    )
    if appointment_count:
        return "has_appointments"

    db.delete(service)
    db.commit()
    return "deleted"
