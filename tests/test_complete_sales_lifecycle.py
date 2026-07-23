from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.address import Address
from app.models.base import BaseModel
from app.models.category import Category
from app.models.notification import Notification
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.models.warehouse import Warehouse
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.platform import (
    PaymentCreate,
    RefundCreate,
    ReturnCreate,
    ReturnItemCreate,
    ShipmentCreate,
    ShipmentItemCreate,
    WebhookEvent,
)
from app.services.order import OrderService
from app.services.platform import FulfillmentService, PaymentService


def test_complete_sales_lifecycle_creates_notifications() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        customer = User(full_name="Customer", email="customer@test.com", hashed_password="x", is_active=True)
        address = Address(
            user=customer,
            recipient_name="Customer",
            phone="9999999999",
            address_line1="1 Main Street",
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600001",
            country="India",
            is_default_shipping=True,
            is_default_billing=True,
        )
        category = Category(name="Sales", is_active=True)
        product = Product(name="Phone", sku="PHONE-1", price=Decimal("100.00"), category=category, is_active=True)
        variant = ProductVariant(name="Default", sku="PHONE-1-DEFAULT", price=Decimal("100.00"), product=product, is_active=True)
        warehouse = Warehouse(
            name="Main Warehouse",
            code="MAIN-SALES",
            address_line1="Warehouse Road",
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600002",
            country="India",
            is_active=True,
        )
        db.add_all([customer, product, warehouse])
        db.commit()

        order = OrderService.create(
            db,
            OrderCreate(
                customer_id=customer.id,
                shipping_address_id=address.id,
                billing_address_id=address.id,
                items=[OrderItemCreate(product_variant_id=variant.id, quantity=1)],
            ),
        )
        payment = PaymentService.create(
            db,
            PaymentCreate(
                order_id=order.id,
                provider="test",
                payment_method="card",
                amount=order.total_amount,
                currency="INR",
                idempotency_key="sales-flow-payment-1",
            ),
        )
        PaymentService.process_webhook(
            db,
            "test",
            WebhookEvent(
                event_id="sales-flow-captured-1",
                event_type="payment.captured",
                payment_reference=payment.payment_reference,
                provider_transaction_id="txn-sales-1",
            ),
        )

        OrderService.change_status(db, order.id, "confirmed")
        OrderService.change_status(db, order.id, "processing")
        OrderService.change_status(db, order.id, "packed")

        shipment = FulfillmentService.create_shipment(
            db,
            ShipmentCreate(
                order_id=order.id,
                warehouse_id=warehouse.id,
                carrier="Test Carrier",
                tracking_number="TRACK-1",
                items=[ShipmentItemCreate(order_item_id=order.items[0].id, quantity=1)],
            ),
        )
        FulfillmentService.update_shipment(db, shipment.id, "packed", None)
        FulfillmentService.update_shipment(db, shipment.id, "shipped", None)
        FulfillmentService.update_shipment(db, shipment.id, "delivered", None)

        returned = FulfillmentService.create_return(
            db,
            ReturnCreate(
                order_id=order.id,
                reason="Changed mind",
                items=[
                    ReturnItemCreate(
                        order_item_id=order.items[0].id,
                        quantity=1,
                        condition="unopened",
                        resolution="refund",
                        refund_amount=order.total_amount,
                    )
                ],
            ),
        )
        FulfillmentService.update_return(db, returned.id, "approved")
        FulfillmentService.update_return(db, returned.id, "received")
        FulfillmentService.update_return(db, returned.id, "completed")

        refund = FulfillmentService.create_refund(
            db,
            RefundCreate(
                order_id=order.id,
                payment_id=payment.id,
                return_id=returned.id,
                amount=order.total_amount,
                currency="INR",
                reason="Approved return",
            ),
        )

        db.refresh(order)
        assert order.status == "delivered"
        assert order.payment_status == "refunded"
        assert refund.status == "processed"
        notifications = db.execute(
            select(Notification).where(Notification.user_id == customer.id).order_by(Notification.id)
        ).scalars().all()
        assert len(notifications) >= 10
        assert notifications[-1].notification_type == "refund_processed"
        notifications[-1].is_read = True
        db.commit()
        assert notifications[-1].is_read is True
