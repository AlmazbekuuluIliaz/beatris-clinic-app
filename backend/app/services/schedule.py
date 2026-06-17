from __future__ import annotations

from sqlalchemy.orm import Session

from app import repositories
from app.schemas.specialists import DoctorSchedule


def list_doctor_schedule(db: Session, specialist_id: str, date_from: str | None = None, date_to: str | None = None) -> list[dict]:
    items = repositories.list_doctor_schedule(db, specialist_id, date_from, date_to)
    return [DoctorSchedule.model_validate(s).model_dump() for s in items]


def get_specialist_by_user_id(db: Session, user_id: str):
    return repositories.get_specialist_by_user_id(db, user_id)
