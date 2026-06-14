from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import repositories
from app.core.database import get_db
from app.schemas import Product, ProductCategory, ProductListResponse
from app.serializers import product_category_to_api, product_to_api

router = APIRouter(tags=["Products"])


@router.get("/product-categories", response_model=list[ProductCategory])
def get_product_categories(db: Session = Depends(get_db)) -> list[dict]:
    categories = repositories.list_product_categories(db)
    return [product_category_to_api(category) for category in categories]


@router.get("/products", response_model=ProductListResponse)
def get_products(
    search: str | None = None,
    categorySlug: str | None = None,
    minPrice: float | None = Query(default=None, ge=0),
    maxPrice: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    products, meta = repositories.list_products(
        db,
        search,
        categorySlug,
        minPrice,
        maxPrice,
        page,
        limit,
    )
    return {"items": [product_to_api(product) for product in products], "meta": meta}


@router.get("/products/{slug}", response_model=Product)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)) -> dict:
    product = repositories.get_product_by_slug(db, slug)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product_to_api(product)
