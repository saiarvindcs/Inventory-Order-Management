from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_verified: bool = False


class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddressCreate(BaseModel):
    label: str | None = Field(default=None, max_length=50)
    recipient_name: str = Field(min_length=2, max_length=150)
    phone: str = Field(min_length=5, max_length=30)
    address_line1: str = Field(min_length=3, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=3, max_length=20)
    country: str = Field(min_length=2, max_length=100)
    is_default_shipping: bool = False
    is_default_billing: bool = False


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=50)
    recipient_name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    address_line1: str | None = Field(default=None, min_length=3, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=100)
    postal_code: str | None = Field(default=None, min_length=3, max_length=20)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    is_default_shipping: bool | None = None
    is_default_billing: bool | None = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    label: str | None
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_default_shipping: bool
    is_default_billing: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
