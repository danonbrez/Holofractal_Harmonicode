#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPO_ROOT:-/opt/hhs/app}
SOURCE="$REPO_ROOT/deployment/digitalocean/gpu"
INSTALL_ROOT=${HHS_GPU_INSTALL_ROOT:-/usr/local/lib/hhs-gpu}
ENV_FILE=${HHS_GPU_ENV_FILE:-/etc/hhs/pass208-gpu.env}
DROPIN_DIR=/etc/systemd/system/hhs.service.d
DROPIN_FILE="$DROPIN_DIR/40-pass208-gpu.conf"
STATE_ROOT=${HHS_PASS208_STATE_ROOT:-/var/lib/hhs/pass208}
CACHE_ROOT=${HHS_PASS207_CACHE_ROOT:-/var/cache/hhs/pass207}
PYTHON=${HHS_PASS208_PYTHON:-/opt/hhs/venv/bin/python}
PIP=${HHS_PASS208_PIP:-/opt/hhs/venv/bin/pip}
SPEC_ROOT=${HHS_JSON_SPEC_PACKAGE_ROOT:-${1:-}}

[[ $EUID -eq 0 ]] || {
  echo "Run as root on the DigitalOcean GPU Droplet." >&2
  exit 2
}
[[ -d "$REPO_ROOT/.git" ]] || {
  echo "Repository not found at $REPO_ROOT" >&2
  exit 3
}
[[ -d "$SOURCE" ]] || {
  echo "GPU deployment source not found at $SOURCE" >&2
  exit 4
}
[[ -n "$SPEC_ROOT" && -d "$SPEC_ROOT" ]] || {
  echo "Provide the 23-file JSON specification package root as HHS_JSON_SPEC_PACKAGE_ROOT or argument 1." >&2
  exit 5
}
[[ -x "$PYTHON" ]] || {
  echo "HHS Python virtual environment not found at $PYTHON" >&2
  exit 6
}

bash -n \
  "$SOURCE/install.sh" \
  "$SOURCE/hhs-gpu-preflight.sh" \
  "$SOURCE/post-merge.sh"
"$PYTHON" -m py_compile \
  "$SOURCE/validate-json-spec-package.py" \
  "$REPO_ROOT/hhs_backend/runtime/hhs_pass208_gpu_branch_manifold_v1.py" \
  "$REPO_ROOT/hhs_backend/api/pass208_gpu_manifold_routes.py"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  clinfo \
  ocl-icd-libopencl1 \
  pciutils

if ! "$PYTHON" -c 'import jsonschema' >/dev/null 2>&1; then
  [[ -x "$PIP" ]] || {
    echo "pip missing at $PIP and jsonschema is not installed" >&2
    exit 7
  }
  "$PIP" install --disable-pip-version-check 'jsonschema>=4.18,<5'
fi

GPU_VENDOR=
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/tmp/hhs-gpu-list.txt 2>&1; then
  GPU_VENDOR=nvidia
elif command -v rocminfo >/dev/null 2>&1 && rocminfo >/tmp/hhs-gpu-list.txt 2>&1; then
  GPU_VENDOR=amd
else
  echo "No operational NVIDIA or AMD GPU runtime was detected." >&2
  echo "Use a DigitalOcean GPU Droplet with the AI/ML-ready image, or install the vendor driver before running this installer." >&2
  lspci -nn | grep -Ei 'vga|3d|display' >&2 || true
  exit 8
fi

clinfo -l >/tmp/hhs-opencl-list.txt 2>&1 || {
  cat /tmp/hhs-opencl-list.txt >&2 || true
  echo "OpenCL ICD discovery failed." >&2
  exit 9
}
grep -Eq 'Platform|Device' /tmp/hhs-opencl-list.txt || {
  cat /tmp/hhs-opencl-list.txt >&2 || true
  echo "OpenCL reports no usable platform or device." >&2
  exit 10
}

install -d -m 0755 "$INSTALL_ROOT" /etc/hhs "$DROPIN_DIR"
install -d -o hhs -g hhs -m 0750 "$STATE_ROOT" "$CACHE_ROOT"
install -m 0755 "$SOURCE/hhs-gpu-preflight.sh" "$INSTALL_ROOT/hhs-gpu-preflight.sh"
install -m 0755 "$SOURCE/post-merge.sh" "$INSTALL_ROOT/post-merge.sh"
install -m 0755 "$SOURCE/validate-json-spec-package.py" "$INSTALL_ROOT/validate-json-spec-package.py"

for group in video render; do
  if getent group "$group" >/dev/null 2>&1; then
    usermod -a -G "$group" hhs
  fi
done

set_env() {
  local key=$1
  local value=$2
  local temporary
  temporary=$(mktemp)
  if [[ -f "$ENV_FILE" ]]; then
    grep -Ev "^${key}=" "$ENV_FILE" >"$temporary" || true
  fi
  printf '%s=%s\n' "$key" "$value" >>"$temporary"
  install -o root -g hhs -m 0640 "$temporary" "$ENV_FILE"
  rm -f "$temporary"
}

