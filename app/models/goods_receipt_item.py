from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.goods_receipt import GoodsReceipt
    from app.models.purchase_order_item import PurchaseOrderItem


class GoodsReceiptItem(TimestampMixin, BaseModel):
    """One purchase-order line received in a goods receipt."""

    __tablename__ = "goods_receipt_items"
    __table_args__ = (
        CheckConstraint(
            "quantity_received > 0",
            name="ck_goods_receipt_items_quantity_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    goods_receipt_id: Mapped[int] = mapped_column(
        ForeignKey("goods_receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    purchase_order_item_id: Mapped[int] = mapped_column(
        ForeignKey("purchase_order_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)

    goods_receipt: Mapped["GoodsReceipt"] = relationship(back_populates="items")
    purchase_order_item: Mapped["PurchaseOrderItem"] = relationship(
        back_populates="goods_receipt_items"
    )
