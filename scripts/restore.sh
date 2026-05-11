#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: ./scripts/restore.sh backups/file.sql"
  exit 1
fi

cat "$1" | docker compose exec -T postgres psql -U secpilot secpilot
