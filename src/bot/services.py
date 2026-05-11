"""Telegram bot presentation and whitelist helper services."""

from ipaddress import ip_address, ip_network

from src.bot.api_client import BotApiError, BotApiUnavailableError, BotAsset, HealthResult
from src.services.target_normalization import normalize_target_candidates


def format_asset_list(assets: list[BotAsset]) -> str:
    active_assets = [asset for asset in assets if asset.status != "deleted"]
    if not active_assets:
        return "Hozircha asset qo‘shilmagan."

    lines = ["📁 Whitelistdagi assetlar:"]
    for index, asset in enumerate(active_assets, start=1):
        lines.append(
            f"{index}. ID: {asset.id[:8]}\n"
            f"   Turi: {asset.asset_type}\n"
            f"   Qiymat: {asset.value}\n"
            f"   Status: {asset.status}"
        )
    return "\n".join(lines)


def is_asset_whitelisted(assets: list[BotAsset], value: str) -> bool:
    candidates = normalize_target_candidates(value)
    if not candidates:
        return False

    active_assets = [asset for asset in assets if asset.status == "active"]
    for asset_type, normalized_value in candidates:
        if any(asset.asset_type == asset_type and asset.normalized_value == normalized_value for asset in active_assets):
            return True

    ip_candidate = next((normalized for asset_type, normalized in candidates if asset_type == "ip"), None)
    if ip_candidate is None:
        return False
    target_ip = ip_address(ip_candidate)
    return any(
        asset.asset_type == "cidr" and target_ip in ip_network(asset.normalized_value, strict=True)
        for asset in active_assets
    )


def format_status_message(
    *,
    bot_online: bool,
    environment: str,
    live: HealthResult,
    ready: HealthResult,
) -> str:
    dependencies = _extract_dependencies(ready.payload)
    database_ready = dependencies.get("database")
    redis_ready = dependencies.get("redis")
    return "\n".join(
        [
            "📊 SecPilot holati:",
            f"Bot: {'online' if bot_online else 'offline'}",
            f"API: {'ishlayapti' if live.ok else 'ulanishda xatolik'}",
            f"DB: {_dependency_label(database_ready)}",
            f"Redis: {_dependency_label(redis_ready)}",
            f"Muhit: {environment}",
        ]
    )


def format_api_error(error: BotApiError) -> str:
    if isinstance(error, BotApiUnavailableError):
        return "Backend API bilan bog‘lanib bo‘lmadi. Keyinroq qayta urinib ko‘ring."
    if error.code == "duplicate_asset":
        return "Bu asset allaqachon whitelistda bor."
    if error.code == "invalid_target":
        return "Asset qiymati noto‘g‘ri. Domain, IP, CIDR yoki URL formatini tekshiring."
    if error.code == "unauthorized":
        return "Bot backend API bilan avtorizatsiyadan o‘ta olmadi. API kalit sozlamasini tekshiring."
    return "Backend API xatolik qaytardi. Keyinroq qayta urinib ko‘ring."


def _dependency_label(value: object) -> str:
    if value is True:
        return "ishlayapti"
    if value is False:
        return "xatolik"
    return "noma’lum"


def _extract_dependencies(payload: dict[str, object]) -> dict[str, object]:
    dependencies = payload.get("dependencies")
    if isinstance(dependencies, dict):
        return dependencies
    detail = payload.get("detail")
    if isinstance(detail, dict):
        detail_dependencies = detail.get("dependencies")
        if isinstance(detail_dependencies, dict):
            return detail_dependencies
    return {}
