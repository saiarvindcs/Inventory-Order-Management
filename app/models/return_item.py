from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    #from app.models.return import Return
    from app.models.return_request import Return


class ReturnItem(TimestampMixin, BaseModel):
    """
    Represents an individual order item included in a return request.
    """

    __tablename__ = "return_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_return_items_quantity_positive",
        ),
        CheckConstraint(
            "refund_amount >= 0",
            name="ck_return_items_refund_amount_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    return_id: Mapped[int] = mapped_column(
        ForeignKey("returns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    condition: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    resolution: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="refund",
    )

    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )

    return_request: Mapped["Return"] = relationship(
        back_populates="items",
    )

    order_item: Mapped["OrderItem"] = relationship(
        back_populates="return_items",
    )