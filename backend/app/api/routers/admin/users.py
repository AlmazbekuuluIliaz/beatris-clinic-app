from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.errors import raise_bad_request, raise_conflict, raise_not_found
from app.core.database import get_db
from app.models import User as UserModel
from app.schemas import (
    AdminUpdateUserRequest,
    CreateUserRequest,
    User as UserSchema,
    UserListResponse,
    UserRole,
)
from app.services import admin as admin_service
from app.services import users as users_service

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
def get_admin_users(
    search: str | None = None,
    role: UserRole | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = admin_service.list_admin_users(db, search, role, page, limit)
    return {"items": items, "meta": meta}


@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    payload: CreateUserRequest,
    db: Session = Depends(get_db),
) -> dict:
    if users_service.get_user_by_phone(db, payload.phone) is not None:
        raise_bad_request("Пользователь с таким телефоном уже существует")
    if payload.email and users_service.get_user_by_email(db, payload.email) is not None:
        raise_bad_request("Пользователь с таким email уже существует")
    try:
        return admin_service.create_admin_user(db, payload)
    except IntegrityError:
        raise_bad_request("Пользователь с такими данными уже существует")


@router.get("/users/{id}", response_model=UserSchema)
def get_admin_user(id: str, db: Session = Depends(get_db)) -> dict:
    result = admin_service.get_admin_user(db, id)
    if result is None:
        raise_not_found("Пользователь не найден")
    return result


@router.patch("/users/{id}", response_model=UserSchema)
def update_admin_user(
    id: str,
    payload: AdminUpdateUserRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.phone:
        existing = users_service.get_user_by_phone(db, payload.phone)
        if existing is not None and existing.id != id:
            raise_bad_request("Пользователь с таким телефоном уже существует")
    if payload.email:
        existing = users_service.get_user_by_email(db, payload.email)
        if existing is not None and existing.id != id:
            raise_bad_request("Пользователь с таким email уже существует")
    try:
        result = admin_service.update_admin_user(db, id, payload)
    except IntegrityError:
        raise_bad_request("Пользователь с такими данными уже существует")
    if result is None:
        raise_not_found("Пользователь не найден")
    return result


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user(
    id: str,
    current_user: UserModel = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    if id == current_user.id:
        raise_bad_request("Нельзя удалить текущего администратора")
    try:
        deleted = admin_service.delete_admin_user(db, id)
    except IntegrityError:
        raise_conflict("Пользователь имеет связанные записи и не может быть удалён")
    if not deleted:
        raise_not_found("Пользователь не найден")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
