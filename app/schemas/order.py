from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderItemCreate(BaseModel):
    product_variant_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    shipping_address_id: int = Field(gt=0)
    billing_address_id: int | None = Field(default=None, gt=0)
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    shipping_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    notes: str | None = Field(default=None, max_length=2000)
    items: list[OrderItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_variants(self):
        ids = [item.product_variant_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product variants are not allowed.")
        return self


class OrderUpdate(BaseModel):
    shipping_address_id: int | None = Field(default=None, gt=0)
    billing_address_id: int | None = Field(default=None, gt=0)
    tax_amount: Decimal | None = Field(default=None, ge=0)
    shipping_amount: Decimal | None = Field(default=None, ge=0)
    discount_amount: Decimal | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)


class OrderStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(confirmed|processing|packed|shipped|delivered|cancelled)$")
    notes: str | None = Field(default=None, max_length=2000)
    changed_by_id: int | None = Field(default=None, gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_variant_id: int
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    line_total: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderStatusHistoryResponse(BaseModel):
    id: int
    status: str
    changed_by_id: int | None
    notes: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    status: str
    payment_status: str
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    shipping_address_id: int
    billing_address_id: int | None
    notes: str | None
    placed_at: datetime | None
    cancelled_at: datetime | None
    items: list[OrderItemResponse]
    status_history: list[OrderStatusHistoryResponse]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
