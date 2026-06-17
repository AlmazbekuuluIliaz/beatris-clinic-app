from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import Product, ProductCategory, ProductListResponse
from app.services import products as products_service

router = APIRouter(tags=["Products"])


@router.get("/product-categories", response_model=list[ProductCategory])
def get_product_categories(db: Session = Depends(get_db)) -> list[dict]:
    return products_service.list_product_categories(db)


@router.get("/products", response_model=ProductListResponse)
def get_products(
    search: str | None = None,
    categorySlug: str | None = None,
    minPrice: float | None = None,
    maxPrice: float | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = products_service.list_products(db, search, categorySlug, minPrice, maxPrice, page, limit)
    return {"items": items, "meta": meta}


@router.get("/products/{slug}", response_model=Product)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)) -> dict:
    result = products_service.get_product_by_slug(db, slug)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return result
