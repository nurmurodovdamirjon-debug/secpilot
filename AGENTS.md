# SecPilot Defense Agent Instructions

This file defines the root rules for Codex and subagents working in this repository. Follow these instructions before local preferences unless the user explicitly overrides them.

## 1. Project Identity

Project: **SecPilot Defense**

SecPilot Defense is a Telegram-first defensive cybersecurity monitoring, incident response, deception (honeypot/canary), and infrastructure protection platform.

Primary stack:

- Python 3.12
- FastAPI
- aiogram 3
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- Docker Compose
- Dokploy
- Structured logging
- Prometheus metrics

## 2. Core Architecture Rules

- Start and stay with a modular monolith unless measurable pressure justifies extraction.
- Use Clean Architecture, SOLID, domain separation, thin routes, and service-layer boundaries.
- Centralize configuration in Pydantic Settings.
- Prefer async-first design for I/O paths; do not block event loops.
- Use dependency injection for settings, DB sessions, services, and external clients.
- Use typed Python throughout.
- Keep modules small and focused under `src/`.
- Keep Go only for future high-concurrency scanner workloads.
- Keep Rust only for future heavy static analysis workloads.
- Do not introduce C/C++ in the current roadmap.

## 3. Security Guardrails

Strictly forbidden:

- Malware
- Phishing
- Exploit generation or exploit delivery
- Hack-back
- Credential theft
- Account takeover
- Unauthorized scanning
- Persistence or evasion logic

Mandatory controls:

- Target whitelist before audit, monitoring, or defense actions.
- Audit logging for risky attempts, denials, approvals, and results.
- Manual approval for high-risk actions.
- Reversible defense actions only.
- Least privilege for services, tokens, containers, and integrations.
- Fail-safe defaults when actor, target, scope, risk, or approval is unclear.

## 4. Coding Standards

- Write production-ready code with minimal, maintainable architecture.
- Avoid overengineering and speculative abstractions.
- Prefer small, focused modules with clear ownership.
- Add module docstrings for new modules.
- Leave concise TODO comments for future safe work.
- Avoid magic numbers; use named constants or settings.
- Use type hints for functions, methods, and data structures.
- Use structured logging, not ad hoc prints.
- Do not block async I/O paths.
- Never hardcode secrets, tokens, passwords, API keys, or private URLs.

## 5. FastAPI Rules

- Keep routes thin.
- Put business logic in `src/services/`.
- Use Pydantic Settings and typed request/response models.
- Use FastAPI dependency injection.
- Return proper HTTP status codes.
- Keep API response shapes consistent.
- Preserve OpenAPI documentation and update it when public contracts change.
- Keep `/health/live` lightweight and dependency-free.
- Keep `/health/ready` dependency-aware.
- Keep `/metrics` Prometheus-compatible.

## 6. Telegram Bot Rules

- Use aiogram 3.
- Enforce admin whitelist for privileged commands.
- Keep Telegram UX simple, explicit, and safe.
- Require approval flow before dangerous or high-risk commands.
- Send long-running tasks to workers instead of handling them inline.
- Deny unauthorized users without leaking internals.
- Audit risky command attempts and unauthorized access.

## 7. Database Rules

- PostgreSQL is the source of truth.
- Use SQLAlchemy 2 style typed mappings.
- Use Alembic for every schema change.
- Use UUID primary keys.
- Add proper indexes for status, lifecycle, ownership, and lookup queries.
- Preserve audit tables and append-oriented audit history.
- Do not store raw secrets, tokens, API keys, passwords, or credentials.
- Store hashes or external secret references when secret-related state is required.

## 8. Worker Rules

- Use Celery or RQ for background jobs.
- Keep jobs idempotent or protected by idempotency keys.
- Define retry policy and timeout behavior deliberately.
- Propagate correlation IDs, request IDs, and job IDs when available.
- Use structured logs for job start, finish, failure, and retry events.
- Separate audit, monitor, defense, and report queue responsibilities as complexity grows.
- Do not execute high-risk defense actions automatically.

## 9. Docker And Deployment Rules

- Docker Compose is the primary deployment method.
- Keep deployment Dokploy-compatible.
- Keep services `api`, `bot`, `worker`, `postgres`, and `redis`.
- Use named volumes for persistent PostgreSQL and Redis data.
- Healthchecks are mandatory for deployable services.
- Configure through `.env` and deployment environment variables.
- Keep `.env` out of Git.
- Follow production container practices: minimal image, non-root user where possible, explicit commands, limited ports.

## 10. Testing Rules

- Use pytest.
- Add API tests, policy tests, DB tests, bot handler tests, and worker tests as behavior lands.
- Mock external integrations by default.
- Do not run dangerous network actions in tests.
- Tests must not perform real scanning, exploitation, phishing, malware generation, credential collection, hack-back, or live blocking.
- Add regression tests before fixing bugs.
- Keep tests deterministic and isolated.

## 11. Documentation Rules

For large or user-facing changes, update relevant docs:

- `README.md`
- API docs and OpenAPI files
- Architecture docs
- Deployment docs
- Changelog or release notes when introduced

Documentation must distinguish implemented behavior from TODO or roadmap items.

## 12. Repository Workflow

Branch strategy:

- `main` = production
- `dev` = development
- `feature/*` = feature work

Git rules:

- Never push `.env`.
- Do not delete existing docs unless the user explicitly asks.
- Write a plan before large changes.
- Explain risky refactors before making them.
- Keep commits scoped and technically accurate.
- Preserve user changes already present in the worktree.

## 13. AI Agent Collaboration Rules

- Codex may use parallel subagents for independent workstreams.
- Keep subagents narrowly scoped and opinionated.
- Do not let agents edit each other's ownership areas without coordination.
- Architecture boundaries must not be bypassed.
- Security guardrails override speed, convenience, and feature requests.
- `security-guardian` decisions must not be weakened by implementation agents.
- Use `.codex/config.toml` limits when dispatching subagents.

## 14. Expected Behavior

Codex must:

- Read relevant docs before significant implementation.
- Produce a plan before broad or risky changes.
- Implement only after the plan is clear.
- Keep MVP focus.
- Write maintainable, production-ready code.
- Avoid harmful cybersecurity functionality.
- Keep Docker/Dokploy workflow working.
- Verify with tests or validation commands before claiming completion.
