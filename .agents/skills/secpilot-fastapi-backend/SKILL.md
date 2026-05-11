---
name: secpilot-fastapi-backend
description: Use when writing or reviewing SecPilot FastAPI backend code, API routes, health endpoints, readiness checks, metrics, dependencies, Pydantic settings, or structured error responses.
---

# SecPilot FastAPI Backend

## Skill Purpose
Build production-ready, simple, testable FastAPI backend code for SecPilot Defense.

## When To Use
- Use when adding or changing API routes under `src/api/`.
- Use when touching `/health/live`, `/health/ready`, `/metrics`, dependency injection, request errors, or settings.
- Use when wiring services into API endpoints.

## When Not To Use
- Do not use for Telegram-only bot changes.
- Do not use for DB migrations unless API behavior is also changing.

## Mandatory Rules
- Keep `/health/live` lightweight and dependency-free.
- Keep `/health/ready` dependency-aware for PostgreSQL and Redis.
- Keep `/metrics` Prometheus-compatible.
- Use dependency injection for settings, DB sessions, and services.
- Return structured errors with stable codes and request context when available.

## File And Folder Naming
- Put app assembly in `src/api/main.py`.
- Put route groups in `src/api/routes/`.
- Use route module names by domain: `health.py`, `metrics.py`, `assets.py`, `jobs.py`.

## Coding Standards
- Keep route handlers thin; put business logic in `src/services/`.
- Use Pydantic request/response models for public API contracts.
- Avoid global mutable state except configured app-level clients.
- Add focused pytest coverage for each behavior.

## Security Constraints
- Do not expose secrets in responses, logs, metrics, or errors.
- Route handlers must call PolicyGate before audit or defense actions.
- Do not add unauthorized scanner or exploit endpoints.

## Expected Output
- Clean FastAPI route code with typed schemas, service calls, structured errors, and tests.
