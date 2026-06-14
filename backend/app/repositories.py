import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import Select, delete, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app import models

ALLOWED_APPOINTMENT_STATUS_TRANSITIONS = {
    models.AppointmentStatus.PENDING: {
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.CANCELLED,
    },
    models.AppointmentStatus.CONFIRMED: {
        models.AppointmentStatus.COMPLETED,
        models.AppointmentStatus.CANCELLED,
        models.AppointmentStatus.PENDING,
    },
    models.AppointmentStatus.COMPLETED: {
        models.AppointmentStatus.PENDING,
    },
    models.AppointmentStatus.CANCELLED: {
        models.AppointmentStatus.PENDING,
    },
}


def pagination_meta(page: int, limit: int, total: int) -> dict:
    return {"page": page, "limit": limit, "total": total}


def paginated(db: Session, statement: Select, page: int, limit: int) -> tuple[list, dict]:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    total_statement = select(func.count()).select_from(statement.order_by(None).subquery())
    total = db.scalar(total_statement) or 0
    items = db.scalars(statement.offset((page - 1) * limit).limit(limit)).all()
    return items, pagination_meta(page, limit, total)


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
    """Hard-delete a service category. Returns 'not_found', 'has_services' or 'deleted'.

    Удаление блокируется, пока на категорию ссылаются услуги (FK без ON DELETE).
    """
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


def get_clinic_info(db: Session) -> models.ClinicInfo | None:
    return db.scalar(select(models.ClinicInfo).order_by(models.ClinicInfo.created_at).limit(1))


def update_clinic_info(db: Session, payload) -> models.ClinicInfo | None:
    info = get_clinic_info(db)
    if info is None:
        return None

    if "name" in payload.model_fields_set and payload.name is not None:
        info.name = payload.name
    if "description" in payload.model_fields_set and payload.description is not None:
        info.description = payload.description
    if "address" in payload.model_fields_set and payload.address is not None:
        info.address = payload.address
    if "phone" in payload.model_fields_set and payload.phone is not None:
        info.phone = payload.phone
    if "whatsapp" in payload.model_fields_set:
        info.whatsapp = payload.whatsapp
    if "instagram" in payload.model_fields_set:
        info.instagram = payload.instagram
    if "workingHours" in payload.model_fields_set and payload.workingHours is not None:
        info.working_hours = payload.workingHours
    if "mapUrl" in payload.model_fields_set:
        info.map_url = payload.mapUrl

    db.add(info)
    db.commit()
    db.refresh(info)
    return info


def get_user(db: Session, user_id: str) -> models.User | None:
    return db.get(models.User, user_id)


def get_user_by_phone(db: Session, phone: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.phone == phone))


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email))


def get_user_by_phone_or_email(db: Session, identifier: str) -> models.User | None:
    normalized_identifier = identifier.strip()
    if "@" in normalized_identifier:
        return db.scalar(
            select(models.User).where(
                func.lower(models.User.email) == normalized_identifier.lower()
            )
        )
    return get_user_by_phone(db, normalized_identifier)


def create_user(db: Session, payload, password_hash: str) -> models.User:
    user = models.User(
        full_name=payload.fullName,
        phone=payload.phone,
        email=payload.email,
        password_hash=password_hash,
        role=models.UserRole.PATIENT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_admin_users(
    db: Session,
    search: str | None,
    role: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.User], dict]:
    statement = select(models.User).order_by(models.User.created_at.desc(), models.User.full_name)

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.User.full_name.ilike(needle),
                models.User.phone.ilike(needle),
                models.User.email.ilike(needle),
            )
        )

    if role:
        statement = statement.where(models.User.role == models.UserRole(role))

    return paginated(db, statement, page, limit)


