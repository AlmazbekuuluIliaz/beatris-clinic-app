from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def get_health() -> dict:
    return {
        "status": "ok",
        "service": "Beatris API",
        "version": "1.0.0",
    }


@router.get("/db")
def get_database_health(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable",
        ) from exc

    return {
        "status": "ok",
        "database": "reachable",
    }
