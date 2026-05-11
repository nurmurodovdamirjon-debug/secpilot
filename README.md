# SecPilot Defense

SecPilot Defense is a Telegram-first defensive cybersecurity monitoring, incident response, deception, and infrastructure protection platform.

The current repository is an MVP security foundation. It contains the service layout, safety policy foundation, health endpoints, metrics endpoint, bot entrypoint, DB-backed authorized target management, PolicyGate enforcement, audit persistence, database and worker scaffolding, Docker Compose deployment, and Codex workflow guardrails. Broader monitoring, enrichment, honeypot, reporting, and defense actions are roadmap capabilities unless explicitly implemented in `src/`.

## Current MVP

Implemented now:

- FastAPI app with `/health/live`, `/health/ready`, and `/metrics`
- API-key protected `/api/v1/assets` CRUD for authorized target management
- aiogram 3 Telegram bot with Uzbek admin UX, reply keyboard, asset list/add/check/delete flows, status, help, and safe placeholders
- Pydantic settings loaded from environment variables
- SQLAlchemy/Alembic skeleton for PostgreSQL
- DB-backed target whitelist persistence on `assets`
- DB-backed `AuditLog` persistence for asset and policy decisions
- Redis integration scaffold
- Celery worker scaffold
- Defensive-only `PolicyGate` service with real DB whitelist validation
- Structured logging and Prometheus metric helpers
- Docker Compose services for `api`, `bot`, `worker`, `postgres`, and `redis`
- Repository Codex guardrails under `AGENTS.md`, `.agents/`, and `.codex/`

Roadmap, not production behavior yet:

- Full server, Docker, Nginx, DB, Redis, SSL, DNS, and HTTP header monitoring
- Honeypot endpoints and canary tokens
- Threat intelligence enrichment
- Cloudflare WAF/rate-limit/Under Attack integrations
- UFW, iptables, or Fail2Ban reversible blocks
- Incident timelines and PDF/JSON reports
- Go scanner service for high-concurrency network checks
- Rust analyzer service for heavy static analysis

## Architecture

SecPilot starts as a Python 3.12 modular monolith:

- `src/api` for FastAPI routes and API startup
- `src/bot` for aiogram Telegram UX and admin checks
- `src/core` for configuration, logging, metrics, and shared security helpers
- `src/db` for SQLAlchemy models, sessions, and Alembic migrations
- `src/services` for business logic such as policy and audit decisions
- `src/workers` for Celery app and background task entrypoints
- `src/integrations` for external systems such as Redis
- `src/agents`, `src/skills`, and `src/reports` for future AI and reporting surfaces

Go and Rust extraction are future options only. Keep the modular monolith until queue depth, p95 latency, CPU, memory, or operational complexity justifies extraction.

## Security Guardrails

SecPilot is defensive-only and authorized-scope only.

Forbidden behavior:

- Malware, phishing, exploit delivery, credential theft, account takeover, persistence, evasion, hack-back, or unauthorized scanning

Mandatory controls:

- Target whitelist before audit, monitoring, or defense actions
- Manual approval for high-risk actions
- Reversible defense actions only
- Audit logging for risky attempts, denials, approvals, and results
- Least privilege for services, tokens, containers, and integrations
- Fail-closed defaults when actor, target, scope, risk, or approval is unclear

The DB whitelist is the source of truth for PolicyGate target checks. `ALLOWED_TARGETS` remains legacy environment context and does not bypass DB validation.

## Local Run

Create a local environment file, then start the stack:

```bash
cp .env.example .env
docker compose up --build
```

