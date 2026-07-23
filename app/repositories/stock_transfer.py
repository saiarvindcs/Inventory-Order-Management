from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.stock_transfer import StockTransfer


class StockTransferRepository:
    @staticmethod
    def get_by_id(db: Session, stock_transfer_id: int, *, for_update: bool = False) -> StockTransfer | None:
        stmt = (
            select(StockTransfer)
            .options(selectinload(StockTransfer.items))
            .where(StockTransfer.id == stock_transfer_id)
        )
        if for_update:
            stmt = stmt.with_for_update()
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list(
        db: Session,
        *,
        source_warehouse_id: int | None = None,
        destination_warehouse_id: int | None = None,
        status: str | None = None,
        sort_by: str = "id",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[StockTransfer]:
        stmt = select(StockTransfer).options(selectinload(StockTransfer.items))
        if source_warehouse_id is not None:
            stmt = stmt.where(StockTransfer.source_warehouse_id == source_warehouse_id)
        if destination_warehouse_id is not None:
            stmt = stmt.where(StockTransfer.destination_warehouse_id == destination_warehouse_id)
        if status is not None:
            stmt = stmt.where(StockTransfer.status == status)
        columns = {
            "id": StockTransfer.id,
            "transfer_number": StockTransfer.transfer_number,
            "status": StockTransfer.status,
            "created_at": StockTransfer.created_at,
        }
        column = columns.get(sort_by, StockTransfer.id)
        stmt = stmt.order_by(desc(column) if sort_order == "desc" else asc(column)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())
