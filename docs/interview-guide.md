# Interview Guide

## Resume description

Built a production-oriented Inventory and Order Management Platform using FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis, and Celery. Implemented multi-warehouse inventory accounting, stock reservations, purchase orders, transfers, order workflows, idempotent payments/webhooks, shipments, returns/refunds, RBAC security, audit logs, Prometheus metrics, Docker, CI/CD, and a recruiter-viewable operations dashboard.

## Resume bullets

- Designed transactional multi-warehouse inventory workflows with immutable movement history, reservations, transfers, negative-stock prevention, and concurrency-aware service operations.
- Implemented JWT authentication, RBAC, idempotent payment/webhook handling, shipment/return/refund safeguards, Redis/Celery processing, audit reporting, and structured observability.
- Containerized API, PostgreSQL, Redis, Celery worker, and scheduler; added Alembic migrations, GitHub Actions quality gates, Render deployment configuration, and an integrated dashboard.

## Likely questions

### Why FastAPI?
It provides typed request validation, dependency injection, async support, and automatic OpenAPI documentation, which suits a service-oriented backend and makes the portfolio API easy to inspect.

### How do you prevent overselling?
Reservations run inside database transactions, verify available inventory, and lock or consistently update the relevant balance before committing. Available quantity is derived from total and reserved quantities rather than independently edited.

### Why keep a stock-movement ledger?
A balance shows the current state; the ledger explains how that state was reached. It supports audits, debugging, reconciliation, and safer corrections.

### How is payment duplication prevented?
The API records idempotency keys and provider event identifiers. Retries resolve to the existing operation, while webhook processing avoids applying the same event twice.

### Why Redis and Celery?
Redis is used as broker/backend infrastructure, while Celery moves maintenance work such as expired-reservation cleanup outside request latency and supports scheduled execution through Beat.

### What would you improve next?
Provider-specific payment integrations, stronger permission administration, load tests, distributed tracing, managed secrets, database backup/restore drills, autoscaling, and a richer frontend.
