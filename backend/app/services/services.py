from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.services import AdminService, Service, ServiceCategory


def list_service_categories(db: Session) -> list[dict]:
    categories = repositories.list_service_categories(db)
    return [ServiceCategory.model_validate(c).model_dump() for c in categories]


def list_services(
    db: Session,
    search: str | None,
    category_slug: str | None,
    min_price: float | None,
    max_price: float | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_services(db, search, category_slug, min_price, max_price, page, limit)
    return [Service.model_validate(s).model_dump() for s in items], meta


def get_service_by_slug(db: Session, slug: str) -> dict | None:
    service = repositories.get_service_by_slug(db, slug)
    if service is None:
        return None
    return Service.model_validate(service).model_dump()


def list_admin_services(
    db: Session,
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_services(db, search, category_slug, is_active, page, limit)
    return [AdminService.model_validate(s).model_dump() for s in items], meta


def get_admin_service(db: Session, service_id: str) -> dict | None:
    service = repositories.get_admin_service(db, service_id)
    if service is None:
        return None
    return AdminService.model_validate(service).model_dump()


def create_admin_service(db: Session, payload) -> dict:
    service = repositories.create_admin_service(db, payload)
    return AdminService.model_validate(service).model_dump()


def update_admin_service(db: Session, service_id: str, payload) -> dict | None:
    service = repositories.update_admin_service(db, service_id, payload)
    if service is None:
        return None
    return AdminService.model_validate(service).model_dump()


def delete_admin_service(db: Session, service_id: str) -> str:
    return repositories.delete_admin_service(db, service_id)


def create_service_category(db: Session, payload) -> dict:
    category = repositories.create_service_category(db, payload)
    return ServiceCategory.model_validate(category).model_dump()


def update_service_category(db: Session, category_id: str, payload) -> dict | None:
    category = repositories.update_service_category(db, category_id, payload)
    if category is None:
        return None
    return ServiceCategory.model_validate(category).model_dump()


def delete_service_category(db: Session, category_id: str) -> str:
    return repositories.delete_service_category(db, category_id)


def get_service_category(db: Session, category_id: str):
    return repositories.get_service_category(db, category_id)


def deactivate_service(db: Session, service_id: str) -> bool:
    return repositories.deactivate_admin_service(db, service_id)


def list_services_by_ids(db: Session, service_ids: list[str]):
    return repositories.list_services_by_ids(db, service_ids)
