"""DNS audit response schemas."""

from pydantic import BaseModel, Field


class DnsAuditResult(BaseModel):
    domain: str
    a_records: list[str] = Field(default_factory=list)
    aaaa_records: list[str] = Field(default_factory=list)
    mx_records: list[str] = Field(default_factory=list)
    ns_records: list[str] = Field(default_factory=list)
    txt_records: list[str] = Field(default_factory=list)
    cname_records: list[str] = Field(default_factory=list)
    spf: bool = False
    dmarc: bool = False
    asn: str | None = None
    country: str | None = None
    provider: str | None = None
