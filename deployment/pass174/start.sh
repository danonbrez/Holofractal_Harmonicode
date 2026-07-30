#!/bin/sh
set -eu

export HHS_REPOSITORY_ROOT="${HHS_REPOSITORY_ROOT:-$(pwd)}"
export HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC="${HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC:-0}"
export HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS="${HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS:-5}"
export HHS_PASS174_BOOT_TIMEOUT_SECONDS="${HHS_PASS174_BOOT_TIMEOUT_SECONDS:-12}"

PORT="${PORT:-8000}"

exec python -m uvicorn hhs_backend.pass174_server:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --workers 1 \
  --timeout-keep-alive 5 \
  --log-level info
