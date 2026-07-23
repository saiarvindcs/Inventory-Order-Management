from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse as WarehouseModel


class WarehouseRepository:
    """
    Database operations for warehouses.
    """

    @staticmethod
    def get_by_id(
        db: Session,
        warehouse_id: int,
    ) -> WarehouseModel | None:
        statement = select(WarehouseModel).where(
            WarehouseModel.id == warehouse_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_by_code(
        db: Session,
        code: str,
    ) -> WarehouseModel | None:
        statement = select(WarehouseModel).where(
            WarehouseModel.code == code
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> WarehouseModel | None:
        statement = select(WarehouseModel).where(
            WarehouseModel.name == name
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        *,
        search: str | None = None,
        is_active: bool | None = True,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[WarehouseModel]:
        statement = select(WarehouseModel)

        if search:
            search_value = f"%{search.strip()}%"

            statement = statement.where(
                or_(
                    WarehouseModel.name.ilike(search_value),
                    WarehouseModel.code.ilike(search_value),
                    WarehouseModel.city.ilike(search_value),
                    WarehouseModel.state.ilike(search_value),
                    WarehouseModel.country.ilike(search_value),
                )
            )

        if is_active is not None:
            statement = statement.where(
                WarehouseModel.is_active == is_active
            )

        sortable_columns = {
            "id": WarehouseModel.id,
            "name": WarehouseModel.name,
            "code": WarehouseModel.code,
            "city": WarehouseModel.city,
            "state": WarehouseModel.state,
            "country": WarehouseModel.country,
            "is_active": WarehouseModel.is_active,
        }

        sort_column = sortable_columns.get(
            sort_by,
            WarehouseModel.id,
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
        warehouse: WarehouseModel,
    ) -> WarehouseModel:
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)

        return warehouse

    @staticmethod
    def update(
        db: Session,
        warehouse: WarehouseModel,
    ) -> WarehouseModel:
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)

        return warehouse