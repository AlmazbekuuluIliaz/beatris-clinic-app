from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import ClinicInfo
from app.services import clinic as clinic_service

router = APIRouter(tags=["Clinic"])


@router.get("/clinic-info", response_model=ClinicInfo)
def get_clinic_info(db: Session = Depends(get_db)) -> dict:
    return clinic_service.get_clinic_info(db)


@router.get("/health")
def health_check():
    return {"status": "ok"}
