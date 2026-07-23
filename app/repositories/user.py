from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Handles database operations related to users."""

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(User.email == email)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        return db.execute(statement).scalar_one_or_none()

    @staticmethod
    def create(
        db: Session,
        *,
        full_name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user