from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin


class PriceHistory(TimestampMixin, BaseModel):
    """
    Stores historical prices for product variants.
    """

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    new_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    product_variant: Mapped[ProductVariant] = relationship(
        back_populates="price_history",
    )


from app.models.product_variant import ProductVariant