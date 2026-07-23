from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Business logic for category operations."""

    @staticmethod
    def create_category(
        db: Session,
        category_data: CategoryCreate,
    ) -> Category:
        existing_category = CategoryRepository.get_by_name(
            db=db,
            name=category_data.name,
        )

        if existing_category is not None:
            raise ValueError("Category name already exists")

        if category_data.parent_id is not None:
            parent_category = CategoryRepository.get_by_id(
                db=db,
                category_id=category_data.parent_id,
            )

            if parent_category is None:
                raise ValueError("Parent category not found")

            if not parent_category.is_active:
                raise ValueError("Parent category is inactive")

        category = Category(
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id,
        )

        return CategoryRepository.create(
            db=db,
            category=category,
        )

    @staticmethod
    def get_category(
        db: Session,
        category_id: int,
    ) -> Category:
        category = CategoryRepository.get_by_id(
            db=db,
            category_id=category_id,
        )

        if category is None:
            raise ValueError("Category not found")

        return category

    @staticmethod
    def list_categories(
        db: Session,
        *,
        search: str | None = None,
        is_active: bool | None = True,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Category]:
         return CategoryRepository.get_all(
            db=db,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    def update_category(
        db: Session,
        category_id: int,
        category_data: CategoryUpdate,
    ) -> Category:
        category = CategoryService.get_category(
            db=db,
            category_id=category_id,
        )

        update_data = category_data.model_dump(
            exclude_unset=True,
        )

        if "name" in update_data:
            existing_category = CategoryRepository.get_by_name(
                db=db,
                name=update_data["name"],
            )

            if (
                existing_category is not None
                and existing_category.id != category_id
            ):
                raise ValueError("Category name already exists")

        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]

            if parent_id == category_id:
                raise ValueError(
                    "Category cannot be its own parent"
                )

            if parent_id is not None:
                parent_category = CategoryRepository.get_by_id(
                    db=db,
                    category_id=parent_id,
                )

                if parent_category is None:
                    raise ValueError("Parent category not found")

                if not parent_category.is_active:
                    raise ValueError(
                        "Parent category is inactive"
                    )

        for field, value in update_data.items():
            setattr(category, field, value)

        return CategoryRepository.update(
            db=db,
            category=category,
        )

    @staticmethod
    def soft_delete_category(
        db: Session,
        category_id: int,
    ) -> Category:
        category = CategoryService.get_category(
            db=db,
            category_id=category_id,
        )

        if not category.is_active:
            raise ValueError("Category is already inactive")

        category.is_active = False

        return CategoryRepository.update(
            db=db,
            category=category,
        )