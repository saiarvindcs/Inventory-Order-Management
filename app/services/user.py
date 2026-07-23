from sqlalchemy.orm import Session

from app.core.security.hashing import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    """Business logic for user management."""

    @staticmethod
    def register_user(
        db: Session,
        user_data: UserCreate,
    ) -> User:
        existing_user = UserRepository.get_by_email(
            db=db,
            email=str(user_data.email),
        )

        if existing_user:
            raise ValueError("A user with this email already exists.")

        return UserRepository.create(
            db=db,
            full_name=user_data.full_name,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
        )

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User:
        user = UserRepository.get_by_email(
            db=db,
            email=email,
        )

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(
            plain_password=password,
            hashed_password=user.hashed_password,
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        return user