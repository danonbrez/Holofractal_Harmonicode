#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPO_ROOT:-/opt/hhs/app}
SOURCE="$REPO_ROOT/deployment/digitalocean/llm"
INSTALL_ROOT=${HHS_LLM_INSTALL_ROOT:-/usr/local/lib/hhs-llm}
ENV_FILE=${HHS_PASS209_ENV_FILE:-/etc/hhs/pass209-llm.env}
LITERT_VENV=${HHS_LITERT_LM_VENV:-/opt/hhs/litert-lm}
LITERT_STATE_ROOT=${LITERT_LM_DIR:-/var/lib/hhs/litert-lm}
STATE_ROOT=${HHS_PASS209_STATE_ROOT:-/var/lib/hhs/pass209}
DROPIN_DIR=/etc/systemd/system/hhs.service.d
DROPIN_FILE="$DROPIN_DIR/50-pass209-llm.conf"
PYTHON=${HHS_PASS209_PYTHON:-/opt/hhs/venv/bin/python}
LITERT_VERSION=${HHS_LITERT_LM_VERSION:-0.14.0}
GEMMA_REPOSITORY=${HHS_GEMMA4_REPOSITORY:-litert-community/gemma-4-E2B-it-litert-lm}
GEMMA_FILE=${HHS_GEMMA4_FILE:-gemma-4-E2B-it.litertlm}
GEMMA_MODEL=${HHS_LITERT_LM_MODEL:-gemma-4-E2B-it}
GEMMA_SHA256=${HHS_GEMMA4_SHA256:-181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c}
KIMI_MODEL=${HHS_KIMI_K3_MODEL:-kimi-k3}
KIMI_BASE_URL=${HHS_KIMI_K3_BASE_URL:-https://api.moonshot.ai/v1}

[[ $EUID -eq 0 ]] || {
  echo "Run as root on the DigitalOcean HHS host." >&2
  exit 2
}
[[ -d "$REPO_ROOT/.git" ]] || {
  echo "Repository not found at $REPO_ROOT" >&2
  exit 3
}
[[ -d "$SOURCE" ]] || {
  echo "Pass 209 deployment source not found at $SOURCE" >&2
  exit 4
}
[[ -x "$PYTHON" ]] || {
  echo "HHS Python virtual environment not found at $PYTHON" >&2
  exit 5
}
id hhs >/dev/null 2>&1 || {
  echo "Required service user 'hhs' does not exist" >&2
  exit 6
}

API_KEY=${MOONSHOT_API_KEY:-${HHS_KIMI_K3_API_KEY:-}}
if [[ -z "$API_KEY" && -r "$ENV_FILE" ]]; then
  API_KEY=$(sed -n -E 's/^(MOONSHOT_API_KEY|HHS_KIMI_K3_API_KEY)=([^[:space:]]+)$/\2/p' "$ENV_FILE" | head -n 1)
fi
[[ -n "$API_KEY" ]] || {
  echo "Set MOONSHOT_API_KEY before running this installer." >&2
  exit 7
}
if [[ "$API_KEY" =~ [[:space:]'"] ]]; then
  echo "MOONSHOT_API_KEY contains unsupported whitespace or quote characters" >&2
  exit 8
fi

bash -n \
  "$SOURCE/install.sh" \
  "$SOURCE/hhs-llm-preflight.sh" \
  "$SOURCE/post-merge.sh"
"$PYTHON" -m py_compile \
  "$REPO_ROOT/hhs_backend/runtime/hhs_kimi_k3_agentic_assistant_v1.py" \
  "$REPO_ROOT/hhs_backend/runtime/hhs_pass209_native_agi_optimizer_v1.py" \
  "$REPO_ROOT/hhs_backend/runtime/hhs_pass209_production_assistant_v1.py" \
  "$REPO_ROOT/hhs_backend/api/pass209_llm_orchestrator_routes.py" \
  "$REPO_ROOT/hhs_backend/api/litert_lm_assistant_routes.py" \
  "$REPO_ROOT/scripts/pass209_native_agi_optimizer_worker.py"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  python3-venv

install -d -m 0755 /etc/hhs "$INSTALL_ROOT" "$DROPIN_DIR"
install -d -o hhs -g hhs -m 0750 "$LITERT_STATE_ROOT" "$STATE_ROOT"

if [[ ! -x "$LITERT_VENV/bin/python" ]]; then
  python3 -m venv "$LITERT_VENV"
fi
"$LITERT_VENV/bin/python" -m pip install --disable-pip-version-check --upgrade pip
"$LITERT_VENV/bin/python" -m pip install --disable-pip-version-check "litert-lm==$LITERT_VERSION"

install -m 0755 "$SOURCE/hhs-llm-preflight.sh" "$INSTALL_ROOT/hhs-llm-preflight.sh"
install -m 0755 "$SOURCE/post-merge.sh" "$INSTALL_ROOT/post-merge.sh"
install -m 0644 "$SOURCE/hhs-litert-lm-gemma4.service" /etc/systemd/system/hhs-litert-lm-gemma4.service
install -m 0644 "$SOURCE/hhs-native-agi-optimizer.service" /etc/systemd/system/hhs-native-agi-optimizer.service

model_matches() {
  HHS_MODEL_ROOT="$LITERT_STATE_ROOT" HHS_MODEL_SHA="$GEMMA_SHA256" \
  "$LITERT_VENV/bin/python" - <<'PY'
import hashlib
import os
from pathlib import Path
root = Path(os.environ["HHS_MODEL_ROOT"])
expected = os.environ["HHS_MODEL_SHA"].lower()
for path in sorted(root.rglob("*.litertlm")):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest().lower() == expected:
        print(path)
        raise SystemExit(0)
raise SystemExit(1)
PY
}

if ! matching_model=$(model_matches); then
  echo "Importing the pinned LiteRT-LM Gemma 4 fallback model..."
  sudo -u hhs env \
    HOME=/var/lib/hhs \
    LITERT_LM_DIR="$LITERT_STATE_ROOT" \
    HF_TOKEN="${HF_TOKEN:-}" \
    "$LITERT_VENV/bin/litert-lm" import \
      --from-huggingface-repo "$GEMMA_REPOSITORY" \
      "$GEMMA_FILE" \
      "$GEMMA_MODEL"
  matching_model=$(model_matches) || {
    echo "Imported Gemma model failed SHA-256 verification" >&2
    exit 9
  }
fi
printf 'Verified Gemma model: %s\n' "$matching_model"
chown -R hhs:hhs "$LITERT_STATE_ROOT" "$STATE_ROOT"
chmod -R go-rwx "$LITERT_STATE_ROOT" "$STATE_ROOT"

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

set_env HHS_KIMI_K3_ENABLED 1
set_env HHS_KIMI_K3_BASE_URL "$KIMI_BASE_URL"
set_env HHS_KIMI_K3_MODEL "$KIMI_MODEL"
set_env MOONSHOT_API_KEY "$API_KEY"
set_env HHS_KIMI_K3_REASONING_EFFORT max
set_env HHS_KIMI_K3_TEMPERATURE 1.0
set_env HHS_KIMI_K3_TOP_P 1.0
set_env HHS_KIMI_K3_MAX_COMPLETION_TOKENS "${HHS_KIMI_K3_MAX_COMPLETION_TOKENS:-32768}"
set_env HHS_KIMI_K3_MAX_TOOL_ROUNDS "${HHS_KIMI_K3_MAX_TOOL_ROUNDS:-8}"
set_env HHS_KIMI_K3_MAX_TOOL_CALLS_PER_ROUND "${HHS_KIMI_K3_MAX_TOOL_CALLS_PER_ROUND:-32}"
set_env HHS_KIMI_K3_MAX_PARALLEL_TOOLS "${HHS_KIMI_K3_MAX_PARALLEL_TOOLS:-8}"
set_env HHS_KIMI_K3_TIMEOUT_SECONDS "${HHS_KIMI_K3_TIMEOUT_SECONDS:-7200}"
set_env HHS_LITERT_LM_BASE_URL http://127.0.0.1:9379/v1
set_env HHS_LITERT_LM_MODEL "$GEMMA_MODEL"
set_env HHS_LITERT_LM_BACKEND cpu
set_env HHS_LITERT_LM_TIMEOUT_SECONDS "${HHS_LITERT_LM_TIMEOUT_SECONDS:-300}"
set_env HHS_LITERT_LM_MAX_OUTPUT_TOKENS "${HHS_LITERT_LM_MAX_OUTPUT_TOKENS:-4096}"
set_env HHS_LITERT_LM_TEMPERATURE "${HHS_LITERT_LM_TEMPERATURE:-0.2}"
set_env HHS_LITERT_LM_TOP_P "${HHS_LITERT_LM_TOP_P:-0.95}"
set_env HHS_LITERT_LM_TOP_K "${HHS_LITERT_LM_TOP_K:-40}"
set_env HHS_LITERT_LM_SEED 72
set_env LITERT_LM_DIR "$LITERT_STATE_ROOT"
set_env HHS_PASS209_OPTIMIZER_DB "$STATE_ROOT/native_agi_optimizer.sqlite3"
set_env HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC "${HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC:-1}"
set_env HHS_PASS209_STATE_ROOT "$STATE_ROOT"
set_env HHS_PASS209_PREFLIGHT_RECEIPT "$STATE_ROOT/PASS209_LLM_PREFLIGHT_RECEIPT.json"
set_env HHS_REPOSITORY_ROOT "$REPO_ROOT"

cat >"$DROPIN_FILE" <<EOF
[Unit]
After=hhs-litert-lm-gemma4.service
Wants=hhs-litert-lm-gemma4.service

[Service]
EnvironmentFile=$ENV_FILE
ExecStartPre=$INSTALL_ROOT/hhs-llm-preflight.sh
ReadWritePaths=$STATE_ROOT $LITERT_STATE_ROOT
EOF
chmod 0644 "$DROPIN_FILE"

if [[ -f /etc/hhs/guarded-update.env ]]; then
  guarded_tmp=$(mktemp)
  grep -Ev \
    '^HHS_SYSTEMD_UNITS=|^HHS_POST_MERGE_COMMAND=|^HHS_ROLLBACK_COMMAND=|^HHS_HEALTH_URLS=' \
    /etc/hhs/guarded-update.env >"$guarded_tmp" || true
  cat >>"$guarded_tmp" <<EOF
HHS_SYSTEMD_UNITS=hhs-litert-lm-gemma4.service hhs.service hhs-native-agi-optimizer.service
HHS_POST_MERGE_COMMAND=$INSTALL_ROOT/post-merge.sh
HHS_ROLLBACK_COMMAND=$INSTALL_ROOT/post-merge.sh
HHS_HEALTH_URLS=http://127.0.0.1:8080/api/system/status http://127.0.0.1:8080/api/assistant/health
EOF
  install -o root -g root -m 0640 "$guarded_tmp" /etc/hhs/guarded-update.env
  rm -f "$guarded_tmp"
fi

systemctl daemon-reload
systemctl enable hhs-litert-lm-gemma4.service hhs-native-agi-optimizer.service
systemctl restart hhs-litert-lm-gemma4.service

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
"$INSTALL_ROOT/hhs-llm-preflight.sh"

kimi_models=$(mktemp)
cleanup() { rm -f "$kimi_models"; }
trap cleanup EXIT
curl -fsS --max-time "${HHS_KIMI_INSTALL_PROBE_TIMEOUT_SECONDS:-60}" \
  -H "Authorization: Bearer $API_KEY" \
  -H 'Accept: application/json' \
  "$KIMI_BASE_URL/models" >"$kimi_models" || {
    echo "Kimi K3 provider probe failed; refusing to claim primary-provider installation closure." >&2
    exit 10
  }
HHS_MODELS_JSON="$kimi_models" HHS_EXPECTED_MODEL="$KIMI_MODEL" python3 - <<'PY'
import json
import os
from pathlib import Path
value = json.loads(Path(os.environ["HHS_MODELS_JSON"]).read_text(encoding="utf-8"))
ids = {
    str(item.get("id"))
    for item in value.get("data", [])
    if isinstance(item, dict) and item.get("id")
}
if os.environ["HHS_EXPECTED_MODEL"] not in ids:
    raise SystemExit(
        f"configured Kimi model {os.environ['HHS_EXPECTED_MODEL']!r} is not registered"
    )
PY

systemctl restart hhs.service
systemctl restart hhs-native-agi-optimizer.service

ready=0
for _ in $(seq 1 "${HHS_PASS209_HEALTH_TIMEOUT_SECONDS:-180}"); do
  if curl -fsS http://127.0.0.1:8080/api/assistant/health \
    >/tmp/hhs-pass209-assistant-health.json 2>/dev/null; then
    if HHS_HEALTH_JSON=/tmp/hhs-pass209-assistant-health.json python3 - <<'PY'
import json
import os
from pathlib import Path
value = json.loads(Path(os.environ["HHS_HEALTH_JSON"]).read_text(encoding="utf-8"))
raise SystemExit(0 if value.get("ok") and value.get("selected_provider_id") else 1)
PY
    then
      ready=1
      break
    fi
  fi
  if systemctl is-failed --quiet hhs.service; then
    break
  fi
  sleep 1
done
if [[ "$ready" != 1 ]]; then
  systemctl status hhs-litert-lm-gemma4.service hhs.service hhs-native-agi-optimizer.service \
    --no-pager --full >&2 || true
  journalctl -u hhs-litert-lm-gemma4.service -u hhs.service \
    -u hhs-native-agi-optimizer.service -n 300 --no-pager >&2 || true
  exit 11
fi

python3 -m json.tool /tmp/hhs-pass209-assistant-health.json
cat <<EOF
Pass 209 production LLM hierarchy installed.

Primary:       Kimi K3 API agentic swarm
Fallback:      LiteRT-LM Gemma 4 E2B on CPU
Backend agent: repository-native HHS learning/optimization observer
Environment:   $ENV_FILE
Gemma state:   $LITERT_STATE_ROOT
Optimizer:     $STATE_ROOT

Inspect:
  systemctl status hhs-litert-lm-gemma4.service hhs.service hhs-native-agi-optimizer.service --no-pager --full
  curl -fsS http://127.0.0.1:8080/api/assistant/health | python3 -m json.tool
  curl -fsS http://127.0.0.1:8080/api/runtime/llm-orchestrator/status | python3 -m json.tool
  cat $STATE_ROOT/PASS209_LLM_PREFLIGHT_RECEIPT.json
EOF
