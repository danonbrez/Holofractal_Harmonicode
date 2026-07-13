from hhs_runtime.hhs_kernel_conformance_decision_v1 import (
    ADMIT_MULTI_INVARIANT_DERIVATION,
    REJECT_MISSING_VALIDATOR_BINDING,
    REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT,
    REJECT_UNDERIVED_RUNTIME_SURFACE,
    evaluate_operation,
    evaluate_surface,
)


def test_fully_derived_surface_is_admitted():
    decision = evaluate_surface({
        "surface_id": "service:control_flow.transition_audit_self_test",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I001", "HHS-I003", "HHS-I007"],
        "contract_schemas": ["HHS_CONTROL_FLOW_TRANSITION_AUDIT_SELF_TEST_V1"],
        "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1"],
        "validators": ["validate_control_flow_transition_audit"],
        "rejection_codes": ["REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
    })
    assert decision["derivation_complete"] is True
    assert decision["status"] == ADMIT_MULTI_INVARIANT_DERIVATION
    assert decision["derivation_root_hash72"]


def test_surface_with_no_invariant_is_rejected():
    decision = evaluate_surface({"surface_id": "service:undocumented", "surface_type": "SERVICE"})
    assert decision["status"] == REJECT_UNDERIVED_RUNTIME_SURFACE
    assert decision["derivation_complete"] is False


def test_surface_with_missing_validator_is_rejected():
    decision = evaluate_surface({
        "surface_id": "service:no_validator",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I011"],
        "contract_schemas": ["C"],
        "witness_schemas": ["W"],
        "validators": [],
        "rejection_codes": ["R"],
    })
    assert REJECT_MISSING_VALIDATOR_BINDING in decision["reasons"]


def test_operation_outside_declared_derivation_is_rejected():
    decision = evaluate_operation({
        "surface_id": "service:example",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I011"],
        "contract_schemas": ["C"],
        "witness_schemas": ["W"],
        "validators": ["V"],
        "rejection_codes": ["R"],
        "declared_operations": ["allowed"],
    }, "forbidden")
    assert decision["status"] == REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT
