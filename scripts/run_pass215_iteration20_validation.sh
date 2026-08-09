#!/usr/bin/env bash
set -euo pipefail

VALIDATION_LOG="$(mktemp)"
trap 'rm -f "$VALIDATION_LOG"' EXIT

{
  bash scripts/run_pass215_iteration19_validation.sh
  python -m py_compile \
    hhs_backend/runtime/hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py \
    tools/pass215_iteration20_shared_checkpoint_terminal.py
  python -m json.tool contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json >/dev/null
  python -m json.tool evidence/pass215/PASS_215_ITERATION_20_IMPLEMENTATION_RECORD.json >/dev/null
  python -m json.tool evidence/pass215/PASS_215_ITERATION_20_SOURCE_EVIDENCE.json >/dev/null
  pytest -q tests/test_hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py
} 2>&1 | tee "$VALIDATION_LOG"

python - "$VALIDATION_LOG" "${PASS215_I20_TEST_COUNT_FILE:-}" <<'PY'
import json
from pathlib import Path
import re
import sys

from hhs_backend.runtime import hhs_pass215_iteration20_shared_checkpoint_terminal_v1 as i20

log_path = Path(sys.argv[1])
count_output = sys.argv[2]
counts = [
    int(value)
    for value in re.findall(r"(?m)^(\d+) passed(?:,| in )", log_path.read_text())
]
measured_count = sum(counts)
if not counts:
    raise SystemExit("PASS215_I20_NO_PYTEST_COUNTS_MEASURED")

contract = json.loads(Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json").read_text())
record = json.loads(Path("evidence/pass215/PASS_215_ITERATION_20_IMPLEMENTATION_RECORD.json").read_text())
evidence = json.loads(Path("evidence/pass215/PASS_215_ITERATION_20_SOURCE_EVIDENCE.json").read_text())
i20.validate_shared_checkpoint_terminal_evidence(evidence)

source = contract["source_execution"]
checkpoints = evidence["sequential_checkpoints"]
control = evidence["bounded_generation_control"]
transition = evidence["downstream_transition"]
measured_summary = {
    "cumulative_test_count": measured_count,
    "selected_token_ids": control["selected_token_ids"],
    "selected_tokens": control["selected_tokens"],
    "termination_reason": control["termination_reason"],
    "earlier_checkpoint_canonical_bytes": checkpoints["earlier_checkpoint_canonical_bytes"],
    "later_checkpoint_canonical_bytes": checkpoints["later_checkpoint_canonical_bytes"],
    "earlier_checkpoint_root_hash216": checkpoints["earlier_checkpoint_root_hash216"],
    "later_checkpoint_root_hash216": checkpoints["later_checkpoint_root_hash216"],
    "checkpoint_manifest_roots_hash216": checkpoints["checkpoint_manifest_roots_hash216"],
    "shared_content_store_root_hash216": checkpoints["shared_content_store_root_hash216"],
    "shared_checkpoint_bundle_root_hash216": checkpoints["shared_checkpoint_bundle_root_hash216"],
    **checkpoints["reuse_metrics"],
    "sequential_checkpoint_reuse_root_hash216": checkpoints["sequential_checkpoint_reuse_root_hash216"],
    "pass215_terminal_completion_root_hash216": evidence["pass215_terminal_completion_root_hash216"],
    "suite_root_hash216": evidence["shared_checkpoint_terminal_suite_root_hash216"],
    "evidence_root_hash216": evidence["evidence_root_hash216"],
    "receipt_hash72": evidence["receipt_hash72"],
    "pass216_status": transition["pass216_status"],
    "next_implemented_pass": transition["next_implemented_pass"],
    "cross_process_replay": True,
    "semantic_exactness": True,
}
if measured_summary != source:
    raise SystemExit("PASS215_I20_MEASURED_SOURCE_SUMMARY_MISMATCH")
if record["status"] != "RESTART_STATE_FROZEN_EXACT_HEAD_REPLAY_PENDING":
    raise SystemExit("PASS215_I20_IMPLEMENTATION_RECORD_STATUS_INVALID")
if record["contract"] != contract["contract"]:
    raise SystemExit("PASS215_I20_IMPLEMENTATION_RECORD_CONTRACT_INVALID")
if record["source_execution"] != source:
    raise SystemExit("PASS215_I20_IMPLEMENTATION_RECORD_SOURCE_INVALID")
if record["pass_completion"] != contract["pass_completion"]:
    raise SystemExit("PASS215_I20_IMPLEMENTATION_RECORD_COMPLETION_INVALID")
if record["downstream_transition"] != contract["downstream_transition"]:
    raise SystemExit("PASS215_I20_IMPLEMENTATION_RECORD_TRANSITION_INVALID")
parent = record["frozen_iteration19_parent"]
inherits = contract["inherits"]
for record_key, contract_key in (
    ("closure_head", "iteration19_closure_head"),
    ("closure_tree", "iteration19_closure_tree"),
    ("closure_run", "iteration19_closure_run"),
    ("closure_job", "iteration19_closure_job"),
    ("closure_artifact_id", "iteration19_closure_artifact_id"),
    ("closure_artifact_sha256", "iteration19_closure_artifact_sha256"),
    ("compact_checkpoint_root_hash216", "iteration19_compact_checkpoint_root_hash216"),
    ("content_store_root_hash216", "iteration19_content_store_root_hash216"),
    ("compaction_root_hash216", "iteration19_compaction_root_hash216"),
    ("suite_root_hash216", "iteration19_suite_root_hash216"),
    ("evidence_root_hash216", "iteration19_evidence_root_hash216"),
    ("receipt_hash72", "iteration19_receipt_hash72"),
):
    if parent[record_key] != inherits[contract_key]:
        raise SystemExit(f"PASS215_I20_IMPLEMENTATION_RECORD_PARENT_INVALID:{record_key}")

print(f"PASS215_ITERATION20_CUMULATIVE_TEST_COUNT={measured_count}")
if count_output:
    output_path = Path(count_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(measured_count) + "\n")
PY

echo PASS215_ITERATION20_VALIDATION_OK
