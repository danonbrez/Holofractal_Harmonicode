#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from hhs_runtime.pass219.harmonicode_modular_pivot_phase_binding import (
    execute_i159_modular_pivot_phase_bindings,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)

SCHEMA = "HHS_PASS219_I159_MODULAR_PIVOT_PHASE_BINDING_BENCHMARK_V1"


def _graph() -> dict[str, object]:
    snapshot = {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "2" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 30,
        "hydration_bits": 5184,
    }
    provenance = {
        "schema": PROVENANCE_SCHEMA,
        "combined_source_sha256": COMBINED_SOURCE_SHA256,
        "source_hash216": "0" * 216,
        "tokens_hash216": "1" * 216,
        "cst_hash216": "2" * 216,
        "ast_hash216": "3" * 216,
        "type_environment_hash216": "4" * 216,
        "constraint_graph_hash216": "5" * 216,
        "hir_hash216": "6" * 216,
        "vmir_hash216": "7" * 216,
        "global_symbol_environment_root": "b" * 64,
        "source_identity_exact": True,
        "gate_occurrence_provenance_exact": True,
        "frontend_chain_complete": True,
        "source_root_lineage_exact": True,
        "pass159_whole_expression_provenance_verified": True,
        "boolean_gate_results_available": False,
        "membrane_input_ready": False,
        "canonical_monolithic_proof": False,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "persistence_mutation_authority": False,
    }
    symbols = {
        "schema": CANDIDATE_SCHEMA,
        "P": 30,
        "p": 29,
        "q": 31,
        "t": 30,
        "m": 267,
        "s": {"numerator": 2, "denominator": 25},
        "f": 900,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }
    return produce_candidate_bound_value_graph(snapshot, provenance, symbols)


def build_receipt() -> dict[str, object]:
    result = execute_i159_modular_pivot_phase_bindings(_graph())
    left = result["pivot_witnesses"]["edge_2"]
    right = result["pivot_witnesses"]["edge_3"]
    profile = result["modular_normalization_profile"]

    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "pass": 219,
        "iteration": "I159",
        "classification": "TYPED_MODULAR_PIVOT_PHASE_BINDING_CAPABILITY_BENCHMARK",
        "fixture_scope": "NONAUTHORITATIVE_DETERMINISTIC_CONFORMANCE_FIXTURE",
        "candidate": {
            "P": 30,
            "p": 29,
            "q": 31,
            "Delta": 1,
            "t": 30,
            "m": 267,
            "modulus_pq": 899,
        },
        "before_i159": {
            "proved": 5,
            "unresolved": 5,
            "rejected": 0,
        },
        "after_i159": result["counts"],
        "decision": result["decision"],
        "profile_sha256": profile["profile_sha256"],
        "left_pivot": {
            "relation": left["relation"],
            "status": left["status"],
            "left_quotient": left["left_lane"]["quotient"],
            "left_residue": left["left_lane"]["residue"],
            "authority_quotient": left["authority_lane"]["quotient"],
            "authority_residue": left["authority_lane"]["residue"],
            "witness_sha256": left["pivot_witness_sha256"],
        },
        "right_pivot": {
            "relation": right["relation"],
            "status": right["status"],
            "authority_quotient": right["authority_lane"]["quotient"],
            "authority_residue": right["authority_lane"]["residue"],
            "right_quotient": right["right_lane"]["quotient"],
            "right_residue": right["right_lane"]["residue"],
            "witness_sha256": right["pivot_witness_sha256"],
        },
        "semantic_guards": result["semantic_guards"],
        "remaining_blockers": result["remaining_blockers"],
        "authority": result["authority"],
        "input_typed_value_graph_sha256": result[
            "input_typed_value_graph_sha256"
        ],
        "inherited_i158_execution_membrane_sha256": result[
            "inherited_i158_execution_membrane_sha256"
        ],
        "i159_execution_sha256": result["i159_execution_sha256"],
        "next_boundary": result["next_boundary"],
        "fixed_resolution": "72^42=5184^21",
        "physical_full_manifold_enumeration_claim": False,
        "canonical_timing_claimed": False,
        "result": "PASS",
    }
    canonical = json.dumps(
        receipt, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="artifacts/pass219/i159/modular_pivot_phase_binding.json",
    )
    args = parser.parse_args()
    receipt = build_receipt()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
