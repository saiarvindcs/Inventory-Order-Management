from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.payment_event import PaymentEvent
from app.models.refund import Refund
from app.models.return_item import ReturnItem
from app.models.return_request import Return
from app.models.shipment import Shipment
from app.models.shipment_item import ShipmentItem
from app.models.stock_reservation import StockReservation
from app.models.warehouse import Warehouse
from app.services.notification import NotificationService
from app.schemas.platform import (
    PaymentCreate,
    RefundCreate,
    ReservationCreate,
    ReturnCreate,
    ShipmentCreate,
    WebhookEvent,
)


def _commit(db: Session, message: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, message) from exc


class ReservationService:
    @staticmethod
    def create(db: Session, data: ReservationCreate) -> StockReservation:
        inventory = db.execute(
            select(Inventory).where(Inventory.id == data.inventory_id).with_for_update()
        ).scalar_one_or_none()
        if inventory is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Inventory record not found.")
        if inventory.quantity_available < data.quantity:
            raise HTTPException(status.HTTP_409_CONFLICT, "Insufficient available inventory.")
        reservation = StockReservation(**data.model_dump(), status="active")
        inventory.quantity_reserved += data.quantity
        db.add(reservation)
        _commit(db, "Reservation reference already exists.")
        db.refresh(reservation)
        return reservation

    @staticmethod
    def release(db: Session, reservation_id: int, *, consume: bool = False) -> StockReservation:
        reservation = db.execute(
            select(StockReservation).where(StockReservation.id == reservation_id).with_for_update()
        ).scalar_one_or_none()
        if reservation is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found.")
        if reservation.status != "active":
            raise HTTPException(status.HTTP_409_CONFLICT, "Reservation is no longer active.")
        inventory = db.execute(
            select(Inventory).where(Inventory.id == reservation.inventory_id).with_for_update()
        ).scalar_one()
        inventory.quantity_reserved -= reservation.quantity
        if consume:
            if inventory.quantity_on_hand < reservation.quantity:
                raise HTTPException(status.HTTP_409_CONFLICT, "Inventory balance changed unexpectedly.")
            inventory.quantity_on_hand -= reservation.quantity
            reservation.status = "consumed"
        else:
            reservation.status = "released"
        db.commit()
        db.refresh(reservation)
        return reservation


