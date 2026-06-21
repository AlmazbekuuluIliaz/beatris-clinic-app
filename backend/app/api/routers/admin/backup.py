from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.errors import raise_not_found
from app.core.database import get_db
from app.backups.backup import create_backup, list_backups, delete_backup

router = APIRouter()


@router.post("/backups")
def create_db_backup(
    current_user=Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    return create_backup(db)


@router.get("/backups")
def get_backups(
    current_user=Depends(require_admin),
) -> dict:
    return {"backups": list_backups()}


@router.delete("/backups/{filename}")
def remove_backup(
    filename: str,
    current_user=Depends(require_admin),
) -> dict:
    if not delete_backup(filename):
        raise_not_found("Backup not found")
    return {"message": "Backup deleted"}
