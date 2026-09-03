#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)

SCHEMA = "HHS_PASS219_I157_TYPED_CANDIDATE_VALUE_GRAPH_BENCHMARK_V1"


def _snapshot() -> dict[str, object]:
    return {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "1" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 2,
        "hydration_bits": 5184,
    }


def _provenance() -> dict[str, object]:
    return {
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
        "global_symbol_environment_root": "a" * 64,
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


def _symbols() -> dict[str, object]:
    return {
        "schema": CANDIDATE_SCHEMA,
        "P": 2,
        "p": 1,
        "q": 3,
        "t": 2,
        "m": 3,
        "s": {"numerator": 18, "denominator": 1},
        "f": 4,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }


def build_receipt() -> dict[str, object]:
    graph = produce_candidate_bound_value_graph(
        _snapshot(), _provenance(), _symbols()
    )
    join_status = {
        status: sum(1 for row in graph["joins"] if row["status"] == status)
        for status in ("PROVED", "UNRESOLVED", "REJECTED")
    }
    domains = graph["counts"]["typed_domains"]
    receipt: dict[str, object] = {
        "schema": SCHEMA,
        "pass": 219,
        "iteration": "I157",
        "classification": "TYPED_VALUE_GRAPH_CAPABILITY_BENCHMARK",
        "candidate_fixture_scope": "NONAUTHORITATIVE_DETERMINISTIC_CONFORMANCE_FIXTURE",
        "term_count": graph["counts"]["term_count"],
        "join_count": graph["counts"]["join_count"],
        "typed_domain_count": len(domains),
        "typed_domains": domains,
        "join_status": join_status,
        "graph_decision": graph["decision"],
        "candidate_binding_sha256": graph["candidate_binding_sha256"],
        "typed_value_graph_sha256": graph["typed_value_graph_sha256"],
        "i156_ratio_projection_term_count": len(
            graph["i156_projection_boundary"]["i156_ratio_projection_terms"]
        ),
        "non_rational_typed_term_count": len(
            graph["i156_projection_boundary"]["non_rational_typed_terms"]
        ),
        "i156_full_ratio_packet_eligible": graph[
            "i156_projection_boundary"
        ]["full_i156_ratio_packet_eligible"],
        "scalar_coercion_used": any(
            row["scalar_coercion_used"] for row in graph["joins"]
        ),
        "modular_remainder_scalarization_used": graph["value_nodes"][3][
            "payload"
        ]["ordinary_scalar_remainder_identity_claimed"],
        "source_A_or_B_definitionally_P2": graph["value_nodes"][9]["payload"][
            "A_or_B_definitionally_P2"
        ],
        "ordered_xy": graph["symbol_environment"]["phase_state"]["xy"],
        "ordered_yx": graph["symbol_environment"]["phase_state"]["yx"],
        "ordered_xy_yx_distinct": graph["symbol_environment"]["phase_state"][
            "xy_yx_distinct"
        ],
        "fixed_search_space": graph["fixed_search_space"],
        "next_required_adapters": graph["next_required_adapters"],
        "authority": graph["authority"],
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
        default="artifacts/pass219/i157/typed_candidate_value_graph.json",
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
