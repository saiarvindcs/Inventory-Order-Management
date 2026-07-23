from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.models.address import Address
from app.models.base import BaseModel
from app.models.category import Category
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate
from app.services.order import OrderService


def _seed(db: Session):
    user = User(
        full_name="Test Customer",
        email="customer@example.com",
        hashed_password="not-a-real-hash",
        is_active=True,
        is_verified=True,
    )
    address = Address(
        user=user,
        label="Home",
        recipient_name="Test Customer",
        phone="9999999999",
        address_line1="1 Test Street",
        city="Chennai",
        state="Tamil Nadu",
        postal_code="600001",
        country="India",
        is_default_shipping=True,
        is_default_billing=True,
    )
    category = Category(name="Phones", is_active=True)
    product = Product(name="Phone", sku="PHONE", price=Decimal("100.00"), category=category, is_active=True)
    variant = ProductVariant(name="Black", sku="PHONE-BLK", price=Decimal("100.00"), product=product, is_active=True)
    db.add_all([user, product])
    db.commit()
    return user, address, variant


def test_order_totals_and_complete_status_history() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        user, address, variant = _seed(db)
        order = OrderService.create(
            db,
            OrderCreate(
                customer_id=user.id,
                shipping_address_id=address.id,
                billing_address_id=address.id,
                tax_amount=Decimal("18.00"),
                shipping_amount=Decimal("10.00"),
                discount_amount=Decimal("5.00"),
                items=[
                    OrderItemCreate(
                        product_variant_id=variant.id,
                        quantity=2,
                        discount_amount=Decimal("20.00"),
                    )
                ],
            ),
        )
        assert order.subtotal == Decimal("180.00")
        assert order.total_amount == Decimal("203.00")
        assert [entry.status for entry in order.status_history] == ["pending"]

        for next_status in ["confirmed", "processing", "packed", "shipped", "delivered"]:
            order = OrderService.change_status(db, order.id, next_status, changed_by_id=user.id)

        assert order.status == "delivered"
        assert [entry.status for entry in order.status_history] == [
            "pending",
            "confirmed",
            "processing",
            "packed",
            "shipped",
            "delivered",
        ]


def test_order_rejects_invalid_transition_and_post_confirmation_edit() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        user, address, variant = _seed(db)
        order = OrderService.create(
            db,
            OrderCreate(
                customer_id=user.id,
                shipping_address_id=address.id,
                items=[OrderItemCreate(product_variant_id=variant.id, quantity=1)],
            ),
        )
        with pytest.raises(HTTPException) as invalid_transition:
            OrderService.change_status(db, order.id, "delivered")
        assert invalid_transition.value.status_code == 409

        OrderService.change_status(db, order.id, "confirmed")
        with pytest.raises(HTTPException) as invalid_edit:
            OrderService.update(db, order.id, OrderUpdate(notes="Too late"))
        assert invalid_edit.value.status_code == 409


def test_order_address_must_belong_to_customer() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    with Session(engine) as db:
        user, _, variant = _seed(db)
        other = User(full_name="Other", email="other@example.com", hashed_password="x", is_active=True)
        wrong_address = Address(
            user=other,
            recipient_name="Other",
            phone="8888888888",
            address_line1="2 Other Street",
            city="Chennai",
            state="Tamil Nadu",
            postal_code="600002",
            country="India",
        )
        db.add(other)
        db.commit()
        with pytest.raises(HTTPException) as exc_info:
            OrderService.create(
                db,
                OrderCreate(
                    customer_id=user.id,
                    shipping_address_id=wrong_address.id,
                    items=[OrderItemCreate(product_variant_id=variant.id, quantity=1)],
                ),
            )
        assert exc_info.value.status_code == 400
