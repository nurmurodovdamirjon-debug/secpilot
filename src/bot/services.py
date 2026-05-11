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


def format_dns_report(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            f"🌐 DNS Audit: {payload.get('domain')}",
            f"A: {_join_values(payload.get('a_records'))}",
            f"AAAA: {_join_values(payload.get('aaaa_records'))}",
            f"MX: {_join_values(payload.get('mx_records'))}",
            f"NS: {_join_values(payload.get('ns_records'))}",
            f"CNAME: {_join_values(payload.get('cname_records'))}",
            f"SPF: {_bool_label(payload.get('spf'))}",
            f"DMARC: {_bool_label(payload.get('dmarc'))}",
            f"ASN: {payload.get('asn') or 'noma’lum'}",
            f"Provider: {payload.get('provider') or 'noma’lum'}",
        ]
    )


def format_ssl_report(payload: dict[str, object]) -> str:
    days = payload.get("days_remaining")
    days_text = f"{days} kun" if days is not None else "noma’lum"
    return "\n".join(
        [
            f"🔐 SSL/TLS Audit: {payload.get('domain')}",
            f"Issuer: {payload.get('issuer') or 'noma’lum'}",
            f"Tugash sanasi: {payload.get('expires_at') or 'noma’lum'}",
            f"Qolgan muddat: {days_text}",
            f"TLS: {payload.get('tls_version') or 'noma’lum'}",
            f"HTTPS: {_bool_label(payload.get('https_available'))}",
            f"HSTS: {_bool_label(payload.get('hsts'))}",
        ]
    )


def format_subdomain_report(payload: dict[str, object]) -> str:
    subdomains = payload.get("subdomains")
    lines = [f"🔎 Subdomainlar: {payload.get('domain')}"]
    if not isinstance(subdomains, list) or not subdomains:
        lines.append("Passive manbalarda subdomain topilmadi.")
        return "\n".join(lines)
    for item in subdomains[:30]:
        if isinstance(item, dict):
            first_seen = item.get("first_seen") or "noma’lum"
            lines.append(f"- {item.get('name')} (first seen: {first_seen})")
    return "\n".join(lines)


def format_monitoring_report(payload: dict[str, object]) -> str:
    enabled = "yoqilgan" if payload.get("enabled") is True else "o‘chirilgan"
    return "\n".join(
        [
            f"📡 Monitoring: {enabled}",
            f"So‘nggi tekshiruv: {payload.get('last_check_at') or 'hali yo‘q'}",
            f"So‘nggi status: {payload.get('last_status') or 'noma’lum'}",
        ]
    )


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


def _join_values(value: object) -> str:
    if isinstance(value, list) and value:
        return ", ".join(str(item) for item in value)
    return "yo‘q"


def _bool_label(value: object) -> str:
    return "bor" if value is True else "yo‘q"
