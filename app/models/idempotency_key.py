from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin


class IdempotencyKey(TimestampMixin, BaseModel):
    """
    Prevents duplicate execution of requests.
    """

    __tablename__ = "idempotency_keys"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    request_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    response_status: Mapped[int] = mapped_column(
        nullable=False,
    )

    response_body: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )