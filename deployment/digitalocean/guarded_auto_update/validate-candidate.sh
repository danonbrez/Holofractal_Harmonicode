#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
PYTHON=${HHS_VALIDATE_PYTHON:-python3}
NATIVE=${HHS_VALIDATE_NATIVE:-1}
NODE_TESTS=${HHS_VALIDATE_NODE_TESTS:-1}
BOOT=${HHS_VALIDATE_BOOT:-1}
BROWSER=${HHS_VALIDATE_BROWSER:-0}
PORT=${HHS_CANDIDATE_PORT:-18080}
STAGE_TIMEOUT=${HHS_VALIDATE_STAGE_TIMEOUT_SECONDS:-900}
BOOT_TIMEOUT=${HHS_CANDIDATE_BOOT_TIMEOUT_SECONDS:-120}
LOG_FILE=${HHS_CANDIDATE_LOG_FILE:-/tmp/hhs-candidate-${PORT}.log}

cd "$ROOT"

run_stage() {
  local name=$1
  shift
  printf '==> %s\n' "$name"
  timeout --signal=TERM --kill-after=30s "$STAGE_TIMEOUT" "$@"
}

git diff --check
git status --short

run_stage "shell syntax" bash -n \
  deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh \
  deployment/digitalocean/guarded_auto_update/validate-candidate.sh \
  deployment/digitalocean/guarded_auto_update/install.sh

python_files=()
for path in \
  hhs_backend/application_ide_server.py \
  hhs_backend/production_ide_server.py \
  hhs_backend/api/repository_history_routes.py \
  applications/holofractal_harmonizer/ux_lab/full_application_smoke.py; do
  [[ -f "$path" ]] && python_files+=("$path")
done
if ((${#python_files[@]})); then
  run_stage "python compilation" "$PYTHON" -m py_compile "${python_files[@]}"
fi

if [[ "$NATIVE" == "1" && -f bin/post_compile ]]; then
  run_stage "native authority build" bash bin/post_compile
  [[ -s hhs_runtime/builds/libhhs_runtime.so ]] || {
    echo "native runtime library was not produced" >&2
    exit 1
  }
fi

pytest_targets=()
for path in \
  tests/test_hhs_guarded_auto_update_contract_v1.py \
  tests/test_hhs_full_application_ide_root_v1.py \
  tests/test_hhs_repository_history_surface_v1.py; do
  [[ -f "$path" ]] && pytest_targets+=("$path")
done
if ((${#pytest_targets[@]})); then
  run_stage "production integration tests" "$PYTHON" -m pytest -q "${pytest_targets[@]}"
fi

if [[ "$NODE_TESTS" == "1" && -d applications/holofractal_harmonizer && -x "$(command -v node || true)" ]]; then
  pushd applications/holofractal_harmonizer >/dev/null
  node_files=(
    src/application-templates.mjs
    src/application-studio.mjs
    src/deployable-app-compiler.mjs
    src/integrated-assistant.mjs
    src/integrated-workbench.mjs
    src/intuitive-ide.mjs
  )
  for path in "${node_files[@]}"; do
    [[ -f "$path" ]] && run_stage "node syntax $path" node --check "$path"
  done
  node_tests=()
  for path in \
    tests/application.studio.test.mjs \
    tests/intuitive.ide.test.mjs \
    tests/integrated.workbench.test.mjs \
    tests/project.lifecycle.test.mjs; do
    [[ -f "$path" ]] && node_tests+=("$path")
  done
  if ((${#node_tests[@]})); then
    run_stage "application studio tests" node --test "${node_tests[@]}"
  fi
  popd >/dev/null
fi

if [[ "$BOOT" == "1" ]]; then
  : >"$LOG_FILE"
  "$PYTHON" -m uvicorn hhs_backend.application_ide_server:app \
    --host 127.0.0.1 --port "$PORT" --workers 1 --log-level info \
    >"$LOG_FILE" 2>&1 &
  server_pid=$!
  cleanup() {
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  }
  trap cleanup EXIT

  ready=0
  for _ in $(seq 1 "$BOOT_TIMEOUT"); do
    if curl --fail --silent "http://127.0.0.1:${PORT}/api/system/status" >/tmp/hhs-candidate-status.json 2>/dev/null; then
      ready=1
      break
    fi
    if ! kill -0 "$server_pid" 2>/dev/null; then
      break
    fi
    sleep 1
  done
  if [[ "$ready" != "1" ]]; then
    cat "$LOG_FILE" >&2
    exit 1
  fi

  curl --fail --silent "http://127.0.0.1:${PORT}/" >/tmp/hhs-candidate-root.html
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/repository/status" >/tmp/hhs-candidate-repository.json
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/workspace/session" >/tmp/hhs-candidate-workspace.json
  "$PYTHON" - <<'PY'
import json
from pathlib import Path
for path in (
    "/tmp/hhs-candidate-status.json",
    "/tmp/hhs-candidate-repository.json",
    "/tmp/hhs-candidate-workspace.json",
):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"non-object candidate response: {path}")
PY

  if [[ "$BROWSER" == "1" && -f applications/holofractal_harmonizer/ux_lab/full_application_smoke.py ]]; then
    HHS_FULL_APPLICATION_IDE_URL="http://127.0.0.1:${PORT}" \
      run_stage "browser acceptance" "$PYTHON" applications/holofractal_harmonizer/ux_lab/full_application_smoke.py
  fi

  cleanup
  trap - EXIT
fi

printf 'Candidate validation passed at %s\n' "$(git rev-parse HEAD)"
