from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stock_transfer import (
    StockTransferCreate,
    StockTransferResponse,
    StockTransferStatusUpdate,
    StockTransferUpdate,
)
from app.services.stock_transfer import StockTransferService

router = APIRouter(prefix="/stock-transfers", tags=["Stock Transfers"])


@router.post("", response_model=StockTransferResponse, status_code=status.HTTP_201_CREATED)
def create_stock_transfer(data: StockTransferCreate, db: Session = Depends(get_db)) -> StockTransferResponse:
    return StockTransferResponse.model_validate(StockTransferService.create(db, data))


@router.get("", response_model=list[StockTransferResponse])
def list_stock_transfers(
    source_warehouse_id: int | None = Query(None, gt=0),
    destination_warehouse_id: int | None = Query(None, gt=0),
    transfer_status: str | None = Query(None, alias="status", pattern="^(pending|approved|in_transit|received|cancelled)$"),
    sort_by: str = Query("id", pattern="^(id|transfer_number|status|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[StockTransferResponse]:
    records = StockTransferService.list(
        db,
        source_warehouse_id=source_warehouse_id,
        destination_warehouse_id=destination_warehouse_id,
        status=transfer_status,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return [StockTransferResponse.model_validate(record) for record in records]


@router.get("/{stock_transfer_id}", response_model=StockTransferResponse)
def get_stock_transfer(stock_transfer_id: int, db: Session = Depends(get_db)) -> StockTransferResponse:
    return StockTransferResponse.model_validate(StockTransferService.get(db, stock_transfer_id))


@router.patch("/{stock_transfer_id}", response_model=StockTransferResponse)
def update_stock_transfer(
    stock_transfer_id: int,
    data: StockTransferUpdate,
    db: Session = Depends(get_db),
) -> StockTransferResponse:
    return StockTransferResponse.model_validate(StockTransferService.update(db, stock_transfer_id, data))


@router.post("/{stock_transfer_id}/status", response_model=StockTransferResponse)
def change_stock_transfer_status(
    stock_transfer_id: int,
    data: StockTransferStatusUpdate,
    db: Session = Depends(get_db),
) -> StockTransferResponse:
    return StockTransferResponse.model_validate(
        StockTransferService.change_status(db, stock_transfer_id, data.status)
    )
