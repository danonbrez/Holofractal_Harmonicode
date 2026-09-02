#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from hhs_runtime.hhs_pass219_cross_modal_reversible_state_manifold_v1 import (
    exact_work_plan,
)


CASES = (
    {
        "case": "five-modality-depth64",
        "depth": 64,
        "modalities": 5,
        "constraints_per_state": 24,
        "cached_prefix_depth": 56,
        "changed_constraints": 2,
    },
    {
        "case": "eight-modality-depth256",
        "depth": 256,
        "modalities": 8,
        "constraints_per_state": 32,
        "cached_prefix_depth": 240,
        "changed_constraints": 2,
    },
    {
        "case": "sixteen-modality-depth1024",
        "depth": 1024,
        "modalities": 16,
        "constraints_per_state": 64,
        "cached_prefix_depth": 1000,
        "changed_constraints": 4,
    },
)


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/cross-modal-reversible-state/benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    results = []
    total_baseline = 0
    total_selected = 0
    for case in CASES:
        plan = dict(
            exact_work_plan(
                depth=case["depth"],
                modalities=case["modalities"],
                constraints_per_state=case["constraints_per_state"],
                cached_prefix_depth=case["cached_prefix_depth"],
                changed_constraints=case["changed_constraints"],
                prefix_proof_valid=True,
                hub_roundtrip_verified=True,
            )
        )
        assert plan["optimization_selected"] is True
        assert plan["candidate_authority_checks"] == plan["baseline_authority_checks"]
        assert plan["selected_total_work"] < plan["baseline_total_work"]
        total_baseline += int(plan["baseline_total_work"])
        total_selected += int(plan["selected_total_work"])
        results.append({"case": case["case"], **plan})

    fallback = dict(
        exact_work_plan(
            depth=64,
            modalities=5,
            constraints_per_state=24,
            cached_prefix_depth=56,
            changed_constraints=2,
            prefix_proof_valid=False,
            hub_roundtrip_verified=True,
        )
    )
    assert fallback["complete_fallback"] is True
    assert fallback["selected_total_work"] == fallback["baseline_total_work"]

    saved = total_baseline - total_selected
    receipt = {
        "schema": "HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_BENCHMARK_V1",
        "metric_class": "EXACT_LOGICAL_WORK_UNITS",
        "timing_is_canonical": False,
        "vm81_addresses": 5184,
        "cases": results,
        "fallback_case": fallback,
        "aggregate": {
            "baseline_total_work": total_baseline,
            "selected_total_work": total_selected,
            "exact_work_saved": saved,
            "reduction_fraction": {
                "numerator": saved,
                "denominator": total_baseline,
            },
            "reduction_permille_floor": (saved * 1000) // total_baseline,
        },
        "proof_requirements": {
            "semantic_root_equality_required": True,
            "ordered_branch_identity_required": True,
            "global_constraint_root_equality_required": True,
            "modality_registry_root_equality_required": True,
            "hub_roundtrip_required": True,
            "sealed_prefix_proof_required": True,
            "authority_check_count_reduced": False,
        },
        "canonical_authority_changed": False,
        "candidate_optimizer_mutation_authority": False,
        "result": "PASS",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
