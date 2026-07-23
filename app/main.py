from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.logging import configure_logging, logger
from app.core.metrics import MetricsMiddleware, metrics_response
from app.middleware.performance import PerformanceMiddleware
from app.middleware.request_context import RequestContextMiddleware
from app.core.redis import redis_client
from app.db.session import SessionLocal
from app.repositories.user import UserRepository
from app.services.role import RoleService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()

    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )

    with SessionLocal() as db:
        RoleService.seed_roles(db)

        if settings.initial_admin_email:
            admin_user = UserRepository.get_by_email(
                db=db,
                email=settings.initial_admin_email,
            )

            if admin_user is not None:
                RoleService.assign_admin_role(
                    db=db,
                    user=admin_user,
                )
            else:
                logger.warning(
                    "initial_admin_user_not_found",
                    email=settings.initial_admin_email,
                )

    try:
        await redis_client.ping()
    except Exception:
        logger.warning("redis_unavailable_at_startup", required=settings.redis_required)
        if settings.redis_required:
            raise

    yield

    logger.info("application_stopping")
    await redis_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    description="Advanced Inventory and Order Management Platform API",
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def handle_app_exception(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    return await app_exception_handler(request, exc)


app.add_exception_handler(
    Exception,
    generic_exception_handler,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts_list,
)
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Idempotency-Key"],
    )
app.add_middleware(RequestContextMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(MetricsMiddleware)


@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_response()


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/dashboard", include_in_schema=False)
async def dashboard_ui() -> FileResponse:
    return FileResponse("app/static/dashboard/index.html")


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.app_env,
        "dashboard": "/dashboard",
        "docs": "/docs",
    }
