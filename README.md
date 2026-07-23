# Inventory & Order Management Platform

A production-oriented backend platform for catalogue management, multi-warehouse inventory accounting, purchasing, stock transfers, customer orders, reservations, payments, fulfilment, returns, reporting, background processing, observability, and deployment.

## Live surfaces

After startup:

- API documentation: `http://localhost:8000/docs`
- Operations dashboard: `http://localhost:8000/dashboard`
- Liveness: `http://localhost:8000/api/v1/health/live`
- Readiness: `http://localhost:8000/api/v1/health/ready`
- Prometheus metrics: `http://localhost:8000/metrics`

## Technology stack

Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Redis, Celery, JWT/OAuth2, Pytest, Prometheus, Docker, Docker Compose, GitHub Actions, and Render.

## Main capabilities

- JWT authentication, role-based access control, and permission checks
- Categories, products, variants, pricing history, warehouses, and suppliers
- Multi-warehouse balances with reserved, available, damaged, and total quantities
- Immutable stock-movement ledger and negative-stock protection
- Purchase orders, goods receipt, and supplier workflows
- Stock-transfer lifecycle with transfer-in and transfer-out movements
- Customer-order state machine and status history
- Transactional stock reservations with expiry and consumption
- Idempotent payments and duplicate-safe webhook processing
- Shipments, returns, return items, and cumulative refund protection
- Redis-backed processing and Celery maintenance tasks
- Reports, audit logs, notifications, structured logs, health checks, and metrics
- Browser dashboard served by FastAPI without a separate Node deployment

## Fastest setup: Docker Compose

Requirements: Docker Desktop and Docker Compose.

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set at minimum:

```env
APP_ENV=production
DEBUG=false
POSTGRES_PASSWORD=choose-a-strong-password
SECRET_KEY=replace-with-a-random-secret-at-least-32-characters
ALLOWED_HOSTS=localhost,127.0.0.1
```

Start the complete stack:

```powershell
docker compose up --build
```

The API container waits for PostgreSQL and Redis, runs Alembic migrations, and then starts Uvicorn. Celery worker and Celery Beat start only after the API is healthy.

Stop services:

```powershell
docker compose down
```

Remove local database and Redis volumes only when a full reset is intended:

```powershell
docker compose down -v
```

## Local development without Docker

Start PostgreSQL and Redis first, then:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Run Celery in separate terminals:

```powershell
celery -A app.core.celery.celery_app worker --loglevel=info --pool=solo
celery -A app.core.celery.celery_app beat --loglevel=info
```

`--pool=solo` is recommended for local Celery workers on Windows.

## Tests and quality checks

```powershell
pytest -q
ruff check app tests
mypy app
alembic heads
```

The GitHub Actions workflow additionally starts PostgreSQL and Redis, applies migrations, runs dependency auditing, executes tests, and builds the Docker image.

## Initial administrator

Registration does not silently grant administrative access. To assign the seeded admin role during startup, register a user first and set:

```env
INITIAL_ADMIN_EMAIL=your-email@example.com
```

Restart the API once. Leave this variable blank when automatic assignment is not needed.

## Project structure

```text
app/
  api/v1/          HTTP endpoints
  core/            configuration, JWT, Redis, Celery, logging, metrics
  db/              engine and session management
  middleware/      request context and performance instrumentation
  models/          SQLAlchemy entities
  repositories/    persistence operations
  schemas/         Pydantic request/response contracts
  services/        business rules and transactions
  static/dashboard browser operations dashboard
  tasks/            Celery jobs
alembic/            database migrations
docs/               architecture, deployment, workflows, interview material
tests/              workflow, security, observability, and deployment tests
```

## Deployment

The repository includes `render.yaml` for a Render Blueprint containing the web API, Celery worker, Celery Beat, PostgreSQL, and Redis. See [`docs/deployment.md`](docs/deployment.md) for the exact deployment and verification sequence.

## Documentation

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/database-design.md`](docs/database-design.md)
- [`docs/workflows.md`](docs/workflows.md)
- [`docs/deployment.md`](docs/deployment.md)
- [`docs/api-guide.md`](docs/api-guide.md)
- [`docs/demo-guide.md`](docs/demo-guide.md)
- [`docs/interview-guide.md`](docs/interview-guide.md)
- [`docs/troubleshooting.md`](docs/troubleshooting.md)

## Roadmap status

All 20 planned phases are implemented in this source package. Runtime acceptance on a target machine still requires a clean dependency installation, PostgreSQL/Redis startup, migrations, complete tests, Docker startup, Swagger workflow checks, and public deployment verification.

## License

This project is intended for portfolio, learning, and interview demonstration use.
