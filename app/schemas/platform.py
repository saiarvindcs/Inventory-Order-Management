from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    inventory_id: int = Field(gt=0)
    reservation_reference: str = Field(min_length=3, max_length=100)
    quantity: int = Field(gt=0)
    expires_at: datetime | None = None


class ReservationResponse(ORMModel):
    id: int
    inventory_id: int
    reservation_reference: str
    quantity: int
    status: str
    expires_at: datetime | None
    created_at: datetime


class PaymentCreate(BaseModel):
    order_id: int = Field(gt=0)
    provider: str = Field(min_length=2, max_length=50)
    payment_method: str = Field(min_length=2, max_length=50)
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    idempotency_key: str = Field(min_length=8, max_length=255)


class PaymentResponse(ORMModel):
    id: int
    order_id: int
    payment_reference: str
    provider: str
    payment_method: str
    status: str
    amount: Decimal
    currency: str
    provider_transaction_id: str | None
    failure_reason: str | None
    authorized_at: datetime | None
    captured_at: datetime | None
    failed_at: datetime | None
    created_at: datetime


class WebhookEvent(BaseModel):
    event_id: str = Field(min_length=3, max_length=255)
    event_type: str = Field(min_length=3, max_length=100)
    payment_reference: str
    provider_transaction_id: str | None = None
    failure_reason: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ShipmentItemCreate(BaseModel):
    order_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class ShipmentCreate(BaseModel):
    order_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    carrier: str | None = Field(default=None, max_length=100)
    tracking_number: str | None = Field(default=None, max_length=150)
    notes: str | None = None
    items: list[ShipmentItemCreate] = Field(min_length=1)


class ShipmentStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|packed|shipped|delivered|cancelled)$")
    tracking_number: str | None = None


class ShipmentResponse(ORMModel):
    id: int
    shipment_number: str
    order_id: int
    warehouse_id: int
    status: str
    carrier: str | None
    tracking_number: str | None
    shipped_at: datetime | None
    delivered_at: datetime | None
    notes: str | None
    created_at: datetime


class ReturnItemCreate(BaseModel):
    order_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    condition: str | None = None
    resolution: str = Field(default="refund", pattern="^(refund|replacement|store_credit)$")
    refund_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class ReturnCreate(BaseModel):
    order_id: int = Field(gt=0)
    reason: str = Field(min_length=3)
    items: list[ReturnItemCreate] = Field(min_length=1)


class ReturnStatusUpdate(BaseModel):
    status: str = Field(pattern="^(requested|approved|rejected|received|completed)$")


class ReturnResponse(ORMModel):
    id: int
    return_number: str
    order_id: int
    status: str
    reason: str
    requested_at: datetime
    approved_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class RefundCreate(BaseModel):
    order_id: int = Field(gt=0)
    payment_id: int | None = Field(default=None, gt=0)
    return_id: int | None = Field(default=None, gt=0)
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    reason: str | None = None


class RefundResponse(ORMModel):
    id: int
    refund_reference: str
    order_id: int
    payment_id: int | None
    return_id: int | None
    amount: Decimal
    currency: str
    status: str
    provider_refund_id: str | None
    reason: str | None
    processed_at: datetime | None
    failed_at: datetime | None
    created_at: datetime


class NotificationResponse(ORMModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class AuditLogResponse(ORMModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: str | None
    request_id: str | None
    ip_address: str | None
    old_values: dict | None
    new_values: dict | None
    extra_metadata: dict | None
    created_at: datetime
