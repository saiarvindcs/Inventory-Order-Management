from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory


class InventoryRepository:
    """
    Database operations for inventory.
    """

    @staticmethod
    def get_by_id(
        db: Session,
        inventory_id: int,
    ) -> Inventory | None:
        statement = select(Inventory).where(
            Inventory.id == inventory_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_by_warehouse_and_variant(
        db: Session,
        *,
        warehouse_id: int,
        product_variant_id: int,
    ) -> Inventory | None:
        statement = select(Inventory).where(
            Inventory.warehouse_id == warehouse_id,
            Inventory.product_variant_id == product_variant_id,
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        *,
        warehouse_id: int | None = None,
        product_variant_id: int | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Inventory]:
        statement = select(Inventory)

        if warehouse_id is not None:
            statement = statement.where(
                Inventory.warehouse_id == warehouse_id
            )

        if product_variant_id is not None:
            statement = statement.where(
                Inventory.product_variant_id == product_variant_id
            )

        sortable_columns = {
            "id": Inventory.id,
            "warehouse_id": Inventory.warehouse_id,
            "product_variant_id": Inventory.product_variant_id,
            "quantity_on_hand": Inventory.quantity_on_hand,
            "quantity_reserved": Inventory.quantity_reserved,
        }

        sort_column = sortable_columns.get(
            sort_by,
            Inventory.id,
        )

        if sort_order.lower() == "desc":
            statement = statement.order_by(
                desc(sort_column)
            )
        else:
            statement = statement.order_by(
                asc(sort_column)
            )

        statement = (
            statement
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def create(
        db: Session,
        inventory: Inventory,
    ) -> Inventory:
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

        return inventory

    @staticmethod
    def update(
        db: Session,
        inventory: Inventory,
    ) -> Inventory:
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

        return inventory