from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.return_item import ReturnItem
    from app.models.refund import Refund
    from app.models.order import Order
    from app.models.user import User


class Return(TimestampMixin, BaseModel):
    """
    Represents a customer return request.
    """

    __tablename__ = "returns"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    return_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="requested",
        index=True,
    )

    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        back_populates="returns",
    )

    customer: Mapped["User"] = relationship()

    items: Mapped[list["ReturnItem"]] = relationship(
        back_populates="return_request",
        cascade="all, delete-orphan",
    )

    refunds: Mapped[list["Refund"]] = relationship(
        back_populates="return_request",
        cascade="all, delete-orphan",
    )