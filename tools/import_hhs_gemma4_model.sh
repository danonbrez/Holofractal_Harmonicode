#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LITERT_LM_BIN="${HHS_LITERT_LM_BIN:-}"
MODEL_ID="${HHS_LITERT_LM_MODEL:-gemma4-12b}"
MODEL_REPOSITORY="${HHS_LITERT_LM_MODEL_REPOSITORY:-litert-community/gemma-4-12B-it-litert-lm}"
MODEL_FILENAME="${HHS_LITERT_LM_MODEL_FILENAME:-gemma-4-12B-it.litertlm}"
CACHE_ROOT="${HHS_LITERT_LM_CACHE_ROOT:-${HOME:-/tmp}/.cache/hhs/litert-lm}"
IMPORT_LOCK_FILE="${HHS_LITERT_LM_IMPORT_LOCK_FILE:-${CACHE_ROOT}/model-import.lock}"
IMPORT_LOCK_TIMEOUT_SECONDS="${HHS_LITERT_LM_IMPORT_LOCK_TIMEOUT_SECONDS:-300}"

prepare_persistent_paths() {
  mkdir -p "$CACHE_ROOT"
  export XDG_CACHE_HOME="${XDG_CACHE_HOME:-${CACHE_ROOT}/xdg}"
  export HF_HOME="${HF_HOME:-${CACHE_ROOT}/huggingface}"
  export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-${HF_HOME}/hub}"
  mkdir -p "$XDG_CACHE_HOME" "$HF_HOME" "$HUGGINGFACE_HUB_CACHE"
}

model_already_imported() {
  "$LITERT_LM_BIN" list 2>/dev/null | awk 'NR > 1 {print $1}' | grep -Fxq "$MODEL_ID"
}

if [[ -z "$LITERT_LM_BIN" ]]; then
  LITERT_LM_BIN="$(bash "${ROOT_DIR}/tools/bootstrap_litert_lm.sh" --print-bin)"
fi

prepare_persistent_paths

mkdir -p "$(dirname "$IMPORT_LOCK_FILE")"
exec {lock_fd}>"$IMPORT_LOCK_FILE"
if ! flock -w "$IMPORT_LOCK_TIMEOUT_SECONDS" "$lock_fd"; then
  echo "[HHS] Timed out waiting for model-import lock (${IMPORT_LOCK_TIMEOUT_SECONDS}s): $IMPORT_LOCK_FILE" >&2
  exit 75
fi

if model_already_imported; then
  echo "[HHS] LiteRT-LM model already imported: $MODEL_ID"
  exit 0
fi

ARGS=(import)
if [[ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]]; then
  ARGS+=(--huggingface-token "$HUGGING_FACE_HUB_TOKEN")
fi
ARGS+=(
  --from-huggingface-repo "$MODEL_REPOSITORY"
  "$MODEL_FILENAME"
  "$MODEL_ID"
)

echo "[HHS] Importing LiteRT-LM model $MODEL_ID from $MODEL_REPOSITORY"
"$LITERT_LM_BIN" "${ARGS[@]}"
