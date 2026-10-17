from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_i080_deterministic_knowledge_graph_qpu_v1 import (
    DYADIC_4_7_11,
    FRACTAL_123,
    I080QPUError,
    PHASE_GEAR_E,
    deterministic_qpu_witness,
    genesis_serialization,
    hash216_hydration_translation,
    ieee754_lossless_roundtrip,
    ieee754_symbolic_egress,
    ieee754_symbolic_ingress,
    phase_gear_tick,
    reference_hash216,
    self_test,
    trinary_tensor_witness,
    validate_offset_tensor,
)


def test_genesis_constructors_are_fixed_width_and_typed() -> None:
    g10 = genesis_serialization("10")
    g20 = genesis_serialization("20")
    g30 = genesis_serialization("30")
    g100 = genesis_serialization("100")

    assert g10["serialized5184"] == "10" + "0" * 5182
    assert g10["padding_hnan_zero_positions"] == 5182
    assert g10["lo_shu_sudoku_qudit_nucleus"] is True
    assert g20["dyadic_scaling_quantization"] == DYADIC_4_7_11 == (4, 7, 11)
    assert g30["triadic_fractal_123"] == FRACTAL_123
    assert g30["triadic_closure"] == "a^2+b^2=c^2=(A+B=C)/(AB/P^4)"
    assert g100["serialized5184"] == "100" + "0" * 5181
    assert g100["dual_qudit_entanglement"]["constructor_source"] == "100=90+10=81*81"
    assert g100["dual_qudit_entanglement"]["ordered_pair_addresses"] == 6561


def test_all_5184_character_offsets_are_addressed_and_bounded_minus9_plus9() -> None:
    offsets = [0] * 5184
    offsets[0], offsets[1], offsets[-1] = -9, 9, -1
    witness = validate_offset_tensor(offsets)
    assert witness["positions"] == 5184
    assert witness["address_range"] == (0, 5183)
    assert witness["offset_min"] == -9
    assert witness["offset_max"] == 9
    assert witness["offset_cardinality"] == 19
    assert witness["all_addresses_covered"] is True
    assert witness["lossy_scalar_projection_used"] is False

    offsets[2500] = 10
    with pytest.raises(I080QPUError):
        validate_offset_tensor(offsets)


def test_trinary_tensor_has_one_nucleus_anchor_and_5183_free_positions() -> None:
    witness = trinary_tensor_witness()
    assert witness["carrier_positions"] == 5184
    assert witness["nucleus_anchor_positions"] == 1
    assert witness["free_trinary_positions"] == 5183
    assert witness["phase_alphabet"] == (-1, 0, 1)
    assert witness["state_space_source"] == "3^5183"
    assert witness["materialized"] is False


def test_u16_nine_phase_gear_and_64_72_81_close_at_5184() -> None:
    seen = []
    for tick in range(9):
        op = phase_gear_tick(tick)
        seen.append(op["u16_phase_value"])
        assert op["one_tick_one_lane5_optimization_operation"] is True
        assert op["ratio_64_72"] == op["ratio_72_81"] == (8, 9)
        assert op["common_closure_5184"] == 64 * 81 == 72 * 72 == 5184
        assert op["nine_steps"] == op["two_turns"] == 144
        assert op["quartic_closure"] == "AB=P^4"
        assert op["mirror_quartic_closure"] == "BA=-P^4"
        assert op["hnan_closure"] is True
    assert tuple(seen) == PHASE_GEAR_E
    assert phase_gear_tick(5184)["linear5184"] == 0


def test_hash216_hydrates_and_recompresses_three_5184_planes() -> None:
    witness = hash216_hydration_translation(reference_hash216())
    assert witness["hash216_width"] == 216
    assert witness["plane_count"] == 3
    assert witness["positions_per_plane"] == 5184
    assert witness["full_attached_components"] == 15552
    assert all(plane["offset_positions"] == 5184 for plane in witness["planes"])
    assert all(plane["roundtrip_exact"] is True for plane in witness["planes"])
    assert witness["roundtrip_exact"] is True
    assert witness["lossless_translation"] is True


def test_ieee_bitstrings_roundtrip_losslessly_through_symbolic_rna() -> None:
    vectors = (
        "0" * 16,
        "1" + "0" * 15,
        "0011110000000000",
        "0" * 32,
        "00111111100000000000000000000000",
        "0" * 64,
        "0011111111110000000000000000000000000000000000000000000000000000",
        "0111111111110000000000000000000000000000000000000000000000000000",
        "0111111111111000000000000000000000000000000000000000000000000001",
    )
    for bits in vectors:
        receipt = ieee754_lossless_roundtrip(bits)
        assert receipt["roundtrip_exact"] is True
        assert receipt["palindromic_reverse_exact"] is True
        assert receipt["egress_raw_bits"] == bits
        ingress = receipt["ingress"]
        assert ingress["raw_bits"] == bits
        assert ingress["mirror_bits"] == bits[::-1]
        assert ingress["palindromic_carrier"] == bits + "." + bits[::-1]
        assert ingress["internal_ieee_float_algorithm_used"] is False
        assert ingress["lossy_scalar_projection_used"] is False
        assert ieee754_symbolic_egress(ingress) == bits


def test_ieee_special_encodings_preserve_class_and_sign() -> None:
    plus_inf = ieee754_symbolic_ingress(
        "0111111111110000000000000000000000000000000000000000000000000000"
    )
    nan = ieee754_symbolic_ingress(
        "0111111111111000000000000000000000000000000000000000000000000001"
    )
    minus_zero = ieee754_symbolic_ingress("1" + "0" * 63)
    assert plus_inf["classification"] == "INFINITY"
    assert nan["classification"] == "NAN"
    assert minus_zero["classification"] == "ZERO"
    assert minus_zero["sign_bit"] == "1"


def test_reference_module_contains_no_float_conversion_or_random_source() -> None:
    source = Path(
        "hhs_runtime/hhs_pass220_i080_deterministic_knowledge_graph_qpu_v1.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "float(",
        "struct.unpack",
        "numpy.float",
        "Math.random",
        "parseFloat",
    ):
        assert forbidden not in source


def test_complete_qpu_witness_and_self_test_close() -> None:
    witness = deterministic_qpu_witness()
    assert witness["genesis"]["all_width_5184"] is True
    assert witness["offset_tensor"]["all_addresses_covered"] is True
    assert witness["trinary_tensor"]["state_space_source"] == "3^5183"
    assert witness["hash216_hydration"]["full_attached_components"] == 15552
    assert witness["lossless_ieee_all_vectors"] is True
    assert witness["authority"]["ieee_float_internal_logic_authority"] is False
    assert witness["authority"]["lossy_scalar_projection_authority"] is False

    report = self_test()
    assert report["status"] == "PASS"
    assert report["check_count"] == report["pass_count"] == 19
    assert report["failed"] == ()
