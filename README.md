# SecPilot Defense

## MVP status

Current MVP skeleton includes FastAPI health and metrics endpoints, aiogram bot entrypoint, Telegram admin whitelist, PostgreSQL/Redis config, SQLAlchemy/Alembic skeleton, Celery worker skeleton, defensive-only PolicyGate and Docker Compose services for `api`, `bot`, `worker`, `postgres`, and `redis`.

## Local run

```bash
cp .env.example .env
docker compose up --build
```

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
```

## Migration

```bash
alembic upgrade head
docker compose exec api alembic upgrade head
```

## Tests

```bash
pytest
```

## GitHub push

```bash
git init
git add .
git commit -m "initial secpilot mvp"
git branch -M main
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```

## Dokploy deploy

Create a Docker Compose project, connect the GitHub repo, add env variables from `.env.example`, enable Auto Deploy, then verify `/health/live`, `/health/ready`, `/metrics`, and Telegram `/status`.

## Security guardrails

Only defensive and authorized cybersecurity workflows are allowed. Target whitelist is mandatory, high-risk actions require manual approval, auto-defense must be reversible, risky actions must be audit logged, and secrets must stay in `.env` or deployment secret storage.

**SecPilot Defense** — Telegram orqali boshqariladigan shaxsiy cybersecurity, server monitoring, active defense, honeypot/canary va AI-assisted incident response platformasi.

## Asosiy maqsad

Loyiha foydalanuvchining o‘ziga tegishli yoki ruxsat berilgan server, sayt, API, Telegram bot va infratuzilmalarni kuzatadi, hujum belgilarini aniqlaydi, dalil yig‘adi va xavfsiz himoya choralarini taklif qiladi yoki tasdiq bilan bajaradi.

## Dastur nima qiladi?

- Server CPU/RAM/Disk/temperature monitoring
- Docker, Nginx, DB, Redis service health check
- SSL/TLS, DNS, HTTP security headers audit
- Brute-force, flood, suspicious endpoint, port scan belgilarini aniqlash
- Honeypot endpoint va canary token orqali attacker izlarini yig‘ish
- IP reputation, ASN, provider, geo va threat-intel enrichment
- Cloudflare WAF/rate-limit/Under Attack mode integratsiyasi
- UFW/iptables/Fail2Ban orqali reversible IP block
- Telegram alert, incident timeline va PDF/JSON report
- AI agentlar orqali triage, tavsiya, report va architecture advice
- Ish hajmiga qarab Python/Go/Rust bo‘yicha tavsiya

## Dastur nima qilmaydi?

- Malware yaratmaydi
- Account buzmaydi
- Phishing qilmaydi
- Hack-back qilmaydi
- Exploit tarqatmaydi
- Ruxsatsiz scanning qilmaydi

## Tavsiya etilgan stack

- Python 3.12
- aiogram 3
- FastAPI
- PostgreSQL
- Redis
- Celery yoki RQ
- Docker Compose
- Cloudflare API
- Go scanner service — keyingi bosqich
- Rust analyzer service — keyingi bosqich

## Hujjatlar xaritasi

- `docs/product/PRODUCT_REQUIREMENTS.md` — mahsulot talablari
- `docs/ARCHITECTURE.md` — arxitektura
- `docs/API.md` — API dizayn
- `docs/DB_SCHEMA.md` — ma’lumotlar bazasi
- `docs/security/SECURITY_POLICY.md` — xavfsizlik siyosati
- `docs/agents/AI_AGENTS.md` — AI agentlar
- `docs/skills/SKILLS.md` — skilllar
- `docs/playbooks/INCIDENT_RESPONSE.md` — incident response
- `docs/HONEYPOT.md` — honeypot/canary
- `docs/DEPLOYMENT.md` — deployment
- `docs/TEST_PLAN.md` — test rejasi
- `docs/ROADMAP.md` — roadmap
