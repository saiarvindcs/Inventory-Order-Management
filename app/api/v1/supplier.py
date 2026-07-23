from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierUpdate
from app.services.supplier import SupplierService

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)) -> SupplierResponse:
    return SupplierResponse.model_validate(SupplierService.create(db, data))


@router.get("", response_model=list[SupplierResponse])
def list_suppliers(
    search: str | None = None,
    is_active: bool | None = None,
    sort_by: str = Query("id", pattern="^(id|name|code|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[SupplierResponse]:
    return [SupplierResponse.model_validate(item) for item in SupplierService.list(
        db, search=search, is_active=is_active, sort_by=sort_by,
        sort_order=sort_order, skip=skip, limit=limit
    )]


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)) -> SupplierResponse:
    return SupplierResponse.model_validate(SupplierService.get(db, supplier_id))


@router.patch("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)) -> SupplierResponse:
    return SupplierResponse.model_validate(SupplierService.update(db, supplier_id, data))
