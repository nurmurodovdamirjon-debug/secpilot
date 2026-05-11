"""Target normalization for authorized asset whitelist entries."""

from ipaddress import ip_address, ip_network
from urllib.parse import urlsplit


class InvalidTargetError(ValueError):
    """Raised when a target cannot be safely normalized."""


def normalize_target(asset_type: str, value: str) -> str:
    asset_type = asset_type.strip().lower()
    raw_value = value.strip()
    if not raw_value:
        raise InvalidTargetError("target_empty")

    if asset_type == "domain":
        return _normalize_domain(raw_value)
    if asset_type == "ip":
        return str(ip_address(raw_value))
    if asset_type == "cidr":
        return str(ip_network(raw_value, strict=True))
    if asset_type == "url":
        return _normalize_url(raw_value)
    raise InvalidTargetError("unsupported_asset_type")


def normalize_target_candidates(value: str) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for asset_type in ("domain", "ip", "cidr", "url"):
        try:
            candidates.append((asset_type, normalize_target(asset_type, value)))
        except ValueError:
            continue
    return candidates


def _normalize_domain(value: str) -> str:
    if "://" in value or "/" in value or ":" in value:
        raise InvalidTargetError("invalid_domain")
    hostname = value.rstrip(".").lower()
    try:
        ip_address(hostname)
    except ValueError:
        pass
    else:
        raise InvalidTargetError("invalid_domain")
    try:
        ascii_hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise InvalidTargetError("invalid_domain") from exc
    labels = ascii_hostname.split(".")
    if len(labels) < 2:
        raise InvalidTargetError("invalid_domain")
    for label in labels:
        if not label or len(label) > 63 or label.startswith("-") or label.endswith("-"):
            raise InvalidTargetError("invalid_domain")
        if not all(char.isalnum() or char == "-" for char in label):
            raise InvalidTargetError("invalid_domain")
    return ascii_hostname


def _normalize_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise InvalidTargetError("invalid_url")
    try:
        hostname = str(ip_address(parsed.hostname))
    except ValueError:
        hostname = _normalize_domain(parsed.hostname)
    try:
        port = parsed.port
    except ValueError as exc:
        raise InvalidTargetError("invalid_url") from exc
    if port is None:
        return f"{parsed.scheme}://{hostname}"
    return f"{parsed.scheme}://{hostname}:{port}"
