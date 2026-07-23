from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.category import CategoryRepository
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Business logic for product operations."""

    @staticmethod
    def create_product(
        db: Session,
        product_data: ProductCreate,
    ) -> Product:
        existing_product = ProductRepository.get_by_sku(
            db=db,
            sku=product_data.sku,
        )

        if existing_product is not None:
            raise ValueError("SKU already exists")

        category = CategoryRepository.get_by_id(
            db=db,
            category_id=product_data.category_id,
        )

        if category is None:
            raise ValueError("Category not found")

        if not category.is_active:
            raise ValueError("Category is inactive")

        product = Product(
            name=product_data.name,
            sku=product_data.sku,
            description=product_data.description,
            image_url=product_data.image_url,
            price=product_data.price,
            category_id=product_data.category_id,
        )

        return ProductRepository.create(
            db=db,
            product=product,
        )

    @staticmethod
    def get_product(
        db: Session,
        product_id: int,
    ) -> Product:
        product = ProductRepository.get_by_id(
            db=db,
            product_id=product_id,
        )

        if product is None:
            raise ValueError("Product not found")

        return product

    @staticmethod
    def list_products(
        db: Session,
        *,
        search: str | None = None,
        category_id: int | None = None,
        is_active: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Product]:
        return ProductRepository.get_all(
            db=db,
            search=search,
            category_id=category_id,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product_data: ProductUpdate,
    ) -> Product:
        product = ProductService.get_product(
            db=db,
            product_id=product_id,
        )

        update_data = product_data.model_dump(
            exclude_unset=True,
        )

        if "sku" in update_data:
            existing_product = ProductRepository.get_by_sku(
                db=db,
                sku=update_data["sku"],
            )

            if (
                existing_product is not None
                and existing_product.id != product_id
            ):
                raise ValueError("SKU already exists")

        if "category_id" in update_data:
            category = CategoryRepository.get_by_id(
                db=db,
                category_id=update_data["category_id"],
            )

            if category is None:
                raise ValueError("Category not found")

            if not category.is_active:
                raise ValueError("Category is inactive")

        for field, value in update_data.items():
            setattr(product, field, value)

        return ProductRepository.update(
            db=db,
            product=product,
        )

    @staticmethod
    def soft_delete_product(
        db: Session,
        product_id: int,
    ) -> Product:
        product = ProductService.get_product(
            db=db,
            product_id=product_id,
        )

        if not product.is_active:
            raise ValueError("Product is already inactive")

        product.is_active = False

        return ProductRepository.update(
            db=db,
            product=product,
        )