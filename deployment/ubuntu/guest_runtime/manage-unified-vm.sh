#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ACTION="${1:-start}"
REPO_ROOT="${HHS_REPO_ROOT:-/opt/hhs/app}"
CURRENT="${HHS_GUEST_INTEGRATION_ROOT:-/var/lib/hhs/ubuntu-guest}/current"
ENV_FILE="$CURRENT/runtime.env"

fail() {
  printf 'HHS_I047_UNIFIED_VM_SUPERVISOR_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ $EUID -eq 0 ]] || fail "root is required"
[[ -d "$REPO_ROOT/.git" ]] || fail "repository missing: $REPO_ROOT"
[[ -L "$CURRENT" ]] || fail "current guest release missing: $CURRENT"
[[ -r "$ENV_FILE" ]] || fail "guest runtime environment missing: $ENV_FILE"

TARGET_SHA="$(basename "$(readlink -f "$CURRENT")")"
LIVE_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD)"
[[ "$TARGET_SHA" == "$LIVE_SHA" ]] || fail "guest/repository SHA mismatch: guest=$TARGET_SHA live=$LIVE_SHA"

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

guest() {
  PYTHONPATH="$REPO_ROOT" "$REPO_ROOT/bin/hhs-guest" "$@"
}

case "$ACTION" in
  start)
    guest start >/tmp/hhs-i047-unified-vm-start.json
    ready=0
    for _ in $(seq 1 180); do
      if curl -fsS --max-time 5         "http://127.0.0.1:${HHS_GUEST_RUNTIME_HTTP_PORT}/api/health"         >/tmp/hhs-i047-unified-vm-health.json 2>/dev/null         && curl -fsS --max-time 5         "http://127.0.0.1:${HHS_GUEST_APPLICATION_API_PORT}/health"         >/tmp/hhs-i047-unified-vm-api-health.json 2>/dev/null; then
        ready=1
        break
      fi
      sleep 2
    done
    [[ "$ready" == "1" ]] || fail "guest runtime did not become healthy"
    python3 - <<'PY'
import json
from pathlib import Path
ide=json.loads(Path("/tmp/hhs-i047-unified-vm-health.json").read_text())
api=json.loads(Path("/tmp/hhs-i047-unified-vm-api-health.json").read_text())
assert ide["runtime_ready"] is True, ide
assert ide["frontend_runtime_authority"] is False, ide
assert api["ok"] is True, api
assert api["new_vm81_authority"] is False, api
print("HHS_I047_UNIFIED_VM_READY")
PY
    ;;
  stop)
    guest stop >/tmp/hhs-i047-unified-vm-stop.json || true
    ;;
  status)
    guest status
    ;;
  *)
    fail "unsupported action: $ACTION"
    ;;
esac
