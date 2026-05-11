import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import Asset, AuditLog
from src.services.assets import create_asset
from src.services.audit_log import write_audit_event
from src.services.target_normalization import normalize_target


def test_sqlite_test_schema_supports_assets_and_audit_json(db_session: Session) -> None:
    asset = Asset(asset_type="domain", value="Example.COM", normalized_value="example.com")
    db_session.add(asset)
    db_session.commit()

    write_audit_event(
        db_session,
        actor_type="api_key",
        actor_id="default",
        action="asset.create",
        result="allowed",
        object_type="asset",
        object_id=str(asset.id),
        meta={"normalized_value": "example.com"},
    )

    audit_row = db_session.query(AuditLog).one()
    assert audit_row.meta_jsonb == {"normalized_value": "example.com"}


def test_normalized_asset_uniqueness_is_enforced(db_session: Session) -> None:
    create_asset(
        db_session,
        asset_type="domain",
        value="Example.COM",
        label=None,
        actor_type="api_key",
        actor_id="default",
    )

    with pytest.raises(IntegrityError):
        create_asset(
            db_session,
            asset_type="domain",
            value="example.com",
            label=None,
            actor_type="api_key",
            actor_id="default",
        )


def test_url_targets_normalize_to_origin_with_domain_or_ip_host() -> None:
    assert normalize_target("url", "https://Example.COM/path?x=1") == "https://example.com"
    assert normalize_target("url", "http://192.0.2.10:8080/admin") == "http://192.0.2.10:8080"
