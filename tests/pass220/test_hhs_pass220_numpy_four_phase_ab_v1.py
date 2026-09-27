from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_numpy_four_phase_ab_v1 import (
    CHANNELS,
    ORDERED_TENSOR_LITERAL,
    PHASE_PLAN,
    experiment_acceptance,
    four_phase_ab_witness_for_scalar,
    supplied_tensor_u9_acceptance,
    supplied_tensor_u9_witness,
    scalar_offset_vector_inverse,
    scalar_offset_vector_transform,
    substitution_tensor_transform,
)
from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import HHSNumPyScalar


@pytest.mark.parametrize(
    "bits",
    (
        0x0000000000000000,
        0x8000000000000000,
        0x3FB999999999999A,
        0xBFF0000000000000,
        0x7FEFFFFFFFFFFFFF,
    ),
)
def test_four_phase_ab_exact_ieee_and_5184_roundtrip(bits: int) -> None:
    scalar = HHSNumPyScalar.from_float64_bits(bits)
    witness = four_phase_ab_witness_for_scalar(scalar)

    assert witness["exact_ieee_roundtrip"] is True
    assert witness["semantic_identity_all_channels"] is True
    assert witness["inverse_roundtrip_all_channels"] is True
    assert witness["zero_spacers_retained_all_channels"] is True
    assert witness["existing_palindromic_constructor_validation_ok"] is True
    assert len(witness["source_5184"]) == 5184
    assert experiment_acceptance(witness) is True

    for channel in CHANNELS:
        row = witness["phase_channels"][channel]
        assert len(row["transformed_5184"]) == 5184
        assert row["arm_a_equals_arm_b"] is True
        assert row["inverse_roundtrip_exact"] is True


def test_scalar_offset_vectorization_equals_dense_substitution_tensor() -> None:
    scalar = HHSNumPyScalar.from_float64_bits(0x400921FB54442D18)
    offsets = tuple(int(v) for v in __import__(
        "hhs_runtime.hhs_pass220_lo_shu_normalization_v1",
        fromlist=["deserialize_offsets_5184"],
    ).deserialize_offsets_5184(scalar.bigint_5184))

    for channel in CHANNELS:
        dense = substitution_tensor_transform(offsets, channel)
        vector = scalar_offset_vector_transform(offsets, channel)
        assert vector == dense
        assert scalar_offset_vector_inverse(vector, channel) == offsets


def test_four_ordered_channels_keep_reciprocal_direction_distinct() -> None:
    nonzero_rows = [row for row in PHASE_PLAN if row["scalar_symbol"] != 0]
    assert nonzero_rows
    for row in nonzero_rows:
        xy = row["channels"]["xy"]["permutation_power"]
        yx = row["channels"]["yx"]["permutation_power"]
        zw = row["channels"]["zw"]["permutation_power"]
        wz = row["channels"]["wz"]["permutation_power"]
        assert (xy + yx) % 9 == 0
        assert (zw + wz) % 9 == 0
        assert row["channels"]["xy"]["label"] == "Aa"
        assert row["channels"]["yx"]["label"] == "Ba"
        assert row["channels"]["zw"]["label"] == "Ab"
        assert row["channels"]["wz"]["label"] == "Bb"


def test_zero_spacers_are_reordered_not_trimmed() -> None:
    scalar = HHSNumPyScalar.from_float64_bits(0x0000000000000001)
    witness = four_phase_ab_witness_for_scalar(scalar)
    source_zero_count = len(witness["source_zero_positions"])
    assert source_zero_count > 0

    for channel in CHANNELS:
        row = witness["phase_channels"][channel]
        assert len(row["transformed_offsets"]) == 81
        assert len(row["zero_positions_after"]) == source_zero_count
        assert row["zero_spacer_count_preserved"] is True


