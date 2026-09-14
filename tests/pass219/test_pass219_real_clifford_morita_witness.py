from __future__ import annotations

import pytest

from hhs_runtime.pass219.bott8_native_correspondence import PASS188_B8_ORDER
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.real_clifford_morita_witness import (
    CL0_RESIDUE_MODELS,
    RealCliffordMoritaError,
    audit_rml5_generators_on_clifford_morita_bridge,
    build_cl08_generators,
    build_cl08_isomorphism_witness,
    build_cl08_word_matrices,
    build_cl0_period8_witness,
    build_clifford_morita_native_packet,
    build_m16_full_corner_morita_context,
)


def _state(
    *,
    x: int = 71,
    y: int = 0,
    z: int = 35,
    w: int = 71,
    xy_sign: int = 1,
    zw_sign: int = 1,
    state_id: str = "rml10:test",
) -> dict[str, object]:
    signs = {"xy": xy_sign, "yx": -xy_sign, "zw": zw_sign, "wz": -zw_sign}
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, signs["xy"]),
        "yx": expected_product_phase(y, signs["yx"]),
        "zw": expected_product_phase(z, signs["zw"]),
        "wz": expected_product_phase(w, signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


def _identity(order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(1 if i == j else 0 for j in range(order)) for i in range(order))


def _matmul(
    left: tuple[tuple[int, ...], ...],
    right: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(len(right[0])))
        for i in range(len(left))
    )


def _add(
    left: tuple[tuple[int, ...], ...],
    right: tuple[tuple[int, ...], ...],
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(left[i][j] + right[i][j] for j in range(len(left[0])))
        for i in range(len(left))
    )


def _scale(
    matrix: tuple[tuple[int, ...], ...], scalar: int
) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(scalar * value for value in row) for row in matrix)


def _frobenius(
    left: tuple[tuple[int, ...], ...],
    right: tuple[tuple[int, ...], ...],
) -> int:
    return sum(
        left[i][j] * right[i][j]
        for i in range(len(left))
        for j in range(len(left[0]))
    )


def test_cl08_eight_exact_generators_square_minus_identity_and_anticommute() -> None:
    generators = build_cl08_generators()
    assert len(generators) == 8
    identity = _identity(16)
    negative_identity = _scale(identity, -1)
    zero = _scale(identity, 0)
    for generator in generators:
        assert len(generator) == 16
        assert all(len(row) == 16 for row in generator)
        assert _matmul(generator, generator) == negative_identity
        assert all(isinstance(value, int) for row in generator for value in row)
    pair_count = 0
    for i in range(8):
        for j in range(i + 1, 8):
            assert _add(
                _matmul(generators[i], generators[j]),
                _matmul(generators[j], generators[i]),
            ) == zero
            pair_count += 1
    assert pair_count == 28


def test_cl08_256_words_form_exact_frobenius_basis_of_m16r() -> None:
    words = build_cl08_word_matrices()
    assert len(words) == 256
    assert len(set(words)) == 256
    for i, left in enumerate(words):
        assert _frobenius(left, left) == 16
        for j in range(i + 1, len(words)):
            assert _frobenius(left, words[j]) == 0

    witness = build_cl08_isomorphism_witness()
    assert witness["signature"] == "Cl_(0,8)"
    assert witness["generator_count"] == 8
    assert witness["matrix_order"] == 16
    assert witness["all_generators_square_to_minus_identity"] is True
    assert witness["pairwise_anticommutation_checks"] == 28
    assert witness["all_distinct_generators_anticommute"] is True
    assert witness["clifford_word_count"] == 256
    assert witness["matrix_space_real_dimension"] == 256
    assert witness["word_basis_dimension"] == 256
    assert witness["frobenius_diagonal_norm"] == 16
    assert witness["frobenius_off_diagonal_failures"] == 0
    assert witness["all_256_words_frobenius_orthogonal"] is True
    assert witness["all_256_words_linearly_independent"] is True
    assert witness["all_256_words_span_M16R"] is True
    assert witness["cl08_to_M16R_exact_isomorphism_constructed"] is True
    assert witness["floating_point_authority"] is False


def test_standard_m16_full_corner_morita_context_is_constructed_exactly() -> None:
    witness = build_m16_full_corner_morita_context()
    assert witness["matrix_order"] == 16
    assert witness["matrix_unit_count"] == 256
    assert witness["matrix_unit_index_relation_cases"] == 65_536
    assert witness["matrix_unit_index_relation_failures"] == 0
    assert witness["corner_idempotent_squared_equals_itself"] is True
    assert witness["full_corner_identity_verified"] is True
    assert witness["corner_e00_M16A_e00_identified_with_A"] is True
    assert witness["standard_column_module"] == "A^16"
    assert witness["standard_matrix_morita_context_constructed"] is True
    assert witness["full_functor_coherence_formalized_in_runtime"] is False


