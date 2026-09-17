#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPOSITORY_ROOT:-${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}}
PROJECTOR_VENV=${HHS_P219_PROJECTOR_VENV:-/opt/hhs/pass219-projector-venv}
PROJECTOR_PYTHON="$PROJECTOR_VENV/bin/python"
REQUIREMENTS=${HHS_P219_PROJECTOR_REQUIREMENTS:-$REPO_ROOT/requirements-pass219-projector.txt}
CACHE_ROOT=${HF_HOME:-${HHS_P219_PROJECTOR_CACHE_ROOT:-/var/lib/hhs/models/huggingface}}
PIP_CACHE_ROOT=${HHS_P219_PROJECTOR_PIP_CACHE_ROOT:-/var/cache/hhs/pass219-projector-pip}
SERVICE_USER=${HHS_PRODUCTION_SERVICE_USER:-hhs}
SERVICE_GROUP=${HHS_PRODUCTION_SERVICE_GROUP:-hhs}
WARM_CACHE=${HHS_P219_PROJECTOR_WARM_CACHE:-1}
MARKER="$PROJECTOR_VENV/.hhs-pass219-projector-requirements.sha256"

[[ -f "$REQUIREMENTS" ]] || { echo "missing Pass 219 projector requirements: $REQUIREMENTS" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 3; }
command -v sha256sum >/dev/null || { echo "sha256sum is required" >&2; exit 4; }
[[ "$WARM_CACHE" == "0" || "$WARM_CACHE" == "1" ]] || { echo "HHS_P219_PROJECTOR_WARM_CACHE must be 0 or 1" >&2; exit 5; }

requirements_sha=$(sha256sum "$REQUIREMENTS" | awk '{print $1}')
installed_sha=""
[[ -f "$MARKER" ]] && installed_sha=$(tr -d '[:space:]' < "$MARKER")

runtime_ok=0
if [[ -x "$PROJECTOR_PYTHON" && "$installed_sha" == "$requirements_sha" ]]; then
  if "$PROJECTOR_PYTHON" - <<'PY' >/dev/null 2>&1
from importlib.metadata import version
assert version("sentence-transformers") == "5.1.1"
import sentence_transformers  # noqa: F401
PY
  then
    runtime_ok=1
  fi
fi

if [[ "$runtime_ok" != "1" ]]; then
  echo "HHS_PASS219_PROJECTOR_RUNTIME_INSTALL=1"
  rm -rf "$PROJECTOR_VENV"
  python3 -m venv "$PROJECTOR_VENV"
  install -d -m 0755 "$PIP_CACHE_ROOT"
  PIP_CACHE_DIR="$PIP_CACHE_ROOT" "$PROJECTOR_VENV/bin/pip" install --disable-pip-version-check --no-input --upgrade pip
  PIP_CACHE_DIR="$PIP_CACHE_ROOT" "$PROJECTOR_VENV/bin/pip" install --disable-pip-version-check --no-input -r "$REQUIREMENTS"
  printf '%s\n' "$requirements_sha" > "$MARKER"
  chmod 0644 "$MARKER"
else
  echo "HHS_PASS219_PROJECTOR_RUNTIME_REUSED=1"
fi

"$PROJECTOR_PYTHON" - <<'PY'
from importlib.metadata import version
assert version("sentence-transformers") == "5.1.1"
print("HHS_PASS219_PROJECTOR_RUNTIME_VERSION=5.1.1")
PY

install -d -o "$SERVICE_USER" -g "$SERVICE_GROUP" -m 0750 "$CACHE_ROOT"

if [[ "$WARM_CACHE" == "1" ]]; then
  warm_text='HHS Pass 219 production projector warm cache.'
  warm_sha=$(printf '%s' "$warm_text" | sha256sum | awk '{print $1}')
  warm_b64=$(printf '%s' "$warm_text" | base64 -w0)
  output=$(mktemp /tmp/hhs-pass219-projector-warm.XXXXXX.json)
  trap 'rm -f "$output"' EXIT
  cat <<JSON | env \
    PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
    HF_HOME="$CACHE_ROOT" \
    HF_HUB_DISABLE_TELEMETRY=1 \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    "$PROJECTOR_PYTHON" -m hhs_runtime.hhs_pass219_approved_projector_execution_v1 --input - --device cpu > "$output"
{"profile_id":"MULTILINGUAL_MPNET_TEXT_V1","source_b64":"$warm_b64","source_sha256":"$warm_sha","source_language":"en","source_modality":"TEXT","pivot_text":"HHS Pass 219 production projector warm cache.","pivot_language":"en","semantic_labels":["warm-cache"],"translation_chain":["en"]}
JSON
  python3 - "$output" <<'PY'
import json, sys
from pathlib import Path
payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert payload["projector_id"] == "EXTERNAL_EVIDENCE_V1", payload
assert payload["projector_profile_id"] == "MULTILINGUAL_MPNET_TEXT_V1", payload
assert payload["candidate_only"] is True, payload
assert len(payload["execution_record_sha256"]) == 64, payload
print("HHS_PASS219_PROJECTOR_WARM_CACHE_VERIFIED=1")
PY
  rm -f "$output"
  trap - EXIT
  chown -R "$SERVICE_USER:$SERVICE_GROUP" "$CACHE_ROOT"
fi

printf 'HHS_PASS219_PROJECTOR_PYTHON=%s\n' "$PROJECTOR_PYTHON"
printf 'HHS_PASS219_PROJECTOR_CACHE_ROOT=%s\n' "$CACHE_ROOT"
