#!/usr/bin/env bash
# HHS production incident 2026-10-11 — pinned causal egress host repair.
# This script does NOT deploy, switch Git commits, restart services, or clear
# the release block. It provisions only the installed venv/model and verifies
# direct native generation using the exact current deployed source; never switches release revisions.
set -Eeuo pipefail
umask 027

PIN="579dbb58f7f9d99419e73cb4d686901e6d123212"
APP="/opt/hhs/app"
PY="/opt/hhs/venv/bin/python"
MODEL="/var/lib/hhs/models/native-causal/smollm2-360m-instruct-a10cc1512ea"
STATUS="/var/lib/hhs/runtime-bootstrap/native-causal-579dbb58-recovery.jsonl"

fail(){ printf 'HHS_CAUSAL_REPAIR_BLOCKED: %s\n' "$*" >&2; exit 1; }
[[ "${EUID}" == 0 ]] || fail "root host SSH authority required"
for binary in flock systemctl git runuser; do
  command -v "$binary" >/dev/null 2>&1 || fail "missing command: $binary"
done
[[ -x "$PY" ]] || fail "venv interpreter missing: $PY"
[[ -d "$APP/.git" ]] || fail "production checkout missing"
[[ "$(git -C "$APP" rev-parse HEAD)" == "$PIN" ]] ||
  fail "host does not contain exact deployed baseline $PIN; do not roll it back"
[[ "$(git -C "$APP" branch --show-current)" == main ]] ||
  fail "production checkout must remain on main"
git -C "$APP" diff-index --quiet HEAD -- ||
  fail "tracked production checkout has uncommitted changes"

# Same canonical lock names and order as the DigitalOcean deploy workflow.
install -d -m 0755 /run/lock
exec 7>/run/lock/hhs-production-mutation.lock
flock -w 30 7 || fail "another production mutation owns the host"

# This incident is a release freeze. Keep the timer STOPPED on both success
# and failure; the next exact-main promotion must be separately accepted.
systemctl stop hhs-guarded-update.timer ||
  fail "cannot pause automatic production promotions"
if systemctl is-active --quiet hhs-guarded-update.service; then
  fail "guarded updater currently active; abort instead of racing it"
fi
exec 8>/run/lock/hhs-guarded-update.lock
flock -w 15 8 || fail "guarded updater owns the mutation lock"

# Reverify exact HEAD under both locks: reject any preflight/lock race.
[[ "$(git -C "$APP" rev-parse HEAD)" == "$PIN" ]] ||
  fail "production HEAD changed while waiting for lock"
[[ "$(git -C "$APP" branch --show-current)" == main ]] ||
  fail "production branch changed while waiting for lock"
git -C "$APP" diff-index --quiet HEAD -- ||
  fail "production checkout became dirty while waiting for lock"
PROMOTION_RECEIPT="/var/lib/hhs-guarded-update/last-success.json"
[[ -r "$PROMOTION_RECEIPT" ]] ||
  fail "deployed release promotion receipt unavailable"
"$PY" - "$PROMOTION_RECEIPT" "$PIN" <<'PYCODE'
import json, sys
from pathlib import Path
r = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert r.get("candidate_sha") == sys.argv[2]
assert r.get("runtime_os_bundle_sha") == sys.argv[2]
assert r.get("outcome") == "PROMOTED"
print("HHS_CAUSAL_REPAIR_PROMOTION_IDENTITY_VERIFIED=1")
PYCODE

cd "$APP"
printf 'HHS_CAUSAL_REPAIR_SOURCE_SHA=%s\n' "$PIN"
"$PY" -m pip --version
printf 'HHS_CAUSAL_REPAIR_INSTALL_PINNED_RUNTIME=1\n'
HHS_NATIVE_CAUSAL_LM_AUTO_PROVISION=1 \
HHS_NATIVE_CAUSAL_LM_REQUIRED=1 \
  "$PY" "$APP/tools/provision_native_causal_model.py" --install

# Import and exact-version check in the production interpreter, not CI Python.
"$PY" - <<'PYCODE'
from importlib.metadata import version
import torch
import transformers
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM
assert version("transformers") == "4.57.6"
assert version("torch") == "2.14.1+cpu"
assert torch.version.cuda is None
assert AutoModelForCausalLM is not None
print("HHS_CAUSAL_REPAIR_VENV_IMPORT_VERIFIED=1")
print("HHS_CAUSAL_REPAIR_TRANSFORMERS_VERSION=" + transformers.__version__)
print("HHS_CAUSAL_REPAIR_TORCH_VERSION=" + torch.__version__)
PYCODE

