from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.product import Product

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin



class Category(TimestampMixin, BaseModel):
    """
    Represents a product category.

    Supports parent-child categories such as:

    Electronics
        ├── Laptops
        └── Mobiles
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    parent: Mapped[Category | None] = relationship(
        remote_side="Category.id",
        back_populates="children",
    )

    children: Mapped[list[Category]] = relationship(
        back_populates="parent",
    )
    products: Mapped[list[Product]] = relationship(
    back_populates="category",
)