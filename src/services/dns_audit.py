"""Passive DNS audit helpers for authorized domains."""

import dns.resolver
import structlog

from src.schemas.dns import DnsAuditResult


logger = structlog.get_logger(__name__)


def collect_dns_audit(domain: str, timeout: float) -> DnsAuditResult:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    resolver.timeout = min(timeout, 2.0)

    a_records = _query_records(resolver, domain, "A")
    aaaa_records = _query_records(resolver, domain, "AAAA")
    mx_records = _query_records(resolver, domain, "MX")
    ns_records = _query_records(resolver, domain, "NS")
    txt_records = _query_records(resolver, domain, "TXT")
    cname_records = _query_records(resolver, domain, "CNAME")
    dmarc_records = _query_records(resolver, f"_dmarc.{domain}", "TXT")
    asn, country, provider = _lookup_asn(resolver, a_records[0] if a_records else None)

    return DnsAuditResult(
        domain=domain,
        a_records=a_records,
        aaaa_records=aaaa_records,
        mx_records=mx_records,
        ns_records=ns_records,
        txt_records=txt_records,
        cname_records=cname_records,
        spf=_detect_spf(txt_records),
        dmarc=_detect_dmarc(dmarc_records),
        asn=asn,
        country=country,
        provider=provider,
    )


def _query_records(resolver: dns.resolver.Resolver, domain: str, record_type: str) -> list[str]:
    try:
        answers = resolver.resolve(domain, record_type)
    except Exception as exc:
        logger.info("dns_record_lookup_failed", domain=domain, record_type=record_type, error=str(exc))
        return []
    return sorted({_clean_dns_value(answer.to_text()) for answer in answers})


def _clean_dns_value(value: str) -> str:
    return " ".join(value.strip().strip(".").replace('" "', "").replace('"', "").split())


def _detect_spf(txt_records: list[str]) -> bool:
    return any(record.strip().strip('"').lower().startswith("v=spf1") for record in txt_records)


def _detect_dmarc(txt_records: list[str]) -> bool:
    return any(record.strip().strip('"').lower().startswith("v=dmarc1") for record in txt_records)


def _lookup_asn(resolver: dns.resolver.Resolver, ip_address: str | None) -> tuple[str | None, str | None, str | None]:
    if not ip_address:
        return None, None, None
    reversed_ip = ".".join(reversed(ip_address.split(".")))
    try:
        answers = resolver.resolve(f"{reversed_ip}.origin.asn.cymru.com", "TXT")
    except Exception:
        return None, None, None
    if not answers:
        return None, None, None
    parts = _clean_dns_value(answers[0].to_text()).split("|")
    if len(parts) < 5:
        return None, None, None
    asn = f"AS{parts[0].strip()}"
    country = parts[2].strip() or None
    provider = parts[4].strip() or None
    return asn, country, provider
