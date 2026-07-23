from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.goods_receipt_item import GoodsReceiptItem
    from app.models.product_variant import ProductVariant
    from app.models.purchase_order import PurchaseOrder


class PurchaseOrderItem(TimestampMixin, BaseModel):
    """
    Represents one product variant included in a purchase order.
    """

    __tablename__ = "purchase_order_items"

    __table_args__ = (
        CheckConstraint(
            "ordered_quantity > 0",
            name="ck_purchase_order_items_ordered_quantity_positive",
        ),
        CheckConstraint(
            "received_quantity >= 0",
            name="ck_purchase_order_items_received_quantity_nonnegative",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_purchase_order_items_unit_price_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    purchase_order_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    ordered_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    received_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    purchase_order: Mapped["PurchaseOrder"] = relationship(
        back_populates="items",
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="purchase_order_items",
    )

    goods_receipt_items: Mapped[list["GoodsReceiptItem"]] = relationship(
        back_populates="purchase_order_item",
    )