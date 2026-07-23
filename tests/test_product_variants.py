from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.base import BaseModel
from app.models.category import Category
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.product_variant import ProductVariantCreate, ProductVariantUpdate
from app.services.product_variant import ProductVariantService


def test_product_variant_crud_and_price_history() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    with Session(engine) as db:
        category = Category(name="Gaming", is_active=True)
        product = Product(
            name="Gaming Laptop",
            sku="GL-1",
            price=Decimal("100.00"),
            category=category,
            is_active=True,
        )
        db.add(product)
        db.commit()

        variant = ProductVariantService.create(
            db,
            ProductVariantCreate(
                product_id=product.id,
                sku="GL-1-16GB",
                name="16 GB RAM",
                price=Decimal("120.00"),
            ),
        )
        assert variant.id is not None
        assert ProductVariantService.get(db, variant.id).sku == "GL-1-16GB"
        assert len(ProductVariantService.list(db, product_id=product.id)) == 1

        updated = ProductVariantService.update(
            db,
            variant.id,
            ProductVariantUpdate(price=Decimal("130.00")),
        )
        assert updated.price == Decimal("130.00")
        history = db.execute(select(PriceHistory)).scalar_one()
        assert history.old_price == Decimal("120.00")
        assert history.new_price == Decimal("130.00")

        deactivated = ProductVariantService.deactivate(db, variant.id)
        assert deactivated.is_active is False
