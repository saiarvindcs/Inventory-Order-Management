from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security.oauth2 import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    try:
        product = ProductService.create_product(
            db=db,
            product_data=product_data,
        )

        return ProductResponse.model_validate(product)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[ProductResponse],
)
def list_products(
    search: str | None = Query(
        default=None,
        description="Search by product name",
    ),
    category_id: int | None = Query(
        default=None,
        ge=1,
    ),
    is_active: bool | None = Query(
        default=None,
    ),
    min_price: float | None = Query(
        default=None,
        ge=0,
    ),
    max_price: float | None = Query(
        default=None,
        ge=0,
    ),
    sort_by: str = Query(
        default="id",
        pattern="^(id|name|price|sku)$",
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
) -> list[ProductResponse]:
    products = ProductService.list_products(
        db=db,
        search=search,
        category_id=category_id,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

    return [
        ProductResponse.model_validate(product)
        for product in products
    ]


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    try:
        product = ProductService.get_product(
            db=db,
            product_id=product_id,
        )

        return ProductResponse.model_validate(product)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    try:
        product = ProductService.update_product(
            db=db,
            product_id=product_id,
            product_data=product_data,
        )

        return ProductResponse.model_validate(product)

    except ValueError as exc:
        message = str(exc)

        if message == "Product not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    try:
        product = ProductService.soft_delete_product(
            db=db,
            product_id=product_id,
        )

        return ProductResponse.model_validate(product)

    except ValueError as exc:
        message = str(exc)

        if message == "Product not found":
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from exc