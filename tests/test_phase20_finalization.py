from pathlib import Path

from app.core.config import Settings


ROOT = Path(__file__).resolve().parents[1]


def test_final_documentation_exists() -> None:
    required = [
        "README.md",
        "PHASE_20_COMPLETION.md",
        "docs/deployment.md",
        "docs/api-guide.md",
        "docs/demo-guide.md",
        "docs/interview-guide.md",
        "docs/troubleshooting.md",
    ]
    assert all((ROOT / path).is_file() for path in required)


def test_initial_admin_is_optional_and_not_hard_coded() -> None:
    settings = Settings(_env_file=None)
    assert settings.initial_admin_email is None
    assert "sai@example.com" not in (ROOT / "app/main.py").read_text(encoding="utf-8")


def test_release_version_is_consistent() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert 'version = "1.0.0"' in pyproject
    assert "APP_VERSION=1.0.0" in env_example
