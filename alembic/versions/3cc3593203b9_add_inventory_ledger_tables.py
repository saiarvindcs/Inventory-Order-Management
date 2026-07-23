"""add inventory ledger tables

Revision ID: 3cc3593203b9
Revises: 81ca58c3f349
Create Date: 2026-07-20 16:02:17.568494
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "3cc3593203b9"
down_revision: Union[str, Sequence[str], None] = "81ca58c3f349"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "inventory",
        "quantity",
        new_column_name="quantity_on_hand",
    )

    op.alter_column(
        "inventory",
        "reserved_quantity",
        new_column_name="quantity_reserved",
    )

    op.create_unique_constraint(
        "uq_inventory_warehouse_variant",
        "inventory",
        [
            "warehouse_id",
            "product_variant_id",
        ],
    )

    op.create_check_constraint(
        "ck_inventory_reserved_not_greater_than_on_hand",
        "inventory",
        "quantity_reserved <= quantity_on_hand",
    )

    op.create_index(
        "ix_stock_movements_movement_type",
        "stock_movements",
        ["movement_type"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_stock_movements_movement_type",
        table_name="stock_movements",
    )

    op.drop_constraint(
        "ck_inventory_reserved_not_greater_than_on_hand",
        "inventory",
        type_="check",
    )

    op.drop_constraint(
        "uq_inventory_warehouse_variant",
        "inventory",
        type_="unique",
    )

    op.alter_column(
        "inventory",
        "quantity_reserved",
        new_column_name="reserved_quantity",
    )

    op.alter_column(
        "inventory",
        "quantity_on_hand",
        new_column_name="quantity",
    )