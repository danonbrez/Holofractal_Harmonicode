#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/opt/holofractal-harmonicode}"
SERVICE_USER="${SERVICE_USER:-hhs}"
HOST="${HHS_APPLICATION_VM_HOST:-127.0.0.1}"
PORT="${HHS_APPLICATION_VM_PORT:-8720}"
ROOT_PATH="${HHS_APPLICATION_VM_ROOT_PATH:-/vm-api}"
REQUIRE_GUI="${HHS_APPLICATION_VM_REQUIRE_GUI:-1}"
INSTALL_GUI="${HHS_APPLICATION_VM_INSTALL_GUI:-0}"

fail() {
  printf 'HHS_APPLICATION_VM_INSTALL_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ -f /etc/os-release ]] || fail "/etc/os-release is required"
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || fail "Ubuntu is required; detected ID=${ID:-unknown}"
[[ -d "$REPO_ROOT/.git" ]] || fail "repository checkout missing at $REPO_ROOT"
[[ -f "$REPO_ROOT/hhs_backend/application_vm_api_server.py" ]] || fail "application VM API source missing"

if [[ "$INSTALL_GUI" == "1" ]] && ! command -v gnome-shell >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y ubuntu-desktop-minimal
fi

if [[ "$REQUIRE_GUI" == "1" ]] && ! command -v gnome-shell >/dev/null 2>&1 && ! command -v ubuntu-session >/dev/null 2>&1; then
  fail "Ubuntu GUI components missing; set HHS_APPLICATION_VM_INSTALL_GUI=1 to install ubuntu-desktop-minimal"
fi

python3 - <<'PY' || fail "Python runtime dependencies missing"
import fastapi, uvicorn
PY

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  useradd --system --home /var/lib/hhs/application-vm --shell /usr/sbin/nologin "$SERVICE_USER"
fi

install -d -o "$SERVICE_USER" -g "$SERVICE_USER" -m 0750 /var/lib/hhs/application-vm
install -d -o root -g "$SERVICE_USER" -m 0750 /etc/hhs

SECRET=""
if [[ -f /etc/hhs/application-vm.env ]]; then
  SECRET="$(sed -n 's/^HHS_PASS190_CAPABILITY_SECRET=//p' /etc/hhs/application-vm.env | tail -n1)"
fi
if [[ -z "$SECRET" ]]; then
  SECRET="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
fi
[[ "${#SECRET}" -ge 32 ]] || fail "generated capability secret is unexpectedly short"

cat > /etc/hhs/application-vm.env <<EOF
HHS_APPLICATION_VM_REPOSITORY_ROOT=$REPO_ROOT
HHS_APPLICATION_VM_STATE_ROOT=/var/lib/hhs/application-vm
HHS_PASS190_DATABASE=/var/lib/hhs/application-vm/pass190-authority.sqlite3
HHS_PASS190_CAPABILITY_SECRET=$SECRET
HHS_APPLICATION_VM_HOST=$HOST
HHS_APPLICATION_VM_PORT=$PORT
HHS_APPLICATION_VM_ROOT_PATH=$ROOT_PATH
EOF
chown root:"$SERVICE_USER" /etc/hhs/application-vm.env
chmod 0640 /etc/hhs/application-vm.env

sed "s#@@REPOSITORY_ROOT@@#$REPO_ROOT#g"   "$REPO_ROOT/deployment/ubuntu/application_vm/hhs-application-vm.service.template"   > /etc/systemd/system/hhs-application-vm.service

install -m 0755 "$REPO_ROOT/bin/hhs-vm" /usr/local/bin/hhs-vm

systemctl daemon-reload
systemctl enable --now hhs-application-vm.service

for _ in $(seq 1 45); do
  if curl --fail --silent "http://$HOST:$PORT/health" >/tmp/hhs-application-vm-health.json; then
    break
  fi
  sleep 1
done
curl --fail --silent "http://$HOST:$PORT/health" >/tmp/hhs-application-vm-health.json   || fail "application VM control plane did not become healthy"

python3 - <<'PY'
import json
p=json.load(open("/tmp/hhs-application-vm-health.json"))
assert p["ok"] is True
assert p["security_configured"] is True
assert p["frontend_attached"] is False
assert p["public_mutation_requires_signed_capability"] is True
PY

printf '%s\n' "HHS Ubuntu application VM control plane is healthy."
printf '%s\n' "Loopback: http://$HOST:$PORT"
printf '%s\n' "Public reverse-proxy prefix: $ROOT_PATH"
printf '%s\n' "Issue an operator token locally with:"
printf '%s\n' "  sudo -u $SERVICE_USER hhs-vm --env-file /etc/hhs/application-vm.env token issue --principal operator --scope runtime.mutate"
