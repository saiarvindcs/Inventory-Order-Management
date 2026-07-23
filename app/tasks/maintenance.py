from datetime import UTC, datetime

from sqlalchemy import select

from app.core.celery import celery_app
from app.db.session import SessionLocal
from app.models.stock_reservation import StockReservation


@celery_app.task(name="expire_stock_reservations")
def expire_stock_reservations() -> int:
    expired_count = 0
    with SessionLocal() as db:
        reservations = db.execute(
            select(StockReservation).where(
                StockReservation.status == "active",
                StockReservation.expires_at.is_not(None),
                StockReservation.expires_at < datetime.now(UTC),
            )
        ).scalars().all()
        for reservation in reservations:
            reservation.inventory.quantity_reserved -= reservation.quantity
            reservation.status = "expired"
            expired_count += 1
        db.commit()
    return expired_count