def create_admin_user(db: Session, payload, password_hash: str) -> models.User:
    user = models.User(
        full_name=payload.fullName,
        phone=payload.phone,
        email=payload.email,
        password_hash=password_hash,
        role=models.UserRole(payload.role),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_admin_user(
    db: Session,
    user_id: str,
    payload,
    password_hash: str | None = None,
) -> models.User | None:
    user = db.get(models.User, user_id)
    if user is None:
        return None

    if "fullName" in payload.model_fields_set and payload.fullName is not None:
        user.full_name = payload.fullName
    if "phone" in payload.model_fields_set and payload.phone is not None:
        user.phone = payload.phone
    if "email" in payload.model_fields_set:
        user.email = payload.email
    if "role" in payload.model_fields_set and payload.role is not None:
        user.role = models.UserRole(payload.role)
    if password_hash is not None:
        user.password_hash = password_hash

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_admin_user(db: Session, user_id: str) -> bool:
    user = db.get(models.User, user_id)
    if user is None:
        return False

    db.delete(user)
    db.commit()
    return True


def update_user_profile(db: Session, user_id: str, payload) -> models.User | None:
    user = db.get(models.User, user_id)
    if user is None:
        return None

    if "fullName" in payload.model_fields_set and payload.fullName is not None:
        user.full_name = payload.fullName
    if "phone" in payload.model_fields_set and payload.phone is not None:
        user.phone = payload.phone
    if "email" in payload.model_fields_set:
        user.email = payload.email

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_refresh_token(
    db: Session,
    user_id: str,
    token_hash: str,
    expires_at: datetime,
) -> models.RefreshToken:
    refresh_token = models.RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at.replace(tzinfo=None),
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_active_refresh_token(db: Session, token_hash: str) -> models.RefreshToken | None:
    return db.scalar(
        select(models.RefreshToken)
        .options(selectinload(models.RefreshToken.user))
        .where(
            models.RefreshToken.token_hash == token_hash,
            models.RefreshToken.revoked_at.is_(None),
            models.RefreshToken.expires_at > datetime.utcnow(),
        )
    )


def revoke_refresh_token(db: Session, refresh_token: models.RefreshToken) -> None:
    refresh_token.revoked_at = datetime.utcnow()
    db.add(refresh_token)
    db.commit()


def revoke_user_refresh_tokens(db: Session, user_id: str) -> None:
    tokens = db.scalars(
        select(models.RefreshToken).where(
            models.RefreshToken.user_id == user_id,
            models.RefreshToken.revoked_at.is_(None),
        )
    ).all()
    for token in tokens:
        token.revoked_at = datetime.utcnow()
        db.add(token)
    db.commit()


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
    """Hard-delete a service. Returns 'not_found', 'has_appointments' or 'deleted'.

    Specialist links cascade away, but appointments reference the service without an
    ON DELETE cascade, so the delete is blocked while any appointment points at it.
    """
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
    """Hard-delete a product. Returns 'not_found', 'has_carts' or 'deleted'.

    Wishlist and recommendation links cascade away (CASCADE). Order items keep
    their row but lose the product reference (SET NULL). Cart items have no
    cascade — if the product still sits in someone's cart, deletion is blocked
    so the user's cart stays consistent.
    """
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


def order_detail_options() -> tuple:
    return (
        selectinload(models.Order.user),
        selectinload(models.Order.items).selectinload(models.OrderItem.product).selectinload(models.Product.category),
        selectinload(models.Order.payments),
    )


def _admin_orders_statement(
    order_status: str | None,
    payment_status: str | None,
    search: str | None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    statement = (
        select(models.Order)
        .join(models.Order.user)
        .options(*order_detail_options())
        .order_by(models.Order.created_at.desc())
    )

    if order_status:
        statement = statement.where(models.Order.order_status == models.OrderStatus(order_status))

    if payment_status:
        statement = statement.where(models.Order.payment_status == models.PaymentStatus(payment_status))

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Order.order_number.ilike(needle),
                models.Order.recipient_name.ilike(needle),
                models.Order.recipient_phone.ilike(needle),
                models.User.full_name.ilike(needle),
                models.User.phone.ilike(needle),
            )
        )

    if date_from is not None:
        statement = statement.where(func.date(models.Order.created_at) >= date_from)

    if date_to is not None:
        statement = statement.where(func.date(models.Order.created_at) <= date_to)

    return statement


def list_admin_orders(
    db: Session,
    order_status: str | None,
    payment_status: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Order], dict]:
    return paginated(
        db,
        _admin_orders_statement(order_status, payment_status, search),
        page,
        limit,
    )


def list_admin_orders_all(
    db: Session,
    order_status: str | None = None,
    payment_status: str | None = None,
    search: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[models.Order]:
    return list(
        db.scalars(
            _admin_orders_statement(order_status, payment_status, search, date_from, date_to)
        ).all()
    )


def get_admin_order(db: Session, order_id: str) -> models.Order | None:
    return db.scalar(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.id == order_id)
    )


ORDER_TO_PAYMENT_STATUS = {
    models.OrderStatus.CREATED: models.PaymentStatus.PENDING,
    models.OrderStatus.PAID: models.PaymentStatus.PAID,
    models.OrderStatus.PROCESSING: models.PaymentStatus.PAID,
    models.OrderStatus.DELIVERED: models.PaymentStatus.PAID,
}


def _payment_status_for_order(new_order_status, current_payment_status):
    if new_order_status == models.OrderStatus.CANCELLED:
        if current_payment_status in (models.PaymentStatus.PAID, models.PaymentStatus.REFUNDED):
            return models.PaymentStatus.REFUNDED
        return models.PaymentStatus.FAILED
    return ORDER_TO_PAYMENT_STATUS[new_order_status]


def update_admin_order_status(db: Session, order_id: str, payload) -> models.Order | None:
    order = db.get(models.Order, order_id)
    if order is None:
        return None

    if "orderStatus" in payload.model_fields_set and payload.orderStatus is not None:
        new_status = models.OrderStatus(payload.orderStatus)
        order.order_status = new_status
        order.payment_status = _payment_status_for_order(new_status, order.payment_status)

    db.add(order)
    db.commit()
    return get_admin_order(db, order_id)


def list_wishlist_items(db: Session, user_id: str) -> list[models.WishlistItem]:
    return db.scalars(
        select(models.WishlistItem)
        .options(selectinload(models.WishlistItem.product).selectinload(models.Product.category))
        .where(models.WishlistItem.user_id == user_id)
        .order_by(models.WishlistItem.created_at.desc())
    ).all()


def add_wishlist_item(db: Session, user_id: str, product_id: str) -> models.WishlistItem:
    item = db.scalar(
        select(models.WishlistItem).where(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.product_id == product_id,
        )
    )
    if item is None:
        item = models.WishlistItem(user_id=user_id, product_id=product_id)
        db.add(item)
        db.commit()
    return db.scalar(
        select(models.WishlistItem)
        .options(selectinload(models.WishlistItem.product).selectinload(models.Product.category))
        .where(models.WishlistItem.id == item.id)
    )


