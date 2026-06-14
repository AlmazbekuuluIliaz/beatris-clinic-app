from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import repositories
from app.core.database import get_db
from app.schemas import ClinicInfo
from app.serializers import clinic_info_to_api

router = APIRouter(tags=["Clinic"])


@router.get("/clinic-info", response_model=ClinicInfo)
def get_clinic_info(db: Session = Depends(get_db)) -> dict:
    info = repositories.get_clinic_info(db)
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic info not found",
        )

    return clinic_info_to_api(info)
