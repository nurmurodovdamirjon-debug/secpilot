"""Async API client used by the Telegram bot."""

from dataclasses import dataclass
from typing import Any

import httpx
import structlog


logger = structlog.get_logger(__name__)
DEFAULT_TIMEOUT_SECONDS = 5.0


class BotApiError(Exception):
    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class BotApiUnavailableError(BotApiError):
    def __init__(self) -> None:
        super().__init__("api_unavailable", "Backend API bilan bog‘lanib bo‘lmadi.")


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


@dataclass(frozen=True)
class HealthResult:
    ok: bool
    payload: dict[str, Any]


class SecPilotApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def list_assets(self) -> list[BotAsset]:
        payload = await self._request("GET", "/api/v1/assets")
        return [BotAsset.from_api(item) for item in payload]

    async def create_asset(self, *, asset_type: str, value: str) -> BotAsset:
        payload = await self._request(
            "POST",
            "/api/v1/assets",
            json={"asset_type": asset_type, "value": value},
        )
        return BotAsset.from_api(payload)

    async def delete_asset(self, asset_id: str) -> None:
        await self._request("DELETE", f"/api/v1/assets/{asset_id}", expect_json=False)

    async def dns_audit(self, asset_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/dns/{asset_id}")

    async def ssl_audit(self, asset_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/ssl/{asset_id}")

    async def subdomains(self, asset_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/subdomains/{asset_id}")

    async def monitoring_status(self, asset_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/monitoring/{asset_id}")

    async def enable_monitoring(self, asset_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/monitoring/{asset_id}/enable")

    async def disable_monitoring(self, asset_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/monitoring/{asset_id}/disable")

    async def live(self) -> HealthResult:
        return await self._health_request("/health/live")

    async def ready(self) -> HealthResult:
        return await self._health_request("/health/ready")

    async def _health_request(self, path: str) -> HealthResult:
        try:
            response = await self._client.get(path)
            payload = response.json() if response.content else {}
            return HealthResult(ok=response.status_code < 400, payload=payload)
        except Exception:
            logger.warning("bot_api_health_unavailable", path=path)
            return HealthResult(ok=False, payload={})

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> Any:
        try:
            response = await self._client.request(
                method,
                path,
                headers={"X-API-Key": self.api_key},
                json=json,
            )
        except Exception as exc:
            logger.warning("bot_api_request_failed", method=method, path=path, error=str(exc))
            raise BotApiUnavailableError() from exc

        if response.status_code >= 400:
            raise _api_error_from_response(response)
        if not expect_json:
            return None
        return response.json()


def _api_error_from_response(response: httpx.Response) -> BotApiError:
    try:
        payload = response.json()
        error = payload.get("error", {})
        return BotApiError(
            code=str(error.get("code") or "api_error"),
            message=str(error.get("message") or "Backend API xatolik qaytardi."),
            status_code=response.status_code,
        )
    except Exception:
        return BotApiError("api_error", "Backend API xatolik qaytardi.", response.status_code)
