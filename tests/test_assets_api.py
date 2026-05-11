from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.main import app
from src.core.config import Settings, get_settings
from src.db.models import AuditLog
from src.db.session import get_db_session


def _override_settings() -> Settings:
    return Settings(API_SECRET_KEY="test-api-key")


def test_asset_endpoints_require_api_key(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _override_settings
    client = TestClient(app)

    response = client.get("/api/v1/assets")

    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_asset_crud_soft_delete_and_audit_persistence(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _override_settings
    client = TestClient(app)
    headers = {"X-API-Key": "test-api-key"}

    create_response = client.post(
        "/api/v1/assets",
        json={"asset_type": "domain", "value": "Example.COM", "label": "Main site"},
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["value"] == "Example.COM"
    assert created["normalized_value"] == "example.com"
    assert created["status"] == "active"

    asset_id = created["id"]
    duplicate_response = client.post(
        "/api/v1/assets",
        json={"asset_type": "domain", "value": "example.com"},
        headers=headers,
    )
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["error"]["code"] == "duplicate_asset"

    update_response = client.patch(
        f"/api/v1/assets/{asset_id}",
        json={"label": "Primary site"},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["label"] == "Primary site"

    delete_response = client.delete(f"/api/v1/assets/{asset_id}", headers=headers)
    assert delete_response.status_code == 204

    list_response = client.get("/api/v1/assets", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json() == []

    deleted_list_response = client.get("/api/v1/assets?include_deleted=true", headers=headers)
    assert deleted_list_response.status_code == 200
    assert deleted_list_response.json()[0]["status"] == "deleted"

    audit_actions = [row.action for row in db_session.query(AuditLog).order_by(AuditLog.created_at).all()]
    app.dependency_overrides.clear()
    assert audit_actions == ["asset.create", "asset.update", "asset.delete"]


def test_asset_create_rejects_invalid_target(db_session: Session) -> None:
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_settings] = _override_settings
    client = TestClient(app)

    response = client.post(
        "/api/v1/assets",
        json={"asset_type": "url", "value": "javascript:alert(1)"},
        headers={"X-API-Key": "test-api-key"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 422
