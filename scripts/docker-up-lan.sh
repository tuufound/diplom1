#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/scripts/write-lan-env.sh"
cd "$ROOT"
if [[ $# -eq 0 ]]; then
  docker compose --env-file .env.lan up --build
else
  docker compose --env-file .env.lan "$@"
fi
