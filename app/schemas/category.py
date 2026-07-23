from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Base schema for category."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Electronics"],
    )

    description: str | None = Field(
        default=None,
        max_length=255,
        examples=["Electronic products"],
    )

    parent_id: int | None = Field(
        default=None,
        examples=[1],
    )


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    parent_id: int | None = None

    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    """Schema returned to clients."""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    is_active: bool