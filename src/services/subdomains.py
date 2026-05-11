"""Passive subdomain discovery from certificate transparency sources."""

import httpx
import structlog

from src.schemas.subdomains import SubdomainDiscoveryResult
from src.services.target_normalization import normalize_target


logger = structlog.get_logger(__name__)


def collect_passive_subdomains(domain: str, timeout: float) -> SubdomainDiscoveryResult:
    try:
        response = httpx.get("https://crt.sh/", params={"q": f"%.{domain}", "output": "json"}, timeout=timeout)
        response.raise_for_status()
        rows = response.json()
    except Exception as exc:
        logger.info("passive_subdomain_lookup_failed", domain=domain, error=str(exc))
        rows = []
    return _parse_crtsh_rows(domain, rows if isinstance(rows, list) else [])


def _parse_crtsh_rows(domain: str, rows: list[dict[str, object]]) -> SubdomainDiscoveryResult:
    discovered: dict[str, str | None] = {}
    for row in rows:
        first_seen = row.get("entry_timestamp")
        for raw_name in str(row.get("name_value", "")).splitlines():
            name = raw_name.strip().lower().lstrip("*.").rstrip(".")
            if not name.endswith(f".{domain}") and name != domain:
                continue
            try:
                normalized = normalize_target("domain", name)
            except ValueError:
                continue
            discovered.setdefault(normalized, str(first_seen) if first_seen else None)
    subdomains = [{"name": name, "first_seen": first_seen} for name, first_seen in sorted(discovered.items())]
    return SubdomainDiscoveryResult(domain=domain, subdomains=subdomains, sources=["crt.sh"])
