from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.customer import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    CustomerCreate,
    CustomerResponse,
)
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers & Addresses"])


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)) -> CustomerResponse:
    return CustomerResponse.model_validate(CustomerService.create(db, data))


@router.get("", response_model=list[CustomerResponse])
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CustomerResponse]:
    return [CustomerResponse.model_validate(x) for x in CustomerService.list_customers(db, skip=skip, limit=limit)]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> CustomerResponse:
    return CustomerResponse.model_validate(CustomerService.get(db, customer_id))


@router.post("/{customer_id}/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(customer_id: int, data: AddressCreate, db: Session = Depends(get_db)) -> AddressResponse:
    return AddressResponse.model_validate(CustomerService.create_address(db, customer_id, data))


@router.get("/{customer_id}/addresses", response_model=list[AddressResponse])
def list_addresses(customer_id: int, db: Session = Depends(get_db)) -> list[AddressResponse]:
    return [AddressResponse.model_validate(x) for x in CustomerService.list_addresses(db, customer_id)]


@router.patch("/{customer_id}/addresses/{address_id}", response_model=AddressResponse)
def update_address(
    customer_id: int,
    address_id: int,
    data: AddressUpdate,
    db: Session = Depends(get_db),
) -> AddressResponse:
    return AddressResponse.model_validate(CustomerService.update_address(db, customer_id, address_id, data))
