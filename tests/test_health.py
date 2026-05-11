from fastapi.testclient import TestClient

from src.api.main import app


def test_liveness_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics_endpoint_exposes_prometheus_payload() -> None:
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "python_info" in response.text or "process_cpu_seconds_total" in response.text
