from pathlib import Path


def test_api_runs_migrations_before_startup() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")

    assert "alembic upgrade head" in compose
    assert "uvicorn src.api.main:app" in compose


def test_worker_waits_for_api_health() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    worker_section = compose.split("  worker:", 1)[1]

    assert "api:" in worker_section
    assert "condition: service_healthy" in worker_section
