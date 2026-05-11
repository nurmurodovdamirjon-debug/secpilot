"""SSL/TLS audit response schemas."""

from pydantic import BaseModel


class SslAuditResult(BaseModel):
    domain: str
    issuer: str | None = None
    expires_at: str | None = None
    days_remaining: int | None = None
    tls_version: str | None = None
    https_available: bool = False
    hsts: bool = False
