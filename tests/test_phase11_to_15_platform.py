from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.address import Address
from app.models.base import BaseModel
from app.models.category import Category
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.platform import PaymentCreate, ReservationCreate, WebhookEvent
from app.services.platform import PaymentService, ReservationService


def test_reservation_and_idempotent_payment_workflows() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        user = User(full_name="Sai", email="sai@test.com", hashed_password="x", is_active=True)
        address = Address(user=user, recipient_name="Sai", phone="9999999999", address_line1="A", city="Chennai", state="TN", postal_code="600001", country="India")
        category = Category(name="Tech", is_active=True)
        product = Product(name="Phone", sku="P1", price=Decimal("100"), category=category, is_active=True)
        variant = ProductVariant(name="Black", sku="P1-B", price=Decimal("100"), product=product, is_active=True)
        warehouse = Warehouse(name="Main", code="WH", address_line1="A", city="Chennai", state="TN", postal_code="600001", country="India", is_active=True)
        db.add_all([user, product, warehouse]); db.flush()
        inventory = Inventory(warehouse_id=warehouse.id, product_variant_id=variant.id, quantity_on_hand=10, quantity_reserved=0)
        order = Order(order_number="ORD-1", customer_id=user.id, shipping_address_id=address.id, status="pending", payment_status="pending", subtotal=Decimal("100"), total_amount=Decimal("100"))
        order.items.append(OrderItem(product_variant_id=variant.id, quantity=1, unit_price=Decimal("100"), discount_amount=Decimal("0"), line_total=Decimal("100")))
        db.add_all([inventory, order]); db.commit()

        reservation = ReservationService.create(db, ReservationCreate(inventory_id=inventory.id, reservation_reference="ORD-1-ITEM-1", quantity=2))
        assert reservation.status == "active"
        assert inventory.quantity_reserved == 2
        ReservationService.release(db, reservation.id, consume=True)
        assert inventory.quantity_on_hand == 8
        assert inventory.quantity_reserved == 0

        data = PaymentCreate(order_id=order.id, provider="test", payment_method="card", amount=Decimal("100"), idempotency_key="same-key-123")
        first = PaymentService.create(db, data)
        second = PaymentService.create(db, data)
        assert first.id == second.id
        captured = PaymentService.process_webhook(db, "test", WebhookEvent(event_id="evt-1", event_type="payment.captured", payment_reference=first.payment_reference, provider_transaction_id="txn-1"))
        assert captured.status == "captured"
        assert order.payment_status == "paid"
