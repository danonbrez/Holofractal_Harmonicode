#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import (
    BASE_COMMIT,
    BASE_TREE,
    CANDIDATES,
    ITERATION6_CANDIDATE_SET_ROOT,
    ITERATION6_RECEIPT,
    PASS213_CLOSURE,
    hash216,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    unsigned = {
        "schema": "HHS_PASS_214_ITERATION_7_MANIFEST_V1",
        "pass": 214,
        "iteration": 7,
        "base_commit": BASE_COMMIT,
        "base_tree": BASE_TREE,
        "pass213_closure": PASS213_CLOSURE,
        "iteration6_candidate_set_root_hash216": ITERATION6_CANDIDATE_SET_ROOT,
        "iteration6_receipt_sha256": ITERATION6_RECEIPT,
        "candidate_count": len(CANDIDATES),
        "candidates": list(CANDIDATES),
        "live_requirements": [
            "operational_rfc3161_reverification",
            "governed_projection_chain_verification",
            "moving_tensor_anchor_equality",
            "native_dispatch_ledger_verification",
            "native_dispatch_tensor_equality",
            "candidate_challenge_governed_projection_commitment",
        ],
        "non_promoting": True,
    }
    payload = {**unsigned, "manifest_root_hash216": hash216("pass214-iteration7-manifest", unsigned)}
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
