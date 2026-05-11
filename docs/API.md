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
| POST | `/api/v1/audits/web` | Roadmap web audit job |
| POST | `/api/v1/audits/dns` | Roadmap DNS audit |
| POST | `/api/v1/audits/ssl` | Roadmap SSL audit |
| POST | `/api/v1/audits/ports` | Roadmap port audit |
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