def test_vectorized_candidate_has_lower_declared_logical_control_storage() -> None:
    scalar = HHSNumPyScalar.from_float64_bits(0x3FB999999999999A)
    cost = four_phase_ab_witness_for_scalar(scalar)["logical_cost"]

    assert cost["arm_a_dense_matrix_cells"] == 2916
    assert cost["arm_a_dense_nonzero_entries"] == 324
    assert cost["arm_b_vector_index_refs"] == 324
    assert cost["arm_b_scalar_symbol_controls"] == 36
    assert cost["arm_b_total_control_units"] == 360
    assert cost["dense_to_vector_control_ratio_exact"] == "81/10"
    assert cost["arm_b_less_logical_storage"] is True
    assert cost["timing_is_canonical"] is False


def test_experiment_does_not_claim_canonical_authority() -> None:
    scalar = HHSNumPyScalar.from_float64_bits(0x3FF0000000000000)
    witness = four_phase_ab_witness_for_scalar(scalar)
    assert witness["canonical_vm81_mutation_authority"] is False
    assert witness["canonical_hash72_authority"] is False
    assert witness["canonical_hash216_authority"] is False
    assert witness["semantics"]["substitution_tensor_is_control_candidate_only"] is True
    assert witness["semantics"]["scalar_offset_vectorization_is_candidate_only"] is True
    assert witness["semantics"]["scalar_symbol_role"] == "PERMUTATION_CONTROL_NOT_PAYLOAD_SCALARIZATION"


def test_supplied_circuit_tensor_runs_under_exact_u9_constraints() -> None:
    witness = supplied_tensor_u9_witness()

    assert witness["u9_order"] == 9
    assert witness["u9_power_9_is_identity"] is True
    assert witness["one_step_not_identity"] is True
    assert witness["nine_distinct_preclosure_states"] is True
    assert witness["full_orbit_returns_literal_tensor_exactly"] is True
    assert witness["full_orbit_tensor"] == ORDERED_TENSOR_LITERAL
    assert witness["state_count_including_closure"] == 10
    assert supplied_tensor_u9_acceptance(witness) is True


def test_supplied_circuit_tensor_u9_preserves_literal_noncommutative_cells() -> None:
    witness = supplied_tensor_u9_witness()

    assert witness[
        "x_times_y_and_y_times_x_remain_distinct_literal_cells"
    ] is True
    assert witness[
        "w_times_z_and_z_times_w_remain_distinct_literal_cells"
    ] is True
    assert witness["center_cell_literal_exact"] is True
    assert witness["notation_projection_used"] is False
    assert witness["algebraic_simplification_used"] is False
    assert witness["commutation_used"] is False
    assert witness["term_reordering_inside_cell_used"] is False

    source_cells = sorted(cell for row in ORDERED_TENSOR_LITERAL for cell in row)
    for case in witness["cases"]:
        state_cells = sorted(
            cell for row in case["tensor_state"] for cell in row
        )
        assert state_cells == source_cells
        assert case["all_literal_cells_preserved"] is True


def test_supplied_circuit_tensor_dense_and_vector_u9_are_identical() -> None:
    witness = supplied_tensor_u9_witness()

    assert witness["dense_vector_u9_identity_all_powers"] is True
    assert witness["direct_iterative_u9_identity_all_powers"] is True
    assert witness["inverse_roundtrip_all_powers"] is True

    for case in witness["cases"]:
        assert case["dense_equals_vector"] is True
        assert case["direct_equals_iterative"] is True
        assert case["inverse_recovers_source"] is True


def test_supplied_u9_tensor_is_required_by_numpy_experiment_acceptance() -> None:
    witness = four_phase_ab_witness_for_scalar(
        HHSNumPyScalar.from_float64_bits(0x400921FB54442D18)
    )
    assert witness["supplied_tensor_u9_acceptance"] is True
    assert witness["supplied_tensor_u9_witness"][
        "full_orbit_returns_literal_tensor_exactly"
    ] is True
    assert experiment_acceptance(witness) is True
