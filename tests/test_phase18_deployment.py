from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_as_non_root_and_has_healthcheck() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "USER app" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "ENTRYPOINT" in dockerfile
    assert "FROM python:3.12-slim AS builder" in dockerfile


def test_compose_has_no_committed_default_password() -> None:
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "Inventory123" not in compose
    assert "POSTGRES_PASSWORD:?" in compose
    assert "celery-worker" in compose
    assert "celery-beat" in compose


def test_render_blueprint_has_api_worker_and_beat() -> None:
    data = yaml.safe_load((ROOT / "render.yaml").read_text())
    assert data["envVarGroups"][0]["name"] == "inventory-shared"
    services = data["services"]
    service_types = [service["type"] for service in services]
    assert service_types.count("web") == 1
    assert service_types.count("worker") == 2
    assert service_types.count("redis") == 1
    migration_values = {service["name"]: service.get("envVars", [])[-1].get("value") for service in services if service["type"] in {"web", "worker"}}
    assert migration_values["inventory-order-api"] is True
    assert migration_values["inventory-order-worker"] is False
    assert migration_values["inventory-order-beat"] is False


def test_ci_builds_container_after_tests() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    assert "mypy app" in workflow
    assert "docker/build-push-action@v6" in workflow
    assert "needs: test" in workflow


def test_entrypoint_applies_migrations_conditionally() -> None:
    entrypoint = (ROOT / "scripts/docker-entrypoint.sh").read_text()
    assert 'RUN_MIGRATIONS:-false' in entrypoint
    assert "alembic upgrade head" in entrypoint
    assert 'exec "$@"' in entrypoint
