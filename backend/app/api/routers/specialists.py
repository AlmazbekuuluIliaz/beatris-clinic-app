from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import repositories
from app.core.database import get_db
from app.schemas import Specialist, SpecialistListResponse
from app.serializers import specialist_to_api

router = APIRouter(tags=["Specialists"])


@router.get("/specialists", response_model=SpecialistListResponse)
def get_specialists(
    search: str | None = None,
    serviceId: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    specialists, meta = repositories.list_specialists(db, search, serviceId, page, limit)
    return {"items": [specialist_to_api(specialist) for specialist in specialists], "meta": meta}


@router.get("/specialists/{id}", response_model=Specialist)
def get_specialist_by_id(id: str, db: Session = Depends(get_db)) -> dict:
    specialist = repositories.get_specialist(db, id)
    if specialist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist not found",
        )

    return specialist_to_api(specialist)
