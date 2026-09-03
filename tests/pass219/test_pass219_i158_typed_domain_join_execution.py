from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from hhs_runtime.pass219.typed_domain_join_executor import (
    MODULAR_WITNESS_SCHEMA,
    SCHEMA,
    TypedDomainExecutionError,
    execute_typed_domain_joins,
    project_rational_to_modular,
    typed_domain_join_executor_self_test,
)
from hhs_runtime.pass219.typed_full_symbolic_candidate_values import (
    CANDIDATE_SCHEMA,
    COMBINED_SOURCE_SHA256,
    PROVENANCE_SCHEMA,
    produce_candidate_bound_value_graph,
)


def _snapshot(P: int = 30) -> dict[str, object]:
    return {
        "schema": "HHS_PASS219_I153_LOCAL_HASH216_5184_P_SNAPSHOT_V1",
        "snapshot_hash216": "2" * 64,
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


def _symbols(*, m: int = 267) -> dict[str, object]:
    return {
        "schema": CANDIDATE_SCHEMA,
        "P": 30,
        "p": 29,
        "q": 31,
        "t": 30,
        "m": m,
        "s": {"numerator": 2, "denominator": 25},
        "f": 900,
        "At": 1,
        "Bt": 1,
        "x": 18,
        "y": 54,
        "z": 18,
        "w": 54,
    }


def _graph(*, m: int = 267) -> dict[str, object]:
    return produce_candidate_bound_value_graph(
        _snapshot(), _provenance(), _symbols(m=m)
    )


def test_modular_closure_candidate_is_exact_before_i158_execution() -> None:
    graph = _graph()
    nodes = graph["value_nodes"]
    assert nodes[0]["payload"]["value"]["text"] == "26970"
    assert nodes[1]["payload"]["value"]["text"] == "26970"
    assert nodes[2]["payload"]["value"]["text"] == "26970"
    assert nodes[3]["payload"]["representative"] == 1
    assert nodes[3]["payload"]["modulus"] == 899
    assert nodes[4]["payload"]["value"]["text"] == "71022"
    assert graph["joins"][0]["status"] == "PROVED"
    assert graph["joins"][1]["status"] == "PROVED"
    assert graph["joins"][2]["status"] == "UNRESOLVED"
    assert graph["joins"][3]["status"] == "UNRESOLVED"


def test_i158_executes_both_modular_pivots_as_typed_projections() -> None:
    result = execute_typed_domain_joins(_graph())
    assert result["schema"] == SCHEMA
    assert result["decision"] == "PARTIALLY_RESOLVED"
    assert result["counts"] == {
        "join_count": 10,
        "proved": 7,
        "unresolved": 3,
        "rejected": 0,
        "newly_resolved_modular_pivots": 2,
    }
    assert result["executed_joins"][2]["execution_status"] == "PROVED"
    assert result["executed_joins"][3]["execution_status"] == "PROVED"
    assert result["executed_joins"][2]["execution_reason"] == "EXACT_TYPED_MODULAR_CLASS_MATCH"
    assert result["executed_joins"][3]["execution_reason"] == "EXACT_TYPED_MODULAR_CLASS_MATCH"


def test_modular_projection_witness_preserves_type_boundary() -> None:
    result = execute_typed_domain_joins(_graph())
    witnesses = result["modular_projection_witnesses"]
    assert len(witnesses) == 2
    for witness in witnesses:
        assert witness["schema"] == MODULAR_WITNESS_SCHEMA
        assert witness["status"] == "PROVED"
        assert witness["modulus"] == 899
        assert witness["projected_representative"] == 1
        assert witness["modular_representative"] == 1
        assert witness["ordinary_scalar_remainder_identity_claimed"] is False
        assert witness["scalar_coercion_used"] is False
        assert witness["reverse_inference_authorized"] is False
        assert witness["projection_audit"]["injective"] is False
        assert witness["projection_audit"]["reverse_rule"] is None
        assert "unique_scalar_preimage" in witness["projection_audit"]["lost_information"]
        assert len(witness["projection_witness_sha256"]) == 64


def test_left_modular_projection_is_26970_mod_899_equals_1() -> None:
    result = execute_typed_domain_joins(_graph())
    left = result["modular_projection_witnesses"][0]
    assert left["scalar_term_id"] == 2
    assert left["rational"] == {"numerator": 26970, "denominator": 1}
    assert left["denominator_inverse"] == 1
    assert left["projected_representative"] == 1


def test_right_modular_projection_is_71022_mod_899_equals_1() -> None:
    result = execute_typed_domain_joins(_graph())
    right = result["modular_projection_witnesses"][1]
    assert right["scalar_term_id"] == 4
    assert right["rational"] == {"numerator": 71022, "denominator": 1}
    assert right["denominator_inverse"] == 1
    assert right["projected_representative"] == 1


def test_modular_mismatch_rejects_exactly_not_unresolved() -> None:
    # m=268 -> m^2-m does not project to [1] mod 899.
    result = execute_typed_domain_joins(_graph(m=268))
    assert result["decision"] == "REJECTED"
    assert result["executed_joins"][3]["execution_status"] == "REJECTED"
    assert result["executed_joins"][3]["execution_reason"] == "EXACT_TYPED_MODULAR_CLASS_MISMATCH"
    assert result["counts"]["rejected"] == 1


def test_noninvertible_rational_denominator_remains_unresolved() -> None:
    graph = _graph()
    scalar = deepcopy(graph["value_nodes"][2])
    scalar["payload"]["value"] = {
        "numerator": 1,
        "denominator": 29,
        "text": "1/29",
    }
    modular = graph["value_nodes"][3]
    witness = project_rational_to_modular(
        scalar,
        modular,
        scalar_term_id=2,
        modular_term_id=3,
        candidate_binding_sha256=graph["candidate_binding_sha256"],
    )
    assert witness["status"] == "UNRESOLVED"
    assert witness["reason"] == "RATIONAL_DENOMINATOR_NOT_INVERTIBLE_IN_MODULAR_DOMAIN"
    assert witness["reverse_inference_authorized"] is False


def test_remaining_three_blockers_are_explicit_and_repository_bound() -> None:
    result = execute_typed_domain_joins(_graph())
    assert result["remaining_blockers"] == [
        {
            "edge_index": 7,
            "join_kind": "AB_ROOT_CORRESPONDENCE",
            "reason": "BOUNDARY_PRODUCT_BINDING_REQUIRED",
        },
        {
            "edge_index": 8,
            "join_kind": "MONOLITHIC_BOUNDARY_EQUALITY",
            "reason": "COMPLETE_MONOLITHIC_BOUNDARY_EXECUTOR_REQUIRED",
        },
        {
            "edge_index": 9,
            "join_kind": "DELTA_RADICAL_PROJECTION",
            "reason": "PASS191_X_SQUARED_PHASE_BINDING_REQUIRED",
        },
    ]
    blockers = result["repository_blocker_evidence"]
    assert blockers["pass191_kernel"]["x_squared_binding_unresolved"] is True
    assert blockers["pass169_contract"]["symbolic_radical_runtime_required"] is True
    assert blockers["pass169_contract"]["exact_algebraic_equality_required"] is True
    assert blockers["pass169_contract"]["vm81_execution_required_for_canonical_commit"] is True
    assert blockers["pass169_contract"]["hash72_receipt_required_for_canonical_commit"] is True
    assert len(blockers["pass191_kernel"]["sha256"]) == 64
    assert len(blockers["pass169_contract"]["sha256"]) == 64


def test_no_downstream_authority_is_manufactured() -> None:
    result = execute_typed_domain_joins(_graph())
    assert result["authority"] == {
        "typed_join_execution_complete": False,
        "canonical_monolithic_boundary_proof": False,
        "pass169_terminal_proof": False,
        "vm81_execution_verified": False,
        "vm81_mutation_authority": False,
        "hash72_execution_receipt_verified": False,
        "hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "deterministic_replay_verified": False,
        "floating_point_authority": False,
    }
    assert result["next_boundary"] == "BOUNDARY_VALUE_EVALUATOR_AND_PHASE_EXPONENT_BINDING"


def test_i157_graph_hash_tampering_fails_closed() -> None:
    graph = _graph()
    graph["value_nodes"][3]["payload"]["representative"] = 2
    with pytest.raises(TypedDomainExecutionError, match="I157_GRAPH_SHA256_MISMATCH"):
        execute_typed_domain_joins(graph)


def test_i157_authority_smuggling_fails_closed_even_with_rehashed_graph() -> None:
    graph = _graph()
    graph["authority"]["vm81_execution_verified"] = True
    core = dict(graph)
    core.pop("typed_value_graph_sha256")
    import hashlib, json

    graph["typed_value_graph_sha256"] = hashlib.sha256(
        json.dumps(
            core,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    with pytest.raises(TypedDomainExecutionError, match="I157_UPSTREAM_AUTHORITY_ESCALATION"):
        execute_typed_domain_joins(graph)


def test_executor_is_deterministic() -> None:
    first = execute_typed_domain_joins(_graph())
    second = execute_typed_domain_joins(_graph())
    assert first == second
    assert len(first["execution_membrane_sha256"]) == 64


def test_public_self_test_closes_only_modular_pivots() -> None:
    receipt = typed_domain_join_executor_self_test()
    assert receipt["ok"] is True
    assert receipt["decision"] == "PARTIALLY_RESOLVED"
    assert receipt["proved"] == 7
    assert receipt["unresolved"] == 3
    assert receipt["rejected"] == 0
    assert receipt["newly_resolved_modular_pivots"] == 2
    assert receipt["canonical_monolithic_boundary_proof"] is False
    assert receipt["vm81_mutation_authority"] is False
    assert receipt["hash72_mint_authority"] is False
    assert receipt["hash216_persistence_authority"] is False


def test_new_surface_has_no_float_or_approximate_admission_path() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "hhs_runtime/pass219/typed_domain_join_executor.py"
    )
    text = path.read_text(encoding="utf-8")
    for forbidden in (
        "math.sqrt",
        "numpy",
        "decimal.Decimal",
        "float(",
        "isclose",
        "tolerance",
    ):
        assert forbidden not in text
    assert "reverse_inference_authorized" in text
    assert "ordinary_scalar_remainder_identity_claimed" in text
    assert "PASS191_X_SQUARED_PHASE_BINDING_REQUIRED" in text