def test_all_eight_cl0_residue_models_have_exact_256x_period_lift() -> None:
    expected_base = (
        "R",
        "C",
        "H",
        "H+H",
        "M2(H)",
        "M4(C)",
        "M8(R)",
        "M8(R)+M8(R)",
    )
    expected_lifted = (
        "M16(R)",
        "M16(C)",
        "M16(H)",
        "M16(H)+M16(H)",
        "M32(H)",
        "M64(C)",
        "M128(R)",
        "M128(R)+M128(R)",
    )
    assert tuple(model["algebra"] for model in CL0_RESIDUE_MODELS) == expected_base
    for residue in range(8):
        witness = build_cl0_period8_witness(residue)
        assert witness["residue_mod8"] == residue
        assert witness["native_b8_ordered_tag"] == PASS188_B8_ORDER[residue]
        assert witness["base_clifford_signature"] == f"Cl_(0,{residue})"
        assert witness["base_algebra_model"] == expected_base[residue]
        assert witness["base_real_dimension"] == 1 << residue
        assert witness["period8_lift_signature"] == f"Cl_(0,{residue + 8})"
        assert witness["period8_lift_algebra_model"] == expected_lifted[residue]
        assert witness["period8_lift_real_dimension"] == 1 << (residue + 8)
        assert witness["dimension_factor"] == 256
        assert witness["cl08_factor_exact_isomorphism_constructed"] is True
        assert witness["matrix_morita_full_corner_verified"] is True
        assert witness["period8_matrix_factor_morita_equivalent_to_base"] is True
        assert witness["phase_channel_is_clifford_matrix_entry"] is False
        assert witness["phase72_is_clifford_coefficient"] is False


def test_rml10_packet_binds_live_b8_state_to_constructive_clifford_witnesses() -> None:
    state = _state()
    packet = build_clifford_morita_native_packet(state)
    assert packet["b8_order"] == list(PASS188_B8_ORDER)
    assert packet["all_eight_real_clifford_period8_witnesses_bound"] is True
    assert packet["explicit_cl08_to_M16R_isomorphism_constructed"] is True
    assert packet["explicit_M16_full_corner_morita_context_constructed"] is True
    assert len(packet["rml6_s7_point_sha256"]) == 64
    assert len(packet["rml7_s4_point_sha256"]) == 64
    rows = packet["basis_rows"]
    assert [row["ordered_tag"] for row in rows] == list(PASS188_B8_ORDER)
    for q, row in enumerate(rows):
        assert row["basis8"] == q
        assert row["phase72"] == state["phases"][row["ordered_tag"]]
        assert row["real_clifford_period8_witness"]["residue_mod8"] == q
        assert row["clifford_annotation_replaces_live_phase_state"] is False
    assert packet["phase_state_reinterpreted_as_matrix_state"] is False
    assert packet["classical_bott_theorem_reproved_by_hhs"] is False
    assert packet["physical_topological_hardware_theorem_claimed"] is False
    assert packet["canonical_vm81_mutation_authority"] is False
    assert packet["canonical_hash72_mint_authority"] is False
    assert packet["canonical_hash216_persistence_authority"] is False
    assert packet["floating_point_authority"] is False
    assert packet["scalar_projection_substitution_authority"] is False


def test_rml10_carries_complete_generator_partition_without_reclassification() -> None:
    audit = audit_rml5_generators_on_clifford_morita_bridge(_state())
    assert audit["total_generator_cases"] == 290
    assert audit["same_base_fiber_preserving_cases"] == 4
    assert audit["base_moving_cases"] == 286
    assert audit["inverse_hopf_base_restoration_failures"] == 0
    assert audit["all_eight_clifford_residue_models_bound"] is True
    assert audit["explicit_cl08_factor_available"] is True
    assert audit["explicit_matrix_morita_context_available"] is True
    assert audit["generator_motion_reclassified_by_clifford_model"] is False
    assert audit["phase_transition_authority_expanded"] is False
    assert audit["canonical_vm81_mutation_authority"] is False


def test_rml10_rejects_invalid_clifford_residue() -> None:
    with pytest.raises(RealCliffordMoritaError, match="CLIFFORD_RESIDUE_OUT_OF_RANGE"):
        build_cl0_period8_witness(8)
    with pytest.raises(RealCliffordMoritaError, match="CLIFFORD_RESIDUE_EXACT_INTEGER_REQUIRED"):
        build_cl0_period8_witness(1.0)  # type: ignore[arg-type]
