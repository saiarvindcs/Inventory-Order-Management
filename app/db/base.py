# from sqlalchemy.orm import DeclarativeBase


# class Base(DeclarativeBase):
# """Base class for all SQLAlchemy models."""

# pass
from app.models.base import BaseModel
from app.models.category import Category
from app.models.product import Product
from app.models.role import Role
from app.models.user import User
from app.models.warehouse import Warehouse

__all__ = [
    "BaseModel",
    "Role",
    "User",
    "Category",
    "Product",
    "Warehouse",
]
