---
name: secpilot-security-guardrails
description: Use when SecPilot work involves cybersecurity behavior, target validation, whitelist, audit log, manual approval, reversible defense, malware, phishing, exploit, hack-back, credential theft, bypass, or scanning.
---

# SecPilot Security Guardrails

## Skill Purpose
Enforce SecPilot Defense safety policy for defensive and authorized cybersecurity only.

## When To Use
- Use before implementing or reviewing any security-sensitive feature.
- Use when a request mentions scanning, blocking, enrichment, honeypot, canary, AI advice, response actions, or Telegram-triggered actions.
- Use when a feature could affect external systems.

## When Not To Use
- Do not use for purely cosmetic documentation edits.
- Do not use to justify unsafe functionality.

## Mandatory Rules
- Refuse malware, phishing, exploit delivery, credential theft, bypass, persistence, evasion, account takeover, hack-back, and unauthorized scanning.
- Require target whitelist checks before any audit or defense job.
- Require manual approval for high-risk actions.
- Allow auto-defense only when reversible, low-risk, scoped, and logged.
- Audit all risky action attempts, approvals, denials, and results.
- Fail closed when scope, identity, target, or risk is unclear.

## File And Folder Naming
- Put safety enforcement in `src/services/policy_gate.py` or focused service modules.
- Put audit logging in `src/services/audit_log.py` or DB-backed audit modules.
- Do not hide security decisions inside bot handlers or worker tasks.

## Coding Standards
- Make allow/deny decisions explicit and typed.
- Return structured decisions with reason codes.
- Keep dry-run behavior available for defense actions.
- Mask tokens, passwords, API keys, and authorization headers in logs.

## Security Constraints
- Never generate offensive payloads, exploit chains, phishing templates, malware, credential collection, or bypass instructions.
- Never add real IP blocking, Cloudflare mutation, service restart, or secret rotation without approval flow and audit trail.

## Expected Output
- Defensive-only code or review findings.
- Explicit whitelist, approval, reversibility, and audit-log handling for risky workflows.
