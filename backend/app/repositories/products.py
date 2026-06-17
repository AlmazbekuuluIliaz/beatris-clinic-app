from __future__ import annotations

from decimal import Decimal

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def list_product_categories(db: Session) -> list[models.ProductCategory]:
    return db.scalars(select(models.ProductCategory).order_by(models.ProductCategory.title)).all()


def get_product_category(db: Session, category_id: str) -> models.ProductCategory | None:
    return db.get(models.ProductCategory, category_id)


def create_product_category(db: Session, payload) -> models.ProductCategory:
    category = models.ProductCategory(title=payload.title, slug=payload.slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def _admin_products_statement(
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
):
    statement = (
        select(models.Product)
        .join(models.Product.category)
        .options(selectinload(models.Product.category))
        .order_by(models.Product.title)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Product.title.ilike(needle),
                models.Product.description.ilike(needle),
            )
        )

    if category_slug:
        statement = statement.where(models.ProductCategory.slug == category_slug)

    if is_active is not None:
        statement = statement.where(models.Product.is_active.is_(is_active))

    return statement


def list_admin_products(
    db: Session,
    search: str | None,
    category_slug: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Product], dict]:
    return paginated(
        db,
        _admin_products_statement(search, category_slug, is_active),
        page,
        limit,
    )


def list_admin_products_all(
    db: Session,
    search: str | None = None,
    category_slug: str | None = None,
    is_active: bool | None = None,
) -> list[models.Product]:
    return list(db.scalars(_admin_products_statement(search, category_slug, is_active)).all())


def get_admin_product(db: Session, product_id: str) -> models.Product | None:
    return db.scalar(
        select(models.Product)
        .options(selectinload(models.Product.category))
        .where(models.Product.id == product_id)
    )


def list_products_by_ids(db: Session, product_ids: list[str]) -> list[models.Product]:
    if not product_ids:
        return []

    unique_product_ids = list(dict.fromkeys(product_ids))
    return db.scalars(select(models.Product).where(models.Product.id.in_(unique_product_ids))).all()


def list_products(
    db: Session,
    search: str | None,
    category_slug: str | None,
    min_price: float | None,
    max_price: float | None,
    page: int,
    limit: int,
) -> tuple[list[models.Product], dict]:
    statement = (
        select(models.Product)
        .join(models.Product.category)
        .options(selectinload(models.Product.category))
        .where(models.Product.is_active.is_(True))
        .order_by(models.Product.title)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Product.title.ilike(needle),
                models.Product.description.ilike(needle),
            )
        )

    if category_slug:
        statement = statement.where(models.ProductCategory.slug == category_slug)

    if min_price is not None:
        statement = statement.where(models.Product.price >= Decimal(str(min_price)))

    if max_price is not None:
        statement = statement.where(models.Product.price <= Decimal(str(max_price)))

    return paginated(db, statement, page, limit)


def get_product_by_slug(db: Session, slug: str) -> models.Product | None:
    return db.scalar(
        select(models.Product)
        .options(selectinload(models.Product.category))
        .where(models.Product.slug == slug, models.Product.is_active.is_(True))
    )


def get_product(db: Session, product_id: str) -> models.Product | None:
    return db.scalar(
        select(models.Product)
        .options(selectinload(models.Product.category))
        .where(models.Product.id == product_id, models.Product.is_active.is_(True))
    )


def create_admin_product(db: Session, payload) -> models.Product:
    product = models.Product(
        category_id=payload.categoryId,
        title=payload.title,
        slug=payload.slug,
        description=payload.description,
        price=Decimal(str(payload.price)),
        image_url=payload.imageUrl,
        stock=payload.stock,
        is_active=payload.isActive,
    )
    db.add(product)
    db.commit()
    return get_admin_product(db, product.id)


def update_admin_product(db: Session, product_id: str, payload) -> models.Product | None:
    product = db.get(models.Product, product_id)
    if product is None:
        return None

    if "categoryId" in payload.model_fields_set and payload.categoryId is not None:
        product.category_id = payload.categoryId
    if "title" in payload.model_fields_set and payload.title is not None:
        product.title = payload.title
    if "slug" in payload.model_fields_set and payload.slug is not None:
        product.slug = payload.slug
    if "description" in payload.model_fields_set and payload.description is not None:
        product.description = payload.description
    if "price" in payload.model_fields_set and payload.price is not None:
        product.price = Decimal(str(payload.price))
    if "imageUrl" in payload.model_fields_set:
        product.image_url = payload.imageUrl
    if "stock" in payload.model_fields_set and payload.stock is not None:
        product.stock = payload.stock
    if "isActive" in payload.model_fields_set and payload.isActive is not None:
        product.is_active = payload.isActive

    db.add(product)
    db.commit()
    return get_admin_product(db, product_id)


def deactivate_admin_product(db: Session, product_id: str) -> bool:
    product = db.get(models.Product, product_id)
    if product is None:
        return False

    product.is_active = False
    db.add(product)
    db.commit()
    return True


def delete_admin_product(db: Session, product_id: str) -> str:
    product = db.get(models.Product, product_id)
    if product is None:
        return "not_found"

    cart_count = db.scalar(
        select(func.count())
        .select_from(models.CartItem)
        .where(models.CartItem.product_id == product_id)
    )
    if cart_count:
        return "has_carts"

    db.delete(product)
    db.commit()
    return "deleted"
