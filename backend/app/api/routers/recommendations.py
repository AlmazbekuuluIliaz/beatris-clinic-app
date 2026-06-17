from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_doctor
from app.core.database import get_db
from app.models import UserRole
from app.schemas import CreateRecommendationRequest, Recommendation
from app.services import recommendations as recommendations_service

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/my", response_model=list[Recommendation])
def get_my_recommendations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return recommendations_service.list_patient_recommendations(db, current_user.id)


@router.post("", response_model=Recommendation, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    payload: CreateRecommendationRequest,
    current_user=Depends(require_doctor),
    db: Session = Depends(get_db),
) -> dict:
    if current_user.role not in (UserRole.DOCTOR, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Необходима роль врача или администратора",
        )
    return recommendations_service.create_recommendation(db, payload, current_user.id)
