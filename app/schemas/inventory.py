from pydantic import BaseModel, ConfigDict, Field


class InventoryBase(BaseModel):
    """
    Shared inventory fields.
    """

    warehouse_id: int = Field(
        gt=0,
    )

    product_variant_id: int = Field(
        gt=0,
    )

    quantity_on_hand: int = Field(
        ge=0,
        default=0,
    )

    quantity_reserved: int = Field(
        ge=0,
        default=0,
    )


class InventoryCreate(InventoryBase):
    """
    Schema for creating inventory.
    """

    pass


class InventoryUpdate(BaseModel):
    """
    Schema for updating inventory.
    """

    quantity_on_hand: int | None = Field(
        default=None,
        ge=0,
    )

    quantity_reserved: int | None = Field(
        default=None,
        ge=0,
    )


class InventoryResponse(InventoryBase):
    """
    Inventory response schema.
    """

    id: int
    quantity_available: int

    model_config = ConfigDict(
        from_attributes=True,
    )