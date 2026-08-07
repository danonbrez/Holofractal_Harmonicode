#!/usr/bin/env bash
set -Eeuo pipefail

# Repair the DigitalOcean production serving path without re-running hydration.
# This script is intentionally idempotent: it installs a systemd drop-in for the
# one canonical HTTP service, disables the known duplicate Pass 196 unit when it
# exists, and verifies the bounded bootstrap gateway before returning success.

HHS_APP_ROOT="${HHS_APP_ROOT:-/opt/hhs/app}"
HHS_SERVICE="${HHS_SERVICE:-hhs.service}"
HHS_RUNTIME_PYTHON="${HHS_RUNTIME_PYTHON:-/opt/hhs/runtime-venv/bin/python}"
HHS_HOST="${HHS_HOST:-127.0.0.1}"
HHS_PORT="${HHS_PORT:-8080}"
HHS_READY_TIMEOUT_SECONDS="${HHS_READY_TIMEOUT_SECONDS:-180}"
HHS_STATE_ROOT="${HHS_STATE_ROOT:-/var/lib/hhs/runtime-bootstrap}"
HHS_DUPLICATE_SERVICE="${HHS_DUPLICATE_SERVICE:-hhs-pass196-integrated-environment.service}"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

note() {
  printf '\n==> %s\n' "$*"
}

[[ "${EUID}" -eq 0 ]] || fail "run as root"
[[ -d "${HHS_APP_ROOT}/.git" ]] || fail "repository not found at ${HHS_APP_ROOT}"
[[ -x "${HHS_RUNTIME_PYTHON}" ]] || fail "runtime Python not executable: ${HHS_RUNTIME_PYTHON}"
command -v systemctl >/dev/null 2>&1 || fail "systemctl is required"
command -v curl >/dev/null 2>&1 || fail "curl is required"
command -v node >/dev/null 2>&1 || fail "node is required"

cd "${HHS_APP_ROOT}"

note "Validating the production gateway and critical browser modules"
"${HHS_RUNTIME_PYTHON}" -m py_compile \
  hhs_backend/cached_visual_server.py \
  hhs_backend/production_visual_server.py \
  hhs_backend/runtime/live_cognition_runtime_v1.py
node --check applications/holofractal_harmonizer/src/production-startup-coordinator.mjs
node --check applications/holofractal_harmonizer/src/pass176-early-bootstrap.mjs
node --check applications/holofractal_harmonizer/src/gui-reliability.mjs
node --check applications/holofractal_harmonizer/src/deployment-health.mjs
node --check applications/holofractal_harmonizer/src/visual-ide.mjs

service_user="$(systemctl show "${HHS_SERVICE}" -p User --value 2>/dev/null || true)"
[[ -n "${service_user}" ]] || service_user=root

note "Preparing writable bootstrap-cache state"
install -d -m 0755 /etc/systemd/system/"${HHS_SERVICE}".d
install -d -m 0750 "${HHS_STATE_ROOT}"
if id "${service_user}" >/dev/null 2>&1; then
  chown "${service_user}:${service_user}" "${HHS_STATE_ROOT}"
fi

note "Installing the canonical production service override"
cat >/etc/systemd/system/"${HHS_SERVICE}".d/30-production-interface.conf <<EOF
[Service]
WorkingDirectory=${HHS_APP_ROOT}
Environment=HHS_COGNITION_AUTO_TICK=0
Environment=HHS_PASS174_BOOT_TIMEOUT_SECONDS=180
Environment=HHS_RUNTIME_STATUS_PROBE=1
Environment=HHS_RUNTIME_STATUS_CACHE=${HHS_STATE_ROOT}/status-cache.json
ExecStart=
ExecStart=${HHS_RUNTIME_PYTHON} -m uvicorn hhs_backend.production_visual_server:app --host ${HHS_HOST} --port ${HHS_PORT} --workers 1
EOF

systemctl daemon-reload

if systemctl list-unit-files "${HHS_DUPLICATE_SERVICE}" --no-legend 2>/dev/null | grep -q "${HHS_DUPLICATE_SERVICE}"; then
  note "Disabling duplicate Pass 196 HTTP ownership"
  systemctl disable --now "${HHS_DUPLICATE_SERVICE}" >/dev/null 2>&1 || true
fi

note "Restarting the single canonical HHS service"
systemctl restart "${HHS_SERVICE}"
systemctl is-active --quiet "${HHS_SERVICE}" || {
  systemctl status "${HHS_SERVICE}" --no-pager --full || true
  fail "${HHS_SERVICE} did not become active"
}

exec_start="$(systemctl show "${HHS_SERVICE}" -p ExecStart --value)"
effective_environment="$(systemctl show "${HHS_SERVICE}" -p Environment --value)"
[[ "${exec_start}" == *"hhs_backend.production_visual_server:app"* ]] \
  || fail "effective ExecStart is not production_visual_server"
[[ "${effective_environment}" == *"HHS_COGNITION_AUTO_TICK=0"* ]] \
  || fail "HHS_COGNITION_AUTO_TICK=0 is not effective"
[[ "${effective_environment}" == *"HHS_PASS174_BOOT_TIMEOUT_SECONDS=180"* ]] \
  || fail "HHS_PASS174_BOOT_TIMEOUT_SECONDS=180 is not effective"

base_url="http://${HHS_HOST}:${HHS_PORT}"
ready=0
for ((attempt=1; attempt<=HHS_READY_TIMEOUT_SECONDS; attempt+=1)); do
  if curl --max-time 2 -fsS "${base_url}/api/system/status" >/tmp/hhs-system-status.json 2>/dev/null; then
    ready=1
    break
  fi
  if systemctl is-failed --quiet "${HHS_SERVICE}"; then
    break
  fi
  sleep 1
done

if [[ "${ready}" != "1" ]]; then
  systemctl status "${HHS_SERVICE}" --no-pager --full || true
  journalctl -u "${HHS_SERVICE}" -n 160 --no-pager || true
  fail "HHS API did not become ready within ${HHS_READY_TIMEOUT_SECONDS}s"
fi

note "Verifying non-blocking runtime bootstrap"
curl --max-time 5 -fsS "${base_url}/api/runtime/bootstrap/status" >/tmp/hhs-runtime-bootstrap-status.json
curl --max-time 5 -fsSI "${base_url}/" \
  | grep -qi '^x-hhs-runtime-bootstrap: v1' \
  || fail "root response is missing the runtime-bootstrap gateway header"

note "Effective service state"
printf 'Service: %s\n' "${HHS_SERVICE}"
printf 'Entrypoint: %s\n' "${exec_start}"
printf 'Cognition auto tick: disabled\n'
printf 'Pass 174 readiness window: 180s\n'
printf 'Bootstrap status:\n'
cat /tmp/hhs-runtime-bootstrap-status.json
printf '\n\nTop HHS-related CPU consumers after restart:\n'
ps -eo pid,ppid,pcpu,pmem,etime,cmd --sort=-pcpu \
  | grep -E '[u]vicorn|[h]hs_backend|[p]ython.*hhs' \
  | head -n 12 || true

printf '\nHHS_DIGITALOCEAN_INTERFACE_REPAIR_VERIFIED\n'