set_env HHS_PASS208_GPU_ENABLED 1
set_env HHS_PASS207_GPU_BACKEND OPENCL
set_env HHS_PASS207_REQUIRE_PHYSICAL_GPU 1
set_env HHS_PASS207_GPU_DEVICE_INDEX "${HHS_PASS207_GPU_DEVICE_INDEX:-0}"
set_env HHS_PASS208_MAX_BRANCHES "${HHS_PASS208_MAX_BRANCHES:-256}"
set_env HHS_PASS207_CACHE_BYTES "${HHS_PASS207_CACHE_BYTES:-536870912}"
set_env HHS_PASS207_CACHE_ENTRIES "${HHS_PASS207_CACHE_ENTRIES:-512}"
set_env HHS_DISABLE_PASS207_C_AUTOBUILD 1
set_env HHS_PASS208_STATE_ROOT "$STATE_ROOT"
set_env HHS_PASS208_PREFLIGHT_RECEIPT "$STATE_ROOT/PASS208_GPU_PREFLIGHT_RECEIPT.json"
set_env HHS_PASS208_SPEC_RECEIPT "$STATE_ROOT/PASS208_JSON_SPEC_VALIDATION_RECEIPT.json"
set_env HHS_JSON_SPEC_PACKAGE_ROOT "$(realpath "$SPEC_ROOT")"
set_env HHS_JSON_SPEC_MANIFEST "${HHS_JSON_SPEC_MANIFEST:-}"
set_env HHS_JSON_SPEC_EXPECTED_FILES "${HHS_JSON_SPEC_EXPECTED_FILES:-23}"
set_env HHS_JSON_SPEC_EXPECTED_EXAMPLES "${HHS_JSON_SPEC_EXPECTED_EXAMPLES:-4}"
set_env HHS_REPOSITORY_ROOT "$REPO_ROOT"
set_env HHS_PASS208_PYTHON "$PYTHON"

cat >"$DROPIN_FILE" <<EOF
[Unit]
After=network-online.target
Wants=network-online.target

[Service]
EnvironmentFile=$ENV_FILE
ExecStartPre=$INSTALL_ROOT/hhs-gpu-preflight.sh
LimitMEMLOCK=infinity
ReadWritePaths=$STATE_ROOT $CACHE_ROOT
EOF
chmod 0644 "$DROPIN_FILE"

cd "$REPO_ROOT"
PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
"$PYTHON" -c \
  'from hhs_python.runtime.hhs_pass207_gpu_driver_native import build_native_library; print(build_native_library(force=True))'
[[ -s hhs_runtime/builds/libhhs_pass207_gpu_driver.so ]] || {
  echo "Pass 207 native GPU library build failed" >&2
  exit 11
}
chmod 0755 hhs_runtime/builds/libhhs_pass207_gpu_driver.so

if [[ -f /etc/hhs/guarded-update.env ]]; then
  guarded_tmp=$(mktemp)
  grep -Ev '^HHS_POST_MERGE_COMMAND=|^HHS_ROLLBACK_COMMAND=|^HHS_VALIDATE_GPU=' \
    /etc/hhs/guarded-update.env >"$guarded_tmp" || true
  cat >>"$guarded_tmp" <<EOF
HHS_VALIDATE_GPU=1
HHS_POST_MERGE_COMMAND=$INSTALL_ROOT/post-merge.sh
HHS_ROLLBACK_COMMAND=$INSTALL_ROOT/post-merge.sh
EOF
  install -o root -g root -m 0640 "$guarded_tmp" /etc/hhs/guarded-update.env
  rm -f "$guarded_tmp"
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
"$INSTALL_ROOT/hhs-gpu-preflight.sh"

systemctl daemon-reload
systemctl restart hhs.service

ready=0
for _ in $(seq 1 "${HHS_GPU_HEALTH_TIMEOUT_SECONDS:-180}"); do
  if curl -fsS http://127.0.0.1:8080/api/runtime/gpu-manifold/status \
    >/tmp/hhs-pass208-hosted-status.json 2>/dev/null; then
    ready=1
    break
  fi
  if systemctl is-failed --quiet hhs.service; then
    break
  fi
  sleep 1
done
if [[ "$ready" != 1 ]]; then
  systemctl status hhs.service --no-pager --full >&2 || true
  journalctl -u hhs.service -n 200 --no-pager >&2 || true
  exit 12
fi

"$PYTHON" - <<'PY'
import json
from pathlib import Path
value = json.loads(Path("/tmp/hhs-pass208-hosted-status.json").read_text(encoding="utf-8"))
payload = value.get("payload", value)
driver = ((payload.get("driver") or {}).get("driver") or {})
failures = []
if not payload.get("enabled"):
    failures.append("MANIFOLD_DISABLED")
if not driver.get("physical_gpu"):
    failures.append("PHYSICAL_GPU_INACTIVE")
if driver.get("backend_name") != "OPENCL_GPU":
    failures.append("OPENCL_GPU_INACTIVE")
if driver.get("logical_lanes_per_batch") != 5184:
    failures.append("LANE_COUNT_MISMATCH")
if failures:
    raise SystemExit(",".join(failures))
print(json.dumps(payload, indent=2, sort_keys=True))
PY

cat <<EOF
Pass 208 DigitalOcean GPU deployment enabled.

Vendor:       $GPU_VENDOR
Environment:  $ENV_FILE
Drop-in:      $DROPIN_FILE
State:        $STATE_ROOT
Cache:        $CACHE_ROOT
Specification package: $(realpath "$SPEC_ROOT")

Inspect:
  systemctl status hhs.service --no-pager --full
  journalctl -u hhs.service -n 200 --no-pager
  curl -fsS http://127.0.0.1:8080/api/runtime/gpu-manifold/status | python3 -m json.tool
  cat $STATE_ROOT/PASS208_GPU_PREFLIGHT_RECEIPT.json
  cat $STATE_ROOT/PASS208_JSON_SPEC_VALIDATION_RECEIPT.json
EOF
