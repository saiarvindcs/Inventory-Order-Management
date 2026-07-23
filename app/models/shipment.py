from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.shipment_item import ShipmentItem
    from app.models.warehouse import Warehouse
    #from app.models.shipment import Shipment


class Shipment(TimestampMixin, BaseModel):
    """
    Represents a shipment created for a customer order.
    """

    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    shipment_number: Mapped[str] = mapped_column(
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

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
        index=True,
    )

    carrier: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    tracking_number: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        unique=True,
        index=True,
    )

    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    order: Mapped["Order"] = relationship(
        back_populates="shipments",
    )

    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="shipments",
    )

    items: Mapped[list["ShipmentItem"]] = relationship(
        back_populates="shipment",
        cascade="all, delete-orphan",
    )