from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory import Inventory


class StockMovement(TimestampMixin, BaseModel):
    """
    Records every inventory stock movement.
    """

    __tablename__ = "stock_movements"

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

    movement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    inventory: Mapped["Inventory"] = relationship(
        back_populates="stock_movements",
    )