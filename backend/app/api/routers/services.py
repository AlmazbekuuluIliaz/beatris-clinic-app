from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import Service, ServiceCategory, ServiceListResponse
from app.services import services as services_service

router = APIRouter(tags=["Services"])


@router.get("/service-categories", response_model=list[ServiceCategory])
def get_service_categories(db: Session = Depends(get_db)) -> list[dict]:
    return services_service.list_service_categories(db)


@router.get("/services", response_model=ServiceListResponse)
def get_services(
    search: str | None = None,
    categorySlug: str | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = services_service.list_services(db, search, categorySlug, minPrice, maxPrice, page, limit)
    return {"items": items, "meta": meta}


@router.get("/services/{slug}", response_model=Service)
def get_service_by_slug(slug: str, db: Session = Depends(get_db)) -> dict:
    result = services_service.get_service_by_slug(db, slug)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Услуга не найдена")
    return result
