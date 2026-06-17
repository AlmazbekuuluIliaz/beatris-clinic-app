from __future__ import annotations

import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import models


def get_settings_map(db: Session) -> dict:
    result: dict = {}
    for row in db.scalars(select(models.AppSetting)).all():
        try:
            result[row.key] = json.loads(row.value)
        except (ValueError, TypeError):
            result[row.key] = row.value
    return result


def replace_settings(db: Session, overrides: dict) -> dict:
    db.execute(delete(models.AppSetting))
    for key, value in overrides.items():
        db.add(models.AppSetting(key=str(key), value=json.dumps(value)))
    db.commit()
    return get_settings_map(db)


def upsert_setting(db: Session, key: str, value) -> None:
    row = db.get(models.AppSetting, key)
    if value is None:
        if row is not None:
            db.delete(row)
            db.commit()
        return
    serialized = json.dumps(value)
    if row is None:
        db.add(models.AppSetting(key=key, value=serialized))
    else:
        row.value = serialized
    db.commit()
