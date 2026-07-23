from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security.oauth2 import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services.product_variant import ProductVariantService

router = APIRouter(prefix="/product-variants", tags=["Product Variants"])


def _http_error(exc: ValueError) -> HTTPException:
    message = str(exc)
    code = status.HTTP_404_NOT_FOUND if message in {
        "Product not found",
        "Product variant not found",
    } else status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=message)


@router.post("", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
def create_product_variant(
    data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductVariantResponse:
    try:
        return ProductVariantResponse.model_validate(ProductVariantService.create(db, data))
    except ValueError as exc:
        raise _http_error(exc) from exc


@router.get("", response_model=list[ProductVariantResponse])
def list_product_variants(
    product_id: int | None = Query(default=None, ge=1),
    is_active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
    sort_by: str = Query(default="id", pattern="^(id|name|sku|price|product_id)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProductVariantResponse]:
    rows = ProductVariantService.list(
        db,
        product_id=product_id,
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )
    return [ProductVariantResponse.model_validate(row) for row in rows]


@router.get("/{variant_id}", response_model=ProductVariantResponse)
def get_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductVariantResponse:
    try:
        return ProductVariantResponse.model_validate(ProductVariantService.get(db, variant_id))
    except ValueError as exc:
        raise _http_error(exc) from exc


@router.patch("/{variant_id}", response_model=ProductVariantResponse)
def update_product_variant(
    variant_id: int,
    data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductVariantResponse:
    try:
        return ProductVariantResponse.model_validate(
            ProductVariantService.update(db, variant_id, data)
        )
    except ValueError as exc:
        raise _http_error(exc) from exc


@router.delete("/{variant_id}", response_model=ProductVariantResponse)
def deactivate_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductVariantResponse:
    try:
        return ProductVariantResponse.model_validate(
            ProductVariantService.deactivate(db, variant_id)
        )
    except ValueError as exc:
        raise _http_error(exc) from exc
