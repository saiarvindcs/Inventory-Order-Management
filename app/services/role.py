from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.role import RoleRepository


class RoleService:
    """Business logic for role management."""

    DEFAULT_ROLES = [
        ("Admin", "System Administrator"),
        ("Manager", "Inventory Manager"),
        ("Warehouse Staff", "Warehouse Staff"),
        ("Viewer", "Read Only User"),
    ]

    @staticmethod
    def seed_roles(
        db: Session,
    ) -> None:
        for name, description in RoleService.DEFAULT_ROLES:
            role = RoleRepository.get_by_name(
                db=db,
                name=name,
            )

            if role is None:
                RoleRepository.create(
                    db=db,
                    name=name,
                    description=description,
                )

    @staticmethod
    def assign_admin_role(
        db: Session,
        user: User,
    ) -> None:
        admin_role = RoleRepository.get_by_name(
            db=db,
            name="Admin",
        )

        if admin_role is not None:
            RoleRepository.assign_role_to_user(
                db=db,
                user=user,
                role=admin_role,
            )