class PaymentService:
    @staticmethod
    def create(db: Session, data: PaymentCreate) -> Payment:
        existing = db.execute(select(Payment).where(Payment.idempotency_key == data.idempotency_key)).scalar_one_or_none()
        if existing is not None:
            return existing
        order = db.get(Order, data.order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found.")
        if data.amount != order.total_amount:
            raise HTTPException(status.HTTP_409_CONFLICT, "Payment amount must match the order total.")
        if order.payment_status in {"paid", "refunded"}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Order is not eligible for a new payment.")
        payment = Payment(
            **data.model_dump(exclude={"currency"}),
            currency=data.currency.upper(),
            payment_reference=f"PAY-{uuid4().hex[:12].upper()}",
            status="pending",
        )
        db.add(payment)
        _commit(db, "Duplicate payment request.")
        db.refresh(payment)
        return payment

    @staticmethod
    def process_webhook(db: Session, provider: str, data: WebhookEvent) -> Payment:
        existing = db.execute(select(PaymentEvent).where(PaymentEvent.event_id == data.event_id)).scalar_one_or_none()
        if existing is not None:
            return existing.payment
        payment = db.execute(
            select(Payment).where(Payment.payment_reference == data.payment_reference).with_for_update()
        ).scalar_one_or_none()
        if payment is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found.")
        now = datetime.now(UTC)
        mapping = {
            "payment.authorized": "authorized",
            "payment.captured": "captured",
            "payment.failed": "failed",
        }
        new_status = mapping.get(data.event_type)
        if new_status is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported payment event type.")
        payment.status = new_status
        payment.provider_transaction_id = data.provider_transaction_id or payment.provider_transaction_id
        if new_status == "authorized":
            payment.authorized_at = now
        elif new_status == "captured":
            payment.captured_at = now
            payment.order.payment_status = "paid"
        else:
            payment.failed_at = now
            payment.failure_reason = data.failure_reason
            payment.order.payment_status = "failed"
        NotificationService.add(
            db,
            user_id=payment.order.customer_id,
            title="Payment update",
            message=f"Payment for order {payment.order.order_number} is {new_status}.",
            notification_type=f"payment_{new_status}",
        )
        db.add(PaymentEvent(
            payment=payment,
            event_id=data.event_id,
            event_type=data.event_type,
            provider=provider,
            processing_status="processed",
            payload=data.payload,
        ))
        _commit(db, "Duplicate webhook event.")
        db.refresh(payment)
        return payment


class FulfillmentService:
    @staticmethod
    def create_shipment(db: Session, data: ShipmentCreate) -> Shipment:
        order = db.get(Order, data.order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found.")
        if db.get(Warehouse, data.warehouse_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Warehouse not found.")
        item_ids = [item.order_item_id for item in data.items]
        items = db.execute(select(OrderItem).where(OrderItem.id.in_(item_ids))).scalars().all()
        item_map = {item.id: item for item in items if item.order_id == order.id}
        if set(item_ids) != set(item_map):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Shipment items must belong to the order.")
        shipment = Shipment(
            shipment_number=f"SHP-{uuid4().hex[:12].upper()}",
            order_id=order.id,
            warehouse_id=data.warehouse_id,
            carrier=data.carrier,
            tracking_number=data.tracking_number,
            notes=data.notes,
            status="pending",
        )
        for item_data in data.items:
            already = db.scalar(select(func.coalesce(func.sum(ShipmentItem.quantity), 0)).where(ShipmentItem.order_item_id == item_data.order_item_id))
            if int(already or 0) + item_data.quantity > item_map[item_data.order_item_id].quantity:
                raise HTTPException(status.HTTP_409_CONFLICT, "Shipment quantity exceeds ordered quantity.")
            shipment.items.append(ShipmentItem(**item_data.model_dump()))
        db.add(shipment)
        NotificationService.add(
            db,
            user_id=order.customer_id,
            title="Shipment created",
            message=f"Shipment {shipment.shipment_number} was created for order {order.order_number}.",
            notification_type="shipment_created",
        )
        _commit(db, "Could not create shipment.")
        db.refresh(shipment)
        return shipment

    @staticmethod
    def update_shipment(db: Session, shipment_id: int, new_status: str, tracking_number: str | None) -> Shipment:
        shipment = db.get(Shipment, shipment_id)
        if shipment is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found.")
        allowed = {"pending": {"packed", "cancelled"}, "packed": {"shipped", "cancelled"}, "shipped": {"delivered"}, "delivered": set(), "cancelled": set()}
        if new_status not in allowed.get(shipment.status, set()):
            raise HTTPException(status.HTTP_409_CONFLICT, "Invalid shipment status transition.")
        shipment.status = new_status
        shipment.tracking_number = tracking_number or shipment.tracking_number
        now = datetime.now(UTC)
        if new_status == "shipped":
            shipment.shipped_at = now
            shipment.order.status = "shipped"
        elif new_status == "delivered":
            shipment.delivered_at = now
            shipment.order.status = "delivered"
        NotificationService.add(
            db,
            user_id=shipment.order.customer_id,
            title="Shipment status updated",
            message=f"Shipment {shipment.shipment_number} is now {new_status}.",
            notification_type="shipment_status",
        )
        db.commit()
        db.refresh(shipment)
        return shipment

    @staticmethod
    def create_return(db: Session, data: ReturnCreate) -> Return:
        order = db.get(Order, data.order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found.")
        if order.status != "delivered":
            raise HTTPException(status.HTTP_409_CONFLICT, "Returns are allowed only for delivered orders.")
        order_items = {item.id: item for item in order.items}
        result = Return(
            return_number=f"RET-{uuid4().hex[:12].upper()}",
            order_id=order.id,
            customer_id=order.customer_id,
            status="requested",
            reason=data.reason,
            requested_at=datetime.now(UTC),
        )
        requested_by_item: dict[int, int] = {}
        for item_data in data.items:
            requested_by_item[item_data.order_item_id] = (
                requested_by_item.get(item_data.order_item_id, 0) + item_data.quantity
            )
        for order_item_id, requested_quantity in requested_by_item.items():
            item = order_items.get(order_item_id)
            if item is None:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Return item must belong to the order.")
            previously_returned = db.scalar(
                select(func.coalesce(func.sum(ReturnItem.quantity), 0))
                .join(Return, Return.id == ReturnItem.return_id)
                .where(
                    Return.order_id == order.id,
                    Return.status != "rejected",
                    ReturnItem.order_item_id == order_item_id,
                )
            )
            if int(previously_returned or 0) + requested_quantity > item.quantity:
                raise HTTPException(status.HTTP_409_CONFLICT, "Return quantity exceeds delivered quantity.")
        for item_data in data.items:
            result.items.append(ReturnItem(**item_data.model_dump()))
        db.add(result)
        NotificationService.add(
            db,
            user_id=order.customer_id,
            title="Return requested",
            message=f"Return {result.return_number} was requested for order {order.order_number}.",
            notification_type="return_created",
        )
        _commit(db, "Could not create return request.")
        db.refresh(result)
        return result

    @staticmethod
    def update_return(db: Session, return_id: int, new_status: str) -> Return:
        result = db.get(Return, return_id)
        if result is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Return request not found.")
        allowed = {"requested": {"approved", "rejected"}, "approved": {"received"}, "received": {"completed"}, "rejected": set(), "completed": set()}
        if new_status not in allowed.get(result.status, set()):
            raise HTTPException(status.HTTP_409_CONFLICT, "Invalid return status transition.")
        result.status = new_status
        now = datetime.now(UTC)
        if new_status == "approved": result.approved_at = now
        elif new_status == "completed": result.completed_at = now
        NotificationService.add(
            db,
            user_id=result.customer_id,
            title="Return status updated",
            message=f"Return {result.return_number} is now {new_status}.",
            notification_type="return_status",
        )
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def create_refund(db: Session, data: RefundCreate) -> Refund:
        order = db.get(Order, data.order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found.")
        if order.payment_status not in {"paid", "partially_refunded"}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only paid orders can be refunded.")
        if data.payment_id is not None:
            payment = db.get(Payment, data.payment_id)
            if payment is None or payment.order_id != order.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Payment must belong to the order.")
        if data.return_id is not None:
            return_request = db.get(Return, data.return_id)
            if return_request is None or return_request.order_id != order.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Return request must belong to the order.")
        refunded_total = db.scalar(
            select(func.coalesce(func.sum(Refund.amount), 0)).where(
                Refund.order_id == order.id,
                Refund.status == "processed",
            )
        )
        if Decimal(refunded_total or 0) + data.amount > order.total_amount:
            raise HTTPException(status.HTTP_409_CONFLICT, "Refund exceeds the remaining refundable amount.")
        refund = Refund(
            **data.model_dump(),
            refund_reference=f"RFD-{uuid4().hex[:12].upper()}",
            status="processed",
            processed_at=datetime.now(UTC),
        )
        db.add(refund)
        total_after_refund = Decimal(refunded_total or 0) + data.amount
        order.payment_status = "refunded" if total_after_refund == order.total_amount else "partially_refunded"
        NotificationService.add(
            db,
            user_id=order.customer_id,
            title="Refund processed",
            message=f"Refund {refund.refund_reference} for {data.currency.upper()} {data.amount} was processed.",
            notification_type="refund_processed",
        )
        _commit(db, "Could not create refund.")
        db.refresh(refund)
        return refund
