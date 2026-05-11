---
name: secpilot-database
description: Use when writing or reviewing SecPilot SQLAlchemy, Alembic, PostgreSQL, models, migrations, User, Asset, Job, Alert, Incident, AuditLog, indexes, or database safety.
---

# SecPilot Database

## Skill Purpose
Keep SecPilot PostgreSQL schema, SQLAlchemy models, and Alembic migrations clean, safe, and migration-friendly.

## When To Use
- Use when changing `src/db/`, `alembic/`, or database-related tests.
- Use when adding or modifying `User`, `Asset`, `Job`, `Alert`, `Incident`, or `AuditLog`.
- Use when changing indexes, constraints, defaults, or relationships.

## When Not To Use
- Do not use for API route-only changes without schema impact.
- Do not use for storing raw secrets or credentials.

## Mandatory Rules
- Use Alembic for schema changes.
- Keep migrations deterministic and reviewable.
- Preserve auditability for risky actions.
- Use UUID primary keys where existing models do.
- Use indexes for lifecycle/status queries and JSONB evidence fields when needed.

## File And Folder Naming
- Put base metadata in `src/db/base.py`.
- Put session/engine setup in `src/db/session.py`.
- Put models in `src/db/models.py` until the file becomes too large, then split by domain.
- Put migrations in `alembic/versions/`.

## Coding Standards
- Use SQLAlchemy 2 typed mappings.
- Prefer explicit constraints, server defaults, nullable choices, and relationships.
- Keep migrations backward-aware for deployed Docker Compose environments.
- Add tests or offline migration checks for schema changes.

## Security Constraints
- Never store raw API keys, tokens, passwords, or credentials.
- Store token hashes or external secret references when secret-related state is required.
- Ensure audit records do not leak sensitive payloads.

## Expected Output
- Safe SQLAlchemy models, Alembic migrations, and tests or migration verification commands.
