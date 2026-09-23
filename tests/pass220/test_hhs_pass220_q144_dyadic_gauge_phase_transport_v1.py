from copy import deepcopy
from fractions import Fraction
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_q144_dyadic_gauge_phase_transport_v1 import (
    CONSTRUCTOR_SCHEMA,
    DYADIC_BASE,
    G3_B_G2,
    G72_AS_Q144_SOURCE,
    LOCAL_CONSTRAINTS,
    PHASE_OPERATOR_SOURCE,
    Q144_CELLS,
    Q144_HALF_STEPS_PER_G72_TOOTH,
    Q144_SIDE,
    Q144_STEP_SOURCE,
    Pass220I035TransportError,
    build_q144_dyadic_gauge_transport,
    g72_q144_bridge_witness,
    q144_dyadic_gauge_phase_transport_self_test,
    q144_exhaustive_transport_witness,
    q144_phase_address,
    q144_phase_step_descriptor,
    validate_q144_dyadic_gauge_transport,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_q144_step_is_exact_half_tooth_bridge():
    descriptor = q144_phase_step_descriptor()
    assert descriptor["source_term"] == Q144_STEP_SOURCE == "2^(1/144)"
    assert descriptor["dyadic_base"] == DYADIC_BASE == 2
    assert descriptor["q144_cells"] == Q144_CELLS == 144
    assert descriptor["g72_teeth"] == 72
    assert (
        descriptor["q144_half_steps_per_g72_tooth"]
        == Q144_HALF_STEPS_PER_G72_TOOTH
        == 2
    )
    assert descriptor["q144_step_exponent"] == {"numerator": 1, "denominator": 144}
    assert descriptor["two_q144_steps_exponent"] == {"numerator": 1, "denominator": 72}
    assert descriptor["g72_step_exponent"] == {"numerator": 1, "denominator": 72}
    assert descriptor["two_q144_steps_equal_one_g72_tooth"] is True
    assert descriptor["bridge_identity"] == G72_AS_Q144_SOURCE
    assert descriptor["scalar_root_evaluation_performed"] is False
    assert descriptor["host_float_arithmetic_used"] is False


@pytest.mark.parametrize(
    ("P", "index", "row", "col", "tooth", "half", "turns"),
    [
        (-145, 143, 11, 11, 71, 1, -2),
        (-1, 143, 11, 11, 71, 1, -1),
        (0, 0, 0, 0, 0, 0, 0),
        (1, 1, 0, 1, 0, 1, 0),
        (2, 2, 0, 2, 1, 0, 0),
        (143, 143, 11, 11, 71, 1, 0),
        (144, 0, 0, 0, 0, 0, 1),
        (145, 1, 0, 1, 0, 1, 1),
    ],
)
def test_q144_phase_address_preserves_wrap_and_unwrapped_provenance(
    P, index, row, col, tooth, half, turns
):
    address = q144_phase_address(P)
    assert address["P"] == P
    assert address["q144_index"] == index
    assert address["q144_row12"] == row
    assert address["q144_col12"] == col
    assert address["g72_tooth72"] == tooth
    assert address["g72_half_step2"] == half
    assert address["completed_q144_turns"] == turns
    assert address["phase_operator_source"] == PHASE_OPERATOR_SOURCE
    assert address["unwrapped_P_provenance_preserved"] is True
    assert address["same_wrapped_coordinate_does_not_identify_unwrapped_state"] is True
    assert address["scalar_root_evaluation_performed"] is False


def test_q144_torus_has_144_unique_cells_and_72_two_cell_teeth():
    rows = [q144_phase_address(P) for P in range(Q144_CELLS)]
    coords = {(row["q144_row12"], row["q144_col12"]) for row in rows}
    assert len(coords) == Q144_SIDE * Q144_SIDE == 144
    assert sorted(row["q144_index"] for row in rows) == list(range(144))

    tooth_counts = {}
    for row in rows:
        tooth_counts[row["g72_tooth72"]] = tooth_counts.get(row["g72_tooth72"], 0) + 1
    assert len(tooth_counts) == 72
    assert set(tooth_counts.values()) == {2}


def test_g72_bridge_reuses_i021_without_scalar_preemption():
    bridge = g72_q144_bridge_witness()
    assert bridge["q144_cells"] == 144
    assert bridge["g72_teeth"] == 72
    assert bridge["q144_half_steps_per_g72_tooth"] == 2
    assert bridge["exact_exponent_bridge"]["q144_two_steps"] == {
        "numerator": 1,
        "denominator": 72,
    }
    assert bridge["exact_exponent_bridge"]["g72_one_tooth"] == {
        "numerator": 1,
        "denominator": 72,
    }
    assert bridge["exact_exponent_bridge"]["equal"] is True
    assert bridge["g72_source_term"] == "2^(1/72)"
    assert bridge["q144_bridge_source_term"] == G72_AS_Q144_SOURCE
    assert bridge["g72_routed_cycles"] == 72
    assert bridge["phase_engine_coefficient"] == 2
    assert bridge["phase_matrix_144_closed"] is True
    assert bridge["generator_scalar_preemption"] is False
    assert bridge["host_float_arithmetic_used"] is False


@pytest.mark.parametrize("depth", [0, 1, 2, 72, 144, 10**30])
def test_phase_engine_output_does_not_inflate_gauge_metric(depth):
    constructor = build_q144_dyadic_gauge_transport(143, depth=depth)
    result = validate_q144_dyadic_gauge_transport(constructor)

    assert result["ok"] is True
    assert result["depth"] == depth
    assert result["q144_index"] == 143
    assert result["phase_engine_coefficient"] == 2
    assert result["canonical_metric_value"] == 1
    assert result["unit_gauge_lock_preserved"] is True
    assert result["dyadic_friction_decoupling_preserved"] is True
    assert result["phase_engine_not_metric_inflation"] is True

    assert constructor["holographic_lock"] == {
        "p4": 9,
        "c4": 9,
        "a_norm2": 1,
        "ratio": (1, 1),
    }
    assert constructor["transition_friction"] == G3_B_G2 == 7
    assert constructor["dyadic_base"] == DYADIC_BASE == 2
    assert constructor["canonical_magnitude_inflation"] is False


def test_full_q144_cycle_is_phase_coefficient_not_metric_replacement():
    constructor = build_q144_dyadic_gauge_transport(144, depth=144)
    full_cycle = constructor["full_cycle_engine"]
    assert full_cycle["q144_steps"] == 144
    assert full_cycle["exact_total_exponent"] == {"numerator": 1, "denominator": 1}
    assert full_cycle["dyadic_engine_coefficient"] == 2
    assert full_cycle["engine_coefficient_semantics"] == "PHASE_GENERATOR_CYCLE_OUTPUT"
    assert full_cycle["canonical_metric_value"] == 1
    assert full_cycle["coefficient_is_canonical_metric_inflation"] is False


def test_wrapped_coordinate_does_not_erase_turn_provenance():
    base = q144_phase_address(17)
    next_turn = q144_phase_address(161)
    assert base["q144_index"] == next_turn["q144_index"] == 17
    assert base["q144_row12"] == next_turn["q144_row12"]
    assert base["q144_col12"] == next_turn["q144_col12"]
    assert next_turn["completed_q144_turns"] == base["completed_q144_turns"] + 1
    assert base["P"] != next_turn["P"]
    assert base["exact_exponent"] != next_turn["exact_exponent"]


def test_constructor_contains_constraints_without_canonical_authority():
    constructor = build_q144_dyadic_gauge_transport(37, depth=9)
    assert constructor["schema"] == CONSTRUCTOR_SCHEMA
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


def test_exhaustive_witness_closes_all_q144_addresses():
    witness = q144_exhaustive_transport_witness()
    assert witness["q144_address_count"] == 144
    assert witness["unique_q144_coordinates"] == 144
    assert witness["all_q144_indices_exactly_once"] is True
    assert witness["all_72_teeth_have_two_half_steps"] is True
    assert witness["half_step_counts"] == {0: 72, 1: 72}
    assert witness["all_wrap_pairs_preserve_coordinate"] is True
    assert witness["all_wrap_pairs_advance_turn_provenance"] is True
    assert witness["all_depths_preserve_phase_metric_separation"] is True


def test_tampering_and_invalid_inputs_fail_closed():
    constructor = build_q144_dyadic_gauge_transport(5, depth=1)

    tampered = deepcopy(constructor)
    tampered["dyadic_base"] = 7
    with pytest.raises(Pass220I035TransportError, match="receipt mismatch"):
        validate_q144_dyadic_gauge_transport(tampered)

    tampered = deepcopy(constructor)
    tampered["canonical_constraint_creation_authority"] = True
    with pytest.raises(Pass220I035TransportError, match="receipt mismatch"):
        validate_q144_dyadic_gauge_transport(tampered)

    with pytest.raises(Pass220I035TransportError):
        q144_phase_address(1.0)
    with pytest.raises(Pass220I035TransportError):
        build_q144_dyadic_gauge_transport(0, depth=-1)


def test_i035_self_test_closes():
    result = q144_dyadic_gauge_phase_transport_self_test()
    assert result["ok"] is True
    witness = result["witness"]
    assert witness["q144_address_count"] == 144
    assert witness["unique_q144_coordinates"] == 144
    assert witness["all_72_teeth_have_two_half_steps"] is True
    assert witness["all_wrap_pairs_advance_turn_provenance"] is True
    assert witness["all_depths_preserve_phase_metric_separation"] is True


def test_service_registry_declares_i035_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.q144_dyadic_gauge_phase_transport.self_test" in source
    assert "hhs_pass220_q144_dyadic_gauge_phase_transport_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.q144_dyadic_gauge_phase_transport.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_q144_dyadic_gauge_phase_transport_v1"
        ),
        "function": "q144_dyadic_gauge_phase_transport_self_test",
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
            "HHS_PASS_220_I035_Q144_DYADIC_GAUGE_PHASE_TRANSPORT_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I035_Q144_DYADIC_GAUGE_TRANSPORT_WITNESS_V1",
        ],
        "validators": [
            "validate_q144_dyadic_gauge_phase_transport",
            "q144_dyadic_gauge_phase_transport_self_test",
        ],
        "rejection_codes": [
            "REJECT_I035_Q144_G72_BRIDGE_DRIFT",
            "REJECT_I035_PHASE_ADDRESS_DRIFT",
            "REJECT_I035_TURN_PROVENANCE_LOSS",
            "REJECT_I035_PHASE_METRIC_CONFLATION",
            "REJECT_I035_DYADIC_FRICTION_REBIND",
            "REJECT_I035_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": (
            "READ_ONLY_Q144_DYADIC_GAUGE_CONSTRUCTOR_NO_VM81_MUTATION"
        ),
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
