from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse as WarehouseModel
from app.repositories.warehouse import WarehouseRepository
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate


class WarehouseService:
    """
    Business logic for warehouse operations.
    """

    @staticmethod
    def create_warehouse(
        db: Session,
        warehouse_data: WarehouseCreate,
    ) -> WarehouseModel:
        existing_code = WarehouseRepository.get_by_code(
            db=db,
            code=warehouse_data.code,
        )

        if existing_code is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse code already exists.",
            )

        existing_name = WarehouseRepository.get_by_name(
            db=db,
            name=warehouse_data.name,
        )

        if existing_name is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse name already exists.",
            )

        warehouse = WarehouseModel(
            name=warehouse_data.name,
            code=warehouse_data.code,
            address_line1=warehouse_data.address_line1,
            address_line2=warehouse_data.address_line2,
            city=warehouse_data.city,
            state=warehouse_data.state,
            postal_code=warehouse_data.postal_code,
            country=warehouse_data.country,
            is_active=warehouse_data.is_active,
        )

        try:
            return WarehouseRepository.create(
                db=db,
                warehouse=warehouse,
            )

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse name or code already exists.",
            ) from error

    @staticmethod
    def get_warehouse(
        db: Session,
        warehouse_id: int,
    ) -> WarehouseModel:
        warehouse = WarehouseRepository.get_by_id(
            db=db,
            warehouse_id=warehouse_id,
        )

        if warehouse is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Warehouse not found.",
            )

        return warehouse

    @staticmethod
    def list_warehouses(
        db: Session,
        *,
        search: str | None = None,
        is_active: bool | None = True,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[WarehouseModel]:
        return WarehouseRepository.get_all(
            db=db,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_warehouse(
        db: Session,
        warehouse_id: int,
        warehouse_data: WarehouseUpdate,
    ) -> WarehouseModel:
        warehouse = WarehouseService.get_warehouse(
            db=db,
            warehouse_id=warehouse_id,
        )

        update_data = warehouse_data.model_dump(
            exclude_unset=True,
        )

        if "code" in update_data:
            existing_code = WarehouseRepository.get_by_code(
                db=db,
                code=update_data["code"],
            )

            if (
                existing_code is not None
                and existing_code.id != warehouse_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Warehouse code already exists.",
                )

        if "name" in update_data:
            existing_name = WarehouseRepository.get_by_name(
                db=db,
                name=update_data["name"],
            )

            if (
                existing_name is not None
                and existing_name.id != warehouse_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Warehouse name already exists.",
                )

        for field, value in update_data.items():
            setattr(warehouse, field, value)

        try:
            return WarehouseRepository.update(
                db=db,
                warehouse=warehouse,
            )

        except IntegrityError as error:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Warehouse name or code already exists.",
            ) from error

    @staticmethod
    def soft_delete_warehouse(
        db: Session,
        warehouse_id: int,
    ) -> WarehouseModel:
        warehouse = WarehouseService.get_warehouse(
            db=db,
            warehouse_id=warehouse_id,
        )

        if not warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse is already inactive.",
            )

        warehouse.is_active = False

        return WarehouseRepository.update(
            db=db,
            warehouse=warehouse,
        )

    @staticmethod
    def activate_warehouse(
        db: Session,
        warehouse_id: int,
    ) -> WarehouseModel:
        warehouse = WarehouseService.get_warehouse(
            db=db,
            warehouse_id=warehouse_id,
        )

        if warehouse.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Warehouse is already active.",
            )

        warehouse.is_active = True

        return WarehouseRepository.update(
            db=db,
            warehouse=warehouse,
        )