from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import get_current_user, require_doctor
from app.core.database import get_db
from app.schemas import CreateRecommendationRequest, Recommendation
from app.serializers import recommendation_to_api

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/my", response_model=list[Recommendation])
def get_my_recommendations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    recommendations = repositories.list_patient_recommendations(db, current_user.id)
    return [recommendation_to_api(recommendation) for recommendation in recommendations]


@router.post("", response_model=Recommendation, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    payload: CreateRecommendationRequest,
    current_user: models.User = Depends(require_doctor),
    db: Session = Depends(get_db),
) -> dict:
    patient = repositories.get_user(db, payload.patientId)
    if patient is None or patient.role != models.UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient not found",
        )

    if payload.appointmentId and repositories.get_appointment(db, payload.appointmentId) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment not found",
        )

    products = repositories.list_products_by_ids(db, payload.productIds)
    found_product_ids = {product.id for product in products}
    missing_product_ids = [
        product_id for product_id in dict.fromkeys(payload.productIds) if product_id not in found_product_ids
    ]
    if missing_product_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Some products were not found", "productIds": missing_product_ids},
        )

    recommendation_payload = SimpleNamespace(
        patientId=payload.patientId,
        doctorId=current_user.id,
        appointmentId=payload.appointmentId,
        text=payload.text,
        productIds=payload.productIds,
    )

    try:
        recommendation = repositories.create_admin_recommendation(db, recommendation_payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation cannot be created",
        ) from exc

    return recommendation_to_api(recommendation)
