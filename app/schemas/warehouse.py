from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseBase(BaseModel):
    """
    Shared warehouse fields.
    """

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    code: str = Field(
        min_length=2,
        max_length=50,
    )

    address_line1: str = Field(
        min_length=2,
        max_length=255,
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str = Field(
        min_length=2,
        max_length=100,
    )

    state: str = Field(
        min_length=2,
        max_length=100,
    )

    postal_code: str = Field(
        min_length=3,
        max_length=20,
    )

    country: str = Field(
        default="India",
        min_length=2,
        max_length=100,
    )

    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    """
    Schema used when creating a warehouse.
    """

    pass


class WarehouseUpdate(BaseModel):
    """
    Schema used when updating a warehouse.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    code: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    address_line1: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
    )

    country: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    is_active: bool | None = None


class WarehouseResponse(WarehouseBase):
    """
    Warehouse response schema.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )