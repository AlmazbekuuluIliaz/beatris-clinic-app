from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AdminSettingsResponse(BaseModel):
    settings: dict[str, Any]


class UpdateAdminSettingsRequest(BaseModel):
    settings: dict[str, Any]
