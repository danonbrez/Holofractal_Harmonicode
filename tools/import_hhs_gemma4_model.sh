#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LITERT_LM_BIN="${HHS_LITERT_LM_BIN:-}"
MODEL_ID="${HHS_LITERT_LM_MODEL:-gemma4-12b}"
MODEL_REPOSITORY="${HHS_LITERT_LM_MODEL_REPOSITORY:-litert-community/gemma-4-12B-it-litert-lm}"
MODEL_FILENAME="${HHS_LITERT_LM_MODEL_FILENAME:-gemma-4-12B-it.litertlm}"

if [[ -z "$LITERT_LM_BIN" ]]; then
  LITERT_LM_BIN="$(bash "${ROOT_DIR}/tools/bootstrap_litert_lm.sh" --print-bin)"
fi

if "$LITERT_LM_BIN" list 2>/dev/null | awk 'NR > 1 {print $1}' | grep -Fxq "$MODEL_ID"; then
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
exec "$LITERT_LM_BIN" "${ARGS[@]}"
