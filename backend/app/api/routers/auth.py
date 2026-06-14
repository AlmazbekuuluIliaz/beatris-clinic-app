from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import repositories
from app.api.deps import get_current_user, unauthorized_exception
from app.core.config import get_settings
from app.core.database import get_db
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
from app.models import User as UserModel
from app.schemas import AuthResponse, LoginRequest, RefreshTokenResponse, RegisterRequest, User
from app.serializers import user_to_api

router = APIRouter(prefix="/auth", tags=["Auth"])
REFRESH_COOKIE_NAME = "refreshToken"
REFRESH_COOKIE_PATH = "/api/v1/auth/refresh"


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    if repositories.get_user_by_phone(db, payload.phone) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким телефоном уже существует",
        )

    if payload.email and repositories.get_user_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    try:
        user = repositories.create_user(db, payload, get_password_hash(payload.password))
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с такими данными уже существует",
        ) from exc

    return _issue_auth_response(db, response, user)


@router.post("/login", response_model=AuthResponse)
def login_user(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    user = repositories.get_user_by_phone(db, payload.phone)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise unauthorized_exception()

    return _issue_auth_response(db, response, user, remember=payload.remember)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> dict:
    if refresh_token is None:
        raise unauthorized_exception()

    try:
        payload = decode_refresh_token(refresh_token)
    except ValueError as exc:
        raise unauthorized_exception() from exc

    refresh_token_record = repositories.get_active_refresh_token(db, hash_token(refresh_token))
    if refresh_token_record is None or refresh_token_record.user_id != payload.get("sub"):
        raise unauthorized_exception()

    user = refresh_token_record.user
    access_token = create_access_token(user.id, user.role.value)
    return {
        "accessToken": access_token,
        "tokenType": "Bearer",
        "expiresIn": access_token_expires_in_seconds(),
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(
    response: Response,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    repositories.revoke_user_refresh_tokens(db, current_user.id)
    _delete_refresh_cookie(response)
    return response


@router.get("/me", response_model=User)
def get_me(current_user: UserModel = Depends(get_current_user)) -> dict:
    return user_to_api(current_user)


def _issue_auth_response(
    db: Session, response: Response, user: UserModel, remember: bool = True
) -> dict:
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    repositories.create_refresh_token(
        db,
        user.id,
        hash_token(refresh_token),
        refresh_token_expires_at(),
    )
    _set_refresh_cookie(response, refresh_token, remember=remember)
    return {
        "accessToken": access_token,
        "tokenType": "Bearer",
        "expiresIn": access_token_expires_in_seconds(),
        "user": user_to_api(user),
    }


def _set_refresh_cookie(
    response: Response, refresh_token: str, remember: bool = True
) -> None:
    settings = get_settings()
    # remember=True → постоянная кука (переживает закрытие браузера),
    # remember=False → сессионная (без max_age, удаляется при закрытии браузера).
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
