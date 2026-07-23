from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.goods_receipt import GoodsReceipt
    from app.models.inventory import Inventory
    from app.models.purchase_order import PurchaseOrder
    from app.models.shipment import Shipment
    from app.models.stock_transfer import StockTransfer


class Warehouse(TimestampMixin, BaseModel):
    """
    Represents a physical warehouse where inventory is stored.
    """

    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    address_line1: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address_line2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    postal_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    shipments: Mapped[list[Shipment]] = relationship(
        "Shipment",
        back_populates="warehouse",
    )

    inventory_items: Mapped[list[Inventory]] = relationship(
        "Inventory",
        back_populates="warehouse",
        cascade="all, delete-orphan",
    )

    goods_receipts: Mapped[list[GoodsReceipt]] = relationship(
        "GoodsReceipt",
        back_populates="warehouse",
    )

    outgoing_stock_transfers: Mapped[list[StockTransfer]] = relationship(
        "StockTransfer",
        foreign_keys="StockTransfer.source_warehouse_id",
        back_populates="source_warehouse",
    )

    incoming_stock_transfers: Mapped[list[StockTransfer]] = relationship(
        "StockTransfer",
        foreign_keys="StockTransfer.destination_warehouse_id",
        back_populates="destination_warehouse",
    )

    purchase_orders: Mapped[list[PurchaseOrder]] = relationship(
        "PurchaseOrder",
        back_populates="warehouse",
    )