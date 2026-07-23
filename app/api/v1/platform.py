from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.inventory import Inventory
from app.models.notification import Notification
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product
from app.models.return_request import Return
from app.models.shipment import Shipment
from app.models.stock_reservation import StockReservation
from app.schemas.platform import (
    AuditLogResponse,
    NotificationResponse,
    PaymentCreate,
    PaymentResponse,
    RefundCreate,
    RefundResponse,
    ReservationCreate,
    ReservationResponse,
    ReturnCreate,
    ReturnResponse,
    ReturnStatusUpdate,
    ShipmentCreate,
    ShipmentResponse,
    ShipmentStatusUpdate,
    WebhookEvent,
)
from app.services.platform import FulfillmentService, PaymentService, ReservationService

router = APIRouter()

@router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED, tags=["Reservations"])
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    return ReservationService.create(db, data)

@router.get("/reservations", response_model=list[ReservationResponse], tags=["Reservations"])
def list_reservations(reservation_status: str | None = Query(None, alias="status"), db: Session = Depends(get_db)):
    stmt = select(StockReservation).order_by(StockReservation.id.desc())
    if reservation_status: stmt = stmt.where(StockReservation.status == reservation_status)
    return db.execute(stmt).scalars().all()

@router.post("/reservations/{reservation_id}/release", response_model=ReservationResponse, tags=["Reservations"])
def release_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return ReservationService.release(db, reservation_id)

@router.post("/reservations/{reservation_id}/consume", response_model=ReservationResponse, tags=["Reservations"])
def consume_reservation(reservation_id: int, db: Session = Depends(get_db)):
    return ReservationService.release(db, reservation_id, consume=True)

@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, tags=["Payments"])
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return PaymentService.create(db, data)

@router.get("/payments", response_model=list[PaymentResponse], tags=["Payments"])
def list_payments(order_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Payment).order_by(Payment.id.desc())
    if order_id: stmt = stmt.where(Payment.order_id == order_id)
    return db.execute(stmt).scalars().all()

@router.post("/payments/webhooks/{provider}", response_model=PaymentResponse, tags=["Payments"])
def payment_webhook(provider: str, data: WebhookEvent, db: Session = Depends(get_db)):
    return PaymentService.process_webhook(db, provider, data)

@router.post("/shipments", response_model=ShipmentResponse, status_code=status.HTTP_201_CREATED, tags=["Shipments"])
def create_shipment(data: ShipmentCreate, db: Session = Depends(get_db)):
    return FulfillmentService.create_shipment(db, data)

@router.get("/shipments", response_model=list[ShipmentResponse], tags=["Shipments"])
def list_shipments(order_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Shipment).order_by(Shipment.id.desc())
    if order_id: stmt = stmt.where(Shipment.order_id == order_id)
    return db.execute(stmt).scalars().all()

@router.post("/shipments/{shipment_id}/status", response_model=ShipmentResponse, tags=["Shipments"])
def update_shipment(shipment_id: int, data: ShipmentStatusUpdate, db: Session = Depends(get_db)):
    return FulfillmentService.update_shipment(db, shipment_id, data.status, data.tracking_number)

@router.post("/returns", response_model=ReturnResponse, status_code=status.HTTP_201_CREATED, tags=["Returns"])
def create_return(data: ReturnCreate, db: Session = Depends(get_db)):
    return FulfillmentService.create_return(db, data)

@router.get("/returns", response_model=list[ReturnResponse], tags=["Returns"])
def list_returns(order_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Return).order_by(Return.id.desc())
    if order_id: stmt = stmt.where(Return.order_id == order_id)
    return db.execute(stmt).scalars().all()

@router.post("/returns/{return_id}/status", response_model=ReturnResponse, tags=["Returns"])
def update_return(return_id: int, data: ReturnStatusUpdate, db: Session = Depends(get_db)):
    return FulfillmentService.update_return(db, return_id, data.status)

@router.post("/refunds", response_model=RefundResponse, status_code=status.HTTP_201_CREATED, tags=["Refunds"])
def create_refund(data: RefundCreate, db: Session = Depends(get_db)):
    return FulfillmentService.create_refund(db, data)


@router.get("/refunds", response_model=list[RefundResponse], tags=["Refunds"])
def list_refunds(order_id: int | None = None, db: Session = Depends(get_db)):
    from app.models.refund import Refund

    stmt = select(Refund).order_by(Refund.id.desc())
    if order_id:
        stmt = stmt.where(Refund.order_id == order_id)
    return db.execute(stmt).scalars().all()

@router.get("/reports/dashboard", tags=["Reports"])
def dashboard(db: Session = Depends(get_db)):
    return {
        "products": db.scalar(select(func.count()).select_from(Product)) or 0,
        "orders": db.scalar(select(func.count()).select_from(Order)) or 0,
        "inventory_units": db.scalar(select(func.coalesce(func.sum(Inventory.quantity_on_hand), 0))) or 0,
        "reserved_units": db.scalar(select(func.coalesce(func.sum(Inventory.quantity_reserved), 0))) or 0,
        "revenue": db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(Order.payment_status == "paid")) or 0,
    }

@router.get("/reports/low-stock", tags=["Reports"])
def low_stock(threshold: int = Query(10, ge=0), db: Session = Depends(get_db)):
    rows = db.execute(select(Inventory).where((Inventory.quantity_on_hand - Inventory.quantity_reserved) <= threshold)).scalars().all()
    return [{"inventory_id": x.id, "warehouse_id": x.warehouse_id, "product_variant_id": x.product_variant_id, "on_hand": x.quantity_on_hand, "reserved": x.quantity_reserved, "available": x.quantity_available} for x in rows]

@router.get("/audit-logs", response_model=list[AuditLogResponse], tags=["Audit Logs"])
def audit_logs(limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).scalars().all()

@router.get("/notifications", response_model=list[NotificationResponse], tags=["Notifications"])
def notifications(user_id: int, db: Session = Depends(get_db)):
    return db.execute(select(Notification).where(Notification.user_id == user_id).order_by(Notification.id.desc())).scalars().all()

@router.post("/notifications/{notification_id}/read", response_model=NotificationResponse, tags=["Notifications"])
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    item = db.get(Notification, notification_id)
    if item is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Notification not found.")
    item.is_read = True
    item.read_at = datetime.now(UTC)
    db.commit(); db.refresh(item)
    return item
