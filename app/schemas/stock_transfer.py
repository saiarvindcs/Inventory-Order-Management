from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StockTransferItemCreate(BaseModel):
    product_variant_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class StockTransferItemResponse(StockTransferItemCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class StockTransferCreate(BaseModel):
    source_warehouse_id: int = Field(gt=0)
    destination_warehouse_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=2000)
    items: list[StockTransferItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_transfer(self):
        if self.source_warehouse_id == self.destination_warehouse_id:
            raise ValueError("Source and destination warehouses must be different.")
        ids = [item.product_variant_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate product variants are not allowed.")
        return self


class StockTransferUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class StockTransferStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(approved|cancelled|in_transit|received)$")


class StockTransferResponse(BaseModel):
    id: int
    transfer_number: str
    source_warehouse_id: int
    destination_warehouse_id: int
    status: str
    notes: str | None
    shipped_at: datetime | None
    received_at: datetime | None
    items: list[StockTransferItemResponse]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
