"""Authorized asset whitelist API routes."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.dependencies import require_api_key
from src.api.errors import ApiError
from src.db.session import get_db_session
from src.services.assets import (
    AssetNotFoundError,
    create_asset,
    delete_asset,
    get_asset,
    list_assets,
    update_asset,
)
from src.services.target_normalization import InvalidTargetError


router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


class AssetCreateRequest(BaseModel):
    asset_type: Literal["domain", "ip", "cidr", "url"]
    value: str = Field(min_length=1, max_length=512)
    label: str | None = Field(default=None, max_length=255)


class AssetUpdateRequest(BaseModel):
    label: str | None = Field(default=None, max_length=255)
    status: Literal["active", "deleted"] | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_type: str
    value: str
    normalized_value: str
    label: str | None
    status: str
    created_at: datetime


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset_endpoint(
    payload: AssetCreateRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
) -> AssetResponse:
    try:
        return create_asset(
            db,
            asset_type=payload.asset_type,
            value=payload.value,
            label=payload.label,
            actor_type=actor[0],
            actor_id=actor[1],
        )
    except InvalidTargetError as exc:
        raise ApiError(status_code=422, code="invalid_target", message=str(exc)) from exc
    except IntegrityError as exc:
        raise ApiError(status_code=409, code="duplicate_asset", message="Asset already exists.") from exc


@router.get("", response_model=list[AssetResponse])
def list_assets_endpoint(
    include_deleted: bool = False,
    db: Session = Depends(get_db_session),
    _: tuple[str, str] = Depends(require_api_key),
) -> list[AssetResponse]:
    return list_assets(db, include_deleted=include_deleted)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    _: tuple[str, str] = Depends(require_api_key),
) -> AssetResponse:
    try:
        return get_asset(db, asset_id)
    except AssetNotFoundError as exc:
        raise ApiError(status_code=404, code="asset_not_found", message="Asset not found.") from exc


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset_endpoint(
    asset_id: UUID,
    payload: AssetUpdateRequest,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
) -> AssetResponse:
    try:
        return update_asset(
            db,
            asset_id,
            label=payload.label,
            status=payload.status,
            actor_type=actor[0],
            actor_id=actor[1],
        )
    except AssetNotFoundError as exc:
        raise ApiError(status_code=404, code="asset_not_found", message="Asset not found.") from exc


@router.delete("/{asset_id}", status_code=204)
def delete_asset_endpoint(
    asset_id: UUID,
    db: Session = Depends(get_db_session),
    actor: tuple[str, str] = Depends(require_api_key),
) -> Response:
    try:
        delete_asset(db, asset_id, actor_type=actor[0], actor_id=actor[1])
    except AssetNotFoundError as exc:
        raise ApiError(status_code=404, code="asset_not_found", message="Asset not found.") from exc
    return Response(status_code=204)