# The service account must see the same local model, tokenizer and config.
runuser -u hhs -- env \
  HHS_NATIVE_CAUSAL_LM_MODEL="$MODEL" \
  HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1 \
  "$PY" - <<'PYCODE'
import torch
import transformers
from transformers import AutoConfig, AutoTokenizer, AutoModelForCausalLM
model="/var/lib/hhs/models/native-causal/smollm2-360m-instruct-a10cc1512ea"
assert AutoConfig.from_pretrained(model, local_files_only=True)
assert AutoTokenizer.from_pretrained(model, local_files_only=True)
assert torch.version.cuda is None
print("HHS_CAUSAL_REPAIR_SERVICE_USER_IMPORT_VERIFIED=1")
PYCODE

# Match the existing production workflow's whitelisted live service env,
# including its native model and cache paths. Never print these variables.
pid="$(systemctl show hhs.service -p MainPID --value)"
[[ "$pid" =~ ^[0-9]+$ && "$pid" -gt 1 ]] ||
  fail "hhs.service PID not healthy: $pid"
[[ -r "/proc/$pid/environ" ]] ||
  fail "cannot read production service environment"
native_env_args=()
while IFS= read -r -d '' item; do
  case "$item" in
    HHS_NATIVE_CAUSAL_LM_*|HHS_NATIVE_LANGUAGE_GENERATION_TIMEOUT_SECONDS=*|HHS_NATIVE_LANGUAGE_FALLBACK_TIMEOUT_SECONDS=*|HF_HOME=*|TRANSFORMERS_CACHE=*|XDG_CACHE_HOME=*)
      native_env_args+=("$item");;
  esac
done <"/proc/$pid/environ"

install -d -m 0750 "$(dirname "$STATUS")"
# pipefail preserves the native CLI's status through tee.
runuser -u hhs -- env \
  PYTHONPATH="$APP" HHS_NATIVE_LANGUAGE_REQUIRE_WORD2VEC=0 \
  "${native_env_args[@]}" \
  HHS_NATIVE_CAUSAL_LM_MODEL="$MODEL" \
  HHS_NATIVE_CAUSAL_LM_LOCAL_FILES_ONLY=1 \
  HHS_NATIVE_CAUSAL_LM_REQUIRED=1 \
  "$PY" "$APP/tools/hhs_native_chat_cli.py" \
  --acceptance --strict-generation --json | tee "$STATUS"

"$PY" - "$STATUS" <<'PYCODE'
import json, sys
from pathlib import Path
rows=[json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.startswith("{")]
reports=[x for x in rows if x.get("schema")=="HHS_NATIVE_CHAT_CLI_ACCEPTANCE_V1"]
assert len(reports)==1, "missing final acceptance report"
r=reports[0]
assert r.get("ok") is True
assert r.get("prompt_count")==4
turns=r.get("turns")
assert isinstance(turns,list) and len(turns)==4
assert r.get("distinct_response_count")==4
hashes=[item.get("response_sha256") for item in turns]
assert all(isinstance(h,str) and len(h)==64 for h in hashes)
assert len(set(hashes))==4
assert not r.get("failures")
for item in turns:
  assert item.get("generation_path")=="NATIVE_CAUSAL_LM_SERIALIZED_BLOCK_STREAM"
  blocks=item.get("response_block_count")
  assert isinstance(blocks,int) and not isinstance(blocks,bool) and blocks>0
  assert item.get("runtime_mutation_admitted") is False
  assert not item.get("causal_generation_failure")
  assert not item.get("strict_failures")
print("HHS_CAUSAL_REPAIR_FOUR_NATIVE_SERIALIZED_RESPONSES_VERIFIED=1")
print("HHS_CAUSAL_REPAIR_RELEASE_GATE_STILL_BLOCKED_PENDING_HTTPS_CHROMIUM=1")
PYCODE

# IMPORTANT: Do not re-enable hhs-guarded-update.timer here.
# User-requested release block stays active until pinned HTTPS and Chromium
# validation have explicit positive receipts; only the same pinned exact-main deployment acceptance may
# follow, after successful native CLI and source verification.
