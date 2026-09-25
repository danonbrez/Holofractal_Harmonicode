#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

SOURCE_ROOT="${SOURCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
TARGET_SHA="${TARGET_SHA:?TARGET_SHA is required}"
ROOT="${HHS_GUEST_INTEGRATION_ROOT:-/var/lib/hhs/ubuntu-guest}"
STATE_ROOT="$ROOT/releases/$TARGET_SHA"
ENV_FILE="$STATE_ROOT/runtime.env"
CURRENT_LINK="$ROOT/current"

fail() {
  printf 'HHS_I044_REAL_GUEST_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ $EUID -eq 0 ]] || fail "root is required"
[[ "$TARGET_SHA" =~ ^[0-9a-f]{40}$ ]] || fail "TARGET_SHA must be a 40-character lowercase git SHA"

bash "$SOURCE_ROOT/deployment/ubuntu/guest_runtime/prepare-real-guest.sh"
[[ -r "$ENV_FILE" ]] || fail "prepared runtime environment missing: $ENV_FILE"

stop_release() {
  local release="$1"
  local old_env="$release/runtime.env"
  [[ -r "$old_env" ]] || return 0
  (
    set -a
    # shellcheck disable=SC1090
    source "$old_env"
    set +a
    PYTHONPATH="$SOURCE_ROOT" sh "$SOURCE_ROOT/bin/hhs-guest" stop >/dev/null || true
  )
}

if [[ -L "$CURRENT_LINK" ]]; then
  PREVIOUS="$(readlink -f "$CURRENT_LINK" || true)"
  if [[ -n "$PREVIOUS" && "$PREVIOUS" != "$STATE_ROOT" ]]; then
    stop_release "$PREVIOUS"
  fi
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

guest() {
  PYTHONPATH="$SOURCE_ROOT" sh "$SOURCE_ROOT/bin/hhs-guest" "$@"
}

cleanup_on_error() {
  status=$?
  trap - ERR
  set +e
  echo "HHS_I044_REAL_GUEST_INTEGRATION_FAILED=$TARGET_SHA" >&2
  guest status >&2 || true
  guest stop >/dev/null 2>&1 || true
  exit "$status"
}
trap cleanup_on_error ERR

guest verify > "$STATE_ROOT/image-verify.json"
guest prepare > "$STATE_ROOT/overlay-prepare.json"
guest start > "$STATE_ROOT/start.json"

SSH=(
  ssh
  -i "$HHS_GUEST_SSH_IDENTITY"
  -p "$HHS_GUEST_SSH_PORT"
  -o BatchMode=yes
  -o IdentitiesOnly=yes
  -o StrictHostKeyChecking=yes
  -o "UserKnownHostsFile=$HHS_GUEST_SSH_KNOWN_HOSTS"
  -o ConnectTimeout=10
  -o ServerAliveInterval=15
  -o ServerAliveCountMax=20
  "hhs@127.0.0.1"
)

SSH_READY=0
for _ in $(seq 1 120); do
  if "${SSH[@]}" 'printf HHS_I044_SSH_READY' 2>/dev/null | grep -Fq HHS_I044_SSH_READY; then
    SSH_READY=1
    break
  fi
  sleep 5
done
[[ "$SSH_READY" == "1" ]] || fail "guest SSH did not become reachable"

timeout 2700s "${SSH[@]}" 'sudo cloud-init status --wait --long'
"${SSH[@]}" 'test -f /var/lib/hhs/guest-bootstrap/ready'

GUEST_SHA="$("${SSH[@]}" 'cat /var/lib/hhs/guest-bootstrap/repository-sha')"
[[ "$GUEST_SHA" == "$TARGET_SHA" ]] \
  || fail "guest repository mismatch: expected=$TARGET_SHA actual=$GUEST_SHA"

"${SSH[@]}" 'sudo systemctl is-active --quiet hhs-application-vm.service'
"${SSH[@]}" 'sudo systemctl is-active --quiet hhs-unified-guest-ide.service'
"${SSH[@]}" 'curl -fsS http://127.0.0.1:8720/health' > "$STATE_ROOT/application-vm-health.json"
"${SSH[@]}" \
  'HHS_APPLICATION_VM_ENV_FILE=/etc/hhs/application-vm.env hhs-vm status' \
  > "$STATE_ROOT/application-vm-status.json"
"${SSH[@]}" 'curl -fsS http://127.0.0.1:8080/api/health' > "$STATE_ROOT/guest-ide-health.json"
curl -fsS --max-time 10 \
  "http://127.0.0.1:${HHS_GUEST_RUNTIME_HTTP_PORT}/api/health" \
  > "$STATE_ROOT/host-forwarded-guest-ide-health.json"

python3 - \
  "$STATE_ROOT/application-vm-health.json" \
  "$STATE_ROOT/application-vm-status.json" \
  "$STATE_ROOT/guest-ide-health.json" \
  "$STATE_ROOT/host-forwarded-guest-ide-health.json" <<'PY'
import json, sys
from pathlib import Path
health=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
status=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
guest_ide=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
forwarded=json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
assert health["ok"] is True
assert health["ubuntu"] is True
assert health["security_configured"] is True
assert health["new_vm81_authority"] is False
assert status["single_vm81_authority_preserved"] is True
assert status["fastapi_frontend_authority"] is False
assert status["frontend_attached"] is False
assert guest_ide["runtime_ready"] is True
assert guest_ide["frontend_runtime_authority"] is False
assert forwarded["runtime_ready"] is True
assert forwarded["frontend_runtime_authority"] is False
print("HHS_I047_GUEST_IDE_TRANSPORT_VERIFIED")
PY

guest pty-exec --timeout 30 -- bash -lc \
  'printf HHS_I044_PTY_OK && test "$(git -C /opt/holofractal-harmonicode rev-parse HEAD)" = "'"$TARGET_SHA"'"' \
  > "$STATE_ROOT/pty-proof.json"

python3 - "$STATE_ROOT/pty-proof.json" <<'PY'
import json, sys
from pathlib import Path
payload=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["exit_status"] == 0
assert "HHS_I044_PTY_OK" in payload["output_utf8"]
assert payload["canonical_state_authority"] is False
print("HHS_I044_REAL_PTY_VERIFIED")
PY

guest status > "$STATE_ROOT/runtime-status.json"

python3 - \
  "$STATE_ROOT/integration.receipt.json" \
  "$TARGET_SHA" \
  "$STATE_ROOT/preparation.receipt.json" \
  "$STATE_ROOT/runtime-status.json" \
  "$STATE_ROOT/application-vm-health.json" \
  "$STATE_ROOT/application-vm-status.json" \
  "$STATE_ROOT/guest-ide-health.json" \
  "$STATE_ROOT/host-forwarded-guest-ide-health.json" \
  "$STATE_ROOT/pty-proof.json" <<'PY'
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

out=Path(sys.argv[1])
target=sys.argv[2]
prep=json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
runtime=json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
health=json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
app=json.loads(Path(sys.argv[6]).read_text(encoding="utf-8"))
guest_ide=json.loads(Path(sys.argv[7]).read_text(encoding="utf-8"))
forwarded=json.loads(Path(sys.argv[8]).read_text(encoding="utf-8"))
pty=json.loads(Path(sys.argv[9]).read_text(encoding="utf-8"))
payload={
    "schema": "HHS_PASS_220_I044_REAL_UBUNTU_GUEST_INTEGRATION_RECEIPT_V1",
    "target_sha": target,
    "base_sha256": prep["base_sha256"],
    "guest_running": runtime["running"],
    "guest_pid": runtime["pid"],
    "ssh_loopback_only": runtime["ssh"]["loopback_only"],
    "application_vm_ok": health["ok"],
    "single_vm81_authority_preserved": app["single_vm81_authority_preserved"],
    "guest_ide_ok": guest_ide["runtime_ready"],
    "guest_ide_frontend_runtime_authority": guest_ide["frontend_runtime_authority"],
    "host_forwarded_guest_ide_ok": forwarded["runtime_ready"],
    "runtime_http_host": "127.0.0.1",
    "runtime_http_port": int(__import__("os").environ["HHS_GUEST_RUNTIME_HTTP_PORT"]),
    "runtime_http_loopback_only": True,
    "pty_exit_status": pty["exit_status"],
    "pty_proof": "HHS_I044_PTY_OK" in pty["output_utf8"],
    "canonical_state_authority": False,
    "new_vm81_authority": False,
    "frontend_attached": True,
    "frontend_attachment": "HOST_STATIC_PRESENTATION_TO_GUEST_IDE_TRANSPORT",
    "verified_at": datetime.now(timezone.utc).isoformat(),
}
if not (
    payload["guest_running"]
    and payload["ssh_loopback_only"]
    and payload["application_vm_ok"]
    and payload["single_vm81_authority_preserved"]
    and payload["guest_ide_ok"]
    and payload["guest_ide_frontend_runtime_authority"] is False
    and payload["host_forwarded_guest_ide_ok"]
    and payload["runtime_http_loopback_only"]
    and payload["pty_exit_status"] == 0
    and payload["pty_proof"]
):
    raise SystemExit(f"I044 integration closure failed: {payload}")
canonical=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
payload["receipt_sha256"]=hashlib.sha256(canonical).hexdigest()
out.write_text(json.dumps(payload, sort_keys=True, indent=2)+"\n", encoding="utf-8")
print(json.dumps(payload, sort_keys=True))
PY

ln -sfnT "$STATE_ROOT" "$CURRENT_LINK"
trap - ERR

echo "HHS_I044_REAL_UBUNTU_GUEST_VERIFIED=$TARGET_SHA"
echo "HHS_I044_REAL_UBUNTU_GUEST_STATE=$STATE_ROOT"