def delete_wishlist_item(db: Session, user_id: str, product_id: str) -> bool:
    item = db.scalar(
        select(models.WishlistItem).where(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.product_id == product_id,
        )
    )
    if item is None:
        return False

    db.delete(item)
    db.commit()
    return True


def list_cart_items(db: Session, user_id: str) -> list[models.CartItem]:
    return db.scalars(
        select(models.CartItem)
        .options(selectinload(models.CartItem.product).selectinload(models.Product.category))
        .where(models.CartItem.user_id == user_id)
        .order_by(models.CartItem.created_at)
    ).all()


def add_cart_item(
    db: Session,
    user_id: str,
    product: models.Product,
    quantity: int,
) -> list[models.CartItem]:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.user_id == user_id,
            models.CartItem.product_id == product.id,
        )
    )
    if item is None:
        item = models.CartItem(
            user_id=user_id,
            product_id=product.id,
            quantity=quantity,
            price=product.price,
        )
    else:
        item.quantity += quantity
        item.price = product.price

    db.add(item)
    db.commit()
    return list_cart_items(db, user_id)


def update_cart_item(db: Session, user_id: str, item_id: str, quantity: int) -> list[models.CartItem] | None:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user_id,
        )
    )
    if item is None:
        return None

    item.quantity = quantity
    db.add(item)
    db.commit()
    return list_cart_items(db, user_id)


def delete_cart_item(db: Session, user_id: str, item_id: str) -> list[models.CartItem] | None:
    item = db.scalar(
        select(models.CartItem).where(
            models.CartItem.id == item_id,
            models.CartItem.user_id == user_id,
        )
    )
    if item is None:
        return None

    db.delete(item)
    db.commit()
    return list_cart_items(db, user_id)


def _next_order_number(db: Session) -> str:
    prefix = f"BT-{datetime.now():%y%m%d}-"
    last = db.scalar(
        select(models.Order.order_number)
        .where(models.Order.order_number.like(f"{prefix}%"))
        .order_by(models.Order.order_number.desc())
        .limit(1)
    )
    sequence = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{sequence:03d}"


def create_order_from_cart(db: Session, user_id: str, payload, cart_items: list[models.CartItem]) -> models.Order:
    total_price = sum((item.price * item.quantity for item in cart_items), Decimal("0.00"))
    order = models.Order(
        order_number=_next_order_number(db),
        user_id=user_id,
        total_price=total_price,
        payment_status=models.PaymentStatus.PENDING,
        order_status=models.OrderStatus.CREATED,
        payment_method=models.PaymentMethod(payload.paymentMethod),
        delivery_method=models.DeliveryMethod(payload.deliveryMethod),
        delivery_address=payload.deliveryAddress,
        recipient_name=payload.recipientName,
        recipient_phone=payload.recipientPhone,
        comment=payload.comment,
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_title=item.product.title,
                product_slug=item.product.slug,
                quantity=item.quantity,
                price=item.price,
                subtotal=item.price * item.quantity,
            )
        )
        db.delete(item)

    db.commit()
    return get_user_order(db, user_id, order.id)


def create_admin_order(db: Session, payload) -> models.Order | None:
    line_items: list[tuple[models.Product, int, Decimal]] = []
    total_price = Decimal("0.00")
    for item in payload.items:
        product = get_product(db, item.productId)
        if product is None or not product.is_active:
            return None
        subtotal = product.price * item.quantity
        total_price += subtotal
        line_items.append((product, item.quantity, subtotal))

    order = models.Order(
        order_number=_next_order_number(db),
        user_id=payload.userId,
        total_price=total_price,
        payment_status=models.PaymentStatus.PENDING,
        order_status=models.OrderStatus.CREATED,
        payment_method=models.PaymentMethod(payload.paymentMethod),
        delivery_method=models.DeliveryMethod(payload.deliveryMethod),
        delivery_address=payload.deliveryAddress,
        recipient_name=payload.recipientName,
        recipient_phone=payload.recipientPhone,
        comment=payload.comment,
    )
    db.add(order)
    db.flush()

    for product, quantity, subtotal in line_items:
        db.add(
            models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_title=product.title,
                product_slug=product.slug,
                quantity=quantity,
                price=product.price,
                subtotal=subtotal,
            )
        )

    db.commit()
    return get_admin_order(db, order.id)


def list_user_orders(db: Session, user_id: str) -> list[models.Order]:
    return db.scalars(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.user_id == user_id)
        .order_by(models.Order.created_at.desc())
    ).all()


def get_user_order(db: Session, user_id: str, order_id: str) -> models.Order | None:
    return db.scalar(
        select(models.Order)
        .options(*order_detail_options())
        .where(models.Order.id == order_id, models.Order.user_id == user_id)
    )


def create_order_payment(db: Session, order: models.Order) -> models.Payment:
    payment = models.Payment(
        order_id=order.id,
        payment_url=f"https://payments.example.test/orders/{order.id}",
        provider_payment_id=None,
        status=models.PaymentStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def list_reviews(db: Session, page: int, limit: int) -> tuple[list[models.Review], dict]:
    statement = (
        select(models.Review)
        .where(models.Review.is_published.is_(True))
        .order_by(
            models.Review.sort_order,
            models.Review.published_at.desc(),
            models.Review.created_at.desc(),
        )
    )
    return paginated(db, statement, page, limit)


def list_admin_reviews(
    db: Session,
    search: str | None,
    is_published: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Review], dict]:
    statement = select(models.Review).order_by(
        models.Review.sort_order,
        models.Review.created_at.desc(),
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Review.author_name.ilike(needle),
                models.Review.text.ilike(needle),
                models.Review.source.ilike(needle),
            )
        )

    if is_published is not None:
        statement = statement.where(models.Review.is_published.is_(is_published))

    return paginated(db, statement, page, limit)


