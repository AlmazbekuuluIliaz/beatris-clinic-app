from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.products import AdminProduct, Product, ProductCategory


def list_product_categories(db: Session) -> list[dict]:
    categories = repositories.list_product_categories(db)
    return [ProductCategory.model_validate(c).model_dump() for c in categories]


def list_products(
    db: Session,
    search: str | None,
    category_slug: str | None,
    min_price: float | None,
    max_price: float | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_products(db, search, category_slug, min_price, max_price, page, limit)
    return [Product.model_validate(p).model_dump() for p in items], meta


def get_product_by_slug(db: Session, slug: str) -> dict | None:
    product = repositories.get_product_by_slug(db, slug)
    if product is None:
        return None
    return Product.model_validate(product).model_dump()


def list_admin_products(
    db: Session,
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_products(db, search, category_slug, is_active, page, limit)
    return [AdminProduct.model_validate(p).model_dump() for p in items], meta


def get_admin_product(db: Session, product_id: str) -> dict | None:
    product = repositories.get_admin_product(db, product_id)
    if product is None:
        return None
    return AdminProduct.model_validate(product).model_dump()


def create_admin_product(db: Session, payload) -> dict:
    product = repositories.create_admin_product(db, payload)
    return AdminProduct.model_validate(product).model_dump()


def update_admin_product(db: Session, product_id: str, payload) -> dict | None:
    product = repositories.update_admin_product(db, product_id, payload)
    if product is None:
        return None
    return AdminProduct.model_validate(product).model_dump()


def delete_admin_product(db: Session, product_id: str) -> str:
    return repositories.delete_admin_product(db, product_id)


def create_product_category(db: Session, payload) -> dict:
    category = repositories.create_product_category(db, payload)
    return ProductCategory.model_validate(category).model_dump()


def deactivate_product(db: Session, product_id: str) -> bool:
    return repositories.deactivate_admin_product(db, product_id)


def list_products_for_export(
    db: Session,
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
):
    return repositories.list_admin_products_all(db, search, category_slug, is_active)


def get_product_category(db: Session, category_id: str):
    return repositories.get_product_category(db, category_id)


def list_products_by_ids(db: Session, product_ids: list[str]):
    return repositories.list_products_by_ids(db, product_ids)
