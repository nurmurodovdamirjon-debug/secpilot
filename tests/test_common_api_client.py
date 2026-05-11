import pytest
from httpx import AsyncClient, MockTransport, ReadTimeout, Request, Response

from src.common.api_client import (
    BackendClient,
    BackendCircuitOpenError,
    BackendTimeoutError,
    InvalidBackendResponseError,
)


@pytest.mark.asyncio
async def test_backend_client_uses_contract_paths_and_correlation_id() -> None:
    seen: list[tuple[str, str, dict[str, object], str]] = []

    async def handler(request: Request) -> Response:
        seen.append(
            (
                request.method,
                request.url.path,
                dict(request.headers),
                request.content.decode(),
            )
        )
        return Response(200, json={"domain": "example.com", "spf": True})

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = BackendClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    payload = await client.dns_audit("asset-1", correlation_id="cid-123")

    await http_client.aclose()
    assert payload["spf"] is True
    method, path, headers, body = seen[0]
    assert method == "POST"
    assert path == "/api/v1/dns/audit"
    assert headers["x-api-key"] == "secret"
    assert headers["x-correlation-id"] == "cid-123"
    assert body == '{"asset_id":"asset-1"}'


@pytest.mark.asyncio
async def test_backend_client_retries_transient_backend_errors() -> None:
    attempts = 0

    async def handler(_: Request) -> Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return Response(503, json={"error": {"code": "not_ready", "message": "Backend not ready."}})
        return Response(200, json={"enabled": True})

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = BackendClient(
        base_url="http://api:8000",
        api_key="secret",
        http_client=http_client,
        retry_backoff_seconds=0,
    )

    payload = await client.monitoring_status("asset-1")

    await http_client.aclose()
    assert attempts == 3
    assert payload["enabled"] is True


@pytest.mark.asyncio
async def test_backend_client_maps_timeout_and_opens_circuit() -> None:
    attempts = 0

    async def handler(_: Request) -> Response:
        nonlocal attempts
        attempts += 1
        raise ReadTimeout("slow backend")

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = BackendClient(
        base_url="http://api:8000",
        api_key="secret",
        http_client=http_client,
        retry_attempts=1,
        circuit_failure_threshold=1,
        circuit_reset_seconds=60,
    )

    with pytest.raises(BackendTimeoutError):
        await client.list_assets()
    with pytest.raises(BackendCircuitOpenError):
        await client.list_assets()

    await http_client.aclose()
    assert attempts == 1


@pytest.mark.asyncio
async def test_backend_client_rejects_invalid_json_response() -> None:
    async def handler(_: Request) -> Response:
        return Response(200, content=b"not-json")

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = BackendClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    with pytest.raises(InvalidBackendResponseError):
        await client.list_assets()

    await http_client.aclose()
