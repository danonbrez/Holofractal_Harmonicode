"""
HHS Commit Acceptance Gate v1
============================

Defines a deterministic gate that must pass before a commit is accepted.

Guarantees:
- no missing data dependencies
- no environment-specific path usage
- runtime systems execute without failure
- unified ledger verifies with zero invalid entries
- prior logic integrity preserved (no silent breakage)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import subprocess

from hhs_runtime.hhs_unified_hash72_ledger_v1 import absorb_json_artifacts, verify_unified_ledger
from hhs_runtime.hhs_language_runtime_validator_cli_v1 import validate_repo_language_runtime
from hhs_runtime.hhs_repo_paths_v1 import repo_root


FORBIDDEN_STRINGS = ["/mnt/data"]


class CommitAcceptanceError(Exception):
    pass


def _scan_forbidden_paths(root: Path) -> List[str]:
    hits: List[str] = []
    for p in root.rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        for token in FORBIDDEN_STRINGS:
            if token in text:
                hits.append(f"{p}: contains '{token}'")
    return hits


def _run_script(path: str) -> Dict[str, Any]:
    proc = subprocess.run(["python", path], capture_output=True, text=True)
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def run_commit_acceptance_gate() -> Dict[str, Any]:
    root = repo_root()

    # 1. path safety
    forbidden = _scan_forbidden_paths(root)
    if forbidden:
        raise CommitAcceptanceError(json.dumps({"forbidden_paths": forbidden}, indent=2))

    # 2. runtime validation
    runtime_status = validate_repo_language_runtime()
    if runtime_status.get("status") != "ACCEPTED":
        raise CommitAcceptanceError(json.dumps({"runtime_validation_failed": runtime_status}, indent=2))

    # 3. execute critical scripts
    scripts = [
        "hhs_runtime_certification_v2.py",
        "hhs_v1_bundle_runner-2.py",
        "hhs_realtime_phase_certification_v1.py",
    ]
    results = {}
    for s in scripts:
        res = _run_script(str(root / s))
        results[s] = res
        if not res["ok"]:
            raise CommitAcceptanceError(json.dumps({"script_failed": s, "result": res}, indent=2))

    # 4. absorb outputs into unified ledger
    artifacts = list((root / "data" / "runtime").glob("*.json"))
    absorption = absorb_json_artifacts(artifacts)
    if not absorption["verification"]["ok"]:
        raise CommitAcceptanceError(json.dumps({"ledger_invalid": absorption}, indent=2))

    # 5. final unified ledger verification
    unified = verify_unified_ledger()
    if not unified["ok"]:
        raise CommitAcceptanceError(json.dumps({"unified_ledger_invalid": unified}, indent=2))

    return {
        "status": "ACCEPTED",
        "scripts": results,
        "runtime": runtime_status,
        "ledger": unified,
    }


if __name__ == "__main__":
    result = run_commit_acceptance_gate()
    print(json.dumps(result, indent=2))
