#!/usr/bin/env bash
set -euo pipefail

TS=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
docker compose exec -T postgres pg_dump -U secpilot secpilot > "backups/secpilot_${TS}.sql"
echo "Backup saved: backups/secpilot_${TS}.sql"
