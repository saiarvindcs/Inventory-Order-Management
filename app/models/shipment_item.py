from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order_item import OrderItem
    from app.models.shipment import Shipment


class ShipmentItem(TimestampMixin, BaseModel):
    """
    Represents an order item and quantity included in a shipment.
    """

    __tablename__ = "shipment_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_shipment_items_quantity_positive",
        ),
        UniqueConstraint(
            "shipment_id",
            "order_item_id",
            name="uq_shipment_item",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    shipment_id: Mapped[int] = mapped_column(
        ForeignKey("shipments.id", ondelete="CASCADE"),
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

    shipment: Mapped["Shipment"] = relationship(
        back_populates="items",
    )

    order_item: Mapped["OrderItem"] = relationship(
        back_populates="shipment_items",
    )