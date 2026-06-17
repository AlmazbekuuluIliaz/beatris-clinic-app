from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories


def _serialize(rec) -> dict:
    if rec.patient:
        patient_name = rec.patient.full_name
        patient_phone = rec.patient.phone
    elif rec.appointment:
        patient_name = rec.appointment.patient_name
        patient_phone = rec.appointment.patient_phone
    else:
        patient_name = None
        patient_phone = None
    return {
        "id": rec.id,
        "patientId": rec.patient_id,
        "patientName": patient_name,
        "patientPhone": patient_phone,
        "doctorId": rec.doctor_id,
        "appointmentId": rec.appointment_id,
        "text": rec.text,
        "productIds": [p.id for p in rec.products],
        "createdAt": rec.created_at,
    }


def list_patient_recommendations(db: Session, patient_id: str) -> list[dict]:
    items = repositories.list_patient_recommendations(db, patient_id)
    return [_serialize(r) for r in items]


def create_recommendation(db: Session, payload, doctor_id: str) -> dict:
    from types import SimpleNamespace

    class _Payload:
        def __init__(self, p, did):
            self.patientId = p.patientId
            self.appointmentId = p.appointmentId
            self.text = p.text
            self.productIds = p.productIds
            self.doctorId = did
            self.model_fields_set = {"patientId", "appointmentId", "text", "productIds", "doctorId"}

    rec = repositories.create_admin_recommendation(db, _Payload(payload, doctor_id))
    return _serialize(rec)


def list_admin_recommendations(
    db: Session,
    patient_id: str | None,
    doctor_id: str | None,
    appointment_id: str | None,
    search: str | None,
    page: int,
    limit: int,
) -> tuple[list[dict], dict]:
    items, meta = repositories.list_admin_recommendations(db, patient_id, doctor_id, appointment_id, search, page, limit)
    return [_serialize(r) for r in items], meta


def get_admin_recommendation(db: Session, recommendation_id: str) -> dict | None:
    rec = repositories.get_admin_recommendation(db, recommendation_id)
    if rec is None:
        return None
    return _serialize(rec)


def create_admin_recommendation(db: Session, payload) -> dict:
    rec = repositories.create_admin_recommendation(db, payload)
    return _serialize(rec)


def update_admin_recommendation(db: Session, recommendation_id: str, payload) -> dict | None:
    rec = repositories.update_admin_recommendation(db, recommendation_id, payload)
    if rec is None:
        return None
    return _serialize(rec)


def delete_admin_recommendation(db: Session, recommendation_id: str) -> bool:
    return repositories.delete_admin_recommendation(db, recommendation_id)
