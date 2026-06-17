from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories


def get_user_by_phone(db: Session, phone: str):
    return repositories.get_user_by_phone(db, phone)


def get_user_by_email(db: Session, email: str):
    return repositories.get_user_by_email(db, email)


def get_user(db: Session, user_id: str):
    return repositories.get_user(db, user_id)
