from fastapi import APIRouter

from app.api.v1 import customer, inventory, order, platform, purchase_order, stock_transfer, supplier, warehouse
from app.api.v1.auth import router as auth_router
from app.api.v1.category import router as category_router
from app.api.v1.health import router as health_router
from app.api.v1.product import router as product_router
from app.api.v1.product_variant import router as product_variant_router


api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(auth_router)
api_router.include_router(category_router)
api_router.include_router(product_router)
api_router.include_router(product_variant_router)
api_router.include_router(customer.router)
api_router.include_router(warehouse.router)
api_router.include_router(inventory.router)
api_router.include_router(supplier.router)
api_router.include_router(purchase_order.router)

api_router.include_router(stock_transfer.router)

api_router.include_router(order.router)

api_router.include_router(platform.router)
