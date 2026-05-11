"""Telegram bot API client compatibility layer."""

from dataclasses import dataclass
from typing import Any

import httpx

from src.common.api_client import (
    BackendCircuitOpenError as BotApiCircuitOpenError,
    BackendClientError as BotApiError,
    BackendClient,
    BackendTimeoutError as BotApiTimeoutError,
    BackendUnavailableError as BotApiUnavailableError,
    HealthResult,
    InvalidBackendResponseError as BotApiInvalidResponseError,
)


@dataclass(frozen=True)
class BotAsset:
    id: str
    asset_type: str
    value: str
    normalized_value: str
    label: str | None
    status: str

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "BotAsset":
        return cls(
            id=str(payload["id"]),
            asset_type=str(payload["asset_type"]),
            value=str(payload["value"]),
            normalized_value=str(payload["normalized_value"]),
            label=payload.get("label"),
            status=str(payload["status"]),
        )


class SecPilotApiClient(BackendClient):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        connect_timeout: float = 5.0,
        read_timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_backoff_seconds: float = 0.25,
        circuit_failure_threshold: int = 5,
        circuit_reset_seconds: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff_seconds,
            circuit_failure_threshold=circuit_failure_threshold,
            circuit_reset_seconds=circuit_reset_seconds,
            http_client=http_client,
        )

    async def list_assets(self) -> list[BotAsset]:
        payload = await super().list_assets()
        if not isinstance(payload, list):
            raise BotApiInvalidResponseError()
        return [BotAsset.from_api(item) for item in payload]

    async def create_asset(self, *, asset_type: str, value: str) -> BotAsset:
        payload = await super().create_asset(asset_type=asset_type, value=value)
        if not isinstance(payload, dict):
            raise BotApiInvalidResponseError()
        return BotAsset.from_api(payload)
