from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import TimestampMixin

class UserRole(TimestampMixin, BaseModel):
    """
    Association table between users and roles.
    """

    __tablename__ = "user_roles"

    __table_args__ = (
       # UniqueConstraint(
        #    "user_id",
         #   "role_id",
          #  name="uq_user_role",
        #),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )