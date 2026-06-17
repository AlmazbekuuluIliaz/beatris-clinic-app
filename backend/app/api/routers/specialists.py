from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import Specialist, SpecialistListResponse
from app.services import specialists as specialists_service

router = APIRouter(tags=["Specialists"])


@router.get("/specialists", response_model=SpecialistListResponse)
def get_specialists(
    search: str | None = None,
    serviceId: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    items, meta = specialists_service.list_specialists(db, search, serviceId, page, limit)
    return {"items": items, "meta": meta}


@router.get("/specialists/{id}", response_model=Specialist)
def get_specialist(id: str, db: Session = Depends(get_db)) -> dict:
    result = specialists_service.get_specialist(db, id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Специалист не найден")
    return result
