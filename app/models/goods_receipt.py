from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.goods_receipt_item import GoodsReceiptItem
    from app.models.purchase_order import PurchaseOrder
    from app.models.warehouse import Warehouse


class GoodsReceipt(TimestampMixin, BaseModel):
    """
    Records the receipt of goods for a purchase order.

    A purchase order can be received in multiple batches.
    """

    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    receipt_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    purchase_order_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_orders.id", ondelete="RESTRICT"),
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
        default="received",
        index=True,
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(
        back_populates="goods_receipts",
    )

    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="goods_receipts",
    )

    items: Mapped[list["GoodsReceiptItem"]] = relationship(
        back_populates="goods_receipt",
        cascade="all, delete-orphan",
    )