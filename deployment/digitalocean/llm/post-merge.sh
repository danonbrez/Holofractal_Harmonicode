#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPO_ROOT:-/opt/hhs/app}
PYTHON=${HHS_PASS209_PYTHON:-/opt/hhs/venv/bin/python}
ENV_FILE=${HHS_PASS209_ENV_FILE:-/etc/hhs/pass209-llm.env}

cd "$REPO_ROOT"
[[ -x "$PYTHON" ]] || { echo "Missing HHS Python: $PYTHON" >&2; exit 2; }
[[ -r "$ENV_FILE" ]] || { echo "Missing Pass 209 environment: $ENV_FILE" >&2; exit 3; }

"$PYTHON" -m py_compile \
  hhs_backend/runtime/hhs_kimi_k3_agentic_assistant_v1.py \
  hhs_backend/runtime/hhs_pass209_native_agi_optimizer_v1.py \
  hhs_backend/runtime/hhs_pass209_production_assistant_v1.py \
  hhs_backend/api/pass209_llm_orchestrator_routes.py \
  hhs_backend/api/litert_lm_assistant_routes.py \
  scripts/pass209_native_agi_optimizer_worker.py

if [[ -f bin/post_compile ]]; then
  bash bin/post_compile
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
/usr/local/lib/hhs-llm/hhs-llm-preflight.sh
