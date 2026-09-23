from copy import deepcopy
from fractions import Fraction
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_holographic_gauge_dyadic_decoupling_v1 import (
    CANONICAL_A_NORM2,
    CANONICAL_C4,
    CANONICAL_P4,
    CONFORMAL_INVARIANT_ID,
    DYADIC_BASE,
    G3_A_G2,
    G3_B_G2,
    G3_C_G2,
    LOCAL_CONSTRAINTS,
    Q144_PHASE_DENOMINATOR,
    Pass220I034GaugeError,
    build_holographic_gauge_constructor,
    conformal_gauge_descriptor,
    dyadic_operator_descriptor,
    gauge_depth_projection,
    holographic_gauge_dyadic_decoupling_self_test,
    holographic_lock_witness,
    validate_holographic_gauge_constructor,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_holographic_lock_is_exact_unit_ratio():
    witness = holographic_lock_witness()
    assert witness["p4"] == CANONICAL_P4 == 9
    assert witness["c4"] == CANONICAL_C4 == 9
    assert witness["a_norm2"] == CANONICAL_A_NORM2 == 1
    assert Fraction(
        witness["ratio_numerator"],
        witness["ratio_denominator"],
    ) == Fraction(1, 1)
    assert witness["p4_over_c4_equals_a_norm2"] is True
    assert witness["cross_product_lock"] is True
    assert witness["p4_equals_c4"] is True
    assert witness["canonical_normalization_unit_retained"] is True
    assert witness["host_float_arithmetic_used"] is False


def test_g3_4711_coordinates_do_not_replace_normalization_unit():
    constructor = build_holographic_gauge_constructor(1)
    projection = constructor["gauge_projection"]
    assert tuple(projection["source_coordinates"]) == (1, 2, 3)
    assert tuple(projection["target_coordinates"]) == (4, 7, 11)
    assert (G3_A_G2, G3_B_G2, G3_C_G2) == (4, 7, 11)
    assert constructor["holographic_lock"]["a_norm2"] == 1
    assert projection["physical_scalar_expansion_authority"] is False
    assert projection["canonical_metric_replacement_authority"] is False


def test_dyadic_operator_is_decoupled_from_transition_friction():
    descriptor = dyadic_operator_descriptor()
    assert descriptor["dyadic_base"] == DYADIC_BASE == 2
    assert descriptor["transition_friction"] == G3_B_G2 == 7
    assert descriptor["base_distinct_from_transition_friction"] is True
    assert descriptor["q144_denominator"] == Q144_PHASE_DENOMINATOR == 144
    assert descriptor["expression"]["source"] == "2^(P*a_norm^2/144)"
    assert descriptor["expression"]["base"] == 2
    assert descriptor["expression"]["exponent"]["denominator"] == 144
    assert descriptor["evaluated_to_host_float"] is False
    assert descriptor["operator_semantics"] == "PHASE_GENERATOR"


@pytest.mark.parametrize("depth", [0, 1, 2, 9, 72, 144, 10**30])
def test_arbitrary_discrete_depth_changes_index_not_canonical_magnitude(depth):
    state = gauge_depth_projection(depth)
    assert state["depth"] == depth
    assert state["resolution_index"] == depth
    assert state["canonical_ratio"] == (1, 1)
    assert state["canonical_a_norm2"] == 1
    assert state["canonical_p4"] == 9
    assert state["canonical_c4"] == 9
    assert state["canonical_magnitude_inflation"] is False
    assert state["depth_multiplies_canonical_p4"] is False
    assert state["depth_multiplies_canonical_c4"] is False
    assert state["depth_multiplies_a_norm2"] is False


def test_conformal_invariant_is_typed_identity_not_scalar_quotient_claim():
    descriptor = conformal_gauge_descriptor()
    assert descriptor["invariant_id"] == CONFORMAL_INVARIANT_ID
    assert descriptor["genesis_view"]["coordinates"] == (1, 2, 3)
    assert descriptor["g3_4711_view"]["coordinates"] == (4, 7, 11)
    assert (
        descriptor["genesis_view"]["invariant_id"]
        == descriptor["g3_4711_view"]["invariant_id"]
        == CONFORMAL_INVARIANT_ID
    )
    assert descriptor["preserved_by_gauge_projection"] is True
    assert descriptor["ordinary_scalar_ratio_equality_claimed"] is False
    assert descriptor["typed_relation_only"] is True


def test_constructor_preserves_ppq_provenance_and_typed_closure():
    constructor = build_holographic_gauge_constructor(144)
    result = validate_holographic_gauge_constructor(constructor)

    assert result["ok"] is True
    assert result["canonical_ratio"] == Fraction(1, 1)
    assert result["gauge_coordinates"] == (4, 7, 11)
    assert result["transition_friction"] == 7
    assert result["dyadic_base"] == 2
    assert result["dyadic_operator_source"] == "2^(P*a_norm^2/144)"
    assert result["p_p_q_provenance_preserved"] is True
    assert result["typed_zero_closure_preserved"] is True
    assert result["omega_true"] is True

    closure = constructor["closure_state"]
    assert closure["delta_e"]["kind"] == "HHS_TYPED_ZERO"
    assert closure["psi"]["kind"] == "HHS_TYPED_ZERO"
    assert closure["delta_e"]["untyped_empty_scalar"] is False
    assert closure["psi"]["untyped_empty_scalar"] is False
    assert closure["omega"]["value"] is True


def test_constructor_contains_constraints_without_canonical_authority():
    constructor = build_holographic_gauge_constructor(2)
    assert constructor["contains_constraints"] is True
    assert tuple(constructor["local_constraints"]) == LOCAL_CONSTRAINTS
    assert constructor["constraint_authority"] == "CONSTRUCTOR_LOCAL_ONLY"
    assert constructor["canonical_service"] is False
    assert constructor["canonical_constraint_creation_authority"] is False
    assert constructor["canonical_constraint_enforcement_authority"] is False
    assert constructor["canonical_vm81_mutation_authority"] is False
    assert constructor["canonical_hash72_authority"] is False
    assert constructor["canonical_hash216_authority"] is False
    assert constructor["direct_canonical_persistence_authority"] is False


def test_tampering_fails_closed():
    constructor = build_holographic_gauge_constructor(9)

    tampered = deepcopy(constructor)
    tampered["dyadic_engine"]["base"] = 7
    with pytest.raises(Pass220I034GaugeError, match="receipt mismatch"):
        validate_holographic_gauge_constructor(tampered)

    tampered = deepcopy(constructor)
    tampered["canonical_constraint_creation_authority"] = True
    with pytest.raises(Pass220I034GaugeError, match="receipt mismatch"):
        validate_holographic_gauge_constructor(tampered)


def test_invalid_holographic_lock_and_depth_fail_closed():
    with pytest.raises(Pass220I034GaugeError):
        holographic_lock_witness(c4=0)
    with pytest.raises(Pass220I034GaugeError):
        gauge_depth_projection(-1)
    with pytest.raises(Pass220I034GaugeError):
        gauge_depth_projection(1.0)


def test_i034_self_test_closes():
    result = holographic_gauge_dyadic_decoupling_self_test()
    assert result["ok"] is True
    witness = result["witness"]
    assert witness["all_depths_preserve_unit_ratio"] is True
    assert witness["all_depths_preserve_a_norm2"] is True
    assert witness["all_depths_keep_transition_friction_7"] is True
    assert witness["all_depths_keep_dyadic_base_2"] is True
    assert witness["all_depths_no_canonical_magnitude_inflation"] is True
    assert witness["closure"] == {
        "delta_e": "TYPED_ZERO",
        "psi": "TYPED_ZERO",
        "omega": True,
    }


def test_service_registry_declares_i034_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.holographic_gauge_dyadic_decoupling.self_test" in source
    assert "hhs_pass220_holographic_gauge_dyadic_decoupling_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.holographic_gauge_dyadic_decoupling.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_holographic_gauge_dyadic_decoupling_v1"
        ),
        "function": "holographic_gauge_dyadic_decoupling_self_test",
        "service_type": "pass220_validated_operation_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I034_HOLOGRAPHIC_GAUGE_DYADIC_DECOUPLING_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I034_GAUGE_DYADIC_WITNESS_V1",
        ],
        "validators": [
            "validate_holographic_gauge_dyadic_decoupling",
            "holographic_gauge_dyadic_decoupling_self_test",
        ],
        "rejection_codes": [
            "REJECT_I034_HOLOGRAPHIC_LOCK_DRIFT",
            "REJECT_I034_GAUGE_SCALAR_INFLATION",
            "REJECT_I034_DYADIC_FRICTION_REBIND",
            "REJECT_I034_CONFORMAL_IDENTITY_DRIFT",
            "REJECT_I034_TYPED_ZERO_COLLAPSE",
            "REJECT_I034_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_GAUGE_CONSTRUCTOR_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
