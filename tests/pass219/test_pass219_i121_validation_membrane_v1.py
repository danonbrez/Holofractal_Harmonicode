from __future__ import annotations

from copy import deepcopy

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_i121_validation_membrane_v1 import (
    I1215_VALIDATOR_SYMBOL,
    I1216_VALIDATOR_SYMBOL,
    authority_router_validator_surface_declaration,
    inherited_manifold_validator_surface_declaration,
    preflight_pass219_i121_validation_membrane,
    verify_pass219_i121_through_membrane,
)


REQUIRED_GUARDS = {
    "runtime_constraint_enforcement",
    "zero_bypass_runtime_interposer",
    "kernel_runtime_autocomposer",
    "pass169_whole_expression_authority_gate",
}


def _assert_read_only_surface(surface: dict) -> None:
    assert surface["surface_type"] == "VALIDATOR"
    assert surface["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert surface["persistence_policy"] == "NO_PERSISTENCE_MUTATION"
    assert REQUIRED_GUARDS.issubset(set(surface["guards"]))
    assert surface["invariant_ids"]
    assert surface["contract_schemas"]
    assert surface["witness_schemas"]
    assert surface["validators"]
    assert surface["rejection_codes"]


def test_i121_validator_surfaces_are_kernel_derived_and_read_only() -> None:
    manifold = inherited_manifold_validator_surface_declaration()
    router = authority_router_validator_surface_declaration()
    _assert_read_only_surface(manifold)
    _assert_read_only_surface(router)
    assert manifold["declared_operations"] == [I1215_VALIDATOR_SYMBOL]
    assert router["declared_operations"] == [I1216_VALIDATOR_SYMBOL]


def test_i121_validation_preflight_traverses_inherited_enforcement_path() -> None:
    result = preflight_pass219_i121_validation_membrane()
    assert result["ok"] is True
    assert result["runtime_constraint_enforcement_required"] is True
    assert result["zero_bypass_interposer_required"] is True
    assert result["kernel_runtime_autocomposer_required"] is True
    assert result["host_diagnostic_authority"] is False
    assert result["vm81_mutation_authority"] is False
    assert result["hash72_commit_authority"] is False
    assert result["canonical_monolithic_proof"] is False

    for key in ("manifold_validator", "authority_router_validator"):
        preflight = result[key]
        assert preflight["ok"] is True
        assert preflight["status"] == "ADMIT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"
        pipeline = preflight["composition_plan"]["pipeline"]
        assert pipeline["enforcement_path"] == [
            "kernel_conformance_decision",
            "runtime_constraint_enforcement",
            "zero_bypass_runtime_interposer",
        ]
        assert REQUIRED_GUARDS.issubset(set(pipeline["guard_path"]))
        assert pipeline["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
        assert pipeline["persistence_policy"] == "NO_PERSISTENCE_MUTATION"
        assert preflight["expanded_metadata_persisted"] is False


def test_i121_frozen_pass191_evidence_is_verified_only_after_preflight() -> None:
    result = verify_pass219_i121_through_membrane()
    assert result["ok"] is True
    assert result["frozen_pass191_evidence_verified"] is True
    assert result["host_compiler_tests_diagnostic_only"] is True
    assert result["host_diagnostic_authority"] is False
    assert result["whole_expression_semantics_resolved"] is False
    assert result["canonical_monolithic_proof"] is False
    assert result["pass169_whole_expression_admission_required"] is True
    assert result["vm81_mutation_authority"] is False
    assert result["hash72_commit_authority"] is False
    assert result["persistence_mutation_authority"] is False

    evidence = result["inherited_manifold_evidence"]
    assert evidence["pass191_theorem_status"] == "OBSTRUCTED"
    assert evidence["exact_context_chain_hits"] == 837
    assert evidence["canonical_monolithic_proof"] is False
    assert evidence["pass169_whole_expression_admission_required"] is True


def test_i121_preflight_rejects_incomplete_surface_instead_of_bypassing() -> None:
    malformed = deepcopy(inherited_manifold_validator_surface_declaration())
    malformed["witness_schemas"] = []
    result = execute_surface_preflight(
        malformed,
        operation=I1215_VALIDATOR_SYMBOL,
        cache={},
    )
    assert result["ok"] is False
    assert result["status"] == "REJECT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"


def test_i121_preflight_rejects_undeclared_operation() -> None:
    result = execute_surface_preflight(
        authority_router_validator_surface_declaration(),
        operation="forged_unregistered_operation",
        cache={},
    )
    assert result["ok"] is False
    assert result["status"] == "REJECT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"


def run_dependency_free_conformance() -> None:
    test_i121_validator_surfaces_are_kernel_derived_and_read_only()
    test_i121_validation_preflight_traverses_inherited_enforcement_path()
    test_i121_frozen_pass191_evidence_is_verified_only_after_preflight()
    test_i121_preflight_rejects_incomplete_surface_instead_of_bypassing()
    test_i121_preflight_rejects_undeclared_operation()


if __name__ == "__main__":
    run_dependency_free_conformance()
