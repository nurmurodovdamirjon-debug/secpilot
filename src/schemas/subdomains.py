"""Passive subdomain discovery response schemas."""

from pydantic import BaseModel, Field


class SubdomainDiscoveryResult(BaseModel):
    domain: str
    subdomains: list[dict[str, str | None]] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
