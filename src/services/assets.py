"""Asset whitelist management services."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import Asset
from src.services.audit_log import write_audit_event
from src.services.target_normalization import normalize_target


class AssetNotFoundError(LookupError):
    """Raised when an asset does not exist."""


def create_asset(
    db: Session,
    *,
    asset_type: str,
    value: str,
    label: str | None,
    actor_type: str,
    actor_id: str,
) -> Asset:
    normalized_value = normalize_target(asset_type, value)
    asset = Asset(
        asset_type=asset_type.lower(),
        value=value,
        normalized_value=normalized_value,
        label=label,
        status="active",
    )
    db.add(asset)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(asset)
    write_audit_event(
        db,
        actor_type=actor_type,
        actor_id=actor_id,
        action="asset.create",
        result="allowed",
        object_type="asset",
        object_id=str(asset.id),
        meta={"asset_type": asset.asset_type, "normalized_value": asset.normalized_value},
    )
    return asset


def list_assets(db: Session, *, include_deleted: bool = False) -> list[Asset]:
    statement = select(Asset).order_by(Asset.created_at)
    if not include_deleted:
        statement = statement.where(Asset.status != "deleted")
    return list(db.scalars(statement).all())


def get_asset(db: Session, asset_id: UUID, *, include_deleted: bool = True) -> Asset:
    statement = select(Asset).where(Asset.id == asset_id)
    if not include_deleted:
        statement = statement.where(Asset.status != "deleted")
    asset = db.scalar(statement)
    if asset is None:
        raise AssetNotFoundError(str(asset_id))
    return asset


def update_asset(
    db: Session,
    asset_id: UUID,
    *,
    label: str | None = None,
    status: str | None = None,
    actor_type: str,
    actor_id: str,
) -> Asset:
    asset = get_asset(db, asset_id)
    if label is not None:
        asset.label = label
    if status is not None:
        asset.status = status
    db.commit()
    db.refresh(asset)
    write_audit_event(
        db,
        actor_type=actor_type,
        actor_id=actor_id,
        action="asset.update",
        result="allowed",
        object_type="asset",
        object_id=str(asset.id),
        meta={"status": asset.status},
    )
    return asset


def delete_asset(db: Session, asset_id: UUID, *, actor_type: str, actor_id: str) -> None:
    asset = get_asset(db, asset_id)
    asset.status = "deleted"
    db.commit()
    write_audit_event(
        db,
        actor_type=actor_type,
        actor_id=actor_id,
        action="asset.delete",
        result="allowed",
        object_type="asset",
        object_id=str(asset.id),
        meta={"status": "deleted"},
    )