def get_admin_review(db: Session, review_id: str) -> models.Review | None:
    return db.get(models.Review, review_id)


def create_admin_review(db: Session, payload) -> models.Review:
    review = models.Review(
        author_name=payload.authorName,
        rating=payload.rating,
        text=payload.text,
        source=payload.source,
        source_url=payload.sourceUrl,
        is_published=payload.isPublished,
        sort_order=payload.sortOrder,
        published_at=payload.publishedAt,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def update_admin_review(db: Session, review_id: str, payload) -> models.Review | None:
    review = db.get(models.Review, review_id)
    if review is None:
        return None

    if "authorName" in payload.model_fields_set and payload.authorName is not None:
        review.author_name = payload.authorName
    if "rating" in payload.model_fields_set and payload.rating is not None:
        review.rating = payload.rating
    if "text" in payload.model_fields_set and payload.text is not None:
        review.text = payload.text
    if "source" in payload.model_fields_set and payload.source is not None:
        review.source = payload.source
    if "sourceUrl" in payload.model_fields_set:
        review.source_url = payload.sourceUrl
    if "isPublished" in payload.model_fields_set and payload.isPublished is not None:
        review.is_published = payload.isPublished
    if "sortOrder" in payload.model_fields_set and payload.sortOrder is not None:
        review.sort_order = payload.sortOrder
    if "publishedAt" in payload.model_fields_set:
        review.published_at = payload.publishedAt

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def delete_admin_review(db: Session, review_id: str) -> bool:
    review = db.get(models.Review, review_id)
    if review is None:
        return False

    db.delete(review)
    db.commit()
    return True


def recommendation_detail_options() -> tuple:
    return (
        selectinload(models.Recommendation.patient),
        selectinload(models.Recommendation.doctor),
        selectinload(models.Recommendation.appointment),
        selectinload(models.Recommendation.products),
    )


def list_admin_recommendations(
    db: Session,
    patient_id: str | None,
    doctor_id: str | None,
    appointment_id: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Recommendation], dict]:
    statement = (
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .order_by(models.Recommendation.created_at.desc())
    )

    if patient_id:
        statement = statement.where(models.Recommendation.patient_id == patient_id)

    if doctor_id:
        statement = statement.where(models.Recommendation.doctor_id == doctor_id)

    if appointment_id:
        statement = statement.where(models.Recommendation.appointment_id == appointment_id)

    if search:
        statement = statement.where(models.Recommendation.text.ilike(f"%{search}%"))

    return paginated(db, statement, page, limit)


def list_patient_recommendations(db: Session, patient_id: str) -> list[models.Recommendation]:
    return db.scalars(
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .where(models.Recommendation.patient_id == patient_id)
        .order_by(models.Recommendation.created_at.desc())
    ).all()


def get_admin_recommendation(
    db: Session,
    recommendation_id: str,
) -> models.Recommendation | None:
    return db.scalar(
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .where(models.Recommendation.id == recommendation_id)
    )


def create_admin_recommendation(db: Session, payload) -> models.Recommendation:
    recommendation = models.Recommendation(
        patient_id=payload.patientId,
        doctor_id=payload.doctorId,
        appointment_id=payload.appointmentId,
        text=payload.text,
    )
    db.add(recommendation)
    db.flush()
    replace_recommendation_products(db, recommendation.id, payload.productIds)
    db.commit()
    return get_admin_recommendation(db, recommendation.id)


def update_admin_recommendation(
    db: Session,
    recommendation_id: str,
    payload,
) -> models.Recommendation | None:
    recommendation = db.get(models.Recommendation, recommendation_id)
    if recommendation is None:
        return None

    if "patientId" in payload.model_fields_set and payload.patientId is not None:
        recommendation.patient_id = payload.patientId
    if "doctorId" in payload.model_fields_set and payload.doctorId is not None:
        recommendation.doctor_id = payload.doctorId
    if "appointmentId" in payload.model_fields_set:
        recommendation.appointment_id = payload.appointmentId
    if "text" in payload.model_fields_set and payload.text is not None:
        recommendation.text = payload.text

    db.add(recommendation)
    if "productIds" in payload.model_fields_set and payload.productIds is not None:
        replace_recommendation_products(db, recommendation_id, payload.productIds)

    db.commit()
    return get_admin_recommendation(db, recommendation_id)


def delete_admin_recommendation(db: Session, recommendation_id: str) -> bool:
    recommendation = db.get(models.Recommendation, recommendation_id)
    if recommendation is None:
        return False

    db.delete(recommendation)
    db.commit()
    return True


def replace_recommendation_products(
    db: Session,
    recommendation_id: str,
    product_ids: list[str],
) -> None:
    db.execute(
        delete(models.RecommendationProduct).where(
            models.RecommendationProduct.recommendation_id == recommendation_id,
        )
    )
    for product_id in dict.fromkeys(product_ids):
        db.add(models.RecommendationProduct(recommendation_id=recommendation_id, product_id=product_id))


def get_specialist_by_user_id(db: Session, user_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.user_id == user_id, models.Specialist.is_active.is_(True))
    )


