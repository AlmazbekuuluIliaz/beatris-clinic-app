from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import UpdateProfileRequest, User
from app.schemas.users import User
from app.services import users as users_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
def get_profile(current_user=Depends(get_current_user)) -> dict:
    return User.model_validate(current_user).model_dump()


@router.patch("/me", response_model=User)
def update_profile(
    payload: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = users_service.update_profile(db, current_user.id, payload)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с такими данными уже существует",
        )
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return result
