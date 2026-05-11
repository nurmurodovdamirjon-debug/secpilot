# Test Plan

## 1. Unit tests

- PolicyGate
- scope validation
- risk scoring
- log parser
- DNS parser
- SSL checker
- report formatter
- AI output validator

## 2. Integration tests

- API + DB
- API + Redis queue
- Bot + API
- Worker + DB
- Cloudflare dry-run
- Threat intel cache

## 3. Security tests

- unauthorized Telegram ID
- whitelist bypass attempt
- SSRF private IP deny
- prompt injection
- malicious log content
- secret leak in logs
- action approval bypass

## 4. E2E tests

- `/check_ssl` -> job -> result
- honeypot hit -> incident -> alert
- brute-force sample log -> detection -> report
- block IP dry-run -> audit log

## 5. Load tests

- 100 fast audits
- 1000 honeypot events
- queue lag behavior
- report generation burst

## 6. Dry-run tests

Defense actionlar avval dry-run rejimda tekshiriladi.

```text
DRY RUN:
IP 185.xxx.xxx.xxx blocked bo‘lardi.
Command: ufw deny from 185.xxx.xxx.xxx
```
