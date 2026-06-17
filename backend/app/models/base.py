from __future__ import annotations

import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import CHAR, DateTime, Text, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uuid_str() -> str:
    return str(uuid4())


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [item.value for item in enum_cls]


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=uuid_str,
        server_default=text("(UUID())"),
    )