def list_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Specialist], dict]:
    statement = (
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.is_active.is_(True))
        .order_by(models.Specialist.full_name)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Specialist.full_name.ilike(needle),
                models.Specialist.position.ilike(needle),
                models.Specialist.specialization.ilike(needle),
            )
        )

    if service_id:
        statement = statement.join(models.Specialist.services).where(models.Service.id == service_id)

    return paginated(db, statement, page, limit)


def get_specialist(db: Session, specialist_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.id == specialist_id, models.Specialist.is_active.is_(True))
    )


def list_admin_specialists(
    db: Session,
    search: str | None,
    service_id: str | None,
    is_active: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.Specialist], dict]:
    statement = (
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .order_by(models.Specialist.full_name)
    )

    if search:
        needle = f"%{search}%"
        statement = statement.where(
            or_(
                models.Specialist.full_name.ilike(needle),
                models.Specialist.position.ilike(needle),
                models.Specialist.specialization.ilike(needle),
            )
        )

    if service_id:
        statement = statement.join(models.Specialist.services).where(models.Service.id == service_id)

    if is_active is not None:
        statement = statement.where(models.Specialist.is_active.is_(is_active))

    return paginated(db, statement, page, limit)


def get_admin_specialist(db: Session, specialist_id: str) -> models.Specialist | None:
    return db.scalar(
        select(models.Specialist)
        .options(selectinload(models.Specialist.services))
        .where(models.Specialist.id == specialist_id)
    )


def create_admin_specialist(db: Session, payload) -> models.Specialist:
    specialist = models.Specialist(
        user_id=payload.userId,
        full_name=payload.fullName,
        position=payload.position,
        specialization=payload.specialization,
        experience_years=payload.experienceYears,
        photo_url=payload.photoUrl,
        is_active=payload.isActive,
    )
    db.add(specialist)
    db.flush()
    replace_specialist_services(db, specialist.id, payload.serviceIds)
    db.commit()
    return get_admin_specialist(db, specialist.id)


def update_admin_specialist(db: Session, specialist_id: str, payload) -> models.Specialist | None:
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return None

    if "userId" in payload.model_fields_set:
        specialist.user_id = payload.userId
    if "fullName" in payload.model_fields_set and payload.fullName is not None:
        specialist.full_name = payload.fullName
    if "position" in payload.model_fields_set and payload.position is not None:
        specialist.position = payload.position
    if "specialization" in payload.model_fields_set and payload.specialization is not None:
        specialist.specialization = payload.specialization
    if "experienceYears" in payload.model_fields_set:
        specialist.experience_years = payload.experienceYears
    if "photoUrl" in payload.model_fields_set:
        specialist.photo_url = payload.photoUrl
    if "isActive" in payload.model_fields_set and payload.isActive is not None:
        specialist.is_active = payload.isActive

    db.add(specialist)
    if "serviceIds" in payload.model_fields_set and payload.serviceIds is not None:
        replace_specialist_services(db, specialist_id, payload.serviceIds)

    db.commit()
    return get_admin_specialist(db, specialist_id)


def deactivate_admin_specialist(db: Session, specialist_id: str) -> bool:
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return False

    specialist.is_active = False
    db.add(specialist)
    db.commit()
    return True


def delete_admin_specialist(db: Session, specialist_id: str) -> str:
    """Hard-delete a specialist. Returns 'not_found', 'has_appointments' or 'deleted'.

    Service links and schedule items cascade away, but appointments reference the
    specialist without an ON DELETE cascade, so the delete is blocked while any
    appointment points at them.
    """
    specialist = db.get(models.Specialist, specialist_id)
    if specialist is None:
        return "not_found"

    appointment_count = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.specialist_id == specialist_id)
    )
    if appointment_count:
        return "has_appointments"

    db.delete(specialist)
    db.commit()
    return "deleted"


def replace_specialist_services(db: Session, specialist_id: str, service_ids: list[str]) -> None:
    db.execute(
        delete(models.SpecialistService).where(
            models.SpecialistService.specialist_id == specialist_id,
        )
    )
    for service_id in dict.fromkeys(service_ids):
        db.add(models.SpecialistService(specialist_id=specialist_id, service_id=service_id))


def doctor_schedule_detail_options() -> tuple:
    return (
        selectinload(models.DoctorSchedule.specialist).selectinload(models.Specialist.services),
    )


def list_admin_doctor_schedule(
    db: Session,
    specialist_id: str | None,
    schedule_date: date | None,
    is_available: bool | None,
    page: int,
    limit: int,
) -> tuple[list[models.DoctorSchedule], dict]:
    statement = (
        select(models.DoctorSchedule)
        .join(models.Specialist, models.DoctorSchedule.specialist_id == models.Specialist.id)
        .options(*doctor_schedule_detail_options())
        .where(models.Specialist.is_active.is_(True))
        .order_by(
            models.DoctorSchedule.schedule_date.desc(),
            models.DoctorSchedule.start_time.asc(),
        )
    )

    if specialist_id:
        statement = statement.where(models.DoctorSchedule.specialist_id == specialist_id)

    if schedule_date:
        statement = statement.where(models.DoctorSchedule.schedule_date == schedule_date)

    if is_available is not None:
        statement = statement.where(models.DoctorSchedule.is_available.is_(is_available))

    return paginated(db, statement, page, limit)


def list_doctor_schedule(db: Session, specialist_id: str) -> list[models.DoctorSchedule]:
    return db.scalars(
        select(models.DoctorSchedule)
        .options(*doctor_schedule_detail_options())
        .where(models.DoctorSchedule.specialist_id == specialist_id)
        .order_by(models.DoctorSchedule.schedule_date, models.DoctorSchedule.start_time)
    ).all()


