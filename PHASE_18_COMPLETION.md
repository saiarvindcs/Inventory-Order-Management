# Phase 18 — Docker, CI/CD and Cloud Deployment

## Completed

- Multi-stage Python 3.12 container image.
- Non-root runtime user and container health check.
- Conditional Alembic migration entrypoint.
- Production Compose stack for API, PostgreSQL, Redis, Celery worker and Celery beat.
- Separate development Compose override with hot reload.
- Removed committed/default database passwords.
- Persistent PostgreSQL and Redis volumes.
- Celery beat schedule for expiring stock reservations.
- Render Blueprint for web API, worker, beat, Redis and PostgreSQL.
- CI quality gate for migrations, Ruff, mypy, dependency audit and pytest.
- CI container build with BuildKit cache.
- Deployment configuration tests.

## Local Docker startup

1. Copy `.env.example` to `.env`.
2. Set a strong `SECRET_KEY` and `POSTGRES_PASSWORD`.
3. Run `docker compose up --build`.
4. Open `http://localhost:8000/docs`.

For hot reload, run:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Render deployment

Create a new Render Blueprint from the repository. Review `ALLOWED_HOSTS` after Render assigns the final hostname. The API service runs migrations; worker and beat do not.
