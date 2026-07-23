# Recruiter Demo Guide

## Five-minute walkthrough

1. Open the deployed root URL and show links to Swagger and the dashboard.
2. Open the dashboard and point out API status, product/order/inventory KPIs, low-stock data, shipments, and recent orders.
3. Open Swagger, authorize with JWT, and show the resource groups.
4. Explain that stock is not edited randomly: reservations, receipts, sales, transfers, returns, damage, and adjustments create auditable movement records.
5. Demonstrate one order reservation and explain row locking/transaction boundaries that protect stock from concurrent overselling.
6. Show idempotent payment/webhook behavior and cumulative return/refund safeguards.
7. Open health/readiness and Prometheus metrics.
8. Show the GitHub Actions workflow and Docker/Render configuration.

## Strong explanation

“This is a modular FastAPI platform built around transactional inventory accounting. Business rules live in services, persistence is isolated in repositories, and SQLAlchemy models are migrated with Alembic. Redis and Celery handle asynchronous maintenance work. The API includes JWT/RBAC security, idempotent financial operations, observability, containerized deployment, CI checks, and a lightweight operations dashboard.”

## Do not overclaim

Describe it as a production-oriented portfolio platform, not a system already proven at enterprise traffic. Mention the tests and safeguards that exist, then explain that load testing, external payment-provider integration, infrastructure monitoring, backups, and disaster recovery would be expanded for a commercial rollout.
