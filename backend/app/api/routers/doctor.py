from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, repositories
from app.api.deps import require_doctor
from app.core.database import get_db
from app.schemas import Appointment, DoctorScheduleItem
from app.serializers import appointment_to_api, doctor_schedule_item_to_api

router = APIRouter(prefix="/doctor", tags=["Doctor"])


def _get_doctor_specialist(db: Session, current_user: models.User) -> models.Specialist:
    specialist = repositories.get_specialist_by_user_id(db, current_user.id)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor specialist profile not found",
        )
    return specialist


@router.get("/schedule", response_model=list[DoctorScheduleItem])
def get_doctor_schedule(
    current_user: models.User = Depends(require_doctor),
    db: Session = Depends(get_db),
) -> list[dict]:
    specialist = _get_doctor_specialist(db, current_user)
    schedule_items = repositories.list_doctor_schedule(db, specialist.id)
    return [doctor_schedule_item_to_api(schedule_item) for schedule_item in schedule_items]


@router.get("/appointments", response_model=list[Appointment])
def get_doctor_appointments(
    current_user: models.User = Depends(require_doctor),
    db: Session = Depends(get_db),
) -> list[dict]:
    specialist = _get_doctor_specialist(db, current_user)
    appointments = repositories.list_doctor_appointments(db, specialist.id)
    return [appointment_to_api(appointment) for appointment in appointments]
