import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production", secret_key="development-only-change-me", _env_file=None)


def test_short_secret_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(secret_key="too-short", _env_file=None)


def test_host_and_cors_lists_are_normalized() -> None:
    settings = Settings(
        secret_key="a-secure-development-secret-key",
        allowed_hosts="localhost, 127.0.0.1 ,,testserver",
        cors_origins="http://localhost:3000, http://localhost:5173",
        _env_file=None,
    )
    assert settings.allowed_hosts_list == ["localhost", "127.0.0.1", "testserver"]
    assert settings.cors_origins_list == [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