def get_admin_doctor_schedule_item(
    db: Session,
    schedule_id: str,
) -> models.DoctorSchedule | None:
    return db.scalar(
        select(models.DoctorSchedule)
        .options(*doctor_schedule_detail_options())
        .where(models.DoctorSchedule.id == schedule_id)
    )


def create_admin_doctor_schedule_item(db: Session, payload) -> models.DoctorSchedule:
    schedule_item = models.DoctorSchedule(
        specialist_id=payload.specialistId,
        schedule_date=payload.parsed_date,
        start_time=payload.parsed_start_time,
        end_time=payload.parsed_end_time,
        is_available=payload.isAvailable,
    )
    db.add(schedule_item)
    db.commit()
    return get_admin_doctor_schedule_item(db, schedule_item.id)


def update_admin_doctor_schedule_item(
    db: Session,
    schedule_id: str,
    payload,
) -> models.DoctorSchedule | None:
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return None

    if "specialistId" in payload.model_fields_set and payload.specialistId is not None:
        schedule_item.specialist_id = payload.specialistId
    if "date" in payload.model_fields_set and payload.date is not None:
        schedule_item.schedule_date = payload.parsed_date
    if "startTime" in payload.model_fields_set and payload.startTime is not None:
        schedule_item.start_time = payload.parsed_start_time
    if "endTime" in payload.model_fields_set and payload.endTime is not None:
        schedule_item.end_time = payload.parsed_end_time
    if "isAvailable" in payload.model_fields_set and payload.isAvailable is not None:
        schedule_item.is_available = payload.isAvailable

    if schedule_item.start_time >= schedule_item.end_time:
        raise ValueError("startTime must be earlier than endTime")

    db.add(schedule_item)
    db.commit()
    return get_admin_doctor_schedule_item(db, schedule_id)


def deactivate_admin_doctor_schedule_item(db: Session, schedule_id: str) -> bool:
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return False

    schedule_item.is_available = False
    db.add(schedule_item)
    db.commit()
    return True


def delete_admin_doctor_schedule_item(db: Session, schedule_id: str) -> bool:
    """Hard-delete a schedule slot row (irreversible)."""
    schedule_item = db.get(models.DoctorSchedule, schedule_id)
    if schedule_item is None:
        return False

    db.delete(schedule_item)
    db.commit()
    return True


def list_schedule_items(
    db: Session,
    specialist_id: str,
    schedule_date: date,
) -> list[models.DoctorSchedule]:
    return db.scalars(
        select(models.DoctorSchedule)
        .join(models.Specialist, models.DoctorSchedule.specialist_id == models.Specialist.id)
        .where(
            models.DoctorSchedule.specialist_id == specialist_id,
            models.DoctorSchedule.schedule_date == schedule_date,
            models.DoctorSchedule.is_available.is_(True),
            models.Specialist.is_active.is_(True),
        )
        .order_by(models.DoctorSchedule.start_time)
    ).all()


def list_busy_appointments(
    db: Session,
    specialist_id: str,
    appointment_date: date,
    exclude_appointment_id: str | None = None,
) -> list[models.Appointment]:
    statement = (
        select(models.Appointment)
        .options(selectinload(models.Appointment.service))
        .where(
            models.Appointment.specialist_id == specialist_id,
            models.Appointment.appointment_date == appointment_date,
            models.Appointment.status != models.AppointmentStatus.CANCELLED,
        )
    )
    if exclude_appointment_id is not None:
        statement = statement.where(models.Appointment.id != exclude_appointment_id)
    return db.scalars(statement).all()


def is_appointment_slot_available(
    db: Session,
    specialist_id: str,
    service: models.Service,
    appointment_date: date,
    appointment_time,
    exclude_appointment_id: str | None = None,
) -> bool:
    duration = service.duration_minutes or 30
    start = appointment_time.hour * 60 + appointment_time.minute
    candidate = (start, start + duration)

    schedule_match = False
    for schedule_item in list_schedule_items(db, specialist_id, appointment_date):
        schedule_start = schedule_item.start_time.hour * 60 + schedule_item.start_time.minute
        schedule_end = schedule_item.end_time.hour * 60 + schedule_item.end_time.minute
        if schedule_start <= candidate[0] and candidate[1] <= schedule_end:
            schedule_match = True
            break
    if not schedule_match:
        return False

    busy_intervals = []
    for appointment in list_busy_appointments(db, specialist_id, appointment_date, exclude_appointment_id):
        busy_start = appointment.appointment_time.hour * 60 + appointment.appointment_time.minute
        busy_end = busy_start + (appointment.service.duration_minutes or 30)
        busy_intervals.append((busy_start, busy_end))

    return not any(candidate[0] < busy[1] and busy[0] < candidate[1] for busy in busy_intervals)


def appointment_detail_options() -> tuple:
    return (
        selectinload(models.Appointment.service).selectinload(models.Service.category),
        selectinload(models.Appointment.specialist).selectinload(models.Specialist.services),
        selectinload(models.Appointment.status_history).selectinload(models.AppointmentStatusHistory.admin),
    )


def is_appointment_status_transition_allowed(
    current_status: models.AppointmentStatus,
    next_status: models.AppointmentStatus | str,
) -> bool:
    next_status = models.AppointmentStatus(next_status)
    if current_status == next_status:
        return True
    return next_status in ALLOWED_APPOINTMENT_STATUS_TRANSITIONS[current_status]


