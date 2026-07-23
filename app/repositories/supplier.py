from sqlalchemy import asc, desc, or_, select
from sqlalchemy.orm import Session
from app.models.supplier import Supplier


class SupplierRepository:
    @staticmethod
    def get_by_id(db: Session, supplier_id: int) -> Supplier | None:
        return db.execute(select(Supplier).where(Supplier.id == supplier_id)).scalar_one_or_none()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Supplier | None:
        return db.execute(select(Supplier).where(Supplier.code == code)).scalar_one_or_none()

    @staticmethod
    def list(db: Session, *, search: str | None = None, is_active: bool | None = None,
             sort_by: str = "id", sort_order: str = "asc", skip: int = 0, limit: int = 100) -> list[Supplier]:
        stmt = select(Supplier)
        if search:
            term = f"%{search}%"
            stmt = stmt.where(or_(Supplier.name.ilike(term), Supplier.code.ilike(term), Supplier.email.ilike(term)))
        if is_active is not None:
            stmt = stmt.where(Supplier.is_active == is_active)
        columns = {"id": Supplier.id, "name": Supplier.name, "code": Supplier.code, "created_at": Supplier.created_at}
        col = columns.get(sort_by, Supplier.id)
        stmt = stmt.order_by(desc(col) if sort_order == "desc" else asc(col)).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())
