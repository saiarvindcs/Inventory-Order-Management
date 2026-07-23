from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.models.product_variant import ProductVariant
from app.repositories.product import ProductRepository
from app.repositories.product_variant import ProductVariantRepository
from app.schemas.product_variant import ProductVariantCreate, ProductVariantUpdate


class ProductVariantService:
    @staticmethod
    def create(db: Session, data: ProductVariantCreate) -> ProductVariant:
        product = ProductRepository.get_by_id(db, data.product_id)
        if product is None:
            raise ValueError("Product not found")
        if not product.is_active:
            raise ValueError("Product is inactive")
        if ProductVariantRepository.get_by_sku(db, data.sku) is not None:
            raise ValueError("Variant SKU already exists")

        variant = ProductVariant(
            product_id=data.product_id,
            sku=data.sku,
            name=data.name,
            price=data.price,
            is_active=data.is_active,
        )
        return ProductVariantRepository.save(db, variant)

    @staticmethod
    def get(db: Session, variant_id: int) -> ProductVariant:
        variant = ProductVariantRepository.get_by_id(db, variant_id)
        if variant is None:
            raise ValueError("Product variant not found")
        return variant

    @staticmethod
    def list(db: Session, **filters: object) -> list[ProductVariant]:
        return ProductVariantRepository.list(db, **filters)

    @staticmethod
    def update(
        db: Session,
        variant_id: int,
        data: ProductVariantUpdate,
    ) -> ProductVariant:
        variant = ProductVariantService.get(db, variant_id)
        changes = data.model_dump(exclude_unset=True)

        new_sku = changes.get("sku")
        if new_sku is not None:
            existing = ProductVariantRepository.get_by_sku(db, str(new_sku))
            if existing is not None and existing.id != variant.id:
                raise ValueError("Variant SKU already exists")

        new_price = changes.get("price")
        if new_price is not None and new_price != variant.price:
            db.add(
                PriceHistory(
                    product_variant_id=variant.id,
                    old_price=variant.price,
                    new_price=new_price,
                )
            )

        for field, value in changes.items():
            setattr(variant, field, value)
        return ProductVariantRepository.save(db, variant)

    @staticmethod
    def deactivate(db: Session, variant_id: int) -> ProductVariant:
        variant = ProductVariantService.get(db, variant_id)
        if not variant.is_active:
            raise ValueError("Product variant is already inactive")
        variant.is_active = False
        return ProductVariantRepository.save(db, variant)
