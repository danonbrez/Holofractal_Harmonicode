#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_authority_conflict_reconciliation_v1 import (
    reconcile_authority_conflicts,
    validate_authority_reconciliation,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile Pass 214 Iteration 2 authority-conflict candidates")
    parser.add_argument("--compatibility-directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    directory = args.compatibility_directory.resolve()
    summary = load(directory / "iteration2_summary.json")
    conflicts = load(directory / "authority_conflicts.json")
    records = load(directory / "callable_conformance_records.json")
    report = reconcile_authority_conflicts(
        authority_conflicts=conflicts,
        callable_records=records,
        compatibility_summary=summary,
    )
    validate_authority_reconciliation(report, compatibility_summary=summary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_conflict_count": report["candidate_conflict_count"],
        "resolution_count": report["resolution_count"],
        "unresolved_conflict_count": report["unresolved_conflict_count"],
        "automatic_merge_count": report["automatic_merge_count"],
        "reconciliation_root_hash216": report["reconciliation_root_hash216"],
        "single_mutation_authority_preserved": report["single_mutation_authority_preserved"],
    }, indent=2, sort_keys=True))
    print("PASS214_AUTHORITY_CONFLICT_RECONCILIATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