Smoke checks:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
```

Asset API smoke check:

```bash
curl -H "X-API-Key: $API_SECRET_KEY" http://localhost:8000/api/v1/assets
```

Telegram bot commands:

```text
/start
/status
/assets
/add_asset
/check_asset
/delete_asset
/help
```

Bot menu buttons:

```text
📊 Status
📁 Assetlar
➕ Asset qo‘shish
🔎 Asset tekshirish
🗑 Asset o‘chirish
📄 Hisobot
⚙️ Sozlamalar
ℹ️ Yordam
```

Manual Telegram smoke test:

1. Set `BOT_TOKEN`, `BOT_ADMIN_IDS`, `API_SECRET_KEY`, and `API_BASE_URL`.
2. Run migrations with `alembic upgrade head`.
3. Start the stack with `docker compose up --build`.
4. Send `/start` from an admin Telegram account and verify the Uzbek menu appears.
5. Use `➕ Asset qo‘shish` to add `domain -> example.com`.
6. Use `📁 Assetlar` to confirm the asset appears.
7. Use `🔎 Asset tekshirish` with `example.com` and verify it is allowed.
8. Use `🗑 Asset o‘chirish`, confirm deletion, then verify the asset list is empty.

Run migrations:

```bash
alembic upgrade head
docker compose exec api alembic upgrade head
```

## Tests And Validation

Run the local test suite:

```bash
python -m pytest tests -q
```

Compile Python sources:

```bash
python -m compileall -q src tests alembic
```

Validate Docker Compose:

```bash
docker compose config
```

Validate Codex workflow files:

```bash
python -m json.tool .codex/hooks.json
python -c "import ast,pathlib,tomllib; tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); [tomllib.loads(p.read_text()) for p in pathlib.Path('.codex/agents').glob('*.toml')]; [ast.parse(p.read_text()) for p in pathlib.Path('.codex/hooks').glob('*.py')]; ast.parse(pathlib.Path('.codex/rules/default.rules').read_text()); print('workflow-ok')"
```

## Dokploy Deploy

Use Docker Compose as the deployment source.

1. Connect the GitHub repository to a Dokploy Compose project.
2. Configure environment variables from `.env.example` in Dokploy secrets/env settings.
3. Keep `.env` out of Git.
4. Enable auto deploy when the deployment environment is ready.
5. Verify `/health/live`, `/health/ready`, `/metrics`, and Telegram `/status`.

Deployable services are `api`, `bot`, `worker`, `postgres`, and `redis`. PostgreSQL and Redis use named volumes for persistent data.

## Codex Workflow Layer

This repository includes local workflow guardrails for Codex sessions:

- `AGENTS.md` is the root project policy for Codex and subagents.
- `.agents/skills/*/SKILL.md` defines repo-specific skills for SecPilot architecture, FastAPI, aiogram, database, deployment, workers, testing, and security guardrails.
- `.codex/agents/*.toml` defines narrow custom subagents such as `security-guardian`, `testing-engineer`, and `docker-deploy-engineer`.
- `.codex/hooks.json` registers runtime hooks for session context, prompt checks, tool checks, permission requests, post-tool review, and stop-time quality gates.
- `.codex/hooks/*.py` contains hook implementations.
- `.codex/rules/default.rules` defines command policy rules for destructive commands, unsafe cybersecurity actions, secret handling, and repository safety.
- `.codex/config.toml` sets local Codex workflow limits.

After changing `AGENTS.md`, `.agents/`, or `.codex/`, restart Codex or start a new session if hooks, agents, or skills are not picked up immediately.

## Git Workflow

Branch policy:

- `main` is production
- `dev` is development
- `feature/*` is feature work

Before pushing:

```bash
git status --short
git diff --cached --name-only
```

Do not stage `.env`, logs, caches, `__pycache__`, `.pytest_cache`, local database files, or generated secrets.

## Documentation Map

- `docs/product/PRODUCT_REQUIREMENTS.md` for product requirements
- `docs/ARCHITECTURE.md` for architecture decisions
- `docs/API.md` for API design
- `docs/DB_SCHEMA.md` for database design
- `docs/security/SECURITY_POLICY.md` for safety policy
- `docs/agents/AI_AGENTS.md` for AI agent design
- `docs/skills/SKILLS.md` for skill design
- `docs/playbooks/INCIDENT_RESPONSE.md` for incident response
- `docs/HONEYPOT.md` for honeypot/canary design
- `docs/DEPLOYMENT.md` for deployment
- `docs/TEST_PLAN.md` for test strategy
- `docs/ROADMAP.md` for planned capabilities
