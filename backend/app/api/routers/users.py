from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import get_current_user
from app.core.database import get_db
from app.schemas import UpdateProfileRequest, User
from app.serializers import user_to_api

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
def get_my_profile(current_user: models.User = Depends(get_current_user)) -> dict:
    return user_to_api(current_user)


@router.patch("/me", response_model=User)
def update_my_profile(
    payload: UpdateProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if payload.phone:
        existing_user = repositories.get_user_by_phone(db, payload.phone)
        if existing_user is not None and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone already exists",
            )

    if payload.email:
        existing_user = repositories.get_user_by_email(db, payload.email)
        if existing_user is not None and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    try:
        user = repositories.update_user_profile(db, current_user.id, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this data already exists",
        ) from exc

    return user_to_api(user)
