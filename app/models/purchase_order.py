from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.goods_receipt import GoodsReceipt
    from app.models.purchase_order_item import PurchaseOrderItem
    from app.models.supplier import Supplier
    from app.models.warehouse import Warehouse


class PurchaseOrder(TimestampMixin, BaseModel):
    """
    Represents an order placed with a supplier to purchase stock.
    """

    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    order_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
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
        default="draft",
        index=True,
    )

    order_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    expected_delivery_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=0,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    supplier: Mapped["Supplier"] = relationship(
        back_populates="purchase_orders",
    )

    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="purchase_orders",
    )

    items: Mapped[list["PurchaseOrderItem"]] = relationship(
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )

    goods_receipts: Mapped[list["GoodsReceipt"]] = relationship(
        back_populates="purchase_order",
        cascade="all, delete-orphan",
    )