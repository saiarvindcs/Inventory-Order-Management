from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.product_variant import ProductVariant
    from app.models.shipment_item import ShipmentItem
    from app.models.return_item import ReturnItem

class OrderItem(TimestampMixin, BaseModel):
    """
    Represents one product variant included in a customer order.
    """

    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_order_items_unit_price_nonnegative",
        ),
        CheckConstraint(
            "discount_amount >= 0",
            name="ck_order_items_discount_amount_nonnegative",
        ),
        CheckConstraint(
            "line_total >= 0",
            name="ck_order_items_line_total_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    return_items: Mapped[list["ReturnItem"]] = relationship(
    back_populates="order_item",
)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    shipment_items: Mapped[list["ShipmentItem"]] = relationship(
    back_populates="order_item",
)

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="items",
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="order_items",
    )