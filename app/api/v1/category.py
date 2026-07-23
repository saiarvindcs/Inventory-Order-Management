from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security.oauth2 import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    try:
        category = CategoryService.create_category(
            db=db,
            category_data=category_data,
        )
        return CategoryResponse.model_validate(category)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def list_categories(
    search: str | None = Query(
        default=None,
        description="Search by category name",
    ),
    is_active: bool | None = Query(
        default=True,
    ),
    sort_by: str = Query(
        default="id",
        pattern="^(id|name)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CategoryResponse]:
    categories = CategoryService.list_categories(
        db=db,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

    return [
        CategoryResponse.model_validate(category)
        for category in categories
    ]


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    try:
        category = CategoryService.get_category(
            db=db,
            category_id=category_id,
        )
        return CategoryResponse.model_validate(category)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    try:
        category = CategoryService.update_category(
            db=db,
            category_id=category_id,
            category_data=category_data,
        )
        return CategoryResponse.model_validate(category)

    except ValueError as exc:
        message = str(exc)

        if message == "Category not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@router.delete(
    "/{category_id}",
    response_model=CategoryResponse,
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryResponse:
    try:
        category = CategoryService.soft_delete_category(
            db=db,
            category_id=category_id,
        )
        return CategoryResponse.model_validate(category)

    except ValueError as exc:
        message = str(exc)

        if message == "Category not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc