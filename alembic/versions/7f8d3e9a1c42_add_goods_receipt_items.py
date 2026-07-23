"""add goods receipt items

Revision ID: 7f8d3e9a1c42
Revises: 3cc3593203b9
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7f8d3e9a1c42"
down_revision: str | None = "3cc3593203b9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "goods_receipt_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("goods_receipt_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_item_id", sa.Integer(), nullable=False),
        sa.Column("quantity_received", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "quantity_received > 0",
            name="ck_goods_receipt_items_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["goods_receipt_id"], ["goods_receipts.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["purchase_order_item_id"],
            ["purchase_order_items.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_goods_receipt_items_id"), "goods_receipt_items", ["id"]
    )
    op.create_index(
        op.f("ix_goods_receipt_items_goods_receipt_id"),
        "goods_receipt_items",
        ["goods_receipt_id"],
    )
    op.create_index(
        op.f("ix_goods_receipt_items_purchase_order_item_id"),
        "goods_receipt_items",
        ["purchase_order_item_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_goods_receipt_items_purchase_order_item_id"),
        table_name="goods_receipt_items",
    )
    op.drop_index(
        op.f("ix_goods_receipt_items_goods_receipt_id"),
        table_name="goods_receipt_items",
    )
    op.drop_index(
        op.f("ix_goods_receipt_items_id"), table_name="goods_receipt_items"
    )
    op.drop_table("goods_receipt_items")
