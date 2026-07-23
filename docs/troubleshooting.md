# Troubleshooting

## `SECRET_KEY must be changed in production`
Set a random value longer than 32 characters and do not use the development default.

## API waits or fails during startup
Check PostgreSQL and Redis health. In production `REDIS_REQUIRED=true` intentionally blocks startup when Redis is unavailable.

## Alembic connection error
Verify `DATABASE_URL`. For local Docker Compose, the application uses host `db`, not `localhost`.

## `pytest` cannot import `app`
Run tests from the repository root after `pip install -e ".[dev]"`. The Pytest configuration also adds the root directory to the import path.

## Celery commands fail on Windows
Activate the virtual environment and use `--pool=solo` for the local worker.

## Dashboard shows unauthorized
Log in again. Tokens are stored in session storage, so closing the tab/session removes them. Confirm the user is active and has required permissions.

## Readiness fails but liveness passes
The process is running, but PostgreSQL or Redis is unavailable. Check service logs and connection variables.

## Render deployment is healthy but host is rejected
Set `ALLOWED_HOSTS` to the exact Render hostname. Add custom domains when configured.
