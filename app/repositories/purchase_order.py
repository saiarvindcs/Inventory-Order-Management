from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, selectinload
from app.models.purchase_order import PurchaseOrder


class PurchaseOrderRepository:
    @staticmethod
    def get_by_id(db: Session, purchase_order_id: int, *, for_update: bool = False) -> PurchaseOrder | None:
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.items), selectinload(PurchaseOrder.goods_receipts)).where(PurchaseOrder.id == purchase_order_id)
        if for_update:
            stmt = stmt.with_for_update()
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list(db: Session, *, supplier_id: int | None = None, warehouse_id: int | None = None,
             status: str | None = None, sort_by: str = "id", sort_order: str = "desc",
             skip: int = 0, limit: int = 100) -> list[PurchaseOrder]:
        stmt = select(PurchaseOrder).options(selectinload(PurchaseOrder.items))
        if supplier_id is not None: stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
        if warehouse_id is not None: stmt = stmt.where(PurchaseOrder.warehouse_id == warehouse_id)
        if status is not None: stmt = stmt.where(PurchaseOrder.status == status)
        columns = {"id": PurchaseOrder.id, "order_date": PurchaseOrder.order_date, "total_amount": PurchaseOrder.total_amount, "status": PurchaseOrder.status}
        col = columns.get(sort_by, PurchaseOrder.id)
        stmt = stmt.order_by(desc(col) if sort_order == "desc" else asc(col)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())
