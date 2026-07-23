from __future__ import annotations

#from sqlalchemy import JSON, String
from sqlalchemy import CheckConstraint, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CheckConstraint, Index, JSON, String
from app.models.base import BaseModel
from app.models.mixins import TimestampMixin


class OutboxEvent(TimestampMixin, BaseModel):
    """
    Stores domain events for reliable asynchronous processing.
    """

    __tablename__ = "outbox_events"

    __table_args__ = (
    CheckConstraint(
        "retry_count >= 0",
        name="ck_outbox_events_retry_count_nonnegative",
    ),
    Index(
        "ix_outbox_status_created",
        "status",
        "created_at",
    ),
)

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    aggregate_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )