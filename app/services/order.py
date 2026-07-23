from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.notification import NotificationService


class OrderService:
    @staticmethod
    def _number() -> str:
        return f"ORD-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:8].upper()}"

    @staticmethod
    def _validate_addresses(db: Session, customer_id: int, shipping_id: int, billing_id: int | None) -> None:
        ids = {shipping_id}
        if billing_id is not None:
            ids.add(billing_id)
        addresses = db.execute(select(Address).where(Address.id.in_(ids))).scalars().all()
        valid = {address.id for address in addresses if address.user_id == customer_id}
        if valid != ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Shipping and billing addresses must belong to the customer.")

    @staticmethod
    def _calculate_total(order: Order) -> None:
        order.subtotal = sum((item.line_total for item in order.items), Decimal("0.00"))
        order.total_amount = max(
            Decimal("0.00"),
            order.subtotal + order.tax_amount + order.shipping_amount - order.discount_amount,
        )

    @staticmethod
    def create(db: Session, data: OrderCreate) -> Order:
        customer = db.get(User, data.customer_id)
        if customer is None or not customer.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Active customer not found.")
        OrderService._validate_addresses(db, data.customer_id, data.shipping_address_id, data.billing_address_id)

        ids = [item.product_variant_id for item in data.items]
        variants = db.execute(select(ProductVariant).where(ProductVariant.id.in_(ids))).scalars().all()
        variant_map = {variant.id: variant for variant in variants if variant.is_active}
        missing = sorted(set(ids) - set(variant_map))
        if missing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid or inactive product variants: {missing}")

        order = Order(
            order_number=OrderService._number(),
            customer_id=data.customer_id,
            shipping_address_id=data.shipping_address_id,
            billing_address_id=data.billing_address_id,
            status="pending",
            payment_status="pending",
            tax_amount=data.tax_amount,
            shipping_amount=data.shipping_amount,
            discount_amount=data.discount_amount,
            notes=data.notes,
            placed_at=datetime.now(UTC),
        )
        for item_data in data.items:
            variant = variant_map[item_data.product_variant_id]
            line_total = max(
                Decimal("0.00"),
                (variant.price * item_data.quantity) - item_data.discount_amount,
            )
            order.items.append(
                OrderItem(
                    product_variant_id=variant.id,
                    quantity=item_data.quantity,
                    unit_price=variant.price,
                    discount_amount=item_data.discount_amount,
                    line_total=line_total,
                )
            )
        OrderService._calculate_total(order)
        order.status_history.append(OrderStatusHistory(status="pending", notes="Order created."))
        db.add(order)
        NotificationService.add(
            db,
            user_id=data.customer_id,
            title="Order placed",
            message=f"Your order {order.order_number} has been placed successfully.",
            notification_type="order_created",
        )
        try:
            db.commit()
            return OrderService.get(db, order.id)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Could not create order.") from exc

    @staticmethod
    def get(db: Session, order_id: int, *, for_update: bool = False) -> Order:
        order = OrderRepository.get_by_id(db, order_id, for_update=for_update)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found.")
        return order

    @staticmethod
    def list(db: Session, **kwargs) -> list[Order]:
        return OrderRepository.list(db, **kwargs)

    @staticmethod
    def update(db: Session, order_id: int, data: OrderUpdate) -> Order:
        order = OrderService.get(db, order_id, for_update=True)
        if order.status != "pending":
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Only pending orders can be edited.")
        values = data.model_dump(exclude_unset=True)
        shipping_id = values.get("shipping_address_id", order.shipping_address_id)
        billing_id = values.get("billing_address_id", order.billing_address_id)
        OrderService._validate_addresses(db, order.customer_id, shipping_id, billing_id)
        for field, value in values.items():
            setattr(order, field, value)
        OrderService._calculate_total(order)
        db.commit()
        return OrderService.get(db, order.id)

    @staticmethod
    def change_status(
        db: Session,
        order_id: int,
        new_status: str,
        *,
        notes: str | None = None,
        changed_by_id: int | None = None,
    ) -> Order:
        order = OrderService.get(db, order_id, for_update=True)
        allowed = {
            "pending": {"confirmed", "cancelled"},
            "confirmed": {"processing", "cancelled"},
            "processing": {"packed", "cancelled"},
            "packed": {"shipped", "cancelled"},
            "shipped": {"delivered"},
            "delivered": set(),
            "cancelled": set(),
        }
        if new_status not in allowed.get(order.status, set()):
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot change status from {order.status} to {new_status}.")
        if changed_by_id is not None and db.get(User, changed_by_id) is None:
            db.rollback()
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Status-change user not found.")
        order.status = new_status
        if new_status == "cancelled":
            order.cancelled_at = datetime.now(UTC)
        order.status_history.append(
            OrderStatusHistory(status=new_status, changed_by_id=changed_by_id, notes=notes)
        )
        NotificationService.add(
            db,
            user_id=order.customer_id,
            title="Order status updated",
            message=f"Order {order.order_number} is now {new_status}.",
            notification_type="order_status",
        )
        db.commit()
        return OrderService.get(db, order.id)
