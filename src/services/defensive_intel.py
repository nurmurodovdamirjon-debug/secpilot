"""Shared authorization and target helpers for passive intelligence modules."""

from uuid import UUID

from sqlalchemy.orm import Session

from src.api.errors import ApiError
from src.db.models import Asset
from src.services.assets import AssetNotFoundError, get_asset
from src.services.audit_log import write_audit_event
from src.services.target_normalization import InvalidTargetError, normalize_target


ALLOWED_DOMAIN_ASSET_TYPES = {"domain", "url"}


def extract_domain_from_asset(asset_type: str, value: str) -> str:
    if asset_type == "domain":
        return normalize_target("domain", value)
    if asset_type == "url":
        normalized_url = normalize_target("url", value)
        return normalized_url.split("://", 1)[1].split(":", 1)[0]
    raise InvalidTargetError("asset_type_not_allowed")


def get_authorized_domain_asset(db: Session, asset_id: UUID) -> tuple[Asset, str]:
    try:
        asset = get_asset(db, asset_id, include_deleted=False)
    except AssetNotFoundError as exc:
        raise ApiError(status_code=404, code="asset_not_found", message="Asset not found.") from exc

    if asset.status != "active":
        raise ApiError(status_code=403, code="asset_not_active", message="Asset is not active.")
    if asset.asset_type not in ALLOWED_DOMAIN_ASSET_TYPES:
        raise ApiError(
            status_code=403,
            code="asset_type_not_allowed",
            message="Only active domain or url assets are allowed for this lookup.",
        )
    try:
        return asset, extract_domain_from_asset(asset.asset_type, asset.normalized_value)
    except InvalidTargetError as exc:
        raise ApiError(status_code=422, code="invalid_asset_target", message="Asset target is invalid.") from exc


def audit_intel_action(
    db: Session,
    *,
    actor_type: str,
    actor_id: str,
    action: str,
    asset: Asset,
    result: str,
    meta: dict[str, object] | None = None,
) -> None:
    write_audit_event(
        db,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        result=result,
        object_type="asset",
        object_id=str(asset.id),
        meta=meta or {"asset_type": asset.asset_type, "normalized_value": asset.normalized_value},
    )
