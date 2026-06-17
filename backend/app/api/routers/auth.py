from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin, unauthorized_exception
from app.core.config import get_settings
from app.core.database import get_db
from app.schemas import AuthResponse, LoginRequest, RefreshTokenResponse, RegisterRequest, User
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])

REFRESH_COOKIE_NAME = "refreshToken"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"


def _set_refresh_cookie(response: Response, refresh_token: str, remember: bool = True) -> None:
    settings = get_settings()
    max_age = settings.refresh_token_expire_days * 24 * 60 * 60 if remember else None
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite="strict",
        path=REFRESH_COOKIE_PATH,
        max_age=max_age,
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        httponly=True,
        secure=get_settings().refresh_cookie_secure,
        samesite="strict",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = auth_service.register_user(db, payload)
    except ValueError as e:
        error_map = {
            "phone_exists": ("Пользователь с таким телефоном уже существует", status.HTTP_400_BAD_REQUEST),
            "email_exists": ("Пользователь с таким email уже существует", status.HTTP_400_BAD_REQUEST),
            "integrity_error": ("Пользователь с такими данными уже существует", status.HTTP_400_BAD_REQUEST),
        }
        detail, code = error_map.get(str(e), ("Ошибка регистрации", status.HTTP_400_BAD_REQUEST))
        raise HTTPException(status_code=code, detail=detail)
    _set_refresh_cookie(response, result.pop("_refreshToken"), remember=result.pop("_remember"))
    return result


@router.post("/login", response_model=AuthResponse)
def login_user(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = auth_service.login_user(db, payload)
    except ValueError:
        raise unauthorized_exception()
    _set_refresh_cookie(response, result.pop("_refreshToken"), remember=result.pop("_remember"))
    return result


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(
    refresh_token: str | None = Cookie(default=None, alias="refreshToken"),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return auth_service.refresh_access_token(db, refresh_token)
    except ValueError:
        raise unauthorized_exception()


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(
    response: Response,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    auth_service.logout_user(db, current_user)
    _delete_refresh_cookie(response)
    return response


@router.get("/me", response_model=User)
def get_me(current_user=Depends(get_current_user)) -> dict:
    return User.model_validate(current_user).model_dump()


admin_router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@admin_router.post("/login", response_model=AuthResponse)
def login_admin(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = auth_service.login_admin(db, payload)
    except ValueError:
        raise unauthorized_exception()
    _set_refresh_cookie(response, result.pop("_refreshToken"), remember=result.pop("_remember"))
    return result


@admin_router.get("/me", response_model=User)
def get_admin_me(current_user=Depends(require_admin)) -> dict:
    return User.model_validate(current_user).model_dump()
