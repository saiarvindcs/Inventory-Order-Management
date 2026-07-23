from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.product_variant import ProductVariant
from app.models.stock_movement import StockMovement
from app.models.stock_transfer import StockTransfer
from app.models.stock_transfer_item import StockTransferItem
from app.models.warehouse import Warehouse
from app.repositories.stock_transfer import StockTransferRepository
from app.schemas.stock_transfer import StockTransferCreate, StockTransferUpdate


class StockTransferService:
    @staticmethod
    def _number() -> str:
        return f"TRF-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:8].upper()}"

    @staticmethod
    def create(db: Session, data: StockTransferCreate) -> StockTransfer:
        source = db.get(Warehouse, data.source_warehouse_id)
        destination = db.get(Warehouse, data.destination_warehouse_id)
        if source is None or not source.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Active source warehouse not found.")
        if destination is None or not destination.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Active destination warehouse not found.")

        variant_ids = [item.product_variant_id for item in data.items]
        variants = db.execute(select(ProductVariant).where(ProductVariant.id.in_(variant_ids))).scalars().all()
        active_ids = {variant.id for variant in variants if variant.is_active}
        missing = sorted(set(variant_ids) - active_ids)
        if missing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid or inactive product variants: {missing}")

        transfer = StockTransfer(
            transfer_number=StockTransferService._number(),
            source_warehouse_id=data.source_warehouse_id,
            destination_warehouse_id=data.destination_warehouse_id,
            status="pending",
            notes=data.notes,
            items=[StockTransferItem(**item.model_dump()) for item in data.items],
        )
        db.add(transfer)
        try:
            db.commit()
            return StockTransferService.get(db, transfer.id)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Could not create stock transfer.") from exc

    @staticmethod
    def get(db: Session, stock_transfer_id: int, *, for_update: bool = False) -> StockTransfer:
        transfer = StockTransferRepository.get_by_id(db, stock_transfer_id, for_update=for_update)
        if transfer is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Stock transfer not found.")
        return transfer

    @staticmethod
    def list(db: Session, **kwargs) -> list[StockTransfer]:
        return StockTransferRepository.list(db, **kwargs)

    @staticmethod
    def update(db: Session, stock_transfer_id: int, data: StockTransferUpdate) -> StockTransfer:
        transfer = StockTransferService.get(db, stock_transfer_id)
        if transfer.status != "pending":
            raise HTTPException(status.HTTP_409_CONFLICT, "Only pending transfers can be edited.")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(transfer, field, value)
        db.commit()
        return StockTransferService.get(db, transfer.id)

    @staticmethod
    def _source_inventory(db: Session, transfer: StockTransfer) -> dict[int, Inventory]:
        variant_ids = [item.product_variant_id for item in transfer.items]
        rows = db.execute(
            select(Inventory)
            .where(
                Inventory.warehouse_id == transfer.source_warehouse_id,
                Inventory.product_variant_id.in_(variant_ids),
            )
            .with_for_update()
        ).scalars().all()
        return {row.product_variant_id: row for row in rows}

    @staticmethod
    def change_status(db: Session, stock_transfer_id: int, new_status: str) -> StockTransfer:
        try:
            transfer = StockTransferService.get(db, stock_transfer_id, for_update=True)
            allowed = {
                "pending": {"approved", "cancelled"},
                "approved": {"in_transit", "cancelled"},
                "in_transit": {"received"},
                "received": set(),
                "cancelled": set(),
            }
            if new_status not in allowed.get(transfer.status, set()):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Cannot change status from {transfer.status} to {new_status}.",
                )

            if new_status in {"approved", "in_transit"}:
                inventories = StockTransferService._source_inventory(db, transfer)
                shortages: list[str] = []
                for item in transfer.items:
                    inventory = inventories.get(item.product_variant_id)
                    available = 0 if inventory is None else inventory.quantity_available
                    if available < item.quantity:
                        shortages.append(
                            f"variant {item.product_variant_id}: required {item.quantity}, available {available}"
                        )
                if shortages:
                    raise HTTPException(
                        status.HTTP_409_CONFLICT,
                        "Insufficient source stock: " + "; ".join(shortages),
                    )

            if new_status == "in_transit":
                inventories = StockTransferService._source_inventory(db, transfer)
                for item in transfer.items:
                    inventory = inventories[item.product_variant_id]
                    inventory.quantity_on_hand -= item.quantity
                    db.add(
                        StockMovement(
                            inventory_id=inventory.id,
                            movement_type="TRANSFER_OUT",
                            quantity=-item.quantity,
                        )
                    )
                transfer.shipped_at = datetime.now(UTC)

            if new_status == "received":
                for item in transfer.items:
                    inventory = db.execute(
                        select(Inventory)
                        .where(
                            Inventory.warehouse_id == transfer.destination_warehouse_id,
                            Inventory.product_variant_id == item.product_variant_id,
                        )
                        .with_for_update()
                    ).scalar_one_or_none()
                    if inventory is None:
                        inventory = Inventory(
                            warehouse_id=transfer.destination_warehouse_id,
                            product_variant_id=item.product_variant_id,
                            quantity_on_hand=0,
                            quantity_reserved=0,
                        )
                        db.add(inventory)
                        db.flush()
                    inventory.quantity_on_hand += item.quantity
                    db.add(
                        StockMovement(
                            inventory_id=inventory.id,
                            movement_type="TRANSFER_IN",
                            quantity=item.quantity,
                        )
                    )
                transfer.received_at = datetime.now(UTC)

            transfer.status = new_status
            db.commit()
            return StockTransferService.get(db, transfer.id)
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Could not update stock transfer.") from exc
