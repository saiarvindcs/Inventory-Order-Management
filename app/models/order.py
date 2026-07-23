from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.order_item import OrderItem
    from app.models.order_status_history import OrderStatusHistory
    from app.models.payment import Payment
    from app.models.refund import Refund
    from app.models.return_request import Return
    from app.models.shipment import Shipment
    from app.models.user import User


class Order(TimestampMixin, BaseModel):
    """Represents a customer order."""

    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_nonnegative"),
        CheckConstraint("tax_amount >= 0", name="ck_orders_tax_amount_nonnegative"),
        CheckConstraint("shipping_amount >= 0", name="ck_orders_shipping_amount_nonnegative"),
        CheckConstraint("discount_amount >= 0", name="ck_orders_discount_amount_nonnegative"),
        CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_nonnegative"),
        Index("ix_orders_customer_status", "customer_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    shipping_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id", ondelete="RESTRICT"), nullable=False, index=True)
    billing_address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    placed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["User"] = relationship(back_populates="orders")
    shipping_address: Mapped["Address"] = relationship(foreign_keys=[shipping_address_id])
    billing_address: Mapped["Address | None"] = relationship(foreign_keys=[billing_address_id])
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", order_by="OrderStatusHistory.created_at"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    returns: Mapped[list["Return"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="order", cascade="all, delete-orphan")
