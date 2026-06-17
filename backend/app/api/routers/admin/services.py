from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import raise_bad_request, raise_conflict, raise_not_found
from app.core.database import get_db
from app.schemas import (
    AdminService,
    AdminServiceListResponse,
    CreateServiceCategoryRequest,
    CreateServiceRequest,
    ServiceCategory,
    UpdateServiceCategoryRequest,
    UpdateServiceRequest,
)
from app.services import services as catalog_service

router = APIRouter()


@router.get("/service-categories", response_model=list[ServiceCategory])
def get_admin_service_categories(db: Session = Depends(get_db)) -> list[dict]:
    return catalog_service.list_service_categories(db)


@router.post("/service-categories", response_model=ServiceCategory, status_code=status.HTTP_201_CREATED)
def create_admin_service_category(
    payload: CreateServiceCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return catalog_service.create_service_category(db, payload)
    except IntegrityError:
        raise_bad_request("Категория услуг с таким slug уже существует")


@router.patch("/service-categories/{id}", response_model=ServiceCategory)
def update_admin_service_category(
    id: str,
    payload: UpdateServiceCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = catalog_service.update_service_category(db, id, payload)
    except IntegrityError:
        raise_bad_request("Категория услуг с таким slug уже существует")
    if result is None:
        raise_not_found("Категория услуг не найдена")
    return result


@router.delete("/service-categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_service_category(id: str, db: Session = Depends(get_db)) -> Response:
    result = catalog_service.delete_service_category(db, id)
    if result == "not_found":
        raise_not_found("Категория услуг не найдена")
    if result == "has_services":
        raise_bad_request("Сначала удалите или перенесите услуги этой категории")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/services", response_model=AdminServiceListResponse)
def get_admin_services(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = catalog_service.list_admin_services(db, search, categorySlug, isActive, page, limit)
    return {"items": items, "meta": meta}


@router.post("/services", response_model=AdminService, status_code=status.HTTP_201_CREATED)
def create_admin_service(
    payload: CreateServiceRequest,
    db: Session = Depends(get_db),
) -> dict:
    if catalog_service.get_service_category(db, payload.categoryId) is None:
        raise_bad_request("Категория услуг не найдена")
    try:
        return catalog_service.create_admin_service(db, payload)
    except IntegrityError:
        raise_bad_request("Услуга с таким slug или данными уже существует")


@router.get("/services/{id}", response_model=AdminService)
def get_admin_service(id: str, db: Session = Depends(get_db)) -> dict:
    result = catalog_service.get_admin_service(db, id)
    if result is None:
        raise_not_found("Услуга не найдена")
    return result


@router.patch("/services/{id}", response_model=AdminService)
def update_admin_service(
    id: str,
    payload: UpdateServiceRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.categoryId and catalog_service.get_service_category(db, payload.categoryId) is None:
        raise_bad_request("Категория услуг не найдена")
    try:
        result = catalog_service.update_admin_service(db, id, payload)
    except IntegrityError:
        raise_bad_request("Услуга с таким slug или данными уже существует")
    if result is None:
        raise_not_found("Услуга не найдена")
    return result


@router.delete("/services/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_service(id: str, db: Session = Depends(get_db)) -> Response:
    if not catalog_service.deactivate_service(db, id):
        raise_not_found("Услуга не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/services/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_service(id: str, db: Session = Depends(get_db)) -> Response:
    result = catalog_service.delete_admin_service(db, id)
    if result == "not_found":
        raise_not_found("Услуга не найдена")
    if result == "has_appointments":
        raise_conflict("Невозможно удалить услугу: на неё есть записи на приём. Сначала скройте её.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
