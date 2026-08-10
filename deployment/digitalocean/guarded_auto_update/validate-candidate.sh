#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
PYTHON=${HHS_VALIDATE_PYTHON:-python3}
NATIVE=${HHS_VALIDATE_NATIVE:-1}
NODE_TESTS=${HHS_VALIDATE_NODE_TESTS:-1}
BOOT=${HHS_VALIDATE_BOOT:-1}
PORT=${HHS_CANDIDATE_PORT:-18080}
STAGE_TIMEOUT=${HHS_VALIDATE_STAGE_TIMEOUT_SECONDS:-900}
BOOT_TIMEOUT=${HHS_CANDIDATE_BOOT_TIMEOUT_SECONDS:-120}
LOG_FILE=${HHS_CANDIDATE_LOG_FILE:-/tmp/hhs-candidate-${PORT}.log}
PASS205_DB=${HHS_PASS205_CANDIDATE_DB:-/tmp/hhs-pass205-candidate-${PORT}.sqlite3}
PASS205_EVIDENCE=${HHS_PASS205_CANDIDATE_EVIDENCE:-/tmp/PASS205_PRODUCTION_VALIDATION_RECEIPT.json}

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
  deployment/digitalocean/guarded_auto_update/build-runtime-os.sh \
  deployment/digitalocean/guarded_auto_update/validate-candidate.sh \
  deployment/digitalocean/guarded_auto_update/install.sh

python_files=()
for path in \
  hhs_backend/runtime_os_projection.py \
  hhs_backend/runtime_os_visual_server.py \
  hhs_backend/runtime_os_application_server.py \
  hhs_backend/production_visual_server.py \
  hhs_backend/application_ide_server.py \
  hhs_backend/production_ide_server.py \
  hhs_backend/api/repository_history_routes.py \
  hhs_backend/api/pass205_continuation_routes.py \
  hhs_backend/runtime/hhs_pass205_continuation_runtime_v1.py \
  hhs_backend/runtime/hhs_pass205_accelerator_translation_v1.py \
  hhs_python/runtime/hhs_pass205_continuation_bridge.py \
  scripts/pass205_production_validation.py \
  tests/test_runtime_os_production_root.py \
  tests/test_hhs_pass205_continuation_runtime_v1.py; do
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

if [[ -f hhs_runtime/c/hhs_pass205_continuation.c ]]; then
  run_stage "Pass 205 native continuation build" "$PYTHON" -c \
    'from hhs_python.runtime.hhs_pass205_continuation_bridge import build_native_library; print(build_native_library(force=True))'
  [[ -s hhs_runtime/builds/libhhs_pass205_continuation.so ]] || {
    echo "Pass 205 continuation library was not produced" >&2
    exit 1
  }
fi

pytest_targets=()
for path in \
  tests/test_hhs_guarded_auto_update_contract_v1.py \
  tests/test_hhs_full_application_ide_root_v1.py \
  tests/test_hhs_repository_history_surface_v1.py \
  tests/test_hhs_pass205_continuation_runtime_v1.py; do
  [[ -f "$path" ]] && pytest_targets+=("$path")
done
if ((${#pytest_targets[@]})); then
  run_stage "production integration tests" "$PYTHON" -m pytest -q "${pytest_targets[@]}"
fi

if [[ -f scripts/pass205_production_validation.py ]]; then
  rm -f "$PASS205_DB" "$PASS205_DB-wal" "$PASS205_DB-shm" "$PASS205_EVIDENCE"
  run_stage \
    "Pass 205 deterministic production receipt" \
    env PYTHONPATH="$ROOT" HHS_PASS205_DB="$PASS205_DB" \
    "$PYTHON" scripts/pass205_production_validation.py \
      --db "$PASS205_DB" \
      --evidence "$PASS205_EVIDENCE"
  grep -Fq 'HHS_PASS_205_DETERMINISTIC_MULTIMODAL_CONTINUATION_RUNTIME_VERIFIED' "$PASS205_EVIDENCE"
  grep -Fq '1259712' "$PASS205_EVIDENCE"
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
    run_stage "inherited application studio tests" node --test "${node_tests[@]}"
  fi
  popd >/dev/null
fi

# The promoted service serves hhs_gui/dist directly. Candidate validation must
# therefore build the exact TypeScript source before the candidate can pass.
run_stage \
  "canonical Runtime OS production build" \
  bash deployment/digitalocean/guarded_auto_update/build-runtime-os.sh "$ROOT"

if [[ "$BOOT" == "1" ]]; then
  : >"$LOG_FILE"
  HHS_PASS205_DB="$PASS205_DB" "$PYTHON" -m uvicorn hhs_backend.runtime_os_application_server:app \
    --host 127.0.0.1 --port "$PORT" --workers 1 --log-level info \
    >"$LOG_FILE" 2>&1 &
  server_pid=$!
  cleanup() {
    kill "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  }
  fail_with_log() {
    cat "$LOG_FILE" >&2 || true
    cleanup
    exit 1
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
  [[ "$ready" == "1" ]] || fail_with_log

  curl --fail --silent "http://127.0.0.1:${PORT}/" >/tmp/hhs-candidate-root.html || fail_with_log
  grep -Fq 'HHS Visual Runtime OS Workspace' /tmp/hhs-candidate-root.html || fail_with_log
  curl --fail --silent "http://127.0.0.1:${PORT}/api/interface/status" >/tmp/hhs-candidate-interface.json || fail_with_log
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/repository/status" >/tmp/hhs-candidate-repository.json || fail_with_log
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/workspace/session" >/tmp/hhs-candidate-workspace.json || fail_with_log
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/continuation/status" >/tmp/hhs-candidate-pass205.json || fail_with_log
  curl --fail --silent "http://127.0.0.1:${PORT}/api/runtime/continuation/studio" >/tmp/hhs-candidate-pass205-studio.html || fail_with_log

  "$PYTHON" - <<'PY'
import json
from pathlib import Path
for path in (
    "/tmp/hhs-candidate-status.json",
    "/tmp/hhs-candidate-interface.json",
    "/tmp/hhs-candidate-repository.json",
    "/tmp/hhs-candidate-workspace.json",
    "/tmp/hhs-candidate-pass205.json",
):
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"non-object candidate response: {path}")
interface = json.loads(Path("/tmp/hhs-candidate-interface.json").read_text(encoding="utf-8"))
if interface.get("interface") != "HHS_VISUAL_RUNTIME_OS_WORKSPACE":
    raise SystemExit("candidate did not select Runtime OS interface")
if interface.get("legacy_harmonizer_is_public_root") is not False:
    raise SystemExit("candidate re-promoted legacy Harmonizer")
pass205 = json.loads(Path("/tmp/hhs-candidate-pass205.json").read_text(encoding="utf-8"))
payload = pass205.get("payload", pass205)
if payload.get("state_bits") != 5184:
    raise SystemExit("Pass 205 hosted state width mismatch")
if payload.get("hydration_projection_count") != 1259712:
    raise SystemExit("Pass 205 hosted q-address count mismatch")
if payload.get("projection_channel_count") != 32:
    raise SystemExit("Pass 205 hosted projection channel mismatch")
studio = Path("/tmp/hhs-candidate-pass205-studio.html").read_text(encoding="utf-8")
if "VM5184 × G243" not in studio or "Advance committed state" not in studio:
    raise SystemExit("Pass 205 visual studio surface incomplete")
PY

  cleanup
  trap - EXIT
fi

printf 'Candidate validation passed at %s\n' "$(git rev-parse HEAD)"
