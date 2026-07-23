from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    """Database operations for products."""

    @staticmethod
    def get_by_id(
        db: Session,
        product_id: int,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_sku(
        db: Session,
        sku: str,
    ) -> Product | None:
        statement = select(Product).where(
            Product.sku == sku
        )

        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        *,
        search: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        statement = select(Product)

        if search:
            statement = statement.where(
                Product.name.ilike(f"%{search}%")
            )

        if category_id is not None:
            statement = statement.where(
                Product.category_id == category_id
            )

        if is_active is not None:
            statement = statement.where(
                Product.is_active == is_active
            )

        if min_price is not None:
            statement = statement.where(
                Product.price >= min_price
            )

        if max_price is not None:
            statement = statement.where(
                Product.price <= max_price
            )

        sortable_columns = {
            "id": Product.id,
            "name": Product.name,
            "price": Product.price,
            "sku": Product.sku,
        }

        sort_column = sortable_columns.get(
            sort_by,
            Product.id,
        )

        if sort_order.lower() == "desc":
            statement = statement.order_by(
                desc(sort_column)
            )
        else:
            statement = statement.order_by(
                asc(sort_column)
            )

        statement = (
            statement
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def create(
        db: Session,
        product: Product,
    ) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    @staticmethod
    def update(
        db: Session,
        product: Product,
    ) -> Product:
        db.add(product)
        db.commit()
        db.refresh(product)

        return product