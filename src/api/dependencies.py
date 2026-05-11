"""FastAPI dependencies shared across route modules."""

import secrets

from fastapi import Depends, Header

from src.api.errors import ApiError
from src.core.config import Settings, get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> tuple[str, str]:
    expected_key = settings.API_SECRET_KEY
    if not x_api_key or not expected_key or not secrets.compare_digest(x_api_key, expected_key):
        raise ApiError(status_code=401, code="unauthorized", message="Valid X-API-Key header is required.")
    return ("api_key", "default")
