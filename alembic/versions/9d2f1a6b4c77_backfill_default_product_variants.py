"""Backfill a default product variant for products that do not have one.

Revision ID: 9d2f1a6b4c77
Revises: 7f8d3e9a1c42
"""

from collections.abc import Sequence

from alembic import op

revision: str = "9d2f1a6b4c77"
down_revision: str | None = "7f8d3e9a1c42"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO product_variants (product_id, sku, name, price, is_active, created_at, updated_at)
        SELECT p.id, p.sku || '-DEFAULT', 'Default', p.price, p.is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM products AS p
        WHERE NOT EXISTS (
            SELECT 1 FROM product_variants AS pv WHERE pv.product_id = p.id
        )
        ON CONFLICT (sku) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM product_variants WHERE name = 'Default' AND sku LIKE '%-DEFAULT'")
