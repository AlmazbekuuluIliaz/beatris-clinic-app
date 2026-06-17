from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import raise_bad_request, raise_not_found
from app.core.database import get_db
from app.schemas import (
    AdminCreateRecommendationRequest,
    Recommendation,
    RecommendationListResponse,
    UpdateRecommendationRequest,
)
from app.services import recommendations as recommendations_service
from app.api.routers.admin.helpers import (
    validate_recommendation_appointment,
    validate_recommendation_product_ids,
    validate_recommendation_user,
)

router = APIRouter()


@router.get("/recommendations", response_model=RecommendationListResponse)
def get_admin_recommendations(
    patientId: str | None = None,
    doctorId: str | None = None,
    appointmentId: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = recommendations_service.list_admin_recommendations(db, patientId, doctorId, appointmentId, search, page, limit)
    return {"items": items, "meta": meta}


@router.post("/recommendations", response_model=Recommendation, status_code=status.HTTP_201_CREATED)
def create_admin_recommendation(
    payload: AdminCreateRecommendationRequest,
    db: Session = Depends(get_db),
) -> dict:
    if payload.patientId is not None:
        validate_recommendation_user(db, payload.patientId, "patient", "Пациент не найден")
    validate_recommendation_user(db, payload.doctorId, "doctor", "Врач не найден")
    validate_recommendation_appointment(db, payload.appointmentId)
    validate_recommendation_product_ids(db, payload.productIds)
    try:
        return recommendations_service.create_admin_recommendation(db, payload)
    except IntegrityError:
        raise_bad_request("Не удалось создать рекомендацию с такими данными")


@router.get("/recommendations/{id}", response_model=Recommendation)
def get_admin_recommendation(id: str, db: Session = Depends(get_db)) -> dict:
    result = recommendations_service.get_admin_recommendation(db, id)
    if result is None:
        raise_not_found("Рекомендация не найдена")
    return result


@router.patch("/recommendations/{id}", response_model=Recommendation)
def update_admin_recommendation(
    id: str,
    payload: UpdateRecommendationRequest,
    db: Session = Depends(get_db),
) -> dict:
    if "patientId" in payload.model_fields_set and payload.patientId is not None:
        validate_recommendation_user(db, payload.patientId, "patient", "Пациент не найден")
    if "doctorId" in payload.model_fields_set and payload.doctorId is not None:
        validate_recommendation_user(db, payload.doctorId, "doctor", "Врач не найден")
    if "appointmentId" in payload.model_fields_set:
        validate_recommendation_appointment(db, payload.appointmentId)
    if "productIds" in payload.model_fields_set and payload.productIds is not None:
        validate_recommendation_product_ids(db, payload.productIds)
    try:
        result = recommendations_service.update_admin_recommendation(db, id, payload)
    except IntegrityError:
        raise_bad_request("Не удалось обновить рекомендацию с такими данными")
    if result is None:
        raise_not_found("Рекомендация не найдена")
    return result


@router.delete("/recommendations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_recommendation(id: str, db: Session = Depends(get_db)) -> Response:
    if not recommendations_service.delete_admin_recommendation(db, id):
        raise_not_found("Рекомендация не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
