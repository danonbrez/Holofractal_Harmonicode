#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence"
DIST = ROOT / "dist"
PASS158_REPORT = ROOT.parent / "hhs_pass158_llabi_nftc_api" / "dist" / "native-test-report.json"
TERMINAL = "HHS_PASS_159_VM81_HASH216_HARMONICODE_INTERPRETER_AND_C11_NATIVE_COMPILER_VERIFIED"


def read_json(path: Path):
    text = path.read_text(encoding="utf-8", errors="strict").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
        raise


ref = os.environ.get("GITHUB_REF", "")
sha = os.environ.get("GITHUB_SHA", "")
if ref != "refs/heads/main" or len(sha) != 40:
    raise SystemExit("authoritative main context required")

pre = read_json(EVIDENCE / "P159_COMPLETION_RECEIPT.json")
full = read_json(DIST / "P159_FULL_VALIDATION_REPORT.json")
cross = read_json(DIST / "P159_CROSS_ARCHITECTURE_INPUT.json")
inherited = read_json(PASS158_REPORT)

checks = {
    "pre_main_omega": pre.get("omega_without_main") is True,
    "full_failures_zero": full.get("failures") == 0,
    "positive_matrix": full.get("positive_total", 0) >= 159,
    "negative_matrix": full.get("negative_total") == 159,
    "hash216_coverage": full.get("hash216_position_coverage") == 216,
    "vm81_coverage": full.get("vm81_cell_coverage") == 81,
    "equivalence_programs": full.get("equivalence_programs", 0) >= 72,
    "no_fallback": full.get("fallback_used") is False,
    "cross_architecture": cross.get("matched") is True,
    "inherited_positive": inherited.get("positive_total", 0) >= 272,
    "inherited_negative": inherited.get("negative_total", 0) >= 81,
    "authoritative_main": ref == "refs/heads/main",
}
if not all(checks.values()):
    raise SystemExit(json.dumps({"classification": "HHS_PASS_159_MAIN_CLOSURE_REJECTED", "checks": checks}, sort_keys=True))

closure_material = {
    "authoritative_main_commit": sha,
    "pre_main_evidence_root": pre.get("evidence_root"),
    "full_validation": full,
    "cross_architecture": cross,
    "inherited_pass158": inherited,
    "checks": checks,
}
closure_root = hashlib.sha256(json.dumps(closure_material, sort_keys=True).encode("utf-8")).hexdigest()
terminal_receipt = {
    "schema": "P159_COMPLETION_RECEIPT_V1",
    "contract": "HHS-P159-VM81-H216-HCI-C11C",
    "classification": TERMINAL,
    "terminal_claimed": True,
    "main_closure_required": False,
    "omega_159": True,
    "authoritative_branch": "main",
    "authoritative_main_commit": sha,
    "pre_main_evidence_root": pre.get("evidence_root"),
    "main_closure_root": closure_root,
    "checks": checks,
}
EVIDENCE.mkdir(exist_ok=True)
(EVIDENCE / "P159_COMPLETION_RECEIPT.json").write_text(
    json.dumps(terminal_receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
(EVIDENCE / "P159_AUTHORITATIVE_MAIN_CLOSURE.json").write_text(
    json.dumps({"schema": "P159_AUTHORITATIVE_MAIN_CLOSURE_V1", **closure_material, "classification": TERMINAL, "omega_159": True, "main_closure_root": closure_root}, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(json.dumps(terminal_receipt, sort_keys=True))
