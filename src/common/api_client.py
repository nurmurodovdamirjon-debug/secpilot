"""Async backend API client with retries, timeouts, and circuit breaking."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from time import monotonic
from typing import Any
from uuid import uuid4

import httpx
import structlog


logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class HealthResult:
    ok: bool
    payload: dict[str, Any]


class BackendClientError(Exception):
    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class BackendApiError(BackendClientError):
    """Raised when the backend returns a structured non-2xx API error."""


class BackendUnavailableError(BackendClientError):
    def __init__(self) -> None:
        super().__init__("backend_offline", "Backend API is offline or unreachable.")


class BackendTimeoutError(BackendClientError):
    def __init__(self) -> None:
        super().__init__("backend_timeout", "Backend API request timed out.")


class InvalidBackendResponseError(BackendClientError):
    def __init__(self) -> None:
        super().__init__("invalid_response", "Backend API returned an invalid response.")


class BackendCircuitOpenError(BackendClientError):
    def __init__(self) -> None:
        super().__init__("circuit_open", "Backend API circuit breaker is open.")


class CircuitBreaker:
    """Small per-client circuit breaker for repeated backend transport failures."""

    def __init__(self, *, failure_threshold: int, reset_seconds: float) -> None:
        self.failure_threshold = max(1, failure_threshold)
        self.reset_seconds = max(0.1, reset_seconds)
        self._failures = 0
        self._opened_at: float | None = None

    def ensure_request_allowed(self) -> None:
        if self._opened_at is None:
            return
        if monotonic() - self._opened_at >= self.reset_seconds:
            self._opened_at = None
            self._failures = 0
            return
        raise BackendCircuitOpenError()

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._opened_at = monotonic()


class BackendClient:
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
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self._circuit = CircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            reset_seconds=circuit_reset_seconds,
        )
        self._owns_client = http_client is None
        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=read_timeout,
            pool=connect_timeout,
        )
        self._client = http_client or httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def list_assets(self, *, correlation_id: str | None = None) -> Any:
        return await self._request("GET", "/api/v1/assets", correlation_id=correlation_id)

    async def create_asset(
        self,
        *,
        asset_type: str,
        value: str,
        correlation_id: str | None = None,
    ) -> Any:
        return await self._request(
            "POST",
            "/api/v1/assets",
            json={"asset_type": asset_type, "value": value},
            correlation_id=correlation_id,
        )

    async def delete_asset(self, asset_id: str, *, correlation_id: str | None = None) -> None:
        await self._request(
            "DELETE",
            f"/api/v1/assets/{asset_id}",
            expect_json=False,
            correlation_id=correlation_id,
        )

    async def dns_audit(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._asset_action("/api/v1/dns/audit", asset_id, correlation_id=correlation_id)

    async def ssl_audit(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._asset_action("/api/v1/ssl/audit", asset_id, correlation_id=correlation_id)

    async def subdomains(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._asset_action("/api/v1/subdomains/passive", asset_id, correlation_id=correlation_id)

    async def monitoring_status(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._asset_action("/api/v1/monitoring/status", asset_id, correlation_id=correlation_id)

    async def enable_monitoring(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/v1/monitoring/{asset_id}/enable",
            correlation_id=correlation_id,
        )

    async def disable_monitoring(self, asset_id: str, *, correlation_id: str | None = None) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/v1/monitoring/{asset_id}/disable",
            correlation_id=correlation_id,
        )

    async def live(self) -> HealthResult:
        return await self._health_request("/health")

    async def ready(self) -> HealthResult:
        return await self._health_request("/ready")

    async def _asset_action(
        self,
        path: str,
        asset_id: str,
        *,
        correlation_id: str | None,
    ) -> dict[str, Any]:
        payload = await self._request(
            "POST",
            path,
            json={"asset_id": asset_id},
            correlation_id=correlation_id,
        )
        if not isinstance(payload, dict):
            raise InvalidBackendResponseError()
        return payload

    async def _health_request(self, path: str) -> HealthResult:
        try:
            response = await self._client.get(path)
            payload = response.json() if response.content else {}
            if not isinstance(payload, dict):
                payload = {}
            return HealthResult(ok=response.status_code < 400, payload=payload)
        except Exception:
            logger.warning("backend_health_unavailable", path=path, exc_info=True)
            return HealthResult(ok=False, payload={})

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expect_json: bool = True,
        correlation_id: str | None = None,
    ) -> Any:
        self._circuit.ensure_request_allowed()
        request_id = correlation_id or str(uuid4())
        headers = {"X-API-Key": self.api_key, "X-Correlation-ID": request_id}
        last_error: BackendClientError | None = None

        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.info(
                    "backend_request_started",
                    method=method,
                    url=f"{self.base_url}{path}",
                    correlation_id=request_id,
                    attempt=attempt,
                    timeout_attempts=self.retry_attempts,
                )
                response = await self._client.request(method, path, headers=headers, json=json)
                logger.info(
                    "backend_request_finished",
                    method=method,
                    url=f"{self.base_url}{path}",
                    status_code=response.status_code,
                    correlation_id=request_id,
                    attempt=attempt,
                )
                if response.status_code >= 500 and attempt < self.retry_attempts:
                    await self._sleep_before_retry(attempt)
                    continue
                if response.status_code >= 500:
                    last_error = _api_error_from_response(response)
                    break
                if response.status_code >= 400:
                    raise _api_error_from_response(response)
                self._circuit.record_success()
                if not expect_json:
                    return None
                return _json_payload(response)
            except httpx.TimeoutException as exc:
                last_error = BackendTimeoutError()
                logger.warning(
                    "backend_request_timeout",
                    method=method,
                    url=f"{self.base_url}{path}",
                    correlation_id=request_id,
                    attempt=attempt,
                    error=str(exc),
                    exc_info=True,
                )
            except httpx.RequestError as exc:
                last_error = BackendUnavailableError()
                logger.warning(
                    "backend_request_transport_failed",
                    method=method,
                    url=f"{self.base_url}{path}",
                    correlation_id=request_id,
                    attempt=attempt,
                    error=str(exc),
                    exc_info=True,
                )
            except OSError as exc:
                last_error = BackendUnavailableError()
                logger.warning(
                    "backend_request_transport_failed",
                    method=method,
                    url=f"{self.base_url}{path}",
                    correlation_id=request_id,
                    attempt=attempt,
                    error=str(exc),
                    exc_info=True,
                )
            except InvalidBackendResponseError as exc:
                last_error = exc
                logger.warning(
                    "backend_response_invalid",
                    method=method,
                    url=f"{self.base_url}{path}",
                    correlation_id=request_id,
                    attempt=attempt,
                    exc_info=True,
                )
                break
            except BackendApiError:
                self._circuit.record_success()
                raise

            if attempt < self.retry_attempts:
                await self._sleep_before_retry(attempt)

        self._circuit.record_failure()
        raise last_error or BackendUnavailableError()

    async def _sleep_before_retry(self, attempt: int) -> None:
        if self.retry_backoff_seconds == 0:
            return
        await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))


def _json_payload(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise InvalidBackendResponseError() from exc


def _api_error_from_response(response: httpx.Response) -> BackendApiError:
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    error = payload.get("error") if isinstance(payload, dict) else None
    if isinstance(error, dict):
        return BackendApiError(
            code=str(error.get("code") or "api_error"),
            message=str(error.get("message") or "Backend API returned an error."),
            status_code=response.status_code,
        )
    return BackendApiError("api_error", "Backend API returned an error.", response.status_code)