def list_admin_appointments(
    db: Session,
    appointment_status: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Appointment], dict]:
    statement = (
        select(models.Appointment)
        .options(*appointment_detail_options())
        .order_by(
            models.Appointment.appointment_date.desc(),
            models.Appointment.appointment_time.asc(),
        )
    )

    if appointment_status:
        statement = statement.where(models.Appointment.status == models.AppointmentStatus(appointment_status))

    return paginated(db, statement, page, limit)


def list_user_appointments(db: Session, user_id: str) -> list[models.Appointment]:
    return db.scalars(
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.patient_id == user_id)
        .order_by(models.Appointment.appointment_date.desc(), models.Appointment.appointment_time.desc())
    ).all()


def list_doctor_appointments(db: Session, specialist_id: str) -> list[models.Appointment]:
    return db.scalars(
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.specialist_id == specialist_id)
        .order_by(models.Appointment.appointment_date.desc(), models.Appointment.appointment_time.desc())
    ).all()


def get_appointment(db: Session, appointment_id: str) -> models.Appointment | None:
    return db.scalar(
        select(models.Appointment)
        .options(*appointment_detail_options())
        .where(models.Appointment.id == appointment_id)
    )


def update_appointment_status(
    db: Session,
    appointment_id: str,
    appointment_status: str,
    admin_id: str | None = None,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    previous_status = appointment.status
    next_status = models.AppointmentStatus(appointment_status)
    appointment.status = next_status
    db.add(appointment)
    if previous_status != next_status:
        db.add(
            models.AppointmentStatusHistory(
                appointment_id=appointment_id,
                admin_id=admin_id,
                previous_status=previous_status,
                new_status=next_status,
            )
        )
    db.commit()
    return get_appointment(db, appointment_id)


def reschedule_appointment(
    db: Session,
    appointment_id: str,
    payload,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    appointment.specialist_id = payload.specialistId
    appointment.appointment_date = payload.parsed_date
    appointment.appointment_time = payload.parsed_time
    if "comment" in payload.model_fields_set:
        appointment.comment = payload.comment
    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def update_appointment_contact(
    db: Session,
    appointment_id: str,
    payload,
) -> models.Appointment | None:
    appointment = db.get(models.Appointment, appointment_id)
    if appointment is None:
        return None

    appointment.patient_contact_status = payload.patientContactStatus
    appointment.patient_contact_comment = payload.patientContactComment
    appointment.patient_contacted_at = datetime.utcnow()
    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def cancel_user_appointment(db: Session, user_id: str, appointment_id: str) -> models.Appointment | None:
    appointment = db.scalar(
        select(models.Appointment).where(
            models.Appointment.id == appointment_id,
            models.Appointment.patient_id == user_id,
        )
    )
    if appointment is None:
        return None

    appointment.status = models.AppointmentStatus.CANCELLED
    db.add(appointment)
    db.commit()
    return get_appointment(db, appointment_id)


def _next_appointment_number(db: Session) -> str:
    prefix = f"AP-{datetime.now():%y%m%d}-"
    last = db.scalar(
        select(models.Appointment.appointment_number)
        .where(models.Appointment.appointment_number.like(f"{prefix}%"))
        .order_by(models.Appointment.appointment_number.desc())
        .limit(1)
    )
    sequence = int(last.rsplit("-", 1)[-1]) + 1 if last else 1
    return f"{prefix}{sequence:03d}"


def create_appointment(
    db: Session,
    payload,
    patient_id: str | None = None,
) -> models.Appointment:
    appointment = models.Appointment(
        appointment_number=_next_appointment_number(db),
        patient_id=patient_id,
        patient_name=payload.patientName,
        patient_phone=payload.patientPhone,
        service_id=payload.serviceId,
        specialist_id=payload.specialistId,
        appointment_date=payload.parsed_date,
        appointment_time=payload.parsed_time,
        requested_date=payload.parsed_date,
        requested_time=payload.parsed_time,
        status=models.AppointmentStatus.PENDING,
        comment=payload.comment,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return db.scalar(
        select(models.Appointment)
        .options(
            *appointment_detail_options(),
        )
        .where(models.Appointment.id == appointment.id)
    )


LOW_STOCK_THRESHOLD = 5


def _enum_key(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def admin_analytics(db: Session, period_days: int, reference_date: date) -> dict:
    """Server-side dashboard aggregates over the full dataset (not paginated).

    `reference_date` is treated as "today"; `period_days` defines the trailing
    window [reference_date - (period_days - 1), reference_date] used for the
    in-period metrics and the top lists.
    """
    today = reference_date
    period_start = today - timedelta(days=period_days - 1)

    # --- Appointments ---
    appt_by_status = {status.value: 0 for status in models.AppointmentStatus}
    total_appointments = 0
    for status_value, count in db.execute(
        select(models.Appointment.status, func.count())
        .group_by(models.Appointment.status)
    ).all():
        appt_by_status[_enum_key(status_value)] = count
        total_appointments += count

    today_appointments = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.appointment_date == today)
    ) or 0

    period_appointments = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(
            models.Appointment.appointment_date >= period_start,
            models.Appointment.appointment_date <= today,
        )
    ) or 0

    # --- Revenue / orders ---
    paid_filter = models.Order.payment_status == models.PaymentStatus.PAID
    total_paid = db.scalar(
        select(func.coalesce(func.sum(models.Order.total_price), 0)).where(paid_filter)
    ) or 0
    paid_orders = db.scalar(
        select(func.count()).select_from(models.Order).where(paid_filter)
    ) or 0
    period_revenue = db.scalar(
        select(func.coalesce(func.sum(models.Order.total_price), 0)).where(
            paid_filter,
            func.date(models.Order.created_at) >= period_start,
            func.date(models.Order.created_at) <= today,
        )
    ) or 0
    average_order_value = float(total_paid) / paid_orders if paid_orders else 0.0

    total_orders = db.scalar(select(func.count()).select_from(models.Order)) or 0
    orders_by_payment = {status.value: 0 for status in models.PaymentStatus}
    for status_value, count in db.execute(
        select(models.Order.payment_status, func.count())
        .group_by(models.Order.payment_status)
    ).all():
        orders_by_payment[_enum_key(status_value)] = count

    orders_by_status = {status.value: 0 for status in models.OrderStatus}
    for status_value, count in db.execute(
        select(models.Order.order_status, func.count())
        .group_by(models.Order.order_status)
    ).all():
        orders_by_status[_enum_key(status_value)] = count

    # --- Catalog ---
    active_services = db.scalar(
        select(func.count()).select_from(models.Service).where(models.Service.is_active.is_(True))
    ) or 0
    active_products = db.scalar(
        select(func.count()).select_from(models.Product).where(models.Product.is_active.is_(True))
    ) or 0
    total_stock = db.scalar(
        select(func.coalesce(func.sum(models.Product.stock), 0)).where(models.Product.is_active.is_(True))
    ) or 0
    low_stock = db.scalar(
        select(func.count())
        .select_from(models.Product)
        .where(
            models.Product.is_active.is_(True),
            models.Product.stock < LOW_STOCK_THRESHOLD,
        )
    ) or 0

    # --- Top lists (in-period, cancelled appointments excluded) ---
    in_period_appt = (
        models.Appointment.appointment_date >= period_start,
        models.Appointment.appointment_date <= today,
        models.Appointment.status != models.AppointmentStatus.CANCELLED,
    )
    top_services = [
        {"id": service_id, "title": title, "count": count}
        for service_id, title, count in db.execute(
            select(models.Service.id, models.Service.title, func.count(models.Appointment.id))
            .join(models.Appointment, models.Appointment.service_id == models.Service.id)
            .where(*in_period_appt)
            .group_by(models.Service.id, models.Service.title)
            .order_by(func.count(models.Appointment.id).desc())
            .limit(5)
        ).all()
    ]
    top_specialists = [
        {"id": specialist_id, "title": full_name, "count": count}
        for specialist_id, full_name, count in db.execute(
            select(models.Specialist.id, models.Specialist.full_name, func.count(models.Appointment.id))
            .join(models.Appointment, models.Appointment.specialist_id == models.Specialist.id)
            .where(*in_period_appt)
            .group_by(models.Specialist.id, models.Specialist.full_name)
            .order_by(func.count(models.Appointment.id).desc())
            .limit(5)
        ).all()
    ]

    return {
        "generatedAt": datetime.now(),
        "periodDays": period_days,
        "appointments": {
            "total": total_appointments,
            "today": today_appointments,
            "inPeriod": period_appointments,
            "byStatus": appt_by_status,
        },
        "revenue": {
            "totalPaid": float(total_paid),
            "inPeriod": float(period_revenue),
            "paidOrders": paid_orders,
            "averageOrderValue": round(average_order_value, 2),
        },
        "orders": {
            "total": total_orders,
            "byPaymentStatus": orders_by_payment,
            "byOrderStatus": orders_by_status,
        },
        "catalog": {
            "activeServices": active_services,
            "activeProducts": active_products,
            "totalStock": int(total_stock),
            "lowStock": low_stock,
        },
        "topServices": top_services,
        "topSpecialists": top_specialists,
    }


def get_settings_map(db: Session) -> dict:
    """Все настройки админ-панели в виде словаря с раскодированными значениями."""
    result: dict = {}
    for row in db.scalars(select(models.AppSetting)).all():
        try:
            result[row.key] = json.loads(row.value)
        except (ValueError, TypeError):
            result[row.key] = row.value
    return result


def replace_settings(db: Session, overrides: dict) -> dict:
    """Полностью заменяет набор настроек переданным словарём.

    Семантика повторяет прежнее localStorage-хранилище: сохраняется именно
    набор переопределений поверх значений по умолчанию, поэтому старые ключи,
    которых нет в `overrides`, удаляются (это и есть «Сбросить» при пустом dict).
    """
    db.execute(delete(models.AppSetting))
    for key, value in overrides.items():
        db.add(models.AppSetting(key=str(key), value=json.dumps(value)))
    db.commit()
    return get_settings_map(db)


def upsert_setting(db: Session, key: str, value) -> None:
    """Точечно создаёт или обновляет одну настройку, не трогая остальные.

    В отличие от replace_settings, используется для боковых операций (например,
    загрузка PDF лицензии), чтобы случайно не сбросить остальные поля формы.
    Если value=None — запись удаляется.
    """
    row = db.get(models.AppSetting, key)
    if value is None:
        if row is not None:
            db.delete(row)
            db.commit()
        return
    serialized = json.dumps(value)
    if row is None:
        db.add(models.AppSetting(key=key, value=serialized))
    else:
        row.value = serialized
    db.commit()
