from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.redis import get_redis
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/live", status_code=status.HTTP_200_OK, summary="Liveness check")
async def liveness_check() -> dict[str, str]:
    return {
        "status": "alive",
        "application": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready", status_code=status.HTTP_200_OK, summary="Readiness check")
async def readiness_check(redis: Redis = Depends(get_redis)) -> dict[str, str]:
    checks = {"database": "available", "redis": "available"}

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        checks["database"] = "unavailable"
        raise HTTPException(status_code=503, detail={"status": "not_ready", **checks}) from exc

    try:
        await redis.ping()
    except Exception as exc:
        checks["redis"] = "unavailable"
        if settings.redis_required:
            raise HTTPException(status_code=503, detail={"status": "not_ready", **checks}) from exc

    return {
        "status": "ready",
        "environment": settings.app_env,
        **checks,
    }
