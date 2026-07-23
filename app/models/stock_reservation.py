from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory import Inventory


class StockReservation(TimestampMixin, BaseModel):
    """
    Represents inventory temporarily reserved for an order or operation.
    """

    __tablename__ = "stock_reservations"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_stock_reservations_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey(
            "inventory.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    reservation_reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        index=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    inventory: Mapped["Inventory"] = relationship(
        back_populates="stock_reservations",
    )