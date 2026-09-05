#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "HHS_PASS219_I156_FULL_SYMBOLIC_MONOLITHIC_LOWERING_BENCHMARK_V1"


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: pass219_i156_full_symbolic_monolithic_lowering_benchmark.py "
            "<conformance.txt> <output.json>"
        )
    conformance = Path(sys.argv[1])
    output = Path(sys.argv[2])
    text = conformance.read_text(encoding="utf-8")
    if "PASS219_I156_FULL_SYMBOLIC_MONOLITHIC_LOWERING_OK" not in text:
        raise SystemExit("I156_C_CONFORMANCE_NOT_GREEN")

    receipt = {
        "schema": SCHEMA,
        "pass": 219,
        "iteration": "I156",
        "metric_class": "EXACT_SYMBOLIC_LOWERING_CAPABILITY",
        "term_count": 15,
        "edge_count": 10,
        "family_count": 8,
        "required_edge_mask": 1023,
        "required_family_mask": 255,
        "historical_residual_mask": 31,
        "residual_mask_for_complete_witness": 0,
        "exact_cross_multiplication": True,
        "source_identity_required": True,
        "pass159_provenance_root_required": True,
        "ordered_xy_yx_required": True,
        "single_candidate_transaction_required": True,
        "legacy_v1_full_symbolic_input_sufficient": False,
        "candidate_value_producer_included": False,
        "vm81_execution_included": False,
        "hash72_execution_receipt_included": False,
        "deterministic_replay_included": False,
        "authority": {
            "canonical_vm81_mutation": False,
            "canonical_hash72_mint": False,
            "canonical_hash216_persistence": False,
            "floating_point": False,
        },
        "fixed_search_space": {
            "target": "72^42=5184^21",
            "working_manifold": "3*72^72",
            "route_multiplicity": "3*72^30",
            "changed": False,
        },
        "conformance_sha256": hashlib.sha256(conformance.read_bytes()).hexdigest(),
        "result": "PASS",
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
