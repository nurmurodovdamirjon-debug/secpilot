---
name: secpilot-architecture
description: Use when changing SecPilot architecture, module boundaries, FastAPI, aiogram, PostgreSQL, Redis, Docker Compose, modular monolith, Go extraction, or Rust extraction decisions.
---

# SecPilot Architecture

## Skill Purpose
Keep SecPilot Defense aligned with its MVP architecture: a Python modular monolith with FastAPI API, aiogram bot, PostgreSQL, Redis, workers, and Docker Compose deployment.

## When To Use
- Use when adding, moving, or refactoring modules under `src/`.
- Use when changing service boundaries, worker layout, deployment topology, or integration shape.
- Use when discussing Go or Rust service extraction.

## When Not To Use
- Do not use for isolated tests, copy edits, or dependency-only updates.
- Do not use to add offensive security behavior.

## Mandatory Rules
- Preserve modular monolith as the default architecture.
- Keep API, bot, DB, workers, integrations, agents, skills, and reports as separate bounded modules.
- Keep Go scanner and Rust analyzer extraction as later-stage options only.
- Require measurable pressure before proposing microservices: queue depth, p95 latency, CPU, memory, or operational complexity.

## File And Folder Naming
- Keep Python code under `src/`.
- Use feature-neutral module names: `api`, `bot`, `core`, `db`, `services`, `workers`, `integrations`, `agents`, `skills`, `reports`.
- Use lowercase snake_case for Python files and clear singular/plural names.

## Coding Standards
- Prefer small, testable modules with explicit dependencies.
- Avoid framework leakage across boundaries: bot handlers should not own DB models; workers should call services.
- Use typed interfaces and Pydantic models where contracts cross module boundaries.

## Security Constraints
- Architecture must enforce defensive-only, authorized workflows.
- PolicyGate must remain in front of audit or defense actions.
- High-risk actions must stay approval-gated and audit-logged.

## Expected Output
- Architecture changes that preserve the MVP stack and boundaries.
- Clear notes when a change affects service ownership, data flow, deployment, or security posture.
