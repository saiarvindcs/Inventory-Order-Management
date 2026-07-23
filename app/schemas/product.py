from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    """Base schema for product data."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Dell Inspiron 15"],
    )

    sku: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["DELL-INS-15-001"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=["15-inch business laptop"],
    )

    image_url: str | None = None

    price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        examples=[54999.99],
    )

    category_id: int = Field(
        ...,
        gt=0,
        examples=[1],
    )

    @field_validator("name", "sku")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Value cannot be empty")

        return cleaned_value


class ProductCreate(ProductBase):
    """Schema for creating a product."""


class ProductUpdate(BaseModel):
    """Schema for partially updating a product."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    sku: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    image_url: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    is_active: bool | None = None

    @field_validator("name", "sku")
    @classmethod
    def strip_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("Value cannot be empty")

        return cleaned_value


class ProductResponse(ProductBase):
    """Schema returned to API clients."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    is_active: bool