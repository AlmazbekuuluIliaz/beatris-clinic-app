from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import require_admin, unauthorized_exception
from app.api.routers.auth import _issue_auth_response
from app.core.database import get_db
from app.core.security import verify_password
from app.schemas import AuthResponse, LoginRequest, User
from app.serializers import user_to_api

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=AuthResponse)
def login_admin(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> dict:
    user = repositories.get_user_by_phone_or_email(db, payload.phone)
    if (
        user is None
        or user.role != models.UserRole.ADMIN
        or not verify_password(payload.password, user.password_hash)
    ):
        raise unauthorized_exception()

    return _issue_auth_response(db, response, user, remember=payload.remember)


@router.get("/me", response_model=User)
def get_admin_me(current_user: models.User = Depends(require_admin)) -> dict:
    return user_to_api(current_user)
