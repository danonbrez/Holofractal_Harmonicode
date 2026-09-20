from fractions import Fraction

from hhs_runtime.harmonicode_lane5_ieee754_palindromic_pivot_v1 import (
    BLOCK_DIGITS,
    REPRESENTATIVE_PATTERNS,
    block72,
    build_pivot_frame,
    carrier_from_bits,
    concatenate_blocks,
    decode_ieee_bits,
    direction_a_frame_from_carrier,
    direction_b_frame_from_carrier,
    exact_decimal_components,
    prove_carrier,
    recover_direction_a,
    recover_direction_b,
    validate_t5184_003,
)


def test_exact_dyadic_to_decimal_identity():
    source = Fraction(3602879701896397, 1 << 55)
    sign, scale, coefficient = exact_decimal_components(source)
    assert sign == 0
    assert scale == 55
    assert Fraction(int(coefficient), 10**scale) == source


def test_decimal_pivot_directions_are_independent_and_exact():
    bits = REPRESENTATIVE_PATTERNS["binary64_point_one"][1]
    carrier = carrier_from_bits(bits, 64)
    a = recover_direction_a(carrier)
    b = recover_direction_b(carrier)
    assert a.source_bits == bits
    assert b.source_bits == bits
    assert a.exact_value == b.exact_value == decode_ieee_bits(bits, 64).exact_value
    assert direction_a_frame_from_carrier(carrier) == direction_b_frame_from_carrier(carrier)
    assert carrier == carrier[::-1]


def test_binary64_point_one_lands_exactly_on_one_72_digit_frame():
    bits = REPRESENTATIVE_PATTERNS["binary64_point_one"][1]
    frame = build_pivot_frame(bits, 64).frame
    assert len(frame) == BLOCK_DIGITS == 72
    assert block72(frame) == (frame,)


def test_binary64_min_subnormal_crosses_the_72_position_boundary_losslessly():
    bits = REPRESENTATIVE_PATTERNS["binary64_min_subnormal"][1]
    frame = build_pivot_frame(bits, 64).frame
    blocks = block72(frame)
    assert len(frame) == 768
    assert len(blocks) == 11
    assert [len(block) for block in blocks] == [72] * 10 + [48]
    assert concatenate_blocks(blocks) == frame
    proof = prove_carrier(bits, 64)
    assert proof["direction_a_roundtrip_exact"]
    assert proof["direction_b_roundtrip_exact"]


def test_binary64_max_finite_crosses_multiple_72_blocks_losslessly():
    bits = REPRESENTATIVE_PATTERNS["binary64_max_finite"][1]
    proof = prove_carrier(bits, 64)
    assert proof["frame_digit_count"] == 326
    assert proof["forward_block_count"] == 5
    assert proof["reverse_block_count"] == 5
    assert proof["direction_a_roundtrip_exact"]
    assert proof["direction_b_roundtrip_exact"]


def test_signed_zero_bit_identity_is_not_flattened():
    positive = prove_carrier(0x0000000000000000, 64)
    negative = prove_carrier(0x8000000000000000, 64)
    assert positive["source_exact_value"] == negative["source_exact_value"] == "0/1"
    assert positive["direction_a_bits_hex"] == "0000000000000000"
    assert negative["direction_a_bits_hex"] == "8000000000000000"
    assert negative["direction_b_bits_hex"] == "8000000000000000"


def test_nan_and_infinity_roundtrip_as_tagged_bits_not_numeric_values():
    for name in ("binary64_infinity", "binary64_nan_payload"):
        width, bits = REPRESENTATIVE_PATTERNS[name]
        proof = prove_carrier(bits, width)
        assert proof["source_exact_value"] is None
        assert proof["exact_decimal_literal"] is None
        assert proof["direction_a_roundtrip_exact"]
        assert proof["direction_b_roundtrip_exact"]
        assert proof["nonfinite_numeric_authority"] is False


def test_t5184_003_full_validation():
    report = validate_t5184_003()
    assert report["result"] == "PASS"
    assert report["check_count"] == 24
    assert all(report["checks"].values())
    assert report["binary16_patterns_exhausted"] == 65536
    assert report["block_size_digits"] == 72
    assert report["serializer_characters"] == 5184
    assert report["authority"]["ieee_arithmetic_authority"] is False
    assert report["authority"]["host_float_authority"] is False
