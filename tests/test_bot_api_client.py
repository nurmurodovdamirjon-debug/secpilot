import pytest
from httpx import AsyncClient, MockTransport, Request, Response

from src.bot.api_client import BotApiError, BotApiUnavailableError, SecPilotApiClient


@pytest.mark.asyncio
async def test_api_client_sends_api_key_and_lists_assets() -> None:
    seen_headers: dict[str, str] = {}

    async def handler(request: Request) -> Response:
        seen_headers["x-api-key"] = request.headers["x-api-key"]
        assert request.url.path == "/api/v1/assets"
        return Response(
            200,
            json=[
                {
                    "id": "asset-1",
                    "asset_type": "domain",
                    "value": "example.com",
                    "normalized_value": "example.com",
                    "label": None,
                    "status": "active",
                    "created_at": "2026-05-11T00:00:00Z",
                }
            ],
        )

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = SecPilotApiClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    assets = await client.list_assets()

    await http_client.aclose()
    assert seen_headers["x-api-key"] == "secret"
    assert assets[0].value == "example.com"


@pytest.mark.asyncio
async def test_api_client_fetches_defensive_intel_reports() -> None:
    async def handler(request: Request) -> Response:
        if request.url.path == "/api/v1/dns/audit":
            return Response(200, json={"domain": "example.com", "a_records": ["1.1.1.1"], "spf": True})
        if request.url.path == "/api/v1/ssl/audit":
            return Response(200, json={"domain": "example.com", "issuer": "Let's Encrypt"})
        if request.url.path == "/api/v1/subdomains/passive":
            return Response(200, json={"domain": "example.com", "subdomains": []})
        if request.url.path == "/api/v1/monitoring/status":
            return Response(200, json={"asset_id": "asset-1", "enabled": True})
        return Response(404)

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = SecPilotApiClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    assert (await client.dns_audit("asset-1"))["spf"] is True
    assert (await client.ssl_audit("asset-1"))["issuer"] == "Let's Encrypt"
    assert (await client.subdomains("asset-1"))["subdomains"] == []
    assert (await client.monitoring_status("asset-1"))["enabled"] is True

    await http_client.aclose()


@pytest.mark.asyncio
async def test_api_client_maps_structured_api_errors() -> None:
    async def handler(_: Request) -> Response:
        return Response(409, json={"error": {"code": "duplicate_asset", "message": "Asset already exists."}})

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = SecPilotApiClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    with pytest.raises(BotApiError) as exc_info:
        await client.create_asset(asset_type="domain", value="example.com")

    await http_client.aclose()
    assert exc_info.value.code == "duplicate_asset"


@pytest.mark.asyncio
async def test_api_client_maps_network_errors() -> None:
    async def handler(_: Request) -> Response:
        raise OSError("network down")

    http_client = AsyncClient(transport=MockTransport(handler), base_url="http://api:8000")
    client = SecPilotApiClient(base_url="http://api:8000", api_key="secret", http_client=http_client)

    with pytest.raises(BotApiUnavailableError):
        await client.list_assets()

    await http_client.aclose()
