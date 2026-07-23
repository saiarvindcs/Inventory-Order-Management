from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderUpdate
from app.services.order import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, db: Session = Depends(get_db)) -> OrderResponse:
    return OrderResponse.model_validate(OrderService.create(db, data))


@router.get("", response_model=list[OrderResponse])
def list_orders(
    customer_id: int | None = Query(None, gt=0),
    order_status: str | None = Query(None, alias="status"),
    payment_status: str | None = Query(None),
    sort_by: str = Query("id", pattern="^(id|order_number|status|total_amount|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    records = OrderService.list(
        db,
        customer_id=customer_id,
        status=order_status,
        payment_status=payment_status,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return [OrderResponse.model_validate(record) for record in records]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)) -> OrderResponse:
    return OrderResponse.model_validate(OrderService.get(db, order_id))


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)) -> OrderResponse:
    return OrderResponse.model_validate(OrderService.update(db, order_id, data))


@router.post("/{order_id}/status", response_model=OrderResponse)
def change_order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)) -> OrderResponse:
    return OrderResponse.model_validate(
        OrderService.change_status(
            db,
            order_id,
            data.status,
            notes=data.notes,
            changed_by_id=data.changed_by_id,
        )
    )
