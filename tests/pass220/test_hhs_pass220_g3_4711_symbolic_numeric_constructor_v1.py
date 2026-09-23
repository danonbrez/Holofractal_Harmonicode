from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_g3_4711_symbolic_numeric_constructor_v1 import (
    G3_BASE_SCALE,
    G3_LIFTED_SCALE,
    LOCAL_CONSTRAINTS,
    REPRESENTATION_VIEW_NAMES,
    Pass220I033ConstructorError,
    build_solver_constructor,
    g3_4711_scaling_witness,
    g3_4711_symbolic_numeric_constructor_self_test,
    recover_solver_constructor,
    validate_solver_constructor,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def _sample():
    source = "A/B*B/A == P^4 == c^4 == TRUE"
    raw = bytes.fromhex("3fb999999999999a")
    offsets = tuple((index * 7 + 3) % 9 for index in range(81))
    return source, raw, offsets


def test_g3_4711_scale_preserves_relation_without_uniform_scalar_reduction():
    witness = g3_4711_scaling_witness()
    assert witness["base_scale"] == G3_BASE_SCALE == (1, 2, 3)
    assert witness["lifted_scale"] == G3_LIFTED_SCALE == (4, 7, 11)
    assert witness["base_closure"] is True
    assert witness["lifted_closure"] is True
    assert witness["same_relation_preserved"] is True
    assert witness["uniform_scalar_multiplier"] is False
    assert witness["scaling_law_retained_as_constructor_relation"] is True
    assert witness["scalar_reduction_used"] is False


def test_constructor_keeps_all_distinct_views_co_resident_and_roundtrips():
    source, raw, offsets = _sample()
    constructor = build_solver_constructor(source, raw, "binary64", offsets)
    result = validate_solver_constructor(constructor)
    recovered = recover_solver_constructor(constructor)

    assert result["ok"] is True
    assert recovered["source_text"] == source
    assert recovered["raw_ieee"] == raw
    assert recovered["offsets"] == offsets
    assert recovered["format"] == "binary64"
    assert recovered["exact_dyadic"]["numerator"] == 3602879701896397
    assert recovered["exact_dyadic"]["denominator"] == 36028797018963968

    views = constructor["representation_views"]
    assert tuple(constructor["representation_view_names"]) == REPRESENTATION_VIEW_NAMES
    assert set(views) == set(REPRESENTATION_VIEW_NAMES)
    assert len(views["bigint_5184"]) == 5184
    assert views["source_symbol_state"]["forward_hex"] == source.encode("utf-8").hex()
    assert views["ieee_storage_state"]["scalar_bits_hex"] == raw.hex()
    assert views["exact_dyadic_projection"] == recovered["exact_dyadic"]
    assert views["full_g3_phase_tensor"] == views["ieee_storage_state"]["forward_tensor"]
    assert isinstance(views["scalar_bigint_projection"], int)


def test_constructor_contains_constraints_without_constraint_authority():
    source, raw, offsets = _sample()
    constructor = build_solver_constructor(source, raw, "binary64", offsets)

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
    assert (
        constructor["repository_os_hydration_role"]
        == "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
    )


def test_reductionist_substitution_is_not_the_constructor_model():
    source, raw, offsets = _sample()
    constructor = build_solver_constructor(source, raw, "binary64", offsets)
    views = constructor["representation_views"]

    assert constructor["reduction_policy"] == "NO_DISTINCT_INFORMATION_VIEW_DISCARDED"
    assert constructor["symbolic_logic_view_present"] is True
    assert constructor["ieee_floating_state_view_present"] is True
    assert constructor["exact_numeric_view_present"] is True
    assert constructor["bigint_view_present"] is True
    assert constructor["phase_geometric_view_present"] is True
    assert constructor["palindromic_reciprocal_view_present"] is True
    assert views["source_symbol_state"] != views["ieee_storage_state"]
    assert views["bigint_5184"] != source
    assert views["scalar_bigint_projection"] != int.from_bytes(raw, "big")


def test_tampered_constructor_fails_closed():
    source, raw, offsets = _sample()
    constructor = build_solver_constructor(source, raw, "binary64", offsets)

    tampered = deepcopy(constructor)
    encoded = tampered["representation_views"]["bigint_5184"]
    tampered["representation_views"]["bigint_5184"] = (
        ("-" if encoded[0] == "+" else "+") + encoded[1:]
    )
    with pytest.raises(Pass220I033ConstructorError, match="receipt mismatch"):
        validate_solver_constructor(tampered)

    tampered = deepcopy(constructor)
    tampered["canonical_constraint_creation_authority"] = True
    with pytest.raises(Pass220I033ConstructorError, match="receipt mismatch"):
        validate_solver_constructor(tampered)


def test_invalid_shape_fails_closed():
    source, raw, offsets = _sample()
    with pytest.raises(Pass220I033ConstructorError):
        build_solver_constructor(source, raw, "binary64", offsets[:-1])
    with pytest.raises(Pass220I033ConstructorError):
        build_solver_constructor(source, b"\x00", "binary64", offsets)


def test_i033_self_test_closes():
    result = g3_4711_symbolic_numeric_constructor_self_test()
    assert result["ok"] is True
    assert result["witness"]["source_roundtrip_exact"] is True
    assert result["witness"]["ieee_roundtrip_exact"] is True
    assert result["witness"]["offset_roundtrip_exact"] is True
    assert result["witness"]["constructor_contains_constraints"] is True
    assert result["witness"]["constructor_has_constraint_authority"] is False


def test_service_registry_declares_i033_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.g3_4711_symbolic_numeric_constructor.self_test" in source
    assert "hhs_pass220_g3_4711_symbolic_numeric_constructor_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.g3_4711_symbolic_numeric_constructor.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_g3_4711_symbolic_numeric_constructor_v1"
        ),
        "function": "g3_4711_symbolic_numeric_constructor_self_test",
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
            "HHS_PASS_220_I033_G3_4711_SYMBOLIC_NUMERIC_SOLVER_CONSTRUCTOR_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I033_G3_4711_MULTI_VIEW_WITNESS_V1",
        ],
        "validators": [
            "validate_g3_4711_symbolic_numeric_constructor",
            "g3_4711_symbolic_numeric_constructor_self_test",
        ],
        "rejection_codes": [
            "REJECT_G3_4711_SCALE_DRIFT",
            "REJECT_CO_RESIDENT_VIEW_LOSS",
            "REJECT_I033_RECIPROCAL_RETURN_MISMATCH",
            "REJECT_I033_5184_ROUNDTRIP_MISMATCH",
            "REJECT_I033_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_VALIDATED_CONSTRUCTOR_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
