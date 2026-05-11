---
name: secpilot-dokploy-deploy
description: Use when changing SecPilot Dokploy, Docker Compose, Dockerfile, deployment env vars, api, bot, worker, postgres, redis services, volumes, healthchecks, logs, or GitHub deploy setup.
---

# SecPilot Dokploy Deploy

## Skill Purpose
Keep SecPilot deployment compatible with Dokploy and Docker Compose.

## When To Use
- Use when changing `docker-compose.yml`, `Dockerfile`, `.env.example`, deployment docs, or service commands.
- Use when configuring `api`, `bot`, `worker`, `postgres`, or `redis`.
- Use when preparing GitHub-backed Dokploy deployment.

## When Not To Use
- Do not use for Kubernetes-only work unless Docker Compose compatibility is affected.
- Do not use to hardcode production secrets.

## Mandatory Rules
- Keep services: `api`, `bot`, `worker`, `postgres`, `redis`.
- Use named volumes for PostgreSQL and Redis persistence.
- Use healthchecks for dependency readiness.
- Drive configuration through environment variables.
- Keep `.env` out of GitHub; commit `.env.example` only.

## File And Folder Naming
- Keep Docker Compose at `docker-compose.yml`.
- Keep container build at `Dockerfile`.
- Keep deployment examples under `deploy/`.
- Keep local secrets in `.env`, never in tracked files.

## Coding Standards
- Use explicit commands for API, bot, and worker containers.
- Prefer simple runtime images and non-root app users.
- Keep ports configurable through env defaults.
- Validate with `docker compose config` and, when Docker is running, `docker compose build`.

## Security Constraints
- Do not commit tokens, passwords, private keys, or production `.env`.
- Do not expose unnecessary ports.
- Do not add privileged containers unless there is a documented defensive requirement and manual approval.

## Expected Output
- Dokploy-ready Docker Compose changes with env-driven config, healthchecks, volumes, and deployment notes.
