from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session


#from app.core.security.oauth2 import get_current_user
from app.db.session import get_db

from app.schemas.warehouse import (
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)
from app.services.warehouse import WarehouseService

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"],
)


@router.post(
    "",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
   
) -> WarehouseResponse:
    try:
        warehouse = WarehouseService.create_warehouse(
            db=db,
            warehouse_data=warehouse_data,
        )

        return WarehouseResponse.model_validate(warehouse)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[WarehouseResponse],
)
def list_warehouses(
    search: str | None = Query(default=None),
    is_active: bool | None = Query(default=True),
    sort_by: str = Query(
        default="id",
        pattern="^(id|name|code)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
   
) -> list[WarehouseResponse]:
    warehouses = WarehouseService.list_warehouses(
        db=db,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

    return [
        WarehouseResponse.model_validate(warehouse)
        for warehouse in warehouses
    ]


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
   
) -> WarehouseResponse:
    try:
        warehouse = WarehouseService.get_warehouse(
            db=db,
            warehouse_id=warehouse_id,
        )

        return WarehouseResponse.model_validate(warehouse)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
    
) -> WarehouseResponse:
    try:
        warehouse = WarehouseService.update_warehouse(
            db=db,
            warehouse_id=warehouse_id,
            warehouse_data=warehouse_data,
        )

        return WarehouseResponse.model_validate(warehouse)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    
) -> WarehouseResponse:
    try:
        warehouse = WarehouseService.soft_delete_warehouse(
            db=db,
            warehouse_id=warehouse_id,
        )

        return WarehouseResponse.model_validate(warehouse)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc