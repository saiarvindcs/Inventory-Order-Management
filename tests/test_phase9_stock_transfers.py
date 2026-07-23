from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.base import BaseModel
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse
from app.schemas.stock_transfer import StockTransferCreate, StockTransferItemCreate
from app.services.stock_transfer import StockTransferService


def _seed(db: Session):
    category = Category(name="Test", is_active=True)
    source = Warehouse(name="Source", code="SRC", address_line1="A", city="Chennai", state="TN", postal_code="600001", country="India", is_active=True)
    destination = Warehouse(name="Destination", code="DST", address_line1="B", city="Bengaluru", state="KA", postal_code="560001", country="India", is_active=True)
    product = Product(name="Phone", sku="PHONE", price=Decimal("100"), category=category, is_active=True)
    variant = ProductVariant(name="Black", sku="PHONE-BLK", price=Decimal("100"), product=product, is_active=True)
    db.add_all([source, destination, product])
    db.flush()
    db.add(Inventory(warehouse_id=source.id, product_variant_id=variant.id, quantity_on_hand=20, quantity_reserved=3))
    db.commit()
    return source, destination, variant


def test_stock_transfer_dispatch_and_receive_updates_both_warehouses() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        source, destination, variant = _seed(db)
        transfer = StockTransferService.create(db, StockTransferCreate(
            source_warehouse_id=source.id,
            destination_warehouse_id=destination.id,
            items=[StockTransferItemCreate(product_variant_id=variant.id, quantity=7)],
        ))
        assert transfer.status == "pending"
        StockTransferService.change_status(db, transfer.id, "approved")
        transfer = StockTransferService.change_status(db, transfer.id, "in_transit")
        assert transfer.shipped_at is not None
        source_inventory = db.execute(select(Inventory).where(Inventory.warehouse_id == source.id)).scalar_one()
        assert source_inventory.quantity_on_hand == 13
        transfer = StockTransferService.change_status(db, transfer.id, "received")
        destination_inventory = db.execute(select(Inventory).where(Inventory.warehouse_id == destination.id)).scalar_one()
        movements = db.execute(select(StockMovement).order_by(StockMovement.id)).scalars().all()
        assert transfer.received_at is not None
        assert destination_inventory.quantity_on_hand == 7
        assert [(m.movement_type, m.quantity) for m in movements] == [("TRANSFER_OUT", -7), ("TRANSFER_IN", 7)]


def test_stock_transfer_rejects_quantity_above_available_stock() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        source, destination, variant = _seed(db)
        transfer = StockTransferService.create(db, StockTransferCreate(
            source_warehouse_id=source.id,
            destination_warehouse_id=destination.id,
            items=[StockTransferItemCreate(product_variant_id=variant.id, quantity=18)],
        ))
        with pytest.raises(HTTPException) as exc_info:
            StockTransferService.change_status(db, transfer.id, "approved")
        assert exc_info.value.status_code == 409
