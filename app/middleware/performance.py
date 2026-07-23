from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.logging import logger


class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.headers["Server-Timing"] = f"app;dur={elapsed_ms:.2f}"

        event = "slow_request" if elapsed_ms >= settings.slow_request_threshold_ms else "request_completed"
        log = logger.warning if event == "slow_request" else logger.info
        log(
            event,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(elapsed_ms, 2),
            request_id=getattr(request.state, "request_id", None),
        )
        return response
