from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.product_variant import ProductVariant


class ProductVariantRepository:
    @staticmethod
    def get_by_id(db: Session, variant_id: int) -> ProductVariant | None:
        return db.execute(
            select(ProductVariant).where(ProductVariant.id == variant_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_sku(db: Session, sku: str) -> ProductVariant | None:
        return db.execute(
            select(ProductVariant).where(ProductVariant.sku == sku)
        ).scalar_one_or_none()

    @staticmethod
    def list(
        db: Session,
        *,
        product_id: int | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[ProductVariant]:
        statement = select(ProductVariant)

        if product_id is not None:
            statement = statement.where(ProductVariant.product_id == product_id)
        if is_active is not None:
            statement = statement.where(ProductVariant.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                ProductVariant.name.ilike(pattern) | ProductVariant.sku.ilike(pattern)
            )

        sortable = {
            "id": ProductVariant.id,
            "name": ProductVariant.name,
            "sku": ProductVariant.sku,
            "price": ProductVariant.price,
            "product_id": ProductVariant.product_id,
        }
        column = sortable.get(sort_by, ProductVariant.id)
        statement = statement.order_by(desc(column) if sort_order == "desc" else asc(column))
        statement = statement.offset(skip).limit(limit)
        return list(db.execute(statement).scalars().all())

    @staticmethod
    def save(db: Session, variant: ProductVariant) -> ProductVariant:
        db.add(variant)
        db.commit()
        db.refresh(variant)
        return variant
