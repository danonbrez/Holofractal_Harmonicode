#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/opt/holofractal-harmonicode}"
SERVICE_USER="${SERVICE_USER:-hhs}"
HOST="${HHS_APPLICATION_VM_HOST:-127.0.0.1}"
PORT="${HHS_APPLICATION_VM_PORT:-8720}"
ROOT_PATH="${HHS_APPLICATION_VM_ROOT_PATH:-/vm-api}"
REQUIRE_GUI="${HHS_APPLICATION_VM_REQUIRE_GUI:-1}"
INSTALL_GUI="${HHS_APPLICATION_VM_INSTALL_GUI:-0}"
PYTHON_BIN="${HHS_APPLICATION_VM_PYTHON_BIN:-}"

fail() {
  printf 'HHS_APPLICATION_VM_INSTALL_FAILED: %s\n' "$*" >&2
  exit 2
}

[[ -f /etc/os-release ]] || fail "/etc/os-release is required"
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == "ubuntu" ]] || fail "Ubuntu is required; detected ID=${ID:-unknown}"
command -v git >/dev/null 2>&1 || fail "git is required to validate the repository release"
git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || fail "repository checkout/worktree missing at $REPO_ROOT"
[[ -f "$REPO_ROOT/hhs_backend/application_vm_api_server.py" ]] || fail "application VM API source missing"

if [[ "$INSTALL_GUI" == "1" ]] && ! command -v gnome-shell >/dev/null 2>&1 && ! command -v ubuntu-session >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y ubuntu-desktop-minimal
fi

if [[ "$REQUIRE_GUI" == "1" ]] && ! command -v gnome-shell >/dev/null 2>&1 && ! command -v ubuntu-session >/dev/null 2>&1; then
  fail "Ubuntu GUI components missing; set HHS_APPLICATION_VM_INSTALL_GUI=1 to install ubuntu-desktop-minimal"
fi

if [[ -z "$PYTHON_BIN" && -x /opt/hhs/venv/bin/python ]]; then
  PYTHON_BIN=/opt/hhs/venv/bin/python
fi
if [[ -z "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi
[[ -n "$PYTHON_BIN" && -x "$PYTHON_BIN" ]] || fail "Python runtime could not be resolved"

"$PYTHON_BIN" - <<'PY' || fail "Python runtime dependencies missing"
import fastapi, uvicorn
PY

NATIVE_TOOLCHAIN_MISSING=0
for tool in make gcc nm gzip; do
  command -v "$tool" >/dev/null 2>&1 || NATIVE_TOOLCHAIN_MISSING=1
done
[[ -f /usr/include/openssl/evp.h ]] || NATIVE_TOOLCHAIN_MISSING=1

if [[ "$NATIVE_TOOLCHAIN_MISSING" == "1" ]]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y build-essential binutils gzip libssl-dev
fi

for tool in make gcc nm gzip; do
  command -v "$tool" >/dev/null 2>&1 || fail "native runtime build tool missing: $tool"
done
[[ -f /usr/include/openssl/evp.h ]] || fail "OpenSSL development headers are required"

RUNTIME_SO="$REPO_ROOT/hhs_runtime/builds/libhhs_runtime.so"
(
  cd "$REPO_ROOT"
  timeout 900s make -B c-abi
) || fail "native runtime shared library build failed"

[[ -s "$RUNTIME_SO" ]] || fail "native runtime shared library missing after build: $RUNTIME_SO"
nm -D "$RUNTIME_SO" | grep -Eq ' hhs_runtime_init$' || fail "native runtime export missing: hhs_runtime_init"
nm -D "$RUNTIME_SO" | grep -Eq ' hhs_validate_abi$' || fail "native runtime export missing: hhs_validate_abi"
nm -D "$RUNTIME_SO" | grep -Eq ' hhs_exact_abi_validate$' || fail "native runtime export missing: hhs_exact_abi_validate"
nm -D "$RUNTIME_SO" | grep -Eq ' hhs_hash216_compute$' || fail "native runtime export missing: hhs_hash216_compute"
if command -v ldd >/dev/null 2>&1 && ldd "$RUNTIME_SO" | grep -q 'not found'; then
  ldd "$RUNTIME_SO" >&2 || true
  fail "native runtime shared library has unresolved dependencies"
fi

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
  SECRET="$("$PYTHON_BIN" - <<'PY'
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
HHS_APPLICATION_VM_PYTHON_BIN=$PYTHON_BIN
HHS_DISABLE_C_AUTOBUILD=1
EOF
chown root:"$SERVICE_USER" /etc/hhs/application-vm.env
chmod 0640 /etc/hhs/application-vm.env

sed \
  -e "s#@@REPOSITORY_ROOT@@#$REPO_ROOT#g" \
  -e "s#@@PYTHON_BIN@@#$PYTHON_BIN#g" \
  "$REPO_ROOT/deployment/ubuntu/application_vm/hhs-application-vm.service.template" \
  > /etc/systemd/system/hhs-application-vm.service

install -m 0755 "$REPO_ROOT/bin/hhs-vm" /usr/local/bin/hhs-vm

set -a
# shellcheck disable=SC1091
source /etc/hhs/application-vm.env
set +a
PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" HHS_DISABLE_C_AUTOBUILD=1 "$PYTHON_BIN" - <<'PY' \
  || fail "application VM import failed with C autobuild disabled"
import hhs_python.runtime.hhs_ctypes_bridge
import hhs_python.runtime.hhs_exact_ctypes_bridge
import hhs_backend.application_vm_api_server
print("HHS_APPLICATION_VM_PREBUILT_NATIVE_IMPORT_VERIFIED")
PY

systemctl daemon-reload
systemctl enable hhs-application-vm.service
systemctl restart hhs-application-vm.service

for _ in $(seq 1 45); do
  if curl --fail --silent "http://$HOST:$PORT/health" >/tmp/hhs-application-vm-health.json; then
    break
  fi
  sleep 1
done
curl --fail --silent "http://$HOST:$PORT/health" >/tmp/hhs-application-vm-health.json \
  || fail "application VM control plane did not become healthy"

"$PYTHON_BIN" - <<'PY'
import json
p=json.load(open("/tmp/hhs-application-vm-health.json"))
assert p["ok"] is True
assert p["security_configured"] is True
assert p["ubuntu"] is True
assert p["ubuntu_desktop_components_present"] is True
assert p["frontend_attached"] is False
assert p["public_mutation_requires_signed_capability"] is True
PY

printf '%s\n' "HHS Ubuntu application VM control plane is healthy."
printf '%s\n' "Loopback: http://$HOST:$PORT"
printf '%s\n' "Public reverse-proxy prefix: $ROOT_PATH"
printf '%s\n' "Python runtime: $PYTHON_BIN"
printf '%s\n' "Issue an operator token locally with:"
printf '%s\n' "  sudo -u $SERVICE_USER hhs-vm token issue --principal operator --scope runtime.mutate"
