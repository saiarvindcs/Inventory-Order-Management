from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryUpdate,
)
from app.services.inventory import InventoryService


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.post(
    "",
    response_model=InventoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_inventory(
    inventory_data: InventoryCreate,
    db: Session = Depends(get_db),
) -> InventoryResponse:
    inventory = InventoryService.create_inventory(
        db=db,
        inventory_data=inventory_data,
    )

    return InventoryResponse.model_validate(inventory)


@router.get(
    "",
    response_model=list[InventoryResponse],
)
def list_inventory(
    warehouse_id: int | None = Query(
        default=None,
        gt=0,
    ),
    product_variant_id: int | None = Query(
        default=None,
        gt=0,
    ),
    sort_by: str = Query(
        default="id",
        pattern=(
            "^(id|warehouse_id|product_variant_id|"
            "quantity_on_hand|quantity_reserved)$"
        ),
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> list[InventoryResponse]:
    inventory_items = InventoryService.list_inventory(
        db=db,
        warehouse_id=warehouse_id,
        product_variant_id=product_variant_id,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

    return [
        InventoryResponse.model_validate(inventory)
        for inventory in inventory_items
    ]


@router.get(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def get_inventory(
    inventory_id: int,
    db: Session = Depends(get_db),
) -> InventoryResponse:
    inventory = InventoryService.get_inventory(
        db=db,
        inventory_id=inventory_id,
    )

    return InventoryResponse.model_validate(inventory)


@router.patch(
    "/{inventory_id}",
    response_model=InventoryResponse,
)
def update_inventory(
    inventory_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
) -> InventoryResponse:
    inventory = InventoryService.update_inventory(
        db=db,
        inventory_id=inventory_id,
        inventory_data=inventory_data,
    )

    return InventoryResponse.model_validate(inventory)