#!/usr/bin/env bash
set -euo pipefail

missing=0
check_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "OK: $1 found at $(command -v "$1")"
  else
    echo "MISSING: $1 is not installed" >&2
    missing=1
  fi
}

check_env() {
  if [ -n "${!1:-}" ]; then
    echo "OK: $1 is set"
  else
    echo "MISSING: $1 is not set" >&2
    missing=1
  fi
}

check_cmd npm
check_cmd git
check_cmd supabase
check_cmd gh

check_env NEXT_PUBLIC_SUPABASE_URL
check_env NEXT_PUBLIC_SUPABASE_ANON_KEY
check_env SUPABASE_SERVICE_ROLE_KEY
check_env APPROVAL_JWT_SECRET
check_env APP_BASE_URL

if [ "$missing" -ne 0 ]; then
  echo "Deployment access check failed. Install missing CLIs or export missing secrets." >&2
  exit 1
fi

echo "Deployment access check passed."
