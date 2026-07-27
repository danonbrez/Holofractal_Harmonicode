#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export HHS_START_LITERT_LM=1
export HHS_LITERT_LM_AUTO_BOOTSTRAP="${HHS_LITERT_LM_AUTO_BOOTSTRAP:-1}"
export HHS_LITERT_LM_HOST="${HHS_LITERT_LM_HOST:-127.0.0.1}"
export HHS_LITERT_LM_PORT="${HHS_LITERT_LM_PORT:-9379}"
export HHS_LITERT_LM_BASE_URL="${HHS_LITERT_LM_BASE_URL:-http://${HHS_LITERT_LM_HOST}:${HHS_LITERT_LM_PORT}/v1}"
export HHS_LITERT_LM_MODEL="${HHS_LITERT_LM_MODEL:-gemma4-12b}"

exec bash "${ROOT_DIR}/start.sh"
