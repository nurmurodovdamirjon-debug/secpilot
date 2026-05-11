"""SSL/TLS audit helpers for authorized domains."""

from datetime import UTC, datetime
import socket
import ssl

import httpx
import structlog

from src.schemas.ssl import SslAuditResult


logger = structlog.get_logger(__name__)


def collect_ssl_audit(domain: str, timeout: float) -> SslAuditResult:
    issuer: str | None = None
    expires_at: str | None = None
    days_remaining: int | None = None
    tls_version: str | None = None
    https_available = False

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=domain) as tls_socket:
                cert = tls_socket.getpeercert()
                tls_version = tls_socket.version()
                https_available = True
                issuer = _issuer_from_cert(cert)
                expires_at, days_remaining = _expiry_from_cert(cert)
    except Exception as exc:
        logger.info("ssl_audit_failed", domain=domain, error=str(exc))

    return SslAuditResult(
        domain=domain,
        issuer=issuer,
        expires_at=expires_at,
        days_remaining=days_remaining,
        tls_version=tls_version,
        https_available=https_available,
        hsts=_detect_hsts(domain, timeout),
    )


def _issuer_from_cert(cert: dict[str, object]) -> str | None:
    for item in cert.get("issuer", []):
        for key, value in item:
            if key == "organizationName":
                return str(value)
            if key == "commonName":
                return str(value)
    return None


def _expiry_from_cert(cert: dict[str, object]) -> tuple[str | None, int | None]:
    not_after = cert.get("notAfter")
    if not isinstance(not_after, str):
        return None, None
    expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
    delta = expires - datetime.now(UTC)
    return expires.isoformat(), delta.days


def _detect_hsts(domain: str, timeout: float) -> bool:
    try:
        response = httpx.get(f"https://{domain}", timeout=timeout, follow_redirects=False)
    except Exception:
        return False
    return "strict-transport-security" in response.headers
