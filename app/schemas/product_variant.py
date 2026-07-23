from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductVariantBase(BaseModel):
    product_id: int = Field(..., gt=0)
    sku: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=1, max_length=150)
    price: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("sku", "name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class ProductVariantCreate(ProductVariantBase):
    is_active: bool = True


class ProductVariantUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    is_active: bool | None = None

    @field_validator("sku", "name")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class ProductVariantResponse(ProductVariantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
