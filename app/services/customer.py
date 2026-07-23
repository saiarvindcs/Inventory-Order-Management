from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security.hashing import hash_password
from app.models.address import Address
from app.models.user import User
from app.schemas.customer import AddressCreate, AddressUpdate, CustomerCreate


class CustomerService:
    @staticmethod
    def create(db: Session, data: CustomerCreate) -> User:
        email = data.email.lower()
        existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "A user with this email already exists.")
        customer = User(
            full_name=data.full_name.strip(),
            email=email,
            hashed_password=hash_password(data.password),
            is_active=True,
            is_verified=data.is_verified,
        )
        db.add(customer)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "A user with this email already exists.") from exc
        db.refresh(customer)
        return customer

    @staticmethod
    def get(db: Session, customer_id: int) -> User:
        customer = db.get(User, customer_id)
        if customer is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found.")
        return customer

    @staticmethod
    def list_customers(db: Session, *, skip: int = 0, limit: int = 100) -> list[User]:
        return list(db.execute(select(User).order_by(User.id.desc()).offset(skip).limit(limit)).scalars().all())

    @staticmethod
    def create_address(db: Session, customer_id: int, data: AddressCreate) -> Address:
        CustomerService.get(db, customer_id)
        if data.is_default_shipping:
            db.execute(update(Address).where(Address.user_id == customer_id).values(is_default_shipping=False))
        if data.is_default_billing:
            db.execute(update(Address).where(Address.user_id == customer_id).values(is_default_billing=False))
        address = Address(user_id=customer_id, **data.model_dump())
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def list_addresses(db: Session, customer_id: int) -> list[Address]:
        CustomerService.get(db, customer_id)
        return list(
            db.execute(select(Address).where(Address.user_id == customer_id).order_by(Address.id.desc()))
            .scalars()
            .all()
        )

    @staticmethod
    def update_address(db: Session, customer_id: int, address_id: int, data: AddressUpdate) -> Address:
        address = db.get(Address, address_id)
        if address is None or address.user_id != customer_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Address not found for this customer.")
        values = data.model_dump(exclude_unset=True)
        if values.get("is_default_shipping") is True:
            db.execute(update(Address).where(Address.user_id == customer_id).values(is_default_shipping=False))
        if values.get("is_default_billing") is True:
            db.execute(update(Address).where(Address.user_id == customer_id).values(is_default_billing=False))
        for field, value in values.items():
            setattr(address, field, value)
        db.commit()
        db.refresh(address)
        return address
