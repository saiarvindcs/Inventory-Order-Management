from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.purchase_order import (
    GoodsReceiptCreate,
    GoodsReceiptResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    PurchaseOrderStatusUpdate,
    PurchaseOrderUpdate,
)
from app.services.purchase_order import PurchaseOrderService

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(data: PurchaseOrderCreate, db: Session = Depends(get_db)) -> PurchaseOrderResponse:
    return PurchaseOrderResponse.model_validate(PurchaseOrderService.create(db, data))


@router.get("", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(
    supplier_id: int | None = Query(None, gt=0),
    warehouse_id: int | None = Query(None, gt=0),
    po_status: str | None = Query(None, alias="status", pattern="^(draft|submitted|approved|partially_received|received|cancelled)$"),
    sort_by: str = Query("id", pattern="^(id|order_date|total_amount|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[PurchaseOrderResponse]:
    records = PurchaseOrderService.list(
        db, supplier_id=supplier_id, warehouse_id=warehouse_id, status=po_status,
        sort_by=sort_by, sort_order=sort_order, skip=skip, limit=limit,
    )
    return [PurchaseOrderResponse.model_validate(record) for record in records]


@router.get("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(purchase_order_id: int, db: Session = Depends(get_db)) -> PurchaseOrderResponse:
    return PurchaseOrderResponse.model_validate(PurchaseOrderService.get(db, purchase_order_id))


@router.patch("/{purchase_order_id}", response_model=PurchaseOrderResponse)
def update_purchase_order(purchase_order_id: int, data: PurchaseOrderUpdate, db: Session = Depends(get_db)) -> PurchaseOrderResponse:
    return PurchaseOrderResponse.model_validate(PurchaseOrderService.update(db, purchase_order_id, data))


@router.post("/{purchase_order_id}/status", response_model=PurchaseOrderResponse)
def change_purchase_order_status(purchase_order_id: int, data: PurchaseOrderStatusUpdate, db: Session = Depends(get_db)) -> PurchaseOrderResponse:
    return PurchaseOrderResponse.model_validate(PurchaseOrderService.change_status(db, purchase_order_id, data.status))


@router.post("/{purchase_order_id}/receipts", response_model=GoodsReceiptResponse, status_code=status.HTTP_201_CREATED)
def receive_purchase_order(purchase_order_id: int, data: GoodsReceiptCreate, db: Session = Depends(get_db)) -> GoodsReceiptResponse:
    return GoodsReceiptResponse.model_validate(PurchaseOrderService.receive(db, purchase_order_id, data))
