# Inventory & Order Management Platform — Completion Handoff

This package extends the supplied Phase 10 project through the remaining backend roadmap.

## Implemented API surface

- Authentication and RBAC
- Product catalogue and variants
- Warehouses and inventory ledger
- Suppliers and purchase orders
- Stock transfers
- Customer order state machine
- Stock reservations with release/consume operations
- Idempotent payments and duplicate-safe webhook events
- Shipments, returns, and refunds
- Redis/Celery maintenance task for expired reservations
- Dashboard and low-stock reports
- Audit-log and notification endpoints
- Prometheus metrics and request/security headers
- Docker Compose, GitHub Actions CI, and Render blueprint

## Verification performed

- Python syntax compilation: passed
- Phase 16 clean-checkout pytest discovery: fixed
- Trusted-host, CORS, secret validation, and response-header hardening: added
- SQLAlchemy mapper configuration: passed
- Existing Phase 8–10 functional tests: 6 passed
- Added Phase 11–15 workflow test: 1 passed
- Total locally executed business workflow tests: 7 passed
- Added Phase 16 API security tests (require installed `python-jose` to execute)

The sandbox package mirror could not provide build dependencies, so a fresh full dependency installation, Ruff run, PostgreSQL migration run, Docker build, and live cloud deployment must be executed on a normal internet-enabled machine or CI runner.

## Local run

```powershell
Copy-Item .env.example .env
# Update secrets and connection values in .env
docker compose up --build -d
docker compose exec api alembic upgrade head
```

Open Swagger at `http://localhost:8000/docs` and metrics at `http://localhost:8000/metrics`.
