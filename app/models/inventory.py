from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.product_variant import ProductVariant
    from app.models.stock_adjustment import StockAdjustment
    from app.models.stock_movement import StockMovement
    from app.models.stock_reservation import StockReservation
    from app.models.warehouse import Warehouse


class Inventory(TimestampMixin, BaseModel):
    """
    Current inventory balance of a product variant in a warehouse.
    """

    __tablename__ = "inventory"

    __table_args__ = (
        CheckConstraint(
            "quantity_on_hand >= 0",
            name="ck_inventory_quantity_on_hand_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved >= 0",
            name="ck_inventory_quantity_reserved_nonnegative",
        ),
        CheckConstraint(
            "quantity_reserved <= quantity_on_hand",
            name="ck_inventory_reserved_not_greater_than_on_hand",
        ),
        UniqueConstraint(
            "warehouse_id",
            "product_variant_id",
            name="uq_inventory_warehouse_variant",
        ),
        Index(
            "ix_inventory_warehouse_variant",
            "warehouse_id",
            "product_variant_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey(
            "warehouses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey(
            "product_variants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    quantity_on_hand: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    quantity_reserved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    warehouse: Mapped["Warehouse"] = relationship(
        back_populates="inventory_items",
    )

    product_variant: Mapped["ProductVariant"] = relationship(
        back_populates="inventory_items",
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    stock_reservations: Mapped[list["StockReservation"]] = relationship(
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    stock_adjustments: Mapped[list["StockAdjustment"]] = relationship(
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    @property
    def quantity_available(self) -> int:
        """
        Quantity currently available for new orders.
        """

        return self.quantity_on_hand - self.quantity_reserved