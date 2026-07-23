from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.repositories.inventory import InventoryRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryService:
    """
    Business logic for inventory operations.
    """

    @staticmethod
    def create_inventory(
        db: Session,
        inventory_data: InventoryCreate,
    ) -> Inventory:
        existing_inventory = (
            InventoryRepository.get_by_warehouse_and_variant(
                db=db,
                warehouse_id=inventory_data.warehouse_id,
                product_variant_id=inventory_data.product_variant_id,
            )
        )

        if existing_inventory is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Inventory already exists for this warehouse "
                    "and product variant."
                ),
            )

        if (
            inventory_data.quantity_reserved
            > inventory_data.quantity_on_hand
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Reserved quantity cannot be greater than "
                    "quantity on hand."
                ),
            )

        inventory = Inventory(
            warehouse_id=inventory_data.warehouse_id,
            product_variant_id=inventory_data.product_variant_id,
            quantity_on_hand=inventory_data.quantity_on_hand,
            quantity_reserved=inventory_data.quantity_reserved,
        )

        try:
            return InventoryRepository.create(
                db=db,
                inventory=inventory,
            )

        except IntegrityError as error:
            db.rollback()

            constraint_name = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                None,
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "constraint": constraint_name,
                    "database_error": str(error.orig),
                },
            ) from error

    @staticmethod
    def get_inventory(
        db: Session,
        inventory_id: int,
    ) -> Inventory:
        inventory = InventoryRepository.get_by_id(
            db=db,
            inventory_id=inventory_id,
        )

        if inventory is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory not found.",
            )

        return inventory

    @staticmethod
    def list_inventory(
        db: Session,
        *,
        warehouse_id: int | None = None,
        product_variant_id: int | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Inventory]:
        return InventoryRepository.get_all(
            db=db,
            warehouse_id=warehouse_id,
            product_variant_id=product_variant_id,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_inventory(
        db: Session,
        inventory_id: int,
        inventory_data: InventoryUpdate,
    ) -> Inventory:
        inventory = InventoryService.get_inventory(
            db=db,
            inventory_id=inventory_id,
        )

        update_data = inventory_data.model_dump(
            exclude_unset=True,
        )

        new_quantity_on_hand = update_data.get(
            "quantity_on_hand",
            inventory.quantity_on_hand,
        )

        new_quantity_reserved = update_data.get(
            "quantity_reserved",
            inventory.quantity_reserved,
        )

        if new_quantity_reserved > new_quantity_on_hand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Reserved quantity cannot be greater than "
                    "quantity on hand."
                ),
            )

        for field, value in update_data.items():
            setattr(inventory, field, value)

        return InventoryRepository.update(
            db=db,
            inventory=inventory,
        )