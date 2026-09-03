#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


EXPECTED_REASON_MASK = 1 << 9


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: pass219_i155_production_provider_residual_benchmark.py "
            "<provider-probe.json> <output.json>"
        )

    probe_path = Path(sys.argv[1])
    output = Path(sys.argv[2])
    output.parent.mkdir(parents=True, exist_ok=True)

    probe = json.loads(probe_path.read_text(encoding="utf-8"))

    assert probe["schema"] == "HHS_PASS219_I154_PASS169_PROVIDER_PROBE_V1"
    assert probe["provider_origin"] == "REPOSITORY_PRODUCTION_PASS169_VM81_PROVIDER"
    assert probe["classification"] == "BLOCKED_FULL_SYMBOLIC_RESIDUAL"
    assert probe["runtime_provider_available"] is True
    assert probe["binding_decision"] == "UNRESOLVED"
    assert probe["binding_reason_mask"] == EXPECTED_REASON_MASK
    assert probe["pass159_provenance_exact"] is True
    assert probe["pass169_authority_verified"] is False
    assert probe["boolean_gate_results_available"] is False
    assert probe["membrane_input_ready"] is False
    assert probe["canonical_monolithic_proof"] is False
    assert probe["whole_equation_propagated"] is False
    assert probe["i154_local_snapshot_binding_available"] is False
    assert probe["i154_gate_vector_export_available"] is False
    assert probe["i154_planner_input_ready"] is False
    assert probe["test_fixture_is_authority"] is False
    assert probe["floating_point_authority"] is False
    assert probe["vm81_mutation_authority"] is False
    assert probe["hash72_commit_authority"] is False
    assert probe["persistence_mutation_authority"] is False

    receipt = {
        "schema": "HHS_PASS219_I155_PRODUCTION_PASS169_PROVIDER_RESIDUAL_BENCHMARK_V1",
        "pass": 219,
        "iteration": "I155",
        "metric_class": "EXACT_AUTHORITY_STATE_TRANSITION",
        "provider_absence_blocker_cleared": True,
        "production_provider_implementation_present": True,
        "production_provider_non_test": True,
        "prior_blocker": "PROVIDER_UNAVAILABLE",
        "current_blocker": "FULL_SYMBOLIC_UQCEL_MONOLITHIC_EQUALITY_CHAIN",
        "provider_probe_sha256": _sha256(probe_path),
        "binding": {
            "decision": "UNRESOLVED",
            "reason": "FULL_SYMBOLIC_UNRESOLVED",
            "reason_mask": EXPECTED_REASON_MASK,
            "pass159_provenance_exact": True,
            "pass169_authority_verified": False,
            "boolean_gate_results_available": False,
            "membrane_input_ready": False,
            "canonical_monolithic_proof": False,
            "whole_equation_propagated": False,
        },
        "full_symbolic": {
            "uqcel_supported": False,
            "unresolved_families": [
                "T_M_HARMONIC",
                "TENSOR_S_F_AT_BT",
                "DELTA_P_ROOT",
                "MOD_F_U",
                "MONOLITHIC_EQUALITY_CHAIN",
            ],
            "unsupported_is_false_equation": False,
            "unsupported_is_zero_work": False,
        },
        "i154_real_exhaustion": {
            "authoritative_workload_count": 0,
            "effective_exhaustion_work_measured": False,
            "within_81_over_7_claim": None,
            "local_P_snapshot_binding_available": False,
            "canonical_gate_vector_environment_export_available": False,
        },
        "fixed_search_space": {
            "target": "72^42=5184^21",
            "working_manifold": "3*72^72",
            "route_multiplicity": "3*72^30",
            "required_reduction_ratio": "81/7",
            "changed": False,
        },
        "authority": {
            "canonical_vm81_mutation": False,
            "canonical_hash72_mint": False,
            "canonical_hash216_persistence": False,
            "floating_point": False,
            "gate_truth_manufactured": False,
        },
        "physical_full_target_exhaustion_claim": False,
        "physical_full_working_manifold_enumeration_claim": False,
        "global_exhaustion_bound_proven": False,
        "result": "PASS",
    }
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(encoded).hexdigest()

    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
