from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from app import repositories
from app.core.security import get_password_hash
from app.schemas.users import User
from app.schemas.orders import Order
from app.schemas.appointments import Appointment
from app.schemas.recommendations import Recommendation
from app.schemas.reviews import Review


def list_admin_users(
    db: Session,
    search: str | None,
    role: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_users(db, search, role, page, limit)
    return [User.model_validate(u).model_dump() for u in items], meta


def create_admin_user(db: Session, payload) -> dict:
    user = repositories.create_admin_user(db, payload, get_password_hash(payload.password))
    return User.model_validate(user).model_dump()


def get_admin_user(db: Session, user_id: str) -> dict | None:
    user = repositories.get_user(db, user_id)
    if user is None:
        return None
    return User.model_validate(user).model_dump()


def update_admin_user(db: Session, user_id: str, payload) -> dict | None:
    password_hash = get_password_hash(payload.password) if payload.password else None
    user = repositories.update_admin_user(db, user_id, payload, password_hash)
    if user is None:
        return None
    return User.model_validate(user).model_dump()


def delete_admin_user(db: Session, user_id: str) -> bool:
    return repositories.delete_admin_user(db, user_id)


def get_sales_analytics(db: Session, date_from: date, date_to: date) -> dict:
    return repositories.get_sales_analytics(db, date_from, date_to)


def get_services_analytics(db: Session, date_from: date, date_to: date) -> dict:
    return repositories.get_services_analytics(db, date_from, date_to)


def get_settings(db: Session) -> dict:
    return repositories.get_settings_map(db)


def update_settings(db: Session, overrides: dict) -> dict:
    return repositories.replace_settings(db, overrides)


def upsert_setting(db: Session, key: str, value) -> None:
    repositories.upsert_setting(db, key, value)
