#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT="${REPO_ROOT:-/opt/holofractal-harmonicode}"
PYTHON_BIN="${HHS_GUEST_IDE_PYTHON_BIN:-/opt/hhs/venv/bin/python}"
PIP_BIN="${HHS_GUEST_IDE_PIP_BIN:-/opt/hhs/venv/bin/pip}"
SERVICE_USER="${HHS_GUEST_IDE_SERVICE_USER:-hhs}"

fail() {
  printf 'HHS_I047_GUEST_IDE_INSTALL_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ $EUID -eq 0 ]] || fail "root is required"
[[ -d "$REPO_ROOT/.git" ]] || fail "repository missing: $REPO_ROOT"
[[ -x "$PYTHON_BIN" && -x "$PIP_BIN" ]] || fail "guest virtualenv missing"
id "$SERVICE_USER" >/dev/null 2>&1 || fail "service user missing: $SERVICE_USER"
[[ -s "$REPO_ROOT/hhs_runtime/builds/libhhs_runtime.so" ]] || fail "prebuilt native runtime missing"

"$PIP_BIN" install --disable-pip-version-check   fastapi==0.128.2 starlette==0.50.0 'httpx>=0.27,<1.0'   'uvicorn[standard]>=0.30,<1.0' 'cryptography>=46.0,<47.0'   requests pyyaml networkx websockets anyio sqlalchemy aiosqlite   numpy sympy >/dev/null

install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0750   /var/lib/hhs/data   /var/lib/hhs/data/runtime   /var/lib/hhs/pass174   /var/lib/hhs/pass194   /var/lib/hhs/pass205   /var/lib/hhs/pass213/surface   /var/lib/hhs/pass218   /var/lib/hhs/pass219/lane5   /var/lib/hhs/runtime-bootstrap \
  /var/lib/hhs/runtime-os

install -d -o root -g "$SERVICE_USER" -m 0750 /etc/hhs
cat > /etc/hhs/unified-guest-ide.env <<EOF
PYTHONUNBUFFERED=1
PYTHONPATH=$REPO_ROOT
HHS_REPOSITORY_ROOT=$REPO_ROOT
HHS_REPO_ROOT=$REPO_ROOT
HHS_DISABLE_C_AUTOBUILD=1
HHS_DATA_DIR=/var/lib/hhs/data
HHS_RUNTIME_OUTPUT_DIR=/var/lib/hhs/data/runtime
HHS_PASS174_STATE_DIR=/var/lib/hhs/pass174
HHS_PASS194_STATE_ROOT=/var/lib/hhs/pass194
HHS_PASS205_DB=/var/lib/hhs/pass205/continuation.sqlite3
HHS_PASS213_SURFACE_STATE_DIR=/var/lib/hhs/pass213/surface
HHS_PASS218_STATE_ROOT=/var/lib/hhs/pass218
HHS_PASS219_LANE5_STATE_ROOT=/var/lib/hhs/pass219/lane5
HHS_RUNTIME_BOOTSTRAP_ROOT=/var/lib/hhs/runtime-bootstrap
HHS_RUNTIME_OS_ASSET_ROOT=/var/lib/hhs/runtime-os/current
HHS_COGNITION_AUTO_TICK=0
EOF
chown root:"$SERVICE_USER" /etc/hhs/unified-guest-ide.env
chmod 0640 /etc/hhs/unified-guest-ide.env

install -m 0644   "$REPO_ROOT/deployment/ubuntu/guest_runtime/hhs-unified-guest-ide.service"   /etc/systemd/system/hhs-unified-guest-ide.service

systemctl daemon-reload
systemctl enable hhs-unified-guest-ide.service >/dev/null
systemctl restart hhs-unified-guest-ide.service

ready=0
for _ in $(seq 1 120); do
  if curl -fsS --max-time 5 http://127.0.0.1:8080/api/health >/tmp/hhs-i047-guest-ide-health.json 2>/dev/null; then
    ready=1
    break
  fi
  sleep 1
done
[[ "$ready" == "1" ]] || {
  systemctl status hhs-unified-guest-ide.service --no-pager --full >&2 || true
  journalctl -u hhs-unified-guest-ide.service -n 300 --no-pager >&2 || true
  fail "guest IDE did not become healthy"
}

"$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
payload=json.loads(Path("/tmp/hhs-i047-guest-ide-health.json").read_text(encoding="utf-8"))
assert payload["runtime_ready"] is True, payload
assert payload["frontend_runtime_authority"] is False, payload
print("HHS_I047_GUEST_IDE_AUTHORITY_VERIFIED")
PY

printf 'HHS_I047_GUEST_IDE_READY=1\n'
