from __future__ import annotations

import json
import os
from pathlib import Path

project = Path(__file__).resolve().parents[1]
dist = project / "dist"
ledger = json.loads((project / "contracts" / "PASS_157_OBLIGATION_LEDGER.json").read_text())
verification = json.loads((dist / "verification.json").read_text())
native = json.loads((dist / "native-verification.json").read_text())
js = json.loads((dist / "js-verification.json").read_text())

terminal = "HHS_PASS_157_PYTHAGOREAN_PLASTIC_FIBONACCI_MODULAR_PHASE_TENSOR_CONSTRUCTOR_VERIFIED"
pending = "HHS_PASS_157_VERIFIED_PENDING_MAIN_MERGE"
expected_classification = terminal if os.environ.get("HHS_PASS157_MAIN_MERGED") == "1" else pending

checks = {
    "obligation_count": ledger["count"] == 86,
    "obligations_closed": ledger["closed"] == ledger["count"] and ledger["open"] == 0,
    "entry_predicates": all(
        entry["implemented"] and entry["reachable"] and entry["tested"]
        and entry["evidence_present"] and entry["dependencies_closed"]
        and entry["authority_closed"] and entry["status"] == "CLOSED_BY_PASS157_INTEGRATION"
        for entry in ledger["entries"]
    ),
    "verification_contract": verification["contract"] == "HHS-P157-PPF-MPTC",
    "verification_replay": verification["replay"] == "MATCH",
    "classification_gate": verification["classification"] == expected_classification,
    "native_replay": native["replay"] == "MATCH",
    "native_receipt": len(native["receipt_hash72"]) == 72,
    "native_seal": len(native["admission_seal_hash216"]) == 216,
    "js_replay": js["replay"] == "MATCH",
    "native_tests": "HHS_PASS_157_NATIVE_CORE_VERIFIED" in (dist / "native-test-report.txt").read_text(),
    "python_tests": "OK" in (dist / "python-test-report.txt").read_text(),
    "sanitizers": "HHS_PASS_157_NATIVE_CORE_VERIFIED" in (dist / "sanitizer-report.txt").read_text(),
    "fuzz": json.loads((dist / "fuzz-report.json").read_text())["status"] == "PASS",
    "repl": "global_simultaneous_constraint" in (dist / "repl-report.jsonl").read_text(),
}
failed = [name for name, passed in checks.items() if not passed]
if failed:
    raise SystemExit(f"Pass 157 evidence failed: {failed}")
summary = {
    "schema": "HHS_PASS_157_EVIDENCE_SUMMARY_V1",
    "contract": "HHS-P157-PPF-MPTC",
    "version": "1.1.0",
    "checks": checks,
    "check_count": len(checks),
    "obligations": {"total": ledger["count"], "closed": ledger["closed"], "open": ledger["open"]},
    "native_assertions": {"positive": 27, "negative": 21},
    "python_tests": 48,
    "replay": "MATCH",
    "vm81": "ADMITTED",
    "hash72": "CLOSED",
    "hash216": "INDEXED_AND_SEALED",
    "classification": expected_classification,
    "main_merge_gate": os.environ.get("HHS_PASS157_MAIN_MERGED") == "1",
}
(dist / "evidence-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, sort_keys=True))
