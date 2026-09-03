from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    EDGE_SPECS,
    MACHINE_SOURCE_SHA256,
    NATIVE_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    TERM_NAMES,
    TypedCandidateValueError,
    candidate_bound_full_symbolic_value_producer_self_test,
    produce_candidate_bound_value_graph,
    verify_frozen_source_identity,
)


def _snapshot(P: int = 2) -> dict[str, object]:
    return {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "1" * 64,
        "snapshot_hash216_format": "PASS150_HASH216_GENOME_ROOT_SHA256",
        "P": P,
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


def _symbols(P: int = 2) -> dict[str, object]:
    return {
        "schema": CANDIDATE_SCHEMA,
        "P": P,
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


def _graph() -> dict[str, object]:
    return produce_candidate_bound_value_graph(
        _snapshot(), _provenance(), _symbols()
    )


def test_frozen_source_triplet_is_exact() -> None:
    receipt = verify_frozen_source_identity()
    assert receipt["native"]["sha256"] == NATIVE_SOURCE_SHA256
    assert receipt["machine"]["sha256"] == MACHINE_SOURCE_SHA256
    assert receipt["combined"]["sha256"] == COMBINED_SOURCE_SHA256
    assert all(row["exact"] for row in receipt.values())


def test_producer_materializes_all_fifteen_typed_terms_and_ten_joins() -> None:
    graph = _graph()
    assert graph["schema"] == "HHS_PASS219_I157_CANDIDATE_BOUND_TYPED_VALUE_GRAPH_V1"
    assert graph["classification"] == "CANDIDATE_BOUND_TYPED_FULL_SYMBOLIC_VALUE_GRAPH"
    assert graph["counts"]["term_count"] == 15 == len(TERM_NAMES)
    assert graph["counts"]["join_count"] == 10 == len(EDGE_SPECS)
    assert [row["term_id"] for row in graph["value_nodes"]] == list(range(15))
    assert [row["term_name"] for row in graph["value_nodes"]] == list(TERM_NAMES)
    assert [row["edge_index"] for row in graph["joins"]] == list(range(10))


def test_candidate_is_bound_to_local_P_snapshot_and_real_pass159_lineage_shape() -> None:
    graph = _graph()
    assert graph["snapshot"]["P"] == 2
    assert graph["snapshot"]["P_scope"] == "LOCAL_HASH216_5184_HYDRATION_PARAMETER_SNAPSHOT"
    assert graph["pass159_provenance"]["combined_source_sha256"] == COMBINED_SOURCE_SHA256
    assert graph["pass159_provenance"]["pass159_whole_expression_provenance_verified"] is True
    assert graph["pass159_provenance"]["boolean_gate_results_available"] is False
    assert graph["pass159_provenance"]["canonical_monolithic_proof"] is False
    assert len(graph["candidate_binding_sha256"]) == 64


def test_exact_harmonic_rational_nodes_are_derived_not_supplied() -> None:
    graph = _graph()
    nodes = graph["value_nodes"]
    assert nodes[0]["payload"]["value"]["text"] == "6"  # t^3-t
    assert nodes[1]["payload"]["value"]["text"] == "6"  # P^3-P/Delta
    assert nodes[2]["payload"]["value"]["text"] == "6"  # (t^3-t)/Delta
    assert nodes[4]["payload"]["value"]["text"] == "6"  # m^2-m
    assert nodes[6]["payload"]["value"]["text"] == "18"  # 72/P^2
    assert nodes[13]["payload"]["value"]["text"] == "1/2"  # Delta/P
    assert graph["joins"][0]["status"] == "PROVED"
    assert graph["joins"][1]["status"] == "PROVED"
    assert graph["joins"][4]["status"] == "PROVED"


def test_mod_operator_is_preserved_as_typed_state_not_scalar_remainder_equality() -> None:
    graph = _graph()
    modular = graph["value_nodes"][3]
    assert modular["domain"] == "MODULAR_STATE"
    assert modular["payload"]["representative"] == 1
    assert modular["payload"]["modulus"] == 3
    assert modular["payload"]["ordinary_scalar_remainder_identity_claimed"] is False

    left_pivot = graph["joins"][2]
    right_pivot = graph["joins"][3]
    assert left_pivot["join_kind"] == "TYPED_MODULAR_PIVOT_JOIN"
    assert right_pivot["join_kind"] == "TYPED_MODULAR_PIVOT_JOIN"
    assert left_pivot["status"] == right_pivot["status"] == "UNRESOLVED"
    assert "NO_SCALAR_REMAINDER_COERCION" in left_pivot["reason"]
    assert left_pivot["scalar_coercion_used"] is False


def test_lo_shu_tensor_projection_and_native_ordered_phase_remain_separate() -> None:
    graph = _graph()
    node = graph["value_nodes"][7]
    payload = node["payload"]
    projection = payload["matrix_projection"]
    phase = payload["ordered_phase_state"]
    matrix_text = [
        [cell["text"] for cell in row]
        for row in projection["matrix"]
    ]
    assert matrix_text == [["4", "9", "2"], ["3", "5", "7"], ["8", "1", "6"]]
    assert projection["projection_scope"] == "PASS191_XY_SCALAR_PROJECTION_EQUALS_1"
    assert projection["native_ordered_phase_substituted"] is False
    assert projection["projection_is_native_state_identity"] is False
    assert phase["xy"] == 0
    assert phase["yx"] == 36
    assert phase["zw"] == 0
    assert phase["wz"] == 36
    assert phase["xy_yx_distinct"] is True
    assert phase["zw_wz_distinct"] is True
    assert payload["scalar_matrix_collapse_used"] is False


def test_mod_f_over_u_preserves_xy_as_ordered_phase_in_symbolic_modulus() -> None:
    graph = _graph()
    node = graph["value_nodes"][8]
    assert node["domain"] == "SYMBOLIC_MODULAR_QUOTIENT"
    assert node["payload"]["modulus_expression"] == "72*(pq+xy)"
    assert node["payload"]["xy_ordered_phase"] == 0
    assert node["payload"]["native_xy_scalar_projection_applied"] is False
    assert node["payload"]["numeric_modulus_claimed"] is False


def test_source_level_A_and_B_are_complete_boundaries_never_P_squared_aliases() -> None:
    graph = _graph()
    ab_over_p2 = graph["value_nodes"][9]
    sqrt_ab = graph["value_nodes"][10]
    lhs = graph["value_nodes"][11]
    rhs = graph["value_nodes"][12]

    assert ab_over_p2["payload"]["A"] == "COMPLETE_MONOLITHIC_LEFT_BOUNDARY"
    assert ab_over_p2["payload"]["B"] == "COMPLETE_MONOLITHIC_RIGHT_BOUNDARY"
    assert ab_over_p2["payload"]["A_or_B_definitionally_P2"] is False
    assert sqrt_ab["payload"]["scalar_root_projection_claimed"] is False
    assert lhs["payload"]["boundary"] == "A"
    assert rhs["payload"]["boundary"] == "B"
    assert lhs["payload"]["scalar_denominator_substitution_used"] is False
    assert rhs["payload"]["scalar_boundary_fixed_point_claimed"] is False


def test_delta_root_preserves_phase_exponent_and_refuses_scalar_x_squared() -> None:
    graph = _graph()
    radical = graph["value_nodes"][14]
    assert radical["domain"] == "SYMBOLIC_RADICAL"
    assert radical["payload"]["base"]["sum"] == 4
    assert radical["payload"]["phase_exponent"]["domain"] == "ORDERED_PHASE_EXPONENT"
    assert radical["payload"]["phase_exponent"]["x_phase"] == 18
    assert radical["payload"]["ordinary_scalar_x_squared_assumed"] is False
    assert radical["payload"]["scalar_radical_projection_claimed"] is False
    assert graph["joins"][9]["status"] == "UNRESOLVED"
    assert graph["joins"][9]["reason"] == "EXACT_PHASE_EXPONENT_RADICAL_ADAPTER_REQUIRED"


def test_typed_constraint_joins_do_not_claim_untyped_scalar_identity() -> None:
    graph = _graph()
    assert graph["joins"][5]["status"] == "PROVED"
    assert graph["joins"][6]["status"] == "PROVED"
    for index in (5, 6):
        row = graph["joins"][index]
        assert row["join_kind"] == "TYPED_CONSTRAINT_JOIN"
        assert row["reason"] == "EXACT_TYPED_WITNESSES_JOIN_ONE_CANDIDATE"
        assert row["scalar_coercion_used"] is False


def test_graph_honestly_remains_unresolved_at_runtime_execution_adapters() -> None:
    graph = _graph()
    assert graph["decision"] == "UNRESOLVED"
    assert graph["counts"]["proved_joins"] == 5
    assert graph["counts"]["unresolved_joins"] == 5
    assert graph["counts"]["rejected_joins"] == 0
    assert graph["joins"][7]["reason"] == "SYMBOLIC_AB_ROOT_EXECUTION_REQUIRED"
    assert graph["joins"][8]["reason"] == "COMPLETE_BOUNDARY_EXECUTION_REQUIRED"
    assert graph["authority"]["canonical_monolithic_proof"] is False
    assert graph["authority"]["vm81_execution_verified"] is False
    assert graph["authority"]["hash72_execution_receipt_verified"] is False
    assert graph["authority"]["deterministic_replay_verified"] is False


def test_i156_ratio_surface_is_explicitly_projection_only_for_this_typed_graph() -> None:
    graph = _graph()
    boundary = graph["i156_projection_boundary"]
    assert boundary["i156_is_full_typed_semantic_authority"] is False
    assert boundary["full_i156_ratio_packet_eligible"] is False
    assert boundary["i156_ratio_projection_terms"] == [0, 1, 2, 4, 5, 6, 13]
    assert boundary["non_rational_typed_terms"] == [3, 7, 8, 9, 10, 11, 12, 14]


def test_fixed_cardinality_and_authority_are_unchanged() -> None:
    graph = _graph()
    fixed = graph["fixed_search_space"]
    assert fixed["target_cardinality_decimal"] == str(5184**21)
    assert fixed["working_manifold_cardinality_decimal"] == str(3 * 72**72)
    assert fixed["route_multiplicity_per_target_decimal"] == str(3 * 72**30)
    assert fixed["changed"] is False
    assert graph["authority"] == {
        "pass169_whole_expression_authority_required": True,
        "canonical_monolithic_proof": False,
        "vm81_execution_verified": False,
        "vm81_mutation_authority": False,
        "hash72_execution_receipt_verified": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "deterministic_replay_verified": False,
        "floating_point_authority": False,
    }


def test_candidate_graph_is_deterministic() -> None:
    first = _graph()
    second = _graph()
    assert first == second
    assert len(first["typed_value_graph_sha256"]) == 64


def test_candidate_P_drift_fails_closed() -> None:
    symbols = _symbols(P=3)
    with pytest.raises(TypedCandidateValueError, match="CANDIDATE_P_SNAPSHOT_DRIFT"):
        produce_candidate_bound_value_graph(_snapshot(P=2), _provenance(), symbols)


@pytest.mark.parametrize(
    "flag",
    [
        "source_identity_exact",
        "gate_occurrence_provenance_exact",
        "frontend_chain_complete",
        "source_root_lineage_exact",
        "pass159_whole_expression_provenance_verified",
    ],
)
def test_missing_pass159_provenance_gate_fails_closed(flag: str) -> None:
    provenance = _provenance()
    provenance[flag] = False
    with pytest.raises(TypedCandidateValueError, match=flag.upper()):
        produce_candidate_bound_value_graph(_snapshot(), provenance, _symbols())


@pytest.mark.parametrize(
    "flag",
    [
        "boolean_gate_results_available",
        "membrane_input_ready",
        "canonical_monolithic_proof",
        "floating_point_authority",
        "vm81_mutation_authority",
        "hash72_commit_authority",
        "persistence_mutation_authority",
    ],
)
def test_input_cannot_smuggle_downstream_authority(flag: str) -> None:
    provenance = _provenance()
    provenance[flag] = True
    with pytest.raises(TypedCandidateValueError, match="AUTHORITY_ESCALATION"):
        produce_candidate_bound_value_graph(_snapshot(), provenance, _symbols())


def test_float_input_is_rejected() -> None:
    symbols = _symbols()
    symbols["s"] = 18.0
    with pytest.raises(TypedCandidateValueError, match="S_EXACT_RATIONAL_REQUIRED"):
        produce_candidate_bound_value_graph(_snapshot(), _provenance(), symbols)


def test_zero_delta_is_not_divided_through() -> None:
    # P=2, p=2, q=2 -> Delta=0.
    symbols = _symbols()
    symbols["p"] = 2
    symbols["q"] = 2
    graph = produce_candidate_bound_value_graph(_snapshot(), _provenance(), symbols)
    assert graph["value_nodes"][1]["value_status"] == "UNRESOLVED_EXACT_DOMAIN"
    assert graph["value_nodes"][2]["value_status"] == "UNRESOLVED_EXACT_DOMAIN"
    assert graph["joins"][0]["status"] == "UNRESOLVED"
    assert graph["joins"][1]["status"] == "UNRESOLVED"


def test_rational_mismatch_rejects_instead_of_becoming_a_typed_join() -> None:
    symbols = _symbols()
    symbols["t"] = 3
    graph = produce_candidate_bound_value_graph(_snapshot(), _provenance(), symbols)
    assert graph["decision"] == "REJECTED"
    assert graph["joins"][0]["status"] == "REJECTED"
    assert graph["joins"][0]["reason"] == "EXACT_RATIONAL_MISMATCH"


def test_service_self_test_stays_read_only() -> None:
    receipt = candidate_bound_full_symbolic_value_producer_self_test()
    assert receipt["ok"] is True
    assert receipt["term_count"] == 15
    assert receipt["join_count"] == 10
    assert receipt["canonical_monolithic_proof"] is False
    assert receipt["vm81_mutation_authority"] is False
    assert receipt["hash72_mint_authority"] is False
    assert receipt["hash216_persistence_authority"] is False


def test_new_surface_contains_no_float_or_scalarization_backdoors() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "hhs_runtime/pass219/typed_full_symbolic_candidate_values.py"
    )
    text = path.read_text(encoding="utf-8")
    for forbidden in (
        "math.sqrt",
        "numpy",
        "decimal.Decimal",
        "float(",
    ):
        assert forbidden not in text
    assert "ordinary_scalar_remainder_identity_claimed" in text
    assert "A_or_B_definitionally_P2" in text
    assert "scalar_coercion_used" in text
