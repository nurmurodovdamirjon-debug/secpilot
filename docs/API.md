# API Design

## 1. API prinsiplar

- REST + JSON
- `/api/v1` public/admin API
- `/internal` service-to-service API
- Har requestda `request_id`
- Risky actionlar uchun `Idempotency-Key`
- OpenAPI schema: `openapi/secpilot.openapi.yaml`

## 2. Endpointlar

| Method | Path | Vazifa |
|---|---|---|
| GET | `/health/live` | liveness |
| GET | `/health/ready` | readiness |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/v1/assets` | target qo‘shish |
| GET | `/api/v1/assets` | targetlar |
| POST | `/api/v1/audits/web` | web audit job |
| POST | `/api/v1/audits/dns` | DNS audit |
| POST | `/api/v1/audits/ssl` | SSL audit |
| POST | `/api/v1/audits/ports` | port audit |
| GET | `/api/v1/jobs/{job_id}` | job status |
| GET | `/api/v1/findings/{id}` | finding details |
| POST | `/api/v1/incidents/{id}/actions/block-ip` | IP block |
| POST | `/api/v1/incidents/{id}/actions/cloudflare-rate-limit` | Cloudflare rate-limit |
| POST | `/api/v1/honeypot/events` | honeypot event |
| POST | `/api/v1/agents/advice` | AI advice |
| GET | `/api/v1/reports/{id}` | report |

## 3. Error modeli

```json
{
  "error": {
    "code": "scope_denied",
    "message": "Target whitelist ichida emas",
    "request_id": "req_123"
  }
}
```

## 4. Job lifecycle

```text
queued -> running -> completed
queued -> running -> failed
queued -> cancelled
```

## 5. Auth

- Telegram owner ID whitelist
- Dashboard/API uchun JWT/session — keyingi bosqich
- Internal service token yoki mTLS — keyingi bosqich

## 6. Scope validation

Har bir audit yoki defense actiondan oldin:

1. target mavjudmi?
2. target ownerga tegishlimi?
3. whitelist ichidami?
4. action xavf darajasi qanday?
5. approval kerakmi?
