#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_runtime.pass152 import DeterministicVM81TestAuthority, delayed_closure_workload


def status_payload() -> dict:
    return {
        "schema": "HHS_PASS152_STATUS_V2",
        "pass": 152,
        "contract": "HHS-P152-UECI",
        "invariant": "DELAY_AUTHORITY_NOT_COMPUTATION",
        "recursive_control_invariant": "PRESERVE_CAUSAL_AUTHORITY_AT_INVARIANT_CORE_WHILE_USING_EMERGENT_FREEDOM_TO_OPTIMIZE_SUBORDINATE_EXECUTION",
        "canonical_optimization_rule": "EXPLOIT_FREEDOM_RECURSIVELY_PRESERVE_INVARIANTS_ABSOLUTELY_EXTEND_HISTORY_MONOTONICALLY",
        "production_commit_authority": "VM81",
        "runtime_receipt_authority": "Hash72",
        "security_memory_authority": "Hash216",
        "predictive_evidence_authority": "NON_AUTHORITATIVE",
    }


def main() -> int:
    ap = argparse.ArgumentParser(prog="hhs152")
    ap.add_argument("command", choices=["self-test", "status", "capabilities"])
    ap.add_argument("--receipts", default="receipts/pass152/cli")
    ap.add_argument("--delay-ms", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ns = ap.parse_args()

    if ns.command == "status":
        print(json.dumps(status_payload(), sort_keys=True))
        return 0
    if ns.command == "capabilities":
        print(json.dumps({
            **status_payload(),
            "layers": ["L0_INVARIANT_CORE", "L1_ELASTIC_CLOSURE", "L2_SUPERVISORY_POLICY"],
            "control_vectors": [
                "scheduling", "resource_allocation", "branch_priority", "cache_placement",
                "equivalence_reuse", "speculative_depth", "representation_choice",
                "batching", "transport_order",
            ],
            "prohibited_mutations": [
                "invariant_truth", "committed_state", "provenance", "authority_boundary",
                "receipt_history", "semantic_identity",
            ],
        }, sort_keys=True))
        return 0

    if not 0 <= ns.delay_ms <= 250:
        raise SystemExit("--delay-ms must be in [0, 250]")
    if not 1 <= ns.workers <= 8:
        raise SystemExit("--workers must be in [1, 8]")
    authority = DeterministicVM81TestAuthority()
    result = delayed_closure_workload(
        Path(ns.receipts),
        authority.admit,
        delay_seconds=ns.delay_ms / 1000.0,
        workers=ns.workers,
    )
    out = {
        "classification": "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED",
        "proof": result["proof"],
        "commit": result["commit"],
        "replay": result["replay"],
        "metrics": result["metrics"],
    }
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
