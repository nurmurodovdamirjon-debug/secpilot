# API Design

## 1. API Principles

- REST + JSON.
- `/api/v1` is the public/admin API.
- `/internal` is reserved for service-to-service APIs.
- Public contracts should stay documented in `openapi/secpilot.openapi.yaml`.
- Risky future actions require explicit authorization, PolicyGate validation, audit logging, and manual approval where required.

## 2. Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health/live` | Liveness |
| GET | `/health/ready` | Readiness |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/v1/assets` | Create authorized target |
| GET | `/api/v1/assets` | List authorized targets |
| GET | `/api/v1/assets/{asset_id}` | Get one authorized target |
| PATCH | `/api/v1/assets/{asset_id}` | Update label or status |
| DELETE | `/api/v1/assets/{asset_id}` | Soft delete authorized target |
| GET | `/api/v1/dns/{asset_id}` | Defensive DNS audit for active domain/url asset |
| GET | `/api/v1/ssl/{asset_id}` | Defensive SSL/TLS audit for active domain/url asset |
| GET | `/api/v1/subdomains/{asset_id}` | Passive subdomain discovery for active domain/url asset |
| GET | `/api/v1/monitoring/{asset_id}` | Monitoring status for active domain/url asset |
| POST | `/api/v1/monitoring/{asset_id}/enable` | Enable monitoring |
| POST | `/api/v1/monitoring/{asset_id}/disable` | Disable monitoring |
| POST | `/api/v1/audits/web` | Roadmap web audit job |
| POST | `/api/v1/audits/dns` | Roadmap DNS audit |
| POST | `/api/v1/audits/ssl` | Roadmap SSL audit |
| GET | `/api/v1/jobs/{job_id}` | Roadmap job status |
| GET | `/api/v1/findings/{id}` | Roadmap finding details |
| POST | `/api/v1/incidents/{id}/actions/block-ip` | Roadmap approval-gated IP block |
| POST | `/api/v1/incidents/{id}/actions/cloudflare-rate-limit` | Roadmap approval-gated Cloudflare rate-limit |
| POST | `/api/v1/honeypot/events` | Roadmap honeypot event |
| POST | `/api/v1/agents/advice` | Roadmap AI advice |
| GET | `/api/v1/reports/{id}` | Roadmap report |

## 3. Error Model

```json
{
  "error": {
    "code": "scope_denied",
    "message": "Target is not whitelisted"
  }
}
```

## 4. Auth

- `/api/v1/assets` requires `X-API-Key` matching `API_SECRET_KEY`.
- Defensive intelligence endpoints require `X-API-Key` and only allow active `domain` or `url` assets.
- Telegram owner ID whitelist protects bot commands.
- Dashboard/API JWT or session auth is roadmap.
- Internal service token or mTLS is roadmap.

## 5. Asset Whitelist Contract

`POST /api/v1/assets` accepts:

```json
{
  "asset_type": "domain",
  "value": "example.com",
  "label": "Main site"
}
```

Allowed `asset_type` values:

- `domain`
- `ip`
- `cidr`
- `url`

Targets are normalized before persistence. Duplicates by `(asset_type, normalized_value)` return `409 duplicate_asset`. Deletes are soft deletes with `status="deleted"`.

## 6. Scope Validation

Every future audit or defense action must check:

1. target exists
2. target is active in the DB whitelist
3. actor is authorized
4. action risk level
5. manual approval requirement
6. audit log persistence

## 7. Defensive Intelligence

Implemented endpoints are passive and authorized-scope only:

- DNS audit collects DNS records, SPF/DMARC presence, CNAME, and best-effort ASN/provider metadata.
- SSL/TLS audit checks HTTPS certificate summary, expiry, TLS version, and HSTS.
- Subdomain discovery uses passive certificate transparency data only.
- Monitoring stores enable/disable state and last check metadata; background checks log alerts to `audit_log` and can notify Telegram admins.

These modules do not brute force, exploit, scan ports, attempt login, collect credentials, or mutate remote infrastructure.
