# Deployment Guide

## Local production-style verification

1. Copy `.env.example` to `.env`.
2. Generate a strong `SECRET_KEY` and `POSTGRES_PASSWORD`.
3. Run `docker compose config` and confirm there are no unresolved variables.
4. Run `docker compose up --build`.
5. Confirm the API, worker, Beat, PostgreSQL, and Redis services remain healthy.
6. Open `/api/v1/health/live`, `/api/v1/health/ready`, `/docs`, `/dashboard`, and `/metrics`.
7. Run `docker compose exec api alembic current` and confirm the database is at the migration head.
8. Run `docker compose exec api pytest -q` when test files are mounted or execute tests before building in CI.

## Render Blueprint deployment

1. Push the repository to GitHub.
2. In Render, create a new Blueprint and select the repository.
3. Render reads `render.yaml` and proposes the web API, worker, Beat, PostgreSQL, and Redis resources.
4. Confirm the generated `SECRET_KEY` and database/Redis connections.
5. Replace the example `ALLOWED_HOSTS` value if Render assigns a different hostname.
6. Deploy the Blueprint.
7. The web service runs migrations. Workers explicitly use `RUN_MIGRATIONS=false` to avoid migration races.
8. Verify `/api/v1/health/ready` before testing business workflows.

## Required production variables

- `APP_ENV=production`
- `DEBUG=false`
- `DATABASE_URL`
- `SECRET_KEY` with at least 32 random characters
- `ALLOWED_HOSTS`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `REDIS_REQUIRED=true`

Optional: `INITIAL_ADMIN_EMAIL`, `CORS_ORIGINS`, pool settings, slow-request threshold, and Celery concurrency.

## Acceptance checklist

- Alembic reports one head and the production database is upgraded to it.
- Readiness confirms both database and Redis connectivity.
- Registration, login, refresh, and current-user endpoints work.
- An authorized user can create a product, warehouse, and inventory balance.
- Reservation prevents overselling and release restores availability.
- Duplicate payment webhook requests do not duplicate effects.
- Return quantities and aggregate refunds cannot exceed original quantities or paid amount.
- Celery worker receives a test task and Beat schedules reservation cleanup.
- Dashboard loads from the public domain and Swagger authorization works.
