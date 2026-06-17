from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models
from app.repositories.base import paginated


def get_user(db: Session, user_id: str) -> models.User | None:
    return db.get(models.User, user_id)


def get_user_by_phone(db: Session, phone: str) -> models.User | None:
    from sqlalchemy.orm import selectinload

    return db.scalar(
        select(models.User)
        .options(selectinload(models.User.specialist_profile))
        .where(models.User.phone == phone)
    )


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email))


def get_user_by_phone_or_email(db: Session, identifier: str) -> models.User | None:
    from sqlalchemy.orm import selectinload

    normalized_identifier = identifier.strip()
    if "@" in normalized_identifier:
        return db.scalar(
            select(models.User)
            .options(selectinload(models.User.specialist_profile))
            .where(models.User.email.ilike(normalized_identifier.lower()))
        )
    return get_user_by_phone(db, normalized_identifier)


def create_user(db: Session, payload, password_hash: str) -> models.User:
    role = models.UserRole(getattr(payload, "role", "patient") or "patient")
    user = models.User(
        full_name=payload.fullName,
        phone=payload.phone,
        email=payload.email,
        password_hash=password_hash,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_specialist_profile(
    db: Session,
    user_id: str,
    full_name: str,
    position: str,
    specialization: str,
) -> models.Specialist:
    specialist = models.Specialist(
        user_id=user_id,
        full_name=full_name,
        position=position,
        specialization=specialization,
    )
    db.add(specialist)
    db.commit()
    db.refresh(specialist)
    return specialist


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
    from sqlalchemy.orm import selectinload

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
