from fastapi.testclient import TestClient

from src.api.main import app


def test_liveness_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_alias_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready_alias_returns_dependency_status(monkeypatch) -> None:
    monkeypatch.setattr("src.api.routes.health.check_database_ready", lambda: True)
    monkeypatch.setattr("src.api.routes.health.check_redis_ready", lambda: True)
    monkeypatch.setattr("src.api.routes.health.check_database_schema_ready", lambda: True)
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["dependencies"] == {"database": True, "redis": True, "schema": True}


def test_ready_returns_not_ready_when_required_schema_is_missing(monkeypatch) -> None:
    monkeypatch.setattr("src.api.routes.health.check_database_ready", lambda: True)
    monkeypatch.setattr("src.api.routes.health.check_redis_ready", lambda: True)
    monkeypatch.setattr("src.api.routes.health.check_database_schema_ready", lambda: False, raising=False)
    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"]["dependencies"] == {"database": True, "redis": True, "schema": False}


def test_metrics_endpoint_exposes_prometheus_payload() -> None:
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "python_info" in response.text or "process_cpu_seconds_total" in response.text
