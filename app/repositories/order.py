from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order


class OrderRepository:
    @staticmethod
    def get_by_id(db: Session, order_id: int, *, for_update: bool = False) -> Order | None:
        statement = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items), selectinload(Order.status_history))
        )
        if for_update:
            statement = statement.with_for_update()
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def list(
        db: Session,
        *,
        customer_id: int | None = None,
        status: str | None = None,
        payment_status: str | None = None,
        sort_by: str = "id",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Order]:
        statement = select(Order).options(selectinload(Order.items), selectinload(Order.status_history))
        if customer_id is not None:
            statement = statement.where(Order.customer_id == customer_id)
        if status is not None:
            statement = statement.where(Order.status == status)
        if payment_status is not None:
            statement = statement.where(Order.payment_status == payment_status)
        sort_column = getattr(Order, sort_by, Order.id)
        statement = statement.order_by((asc if sort_order == "asc" else desc)(sort_column)).offset(skip).limit(limit)
        return list(db.execute(statement).scalars().unique().all())
