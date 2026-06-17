from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import raise_bad_request, raise_conflict, raise_not_found
from app.core.database import get_db
from app.schemas import (
    AdminProduct,
    AdminProductListResponse,
    CreateProductCategoryRequest,
    CreateProductRequest,
    ProductCategory,
    UpdateProductRequest,
)
from app.services import products as products_service
from app.api.routers.admin.helpers import validate_product_category, csv_response, format_money_for_excel

router = APIRouter()


@router.get("/product-categories", response_model=list[ProductCategory])
def get_admin_product_categories(db: Session = Depends(get_db)) -> list[dict]:
    return products_service.list_product_categories(db)


@router.post("/product-categories", response_model=ProductCategory, status_code=status.HTTP_201_CREATED)
def create_admin_product_category(
    payload: CreateProductCategoryRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        return products_service.create_product_category(db, payload)
    except IntegrityError:
        raise_bad_request("Категория товаров с таким slug уже существует")


@router.get("/products", response_model=AdminProductListResponse)
def get_admin_products(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = products_service.list_admin_products(db, search, categorySlug, isActive, page, limit)
    return {"items": items, "meta": meta}


@router.post("/products", response_model=AdminProduct, status_code=status.HTTP_201_CREATED)
def create_admin_product(
    payload: CreateProductRequest,
    db: Session = Depends(get_db),
) -> dict:
    validate_product_category(db, payload.categoryId)
    try:
        return products_service.create_admin_product(db, payload)
    except IntegrityError:
        raise_bad_request("Товар с таким slug или данными уже существует")


@router.get("/products/{id}", response_model=AdminProduct)
def get_admin_product(id: str, db: Session = Depends(get_db)) -> dict:
    result = products_service.get_admin_product(db, id)
    if result is None:
        raise_not_found("Товар не найден")
    return result


@router.patch("/products/{id}", response_model=AdminProduct)
def update_admin_product(
    id: str,
    payload: UpdateProductRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "categoryId" in payload.model_fields_set:
        validate_product_category(db, payload.categoryId)
    try:
        result = products_service.update_admin_product(db, id, payload)
    except IntegrityError:
        raise_bad_request("Товар с таким slug или данными уже существует")
    if result is None:
        raise_not_found("Товар не найден")
    return result


@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_product(id: str, db: Session = Depends(get_db)) -> Response:
    if not products_service.deactivate_product(db, id):
        raise_not_found("Товар не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/products/{id}/hard", status_code=status.HTTP_204_NO_CONTENT)
def hard_delete_admin_product(id: str, db: Session = Depends(get_db)) -> Response:
    result = products_service.delete_admin_product(db, id)
    if result == "not_found":
        raise_not_found("Товар не найден")
    if result == "has_carts":
        raise_conflict("Невозможно удалить товар: он находится в корзине у пользователей. Сначала скройте его.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/exports/products.csv")
def export_admin_products(
    search: str | None = None,
    categorySlug: str | None = None,
    isActive: bool | None = None,
    db: Session = Depends(get_db),
):
    products = products_service.list_products_for_export(db, search, categorySlug, isActive)
    header = ["Название", "Slug", "Категория", "Цена", "Остаток", "Статус", "Описание"]
    rows = [
        [
            p.title,
            p.slug,
            p.category.title if p.category else "",
            format_money_for_excel(p.price),
            p.stock,
            "Активен" if p.is_active else "Скрыт",
            p.description or "",
        ]
        for p in products
    ]
    return csv_response("products.csv", header, rows)
