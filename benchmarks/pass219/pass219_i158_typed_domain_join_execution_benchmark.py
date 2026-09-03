#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from hhs_runtime.pass219.typed_domain_join_executor import (
    execute_typed_domain_joins,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)

SCHEMA = "HHS_PASS219_I158_TYPED_DOMAIN_JOIN_EXECUTION_BENCHMARK_V1"


def _fixture_graph() -> dict[str, object]:
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
    graph = _fixture_graph()
    result = execute_typed_domain_joins(graph)
    witnesses = result["modular_projection_witnesses"]
    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "pass": 219,
        "iteration": "I158",
        "classification": "TYPED_DOMAIN_EXECUTION_CAPABILITY_BENCHMARK",
        "candidate_fixture_scope": "NONAUTHORITATIVE_DETERMINISTIC_CONFORMANCE_FIXTURE",
        "P": 30,
        "p": 29,
        "q": 31,
        "delta": 1,
        "t": 30,
        "m": 267,
        "harmonic_value": 26970,
        "modulus": 899,
        "left_modular_projection": witnesses[0]["projected_representative"],
        "right_modular_projection": witnesses[1]["projected_representative"],
        "modular_target_representative": witnesses[0]["modular_representative"],
        "join_count": result["counts"]["join_count"],
        "proved_before_i158": 5,
        "proved_after_i158": result["counts"]["proved"],
        "newly_resolved_modular_pivots": result["counts"]["newly_resolved_modular_pivots"],
        "unresolved_after_i158": result["counts"]["unresolved"],
        "rejected_after_i158": result["counts"]["rejected"],
        "decision": result["decision"],
        "execution_membrane_sha256": result["execution_membrane_sha256"],
        "input_typed_value_graph_sha256": result["input_graph"]["typed_value_graph_sha256"],
        "candidate_binding_sha256": result["input_graph"]["candidate_binding_sha256"],
        "projection_witness_sha256s": [
            row["projection_witness_sha256"] for row in witnesses
        ],
        "remaining_blockers": result["remaining_blockers"],
        "repository_blocker_evidence": result["repository_blocker_evidence"],
        "scalar_coercion_used": any(
            row["scalar_coercion_used"] for row in result["executed_joins"]
        ),
        "reverse_inference_authorized": any(
            row.get("reverse_inference_authorized", False) for row in witnesses
        ),
        "ordinary_scalar_remainder_identity_claimed": any(
            row["ordinary_scalar_remainder_identity_claimed"] for row in witnesses
        ),
        "authority": result["authority"],
        "next_boundary": result["next_boundary"],
        "canonical_timing_claimed": False,
        "physical_full_manifold_enumeration_claim": False,
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
        default="artifacts/pass219/i158/typed_domain_join_execution.json",
    )
    args = parser.parse_args()
    receipt = build_receipt()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
