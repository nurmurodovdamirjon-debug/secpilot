---
name: secpilot-testing
description: Use when writing or reviewing SecPilot pytest tests, health endpoint tests, config tests, PolicyGate tests, database model tests, bot handler tests, safe mocks, or test isolation.
---

# SecPilot Testing

## Skill Purpose
Create safe, focused pytest coverage for SecPilot Defense MVP and future defensive features.

## When To Use
- Use when adding or changing tests under `tests/`.
- Use when adding behavior to health endpoints, config, PolicyGate, DB models, bot handlers, or workers.
- Use when fixing bugs or preventing regressions.

## When Not To Use
- Do not use for manual-only smoke checks without automated tests.
- Do not use to run harmful network actions in tests.

## Mandatory Rules
- Prefer pytest unit tests for new behavior.
- Test PolicyGate deny/allow/manual-approval outcomes.
- Test `/health/live`, `/health/ready`, and `/metrics` behavior without requiring external services unless explicitly integration-scoped.
- Keep tests deterministic and isolated.
- Use mocks or fakes for external APIs, Telegram, Redis, PostgreSQL, Cloudflare, and threat-intel services unless running a declared integration test.

## File And Folder Naming
- Put tests under `tests/`.
- Use `test_<module>.py` filenames.
- Name tests by behavior, for example `test_unknown_target_is_denied`.

## Coding Standards
- Test public behavior, not private implementation details.
- Keep one main assertion theme per test.
- Add regression tests before fixing bugs.
- Keep fixtures small and local unless reused broadly.

## Security Constraints
- Tests must not perform real scanning, exploitation, credential collection, phishing, malware generation, hack-back, or real blocking.
- Tests must not call production networks or mutate live security providers.
- Tests must not print secrets.

## Expected Output
- Focused pytest files that verify safe behavior, config parsing, policy enforcement, route responses, and handler authorization.
