from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.goods_receipt import GoodsReceipt
from app.models.goods_receipt_item import GoodsReceiptItem
from app.models.inventory import Inventory
from app.models.product_variant import ProductVariant
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.stock_movement import StockMovement
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.repositories.purchase_order import PurchaseOrderRepository
from app.schemas.purchase_order import GoodsReceiptCreate, PurchaseOrderCreate, PurchaseOrderUpdate


ALLOWED_TRANSITIONS = {
    "draft": {"submitted", "cancelled"},
    "submitted": {"approved", "cancelled"},
    "approved": set(),
    "partially_received": set(),
    "received": set(),
    "cancelled": set(),
}


class PurchaseOrderService:
    @staticmethod
    def _number(prefix: str) -> str:
        return f"{prefix}-{datetime.now(UTC):%Y%m%d%H%M%S}-{uuid4().hex[:8].upper()}"

    @staticmethod
    def create(db: Session, data: PurchaseOrderCreate) -> PurchaseOrder:
        supplier = db.get(Supplier, data.supplier_id)
        if supplier is None or not supplier.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Active supplier not found.")
        warehouse = db.get(Warehouse, data.warehouse_id)
        if warehouse is None or not warehouse.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Active warehouse not found.")

        variant_ids = [item.product_variant_id for item in data.items]
        variants = db.execute(select(ProductVariant).where(ProductVariant.id.in_(variant_ids))).scalars().all()
        active_ids = {variant.id for variant in variants if variant.is_active}
        missing = sorted(set(variant_ids) - active_ids)
        if missing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid or inactive product variants: {missing}")

        total = sum((Decimal(item.ordered_quantity) * item.unit_price for item in data.items), Decimal("0.00"))
        po = PurchaseOrder(
            order_number=PurchaseOrderService._number("PO"),
            supplier_id=data.supplier_id,
            warehouse_id=data.warehouse_id,
            status="draft",
            order_date=data.order_date,
            expected_delivery_date=data.expected_delivery_date,
            total_amount=total,
            notes=data.notes,
            items=[PurchaseOrderItem(**item.model_dump()) for item in data.items],
        )
        db.add(po)
        try:
            db.commit()
            return PurchaseOrderService.get(db, po.id)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Could not create purchase order.") from exc

    @staticmethod
    def get(db: Session, purchase_order_id: int, *, for_update: bool = False) -> PurchaseOrder:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items), selectinload(PurchaseOrder.goods_receipts).selectinload(GoodsReceipt.items))
            .where(PurchaseOrder.id == purchase_order_id)
        )
        if for_update:
            stmt = stmt.with_for_update()
        po = db.execute(stmt).scalar_one_or_none()
        if po is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Purchase order not found.")
        return po

    @staticmethod
    def list(db: Session, **kwargs) -> list[PurchaseOrder]:
        return PurchaseOrderRepository.list(db, **kwargs)

    @staticmethod
    def update(db: Session, purchase_order_id: int, data: PurchaseOrderUpdate) -> PurchaseOrder:
        po = PurchaseOrderService.get(db, purchase_order_id)
        if po.status != "draft":
            raise HTTPException(status.HTTP_409_CONFLICT, "Only draft purchase orders can be edited.")
        updates = data.model_dump(exclude_unset=True)
        expected = updates.get("expected_delivery_date")
        if expected is not None and expected < po.order_date:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Expected delivery date cannot be before order date.")
        for field, value in updates.items():
            setattr(po, field, value)
        db.commit()
        return PurchaseOrderService.get(db, po.id)

    @staticmethod
    def change_status(db: Session, purchase_order_id: int, new_status: str) -> PurchaseOrder:
        po = PurchaseOrderService.get(db, purchase_order_id, for_update=True)
        if new_status not in ALLOWED_TRANSITIONS.get(po.status, set()):
            raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot change status from {po.status} to {new_status}.")
        po.status = new_status
        db.commit()
        return PurchaseOrderService.get(db, po.id)

    @staticmethod
    def receive(db: Session, purchase_order_id: int, data: GoodsReceiptCreate) -> GoodsReceipt:
        try:
            po = PurchaseOrderService.get(db, purchase_order_id, for_update=True)
            if po.status not in {"approved", "partially_received"}:
                raise HTTPException(status.HTTP_409_CONFLICT, "Only approved purchase orders can be received.")

            po_items = {item.id: item for item in po.items}
            for received in data.items:
                line = po_items.get(received.purchase_order_item_id)
                if line is None:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Receipt item does not belong to this purchase order.")
                remaining = line.ordered_quantity - line.received_quantity
                if received.quantity_received > remaining:
                    raise HTTPException(status.HTTP_409_CONFLICT, f"Received quantity exceeds remaining quantity for PO item {line.id}.")

            receipt = GoodsReceipt(
                receipt_number=PurchaseOrderService._number("GRN"),
                purchase_order_id=po.id,
                warehouse_id=po.warehouse_id,
                status="received",
                received_at=data.received_at,
                notes=data.notes,
            )
            db.add(receipt)
            db.flush()

            for received in data.items:
                line = po_items[received.purchase_order_item_id]
                line.received_quantity += received.quantity_received
                receipt.items.append(GoodsReceiptItem(
                    purchase_order_item_id=line.id,
                    quantity_received=received.quantity_received,
                ))
                inventory = db.execute(
                    select(Inventory).where(
                        Inventory.warehouse_id == po.warehouse_id,
                        Inventory.product_variant_id == line.product_variant_id,
                    ).with_for_update()
                ).scalar_one_or_none()
                if inventory is None:
                    inventory = Inventory(
                        warehouse_id=po.warehouse_id,
                        product_variant_id=line.product_variant_id,
                        quantity_on_hand=0,
                        quantity_reserved=0,
                    )
                    db.add(inventory)
                    db.flush()
                inventory.quantity_on_hand += received.quantity_received
                db.add(StockMovement(
                    inventory_id=inventory.id,
                    movement_type="PURCHASE_RECEIPT",
                    quantity=received.quantity_received,
                ))

            po.status = "received" if all(item.received_quantity == item.ordered_quantity for item in po.items) else "partially_received"
            db.commit()
            return db.execute(
                select(GoodsReceipt).options(selectinload(GoodsReceipt.items)).where(GoodsReceipt.id == receipt.id)
            ).scalar_one()
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Could not record goods receipt.") from exc
