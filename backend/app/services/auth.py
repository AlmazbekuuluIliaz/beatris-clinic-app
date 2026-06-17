from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import repositories
from app.core.config import get_settings
from app.core.security import (
    access_token_expires_in_seconds,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    hash_token,
    refresh_token_expires_at,
    verify_password,
)
from app.schemas.users import User


def register_user(db: Session, payload) -> dict:
    from app.models import UserRole

    if repositories.get_user_by_phone(db, payload.phone) is not None:
        raise ValueError("phone_exists")

    if payload.email and repositories.get_user_by_email(db, payload.email) is not None:
        raise ValueError("email_exists")

    try:
        user = repositories.create_user(db, payload, get_password_hash(payload.password))
    except IntegrityError:
        db.rollback()
        raise ValueError("integrity_error")

    if getattr(payload, "role", None) == "doctor":
        repositories.create_specialist_profile(
            db,
            user_id=user.id,
            full_name=user.full_name,
            position=payload.position,
            specialization=payload.specialization,
        )

    return _issue_auth_response(db, user)


def login_user(db: Session, payload) -> dict:
    user = repositories.get_user_by_phone(db, payload.phone)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise ValueError("invalid_credentials")

    return _issue_auth_response(db, user, remember=payload.remember)


def login_admin(db: Session, payload) -> dict:
    from app.models import UserRole

    user = repositories.get_user_by_phone_or_email(db, payload.phone)
    if (
        user is None
        or user.role != UserRole.ADMIN
        or not verify_password(payload.password, user.password_hash)
    ):
        raise ValueError("invalid_credentials")

    return _issue_auth_response(db, user, remember=payload.remember)


def refresh_access_token(db: Session, refresh_token_value: str) -> dict:
    if refresh_token_value is None:
        raise ValueError("no_refresh_token")

    try:
        payload = decode_refresh_token(refresh_token_value)
    except ValueError:
        raise ValueError("invalid_token")

    refresh_token_record = repositories.get_active_refresh_token(db, hash_token(refresh_token_value))
    if refresh_token_record is None or refresh_token_record.user_id != payload.get("sub"):
        raise ValueError("invalid_token")

    user = refresh_token_record.user
    access_token = create_access_token(user.id, user.role.value)
    return {
        "accessToken": access_token,
        "tokenType": "Bearer",
        "expiresIn": access_token_expires_in_seconds(),
    }


def logout_user(db: Session, current_user) -> None:
    repositories.revoke_user_refresh_tokens(db, current_user.id)


def _issue_auth_response(
    db: Session, user, remember: bool = True
) -> dict:
    from app.models import UserRole

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    repositories.create_refresh_token(
        db,
        user.id,
        hash_token(refresh_token),
        refresh_token_expires_at(),
    )

    result = {
        "accessToken": access_token,
        "tokenType": "Bearer",
        "expiresIn": access_token_expires_in_seconds(),
        "role": user.role.value,
        "user": User.model_validate(user).model_dump(),
        "_refreshToken": refresh_token,
        "_remember": remember,
    }

    if user.role == UserRole.DOCTOR and user.specialist_profile:
        sp = user.specialist_profile
        result["specialistProfile"] = {
            "specialistId": sp.id,
            "position": sp.position,
            "specialization": sp.specialization,
            "experienceYears": sp.experience_years,
        }

    return result
