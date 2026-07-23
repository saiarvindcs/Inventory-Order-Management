from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.base import BaseModel
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.schemas.purchase_order import (
    GoodsReceiptCreate,
    GoodsReceiptItemCreate,
    PurchaseOrderCreate,
    PurchaseOrderItemCreate,
)
from app.services.purchase_order import PurchaseOrderService


def test_purchase_order_partial_and_full_receipt_updates_inventory() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)

    with Session(engine) as db:
        category = Category(name="Test", is_active=True)
        supplier = Supplier(name="Supplier", code="SUP1", is_active=True)
        warehouse = Warehouse(
            name="Main",
            code="WH1",
            address_line1="Address",
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600001",
            country="India",
            is_active=True,
        )
        product = Product(
            name="Phone",
            sku="PHONE",
            price=Decimal("100.00"),
            category=category,
            is_active=True,
        )
        variant = ProductVariant(
            name="Black",
            sku="PHONE-BLK",
            price=Decimal("100.00"),
            product=product,
            is_active=True,
        )
        db.add_all([supplier, warehouse, product])
        db.commit()

        purchase_order = PurchaseOrderService.create(
            db,
            PurchaseOrderCreate(
                supplier_id=supplier.id,
                warehouse_id=warehouse.id,
                order_date=date.today(),
                items=[
                    PurchaseOrderItemCreate(
                        product_variant_id=variant.id,
                        ordered_quantity=10,
                        unit_price=Decimal("25.50"),
                    )
                ],
            ),
        )
        assert purchase_order.total_amount == Decimal("255.00")

        PurchaseOrderService.change_status(db, purchase_order.id, "submitted")
        purchase_order = PurchaseOrderService.change_status(
            db, purchase_order.id, "approved"
        )

        PurchaseOrderService.receive(
            db,
            purchase_order.id,
            GoodsReceiptCreate(
                received_at=datetime.now(UTC),
                items=[
                    GoodsReceiptItemCreate(
                        purchase_order_item_id=purchase_order.items[0].id,
                        quantity_received=4,
                    )
                ],
            ),
        )
        purchase_order = PurchaseOrderService.get(db, purchase_order.id)
        assert purchase_order.status == "partially_received"

        PurchaseOrderService.receive(
            db,
            purchase_order.id,
            GoodsReceiptCreate(
                received_at=datetime.now(UTC),
                items=[
                    GoodsReceiptItemCreate(
                        purchase_order_item_id=purchase_order.items[0].id,
                        quantity_received=6,
                    )
                ],
            ),
        )

        purchase_order = PurchaseOrderService.get(db, purchase_order.id)
        inventory = db.execute(select(Inventory)).scalar_one()
        movements = db.execute(select(StockMovement)).scalars().all()

        assert purchase_order.status == "received"
        assert purchase_order.items[0].received_quantity == 10
        assert inventory.quantity_on_hand == 10
        assert [movement.quantity for movement in movements] == [4, 6]
