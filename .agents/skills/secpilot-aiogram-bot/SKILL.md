---
name: secpilot-aiogram-bot
description: Use when writing or reviewing SecPilot aiogram 3 Telegram bot code, commands, handlers, /start, /status, admin whitelist, safe actions, or approval flows.
---

# SecPilot aiogram Bot

## Skill Purpose
Keep the Telegram bot safe, admin-scoped, and compatible with aiogram 3.

## When To Use
- Use when changing `src/bot/`.
- Use when adding Telegram commands, callbacks, admin checks, status output, alerts, or approval flows.
- Use when bot commands enqueue jobs or request risky actions.

## When Not To Use
- Do not use for API-only or DB-only changes.
- Do not use to create unsafe automation through Telegram.

## Mandatory Rules
- Enforce `BOT_ADMIN_IDS` whitelist for privileged commands.
- Keep `/start` and `/status` safe and non-destructive.
- Require explicit manual approval before high-risk actions.
- Send clear denial messages for unauthorized users without leaking internals.
- Audit unauthorized access and risky action attempts.

## File And Folder Naming
- Put polling entrypoint in `src/bot/main.py`.
- Put handlers in `src/bot/handlers.py` or domain-specific handler modules.
- Put auth helpers in `src/bot/auth.py`.

## Coding Standards
- Use aiogram 3 routers and filters.
- Keep handlers thin; call services for business logic.
- Avoid blocking I/O in async handlers.
- Add tests for authorization and command behavior.

## Security Constraints
- Never implement commands for exploit, malware, credential theft, phishing, bypass, hack-back, or unauthorized scanning.
- Never execute defense actions directly from a message without PolicyGate and approval state.

## Expected Output
- Safe aiogram command handlers with admin whitelist, approval-aware flow, audit logging, and tests.
