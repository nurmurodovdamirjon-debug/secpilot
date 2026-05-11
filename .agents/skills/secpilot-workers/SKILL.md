---
name: secpilot-workers
description: Use when writing or reviewing SecPilot Celery or RQ workers, background jobs, audit jobs, monitor jobs, defense jobs, report jobs, retries, timeouts, idempotency, or worker logging.
---

# SecPilot Workers

## Skill Purpose
Build safe background job skeletons and worker tasks for SecPilot Defense.

## When To Use
- Use when changing `src/workers/`.
- Use when adding audit, monitor, defense, report, queue, retry, timeout, or scheduling behavior.
- Use when a bot or API endpoint enqueues work.

## When Not To Use
- Do not use for synchronous API-only logic.
- Do not use to add real scanner or active defense behavior without safety gates.

## Mandatory Rules
- Keep audit, monitor, defense, and report jobs separated by responsibility.
- Make jobs idempotent or reject duplicates with stable keys.
- Configure retries and timeouts deliberately.
- Log job start, finish, failure, request_id, correlation_id, and job_id when available.
- Call PolicyGate before any security-sensitive action.

## File And Folder Naming
- Put Celery app setup in `src/workers/celery_app.py`.
- Put simple tasks in `src/workers/tasks.py`.
- Split into `audit_tasks.py`, `monitor_tasks.py`, `defense_tasks.py`, and `report_tasks.py` when task count grows.

## Coding Standards
- Keep task bodies small; call services for business logic.
- Avoid unbounded network calls.
- Prefer dry-run mode for defense actions.
- Add tests for task routing, idempotency, and policy denial.

## Security Constraints
- Do not run unauthorized scanning.
- Do not execute irreversible actions.
- Do not retry external mutation failures in a storm; require human review for high-risk failures.

## Expected Output
- Worker code with clear task ownership, safe retry behavior, structured logging, and tests.
