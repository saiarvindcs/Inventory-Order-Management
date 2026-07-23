from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory import Inventory


class StockAdjustment(TimestampMixin, BaseModel):
    """
    Records manual inventory quantity corrections.

    Examples:
    - Damaged stock
    - Lost stock
    - Physical inventory audit correction
    - Extra stock discovered
    """

    __tablename__ = "stock_adjustments"

    __table_args__ = (
        CheckConstraint(
            "quantity_change <> 0",
            name="ck_stock_adjustments_quantity_change_nonzero",
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

    adjustment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    quantity_change: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    inventory: Mapped["Inventory"] = relationship(
        back_populates="stock_adjustments",
    )