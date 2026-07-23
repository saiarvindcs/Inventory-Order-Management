from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.repositories.supplier import SupplierRepository
from app.schemas.supplier import SupplierCreate, SupplierUpdate


class SupplierService:
    @staticmethod
    def create(db: Session, data: SupplierCreate) -> Supplier:
        code = data.code.strip().upper()
        if SupplierRepository.get_by_code(db, code):
            raise HTTPException(status.HTTP_409_CONFLICT, "Supplier code already exists.")
        supplier = Supplier(**data.model_dump(exclude={"code"}), code=code)
        db.add(supplier)
        try:
            db.commit()
            db.refresh(supplier)
            return supplier
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Supplier data conflicts with an existing supplier.") from exc

    @staticmethod
    def get(db: Session, supplier_id: int) -> Supplier:
        supplier = SupplierRepository.get_by_id(db, supplier_id)
        if supplier is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Supplier not found.")
        return supplier

    @staticmethod
    def list(db: Session, **kwargs) -> list[Supplier]:
        return SupplierRepository.list(db, **kwargs)

    @staticmethod
    def update(db: Session, supplier_id: int, data: SupplierUpdate) -> Supplier:
        supplier = SupplierService.get(db, supplier_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(supplier, field, value)
        try:
            db.commit()
            db.refresh(supplier)
            return supplier
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Supplier data conflicts with an existing supplier.") from exc
