# Incident Response Playbooks

## 1. Lifecycle

1. Detect
2. Analyze
3. Contain
4. Recover
5. Postmortem

## 2. Brute-force playbook

Trigger:
- login fail threshold oshdi
- bitta IPdan ko‘p POST
- 401/403 spike

Auto:
- evidence save
- Telegram alert
- temporary rate limit

Manual:
- IP block approve
- account security review
- threshold tuning

## 3. L7 flood playbook

Trigger:
- req/min baseline x5
- 5xx oshishi
- CPU/RAM spike

Auto:
- Telegram urgent alert
- Cloudflare rate-limit draft
- heavy jobs pause

Manual:
- Under Attack mode approve
- WAF rule review
- origin health check

## 4. Honeypot trigger playbook

Trigger:
- decoy endpointga request
- canary token touched

Auto:
- event log
- threat intel enrichment
- incident timeline update

Manual:
- block approve
- related logs review
- provider abuse report tayyorlash

## 5. Secret exposure playbook

Trigger:
- canary secret ishlatilgan
- token leak signali

Auto:
- incident critical
- related integration freeze recommendation

Manual:
- token rotate
- blast radius analysis
- postmortem

## 6. Server overload playbook

Trigger:
- CPU > 85%
- RAM > 90%
- Disk > 90%
- temperature high

Auto:
- alert
- heavy scans pause
- metrics snapshot

Manual:
- process review
- service restart
- scale decision
