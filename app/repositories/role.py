from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User


class RoleRepository:
    """Repository for role operations."""

    @staticmethod
    def get_by_name(
        db: Session,
        name: str,
    ) -> Role | None:
        statement = select(Role).where(
            Role.name == name
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        name: str,
        description: str | None = None,
    ) -> Role:
        role = Role(
            name=name,
            description=description,
        )

        db.add(role)
        db.commit()
        db.refresh(role)

        return role

    @staticmethod
    def assign_role_to_user(
        db: Session,
        user: User,
        role: Role,
    ) -> None:
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)