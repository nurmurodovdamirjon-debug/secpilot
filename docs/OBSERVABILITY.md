# Observability

## 1. Logging

Format: structured JSON

Majburiy fieldlar:

```text
timestamp
level
service
request_id
correlation_id
job_id
actor_id
action
result
```

## 2. Metrics

Prometheus metrics:

- api_requests_total
- api_request_duration_seconds
- jobs_total
- job_duration_seconds
- worker_queue_depth
- alerts_total
- incidents_total
- defense_actions_total
- ai_agent_requests_total
- ai_agent_confidence

## 3. Alerts

| Alert | Trigger |
|---|---|
| API down | readiness fail |
| Worker lag | queue depth > 500 |
| Critical incident | severity critical |
| DB unavailable | connection fail |
| Redis unavailable | ping fail |
| SSL expiry | < 14 kun |
| High CPU | > 85% 10 min |
| Honeypot burst | > 20 hits / 10 min |

## 4. Tracing

Keyingi bosqich:
- OpenTelemetry
- request trace
- job trace
- AI tool call trace
