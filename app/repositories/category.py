from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    """Database operations for categories."""

    @staticmethod
    def get_by_id(
        db: Session,
        category_id: int,
    ) -> Category | None:
        statement = select(Category).where(
            Category.id == category_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Category | None:
        statement = select(Category).where(
            Category.name == name
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def get_all(
        db: Session,
        *,
        search: str | None = None,
        is_active: bool | None = True,
        sort_by: str = "id",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> list[Category]:
        statement = select(Category)

        if search:
            statement = statement.where(
                Category.name.ilike(f"%{search}%")
            )

        if is_active is not None:
            statement = statement.where(
                Category.is_active == is_active
            )

        sortable_columns = {
            "id": Category.id,
            "name": Category.name,
        }

        sort_column = sortable_columns.get(
            sort_by,
            Category.id,
        )

        if sort_order.lower() == "desc":
            statement = statement.order_by(
                desc(sort_column)
            )
        else:
            statement = statement.order_by(
                asc(sort_column)
            )

        statement = (
            statement
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.execute(statement).scalars().all()
        )

    @staticmethod
    def create(
        db: Session,
        category: Category,
    ) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def update(
        db: Session,
        category: Category,
    ) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)

        return category