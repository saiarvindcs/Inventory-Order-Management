from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PurchaseOrderItemCreate(BaseModel):
    product_variant_id: int = Field(gt=0)
    ordered_quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class PurchaseOrderItemResponse(PurchaseOrderItemCreate):
    id: int
    received_quantity: int
    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderCreate(BaseModel):
    supplier_id: int = Field(gt=0)
    warehouse_id: int = Field(gt=0)
    order_date: date
    expected_delivery_date: date | None = None
    notes: str | None = None
    items: list[PurchaseOrderItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dates_and_items(self):
        if self.expected_delivery_date and self.expected_delivery_date < self.order_date:
            raise ValueError("Expected delivery date cannot be before order date.")
        ids = [item.product_variant_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product variants are not allowed.")
        return self


class PurchaseOrderUpdate(BaseModel):
    expected_delivery_date: date | None = None
    notes: str | None = None


class PurchaseOrderStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(submitted|approved|cancelled)$")


class PurchaseOrderResponse(BaseModel):
    id: int
    order_number: str
    supplier_id: int
    warehouse_id: int
    status: str
    order_date: date
    expected_delivery_date: date | None
    total_amount: Decimal
    notes: str | None
    items: list[PurchaseOrderItemResponse]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptItemCreate(BaseModel):
    purchase_order_item_id: int = Field(gt=0)
    quantity_received: int = Field(gt=0)


class GoodsReceiptCreate(BaseModel):
    received_at: datetime
    notes: str | None = None
    items: list[GoodsReceiptItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_lines(self):
        ids = [item.purchase_order_item_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate purchase-order items are not allowed.")
        return self


class GoodsReceiptItemResponse(GoodsReceiptItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    purchase_order_id: int
    warehouse_id: int
    status: str
    received_at: datetime
    notes: str | None
    items: list[GoodsReceiptItemResponse]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
