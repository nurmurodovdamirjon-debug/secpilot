#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
echo "Edit .env, then run: docker compose up --build"
