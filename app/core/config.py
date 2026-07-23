from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Inventory Order Management API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    cors_origins: str = ""

    # Database
    database_url: str = "sqlite+pysqlite:///./inventory_order_management.db"

    # Authentication
    secret_key: str = "development-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    initial_admin_email: str | None = None

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Logging / performance
    log_level: str = "INFO"
    slow_request_threshold_ms: float = 500.0
    redis_required: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout_seconds: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("secret_key")
    @classmethod
    def reject_insecure_production_secret(cls, value: str, info):
        app_env = str(info.data.get("app_env", "development")).lower()
        if app_env in {"production", "prod"} and value == "development-only-change-me":
            raise ValueError("SECRET_KEY must be changed in production")
        if len(value) < 16:
            raise ValueError("SECRET_KEY must contain at least 16 characters")
        return value

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
