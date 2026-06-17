from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.repositories.base import paginated


def recommendation_detail_options() -> tuple:
    return (
        selectinload(models.Recommendation.patient),
        selectinload(models.Recommendation.doctor),
        selectinload(models.Recommendation.appointment),
        selectinload(models.Recommendation.products),
    )


def list_admin_recommendations(
    db: Session,
    patient_id: str | None,
    doctor_id: str | None,
    appointment_id: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[models.Recommendation], dict]:
    statement = (
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .order_by(models.Recommendation.created_at.desc())
    )

    if patient_id:
        statement = statement.where(models.Recommendation.patient_id == patient_id)

    if doctor_id:
        statement = statement.where(models.Recommendation.doctor_id == doctor_id)

    if appointment_id:
        statement = statement.where(models.Recommendation.appointment_id == appointment_id)

    if search:
        statement = statement.where(models.Recommendation.text.ilike(f"%{search}%"))

    return paginated(db, statement, page, limit)


def list_patient_recommendations(db: Session, patient_id: str) -> list[models.Recommendation]:
    return db.scalars(
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .where(models.Recommendation.patient_id == patient_id)
        .order_by(models.Recommendation.created_at.desc())
    ).all()


def get_admin_recommendation(
    db: Session,
    recommendation_id: str,
) -> models.Recommendation | None:
    return db.scalar(
        select(models.Recommendation)
        .options(*recommendation_detail_options())
        .where(models.Recommendation.id == recommendation_id)
    )


def create_admin_recommendation(db: Session, payload) -> models.Recommendation:
    recommendation = models.Recommendation(
        patient_id=payload.patientId,
        doctor_id=payload.doctorId,
        appointment_id=payload.appointmentId,
        text=payload.text,
    )
    db.add(recommendation)
    db.flush()
    replace_recommendation_products(db, recommendation.id, payload.productIds)
    db.commit()
    return get_admin_recommendation(db, recommendation.id)


def update_admin_recommendation(
    db: Session,
    recommendation_id: str,
    payload,
) -> models.Recommendation | None:
    recommendation = db.get(models.Recommendation, recommendation_id)
    if recommendation is None:
        return None

    if "patientId" in payload.model_fields_set and payload.patientId is not None:
        recommendation.patient_id = payload.patientId
    if "doctorId" in payload.model_fields_set and payload.doctorId is not None:
        recommendation.doctor_id = payload.doctorId
    if "appointmentId" in payload.model_fields_set:
        recommendation.appointment_id = payload.appointmentId
    if "text" in payload.model_fields_set and payload.text is not None:
        recommendation.text = payload.text

    db.add(recommendation)
    if "productIds" in payload.model_fields_set and payload.productIds is not None:
        replace_recommendation_products(db, recommendation_id, payload.productIds)

    db.commit()
    return get_admin_recommendation(db, recommendation_id)


def delete_admin_recommendation(db: Session, recommendation_id: str) -> bool:
    recommendation = db.get(models.Recommendation, recommendation_id)
    if recommendation is None:
        return False

    db.delete(recommendation)
    db.commit()
    return True


def replace_recommendation_products(
    db: Session,
    recommendation_id: str,
    product_ids: list[str],
) -> None:
    db.execute(
        delete(models.RecommendationProduct).where(
            models.RecommendationProduct.recommendation_id == recommendation_id,
        )
    )
    for product_id in dict.fromkeys(product_ids):
        db.add(models.RecommendationProduct(recommendation_id=recommendation_id, product_id=product_id))
