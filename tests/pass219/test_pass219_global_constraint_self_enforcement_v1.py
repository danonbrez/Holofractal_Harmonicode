from __future__ import annotations

from copy import deepcopy
import json

import pytest

from hhs_runtime.pass219.complete_monolithic_boundary_executor import (
    CompleteBoundaryExecutorError,
    execute_i161_complete_monolithic_boundary,
    prove_complete_monolithic_boundary,
    prove_renewed_unit_closure_relation,
    prove_scalar_zero_phase_relation,
    verify_i161_typed_zero_renewed_unit_profile,
)
from hhs_runtime.pass219.source_bound_ab_x2_phase_binding import (
    _self_test_graph,
    execute_i160_source_bound_bindings,
)
from hhs_runtime.pass219.typed_domain_join_executor import TypedDomainExecutionError
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    EDGE_SPECS,
    PROVENANCE_SCHEMA,
    TERM_NAMES,
    produce_candidate_bound_value_graph,
)


def _raw_seed() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """Return only the source-bound snapshot/provenance/symbol seed used by I157."""

    snapshot: dict[str, object] = {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "2" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": 30,
        "hydration_bits": 5184,
    }
    provenance: dict[str, object] = {
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
    symbols: dict[str, object] = {
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
    return snapshot, provenance, symbols


def _all_mapping_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            keys.update(_all_mapping_keys(child))
    elif isinstance(value, (list, tuple)):
        for child in value:
            keys.update(_all_mapping_keys(child))
    return keys


def _i161_boundary_inputs(
    graph: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    i160 = execute_i160_source_bound_bindings(graph)
    env = graph["symbol_environment"]
    assert isinstance(env, dict)
    phase_state = env["phase_state"]
    assert isinstance(phase_state, dict)

    profile = verify_i161_typed_zero_renewed_unit_profile()
    scalar_zero = prove_scalar_zero_phase_relation(
        phase_state,
        profile_sha256=str(profile["profile_sha256"]),
    )
    renewed = prove_renewed_unit_closure_relation(
        P=int(env["P"]),
        p=int(env["p"]),
        q=int(env["q"]),
        phase_state=phase_state,
        scalar_zero_witness=scalar_zero,
        profile_sha256=str(profile["profile_sha256"]),
    )
    return i160, profile, scalar_zero, renewed


def _boundary(
    graph: dict[str, object],
    i160: dict[str, object],
    profile: dict[str, object],
    scalar_zero: dict[str, object],
    renewed: dict[str, object],
) -> dict[str, object]:
    return prove_complete_monolithic_boundary(
        graph,
        i160,
        scalar_zero_witness=scalar_zero,
        renewed_unit_witness=renewed,
        profile_sha256=str(profile["profile_sha256"]),
    )


def test_raw_seed_reconstructs_identical_fifteen_node_ten_join_tensor() -> None:
    snapshot, provenance, symbols = _raw_seed()

    # The seed intentionally carries no derived I157 node/join annotations.
    seed_keys = _all_mapping_keys((snapshot, provenance, symbols))
    for derived_key in (
        "term_id",
        "term_name",
        "edge_index",
        "join_kind",
        "left_term_id",
        "right_term_id",
        "value_status",
        "scalar_coercion_used",
    ):
        assert derived_key not in seed_keys

    rebuilt = produce_candidate_bound_value_graph(snapshot, provenance, symbols)
    fixture = _self_test_graph()

    assert rebuilt == fixture
    assert rebuilt["typed_value_graph_sha256"] == fixture["typed_value_graph_sha256"]
    assert rebuilt["candidate_binding_sha256"] == fixture["candidate_binding_sha256"]
    assert rebuilt["counts"]["term_count"] == len(TERM_NAMES) == 15
    assert rebuilt["counts"]["join_count"] == len(EDGE_SPECS) == 10

    closed = execute_i161_complete_monolithic_boundary(rebuilt)
    assert closed["counts"] == {
        "join_count": 10,
        "proved": 10,
        "unresolved": 0,
        "rejected": 0,
        "newly_resolved_complete_boundary_bindings": 1,
    }
    assert closed["decision"] == "ALL_TYPED_JOINS_RESOLVED"


@pytest.mark.parametrize("term_index", range(15))
def test_every_generated_tensor_node_is_integrity_bound(term_index: int) -> None:
    graph = deepcopy(_self_test_graph())
    nodes = graph["value_nodes"]
    assert isinstance(nodes, list)
    node = nodes[term_index]
    assert isinstance(node, dict)
    payload = node.get("payload")
    if not isinstance(payload, dict):
        payload = {"original_payload": payload}
        node["payload"] = payload
    payload["_global_self_enforcement_mutation_probe"] = term_index

    # Leave the stored graph root untouched. The repository-native I158
    # validator must detect every mutation before later semantic adapters run.
    with pytest.raises(TypedDomainExecutionError, match="I157_GRAPH_SHA256_MISMATCH"):
        execute_i161_complete_monolithic_boundary(graph)


@pytest.mark.parametrize("edge_index", range(10))
def test_every_executed_relation_is_fail_closed_or_changes_global_boundary_root(
    edge_index: int,
) -> None:
    graph = _self_test_graph()
    i160, profile, scalar_zero, renewed = _i161_boundary_inputs(graph)
    baseline = _boundary(graph, i160, profile, scalar_zero, renewed)

    mutated_i160 = deepcopy(i160)
    rows = mutated_i160["executed_joins"]
    assert isinstance(rows, list)
    row = rows[edge_index]
    assert isinstance(row, dict)

    if edge_index == 8:
        # Edge 8 has an explicit semantic state transition: I161 is allowed to
        # resolve it only from the exact unresolved monolithic-boundary state.
        row["execution_reason"] = "ERASED_MONOLITHIC_BOUNDARY_SEMANTICS"
        with pytest.raises(
            CompleteBoundaryExecutorError,
            match="EDGE8_FAIL_CLOSED_BOUNDARY_REQUIRED",
        ):
            _boundary(graph, mutated_i160, profile, scalar_zero, renewed)
        return

    original_receipt = str(row["execution_row_sha256"])
    assert len(original_receipt) == 64
    replacement_head = "0" if original_receipt[0] != "0" else "1"
    row["execution_row_sha256"] = replacement_head + original_receipt[1:]

    changed = _boundary(graph, mutated_i160, profile, scalar_zero, renewed)
    assert changed["status"] == "PROVED"
    assert changed["constraint_fold_root_sha256"] != baseline["constraint_fold_root_sha256"]
    assert changed["boundary_event_root_sha256"] != baseline["boundary_event_root_sha256"]


def test_global_fold_covers_all_nine_nonboundary_relations_in_order() -> None:
    graph = _self_test_graph()
    i160, profile, scalar_zero, renewed = _i161_boundary_inputs(graph)
    boundary = _boundary(graph, i160, profile, scalar_zero, renewed)

    expected_edges = [index for index in range(10) if index != 8]
    rows = i160["executed_joins"]
    assert isinstance(rows, list)
    expected_receipts = [rows[index]["execution_row_sha256"] for index in expected_edges]

    event = boundary["boundary_event"]
    assert isinstance(event, dict)
    assert boundary["checks"]["nine_non_boundary_joins_proved"] is True
    assert len(set(expected_receipts)) == len(expected_receipts)
    assert event["constraint_fold_root_sha256"] == boundary["constraint_fold_root_sha256"]
    assert event["candidate_binding_sha256"] == graph["candidate_binding_sha256"]


def test_completed_global_tensor_remains_exact_and_non_authority_minting() -> None:
    row = execute_i161_complete_monolithic_boundary(_self_test_graph())

    def reject_float(value: object) -> None:
        if isinstance(value, dict):
            for child in value.values():
                reject_float(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                reject_float(child)
        else:
            assert not isinstance(value, float)

    reject_float(row)
    assert row["authority"]["canonical_monolithic_boundary_proof"] is True
    assert row["authority"]["pass169_terminal_proof"] is False
    assert row["authority"]["vm81_mutation_authority"] is False
    assert row["authority"]["hash72_mint_authority"] is False
    assert row["authority"]["hash216_persistence_authority"] is False
    assert row["authority"]["floating_point_authority"] is False
