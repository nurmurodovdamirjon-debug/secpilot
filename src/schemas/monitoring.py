"""Monitoring response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MonitoringStatus(BaseModel):
    asset_id: UUID
    enabled: bool
    last_check_at: datetime | None = None
    last_status: str | None = None
    last_detail: dict[str, object] | None = None
    scheduler: dict[str, object] | None = None
