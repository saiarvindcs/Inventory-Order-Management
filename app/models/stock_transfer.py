from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.stock_transfer_item import StockTransferItem
    from app.models.warehouse import Warehouse


class StockTransfer(TimestampMixin, BaseModel):
    """
    Represents a stock transfer between two warehouses.
    """

    __tablename__ = "stock_transfers"

    __table_args__ = (
        CheckConstraint(
            "source_warehouse_id <> destination_warehouse_id",
            name="ck_stock_transfers_different_warehouses",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    transfer_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    source_warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    destination_warehouse_id: Mapped[int] = mapped_column(
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

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    source_warehouse: Mapped["Warehouse"] = relationship(
        foreign_keys=[source_warehouse_id],
        back_populates="outgoing_stock_transfers",
    )

    destination_warehouse: Mapped["Warehouse"] = relationship(
        foreign_keys=[destination_warehouse_id],
        back_populates="incoming_stock_transfers",
    )

    items: Mapped[list["StockTransferItem"]] = relationship(
        back_populates="stock_transfer",
        cascade="all, delete-orphan",
    )