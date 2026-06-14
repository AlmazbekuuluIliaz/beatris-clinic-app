from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import repositories
from app.core.database import get_db
from app.schemas import Service, ServiceCategory, ServiceListResponse
from app.serializers import service_category_to_api, service_to_api

router = APIRouter(tags=["Services"])


@router.get("/service-categories", response_model=list[ServiceCategory])
def get_service_categories(db: Session = Depends(get_db)) -> list[dict]:
    categories = repositories.list_service_categories(db)
    return [service_category_to_api(category) for category in categories]


@router.get("/services", response_model=ServiceListResponse)
def get_services(
    search: str | None = None,
    categorySlug: str | None = None,
    minPrice: float | None = Query(default=None, ge=0),
    maxPrice: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    services, meta = repositories.list_services(
        db,
        search,
        categorySlug,
        minPrice,
        maxPrice,
        page,
        limit,
    )
    return {"items": [service_to_api(service) for service in services], "meta": meta}


@router.get("/services/{slug}", response_model=Service)
def get_service_by_slug(slug: str, db: Session = Depends(get_db)) -> dict:
    service = repositories.get_service_by_slug(db, slug)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service_to_api(service)
