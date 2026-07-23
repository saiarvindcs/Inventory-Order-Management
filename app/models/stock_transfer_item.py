from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant
    from app.models.stock_transfer import StockTransfer
    #from app.models.stock_transfer_item import StockTransferItem


class StockTransferItem(TimestampMixin, BaseModel):
    """
    Represents one product variant inside a warehouse stock transfer.
    """

    __tablename__ = "stock_transfer_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_stock_transfer_items_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    stock_transfer_id: Mapped[int] = mapped_column(
        ForeignKey("stock_transfers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    stock_transfer: Mapped["StockTransfer"] = relationship(
        back_populates="items",
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="stock_transfer_items",
    )