from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal
if TYPE_CHECKING:
    from app.models.inventory import Inventory
    from decimal import Decimal
    from app.models.stock_transfer_item import StockTransferItem
    from app.models.purchase_order_item import PurchaseOrderItem
    from app.models.order_item import OrderItem

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin



class ProductVariant(TimestampMixin, BaseModel):
    """
    Represents a sellable variant of a product.

    Example:
        Product: iPhone 16

        Variants:
        - 128 GB Black
        - 256 GB Black
        - 512 GB White
    """

    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stock_transfer_items: Mapped[list["StockTransferItem"]] = relationship(
    back_populates="product_variant",
)

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
    back_populates="product_variant",
)
    purchase_order_items: Mapped[list["PurchaseOrderItem"]] = relationship(
    back_populates="product_variant",
)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    inventory_items: Mapped[list["Inventory"]] = relationship(
    back_populates="product_variant",
    cascade="all, delete-orphan",
)

    product: Mapped[Product] = relationship(
        back_populates="variants",
    )
    price_history: Mapped[list[PriceHistory]] = relationship(
    back_populates="product_variant",
    cascade="all, delete-orphan",
)

from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.inventory import Inventory