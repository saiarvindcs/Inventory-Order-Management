# Phase 17 — Performance and Observability

## Completed

- Prometheus request counters and latency histograms use route templates rather than raw URLs, preventing high-cardinality metrics.
- Added structured request-completion and slow-request logging with request IDs and durations.
- Added `Server-Timing` response headers.
- Readiness now performs a real database `SELECT 1` and Redis check.
- Redis can be optional in development and mandatory in production via `REDIS_REQUIRED`.
- Application startup no longer crashes on an optional Redis outage.
- SQLAlchemy connections use `pool_pre_ping`; PostgreSQL deployments receive configurable pool sizing, overflow, and timeout settings.
- Sessions use `expire_on_commit=False` to avoid unnecessary reload queries after writes.
- Added focused Phase 17 observability tests.

## New environment settings

- `SLOW_REQUEST_THRESHOLD_MS=500`
- `REDIS_REQUIRED=false`
- `DATABASE_POOL_SIZE=5`
- `DATABASE_MAX_OVERFLOW=10`
- `DATABASE_POOL_TIMEOUT_SECONDS=30`
