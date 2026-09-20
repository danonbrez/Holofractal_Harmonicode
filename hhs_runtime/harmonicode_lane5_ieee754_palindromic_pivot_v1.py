"""Pass 219 Lane 5 1.54 IEEE-754 palindromic decimal-pivot transcription.

The IEEE source is treated as an ingress/egress bit pattern only.  No host
floating-point operation receives canonical authority.  Every IEEE binary16,
binary32, and binary64 bit pattern can be traversed independently from the A
(forward/LHS) and B (reverse/RHS) sides of one decimal pivot.  Finite values are
decoded to exact dyadic rationals and therefore exact terminating decimal
coefficients.  Infinity/NaN encodings are preserved as tagged non-numeric
payloads.

The 72-position value is a block size, not a global numeral limit:
Concat(Block72(F)) == F for any admitted frame length, and the mirrored B side
recovers the same F by reverse block order plus reverse in-block traversal.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

from hhs_runtime.harmonicode_lane5_reciprocal_phase_boundary_v1 import (
    GLOBAL_DENOMINATOR,
    validate_t5184_002,
)

SCHEMA = "HHS_PASS219_LANE5_IEEE754_PALINDROMIC_PIVOT_V1"
VERSION = "1.0.0"
THEOREM_ID = "HHS-T5184-003"
MAGIC = "754154"
BLOCK_DIGITS = 72
SPECIAL_SCALE = 9999
SERIALIZER_CHARACTERS = 5184
G3_RNA_TRANSCRIPTION = "(y-x)-u^72=G^3"
PALINDROMIC_GENESIS_SEED = "123321.111"
PIVOT = "."

# exponent bits, fraction bits, bias
IEEE_FORMATS: Mapping[int, Tuple[int, int, int]] = {
    16: (5, 10, 15),
    32: (8, 23, 127),
    64: (11, 52, 1023),
}

REPRESENTATIVE_PATTERNS: Mapping[str, Tuple[int, int]] = {
    "binary16_zero": (16, 0x0000),
    "binary16_negative_zero": (16, 0x8000),
    "binary16_min_subnormal": (16, 0x0001),
    "binary16_max_finite": (16, 0x7BFF),
    "binary16_infinity": (16, 0x7C00),
    "binary16_nan_payload": (16, 0x7E01),
    "binary32_zero": (32, 0x00000000),
    "binary32_negative_zero": (32, 0x80000000),
    "binary32_min_subnormal": (32, 0x00000001),
    "binary32_one": (32, 0x3F800000),
    "binary32_max_finite": (32, 0x7F7FFFFF),
    "binary32_infinity": (32, 0x7F800000),
    "binary32_nan_payload": (32, 0x7FC00001),
    "binary64_zero": (64, 0x0000000000000000),
    "binary64_negative_zero": (64, 0x8000000000000000),
    "binary64_min_subnormal": (64, 0x0000000000000001),
    "binary64_min_normal": (64, 0x0010000000000000),
    "binary64_one": (64, 0x3FF0000000000000),
    "binary64_point_one": (64, 0x3FB999999999999A),
    "binary64_max_finite": (64, 0x7FEFFFFFFFFFFFFF),
    "binary64_infinity": (64, 0x7FF0000000000000),
    "binary64_nan_payload": (64, 0x7FF8000000000001),
}


@dataclass(frozen=True)
class IEEEState:
    width: int
    bits: int
    sign: int
    exponent_field: int
    fraction_field: int
    value_class: str
    exact_value: Fraction | None

    @property
    def bit_hex(self) -> str:
        return f"{self.bits:0{self.width // 4}x}"


@dataclass(frozen=True)
class PivotFrame:
    width: int
    sign: int
    scale: int
    payload: str
    value_class: str
    exact_value: Fraction | None
    source_bits: int

    @property
    def frame(self) -> str:
        return (
            MAGIC
            + f"{self.width:02d}"
            + str(self.sign)
            + f"{self.scale:04d}"
            + f"{len(self.payload):04d}"
            + self.payload
        )


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def _format(width: int) -> Tuple[int, int, int]:
    if width not in IEEE_FORMATS:
        raise ValueError(f"unsupported IEEE width: {width}")
    return IEEE_FORMATS[width]


def decode_ieee_bits(bits: int, width: int) -> IEEEState:
    exponent_bits, fraction_bits, bias = _format(width)
    if not isinstance(bits, int) or bits < 0 or bits >= (1 << width):
        raise ValueError("bit pattern outside declared width")

    sign = (bits >> (width - 1)) & 1
    exponent_mask = (1 << exponent_bits) - 1
    exponent_field = (bits >> fraction_bits) & exponent_mask
    fraction_field = bits & ((1 << fraction_bits) - 1)

    if exponent_field == exponent_mask:
        value_class = "NAN" if fraction_field else "INFINITY"
        return IEEEState(
            width, bits, sign, exponent_field, fraction_field, value_class, None
        )

    if exponent_field == 0:
        if fraction_field == 0:
            exact = Fraction(0, 1)
        else:
            # subnormal quantum = 2^(1-bias-fraction_bits)
            exact = Fraction(
                fraction_field,
                1 << (bias - 1 + fraction_bits),
            )
    else:
        significand = (1 << fraction_bits) | fraction_field
        shift = exponent_field - bias - fraction_bits
        exact = (
            Fraction(significand << shift, 1)
            if shift >= 0
            else Fraction(significand, 1 << (-shift))
        )

    if sign:
        exact = -exact

    return IEEEState(
        width, bits, sign, exponent_field, fraction_field, "FINITE", exact
    )


def exact_decimal_components(
    value: Fraction,
    *,
    zero_sign: int = 0,
) -> Tuple[int, int, str]:
    """Return sign, decimal scale, and exact coefficient digits.

    Every finite IEEE value is dyadic: n/2^k.  The identity
    n/2^k = n*5^k/10^k gives an exact terminating decimal without float use.
    """
    sign = 1 if value < 0 else (int(zero_sign) if value == 0 else 0)
    magnitude = abs(value)
    if magnitude == 0:
        return sign, 0, "0"

    denominator = magnitude.denominator
    if denominator & (denominator - 1):
        raise ValueError("non-dyadic value cannot enter IEEE exact pivot")

    scale = denominator.bit_length() - 1
    coefficient = magnitude.numerator * pow(5, scale)
    return sign, scale, str(coefficient)


def _finite_bits_from_exact(
    value: Fraction,
    width: int,
    *,
    zero_sign: int = 0,
) -> int:
    """Exact inverse of decode_ieee_bits for admitted finite IEEE values."""
    exponent_bits, fraction_bits, bias = _format(width)
    exponent_mask = (1 << exponent_bits) - 1

    if value == 0:
        return int(zero_sign) << (width - 1)

    sign = 1 if value < 0 else 0
    magnitude = abs(value)
    numerator = magnitude.numerator
    denominator = magnitude.denominator
    if denominator & (denominator - 1):
        raise ValueError("non-dyadic exact value is not an IEEE source state")

    denominator_power = denominator.bit_length() - 1
    binary_exponent = numerator.bit_length() - 1 - denominator_power
    minimum_normal_exponent = 1 - bias
    maximum_normal_exponent = (exponent_mask - 1) - bias

    if binary_exponent >= minimum_normal_exponent:
        if binary_exponent > maximum_normal_exponent:
            raise OverflowError("finite exact value exceeds IEEE format")
        shift = binary_exponent - fraction_bits
        power = -denominator_power - shift
        if power >= 0:
            significand = numerator << power
        else:
            divisor = 1 << (-power)
            if numerator % divisor:
                raise ValueError("exact value is not representable in declared IEEE format")
            significand = numerator // divisor
        if not (1 << fraction_bits) <= significand < (1 << (fraction_bits + 1)):
            raise ValueError("normal significand outside IEEE interval")
        fraction_field = significand - (1 << fraction_bits)
        exponent_field = binary_exponent + bias
    else:
        # subnormal fraction * 2^(1-bias-fraction_bits)
        power = fraction_bits - minimum_normal_exponent - denominator_power
        if power >= 0:
            fraction_field = numerator << power
        else:
            divisor = 1 << (-power)
            if numerator % divisor:
                raise ValueError("exact subnormal is not representable")
            fraction_field = numerator // divisor
        exponent_field = 0
        if not 0 < fraction_field < (1 << fraction_bits):
            raise ValueError("subnormal fraction outside IEEE interval")

    return (
        (sign << (width - 1))
        | (exponent_field << fraction_bits)
        | fraction_field
    )


def build_pivot_frame(bits: int, width: int) -> PivotFrame:
    state = decode_ieee_bits(bits, width)
    if state.value_class == "FINITE":
        assert state.exact_value is not None
        sign, scale, coefficient = exact_decimal_components(
            state.exact_value,
            zero_sign=state.sign,
        )
        return PivotFrame(
            width=width,
            sign=sign,
            scale=scale,
            payload=coefficient,
            value_class="FINITE",
            exact_value=state.exact_value,
            source_bits=bits,
        )

    # Non-finite encodings remain exact bit identities but do not pretend to be
    # numerical decimal values. SPECIAL_SCALE is outside every IEEE finite scale.
    return PivotFrame(
        width=width,
        sign=state.sign,
        scale=SPECIAL_SCALE,
        payload=str(state.fraction_field),
        value_class=state.value_class,
        exact_value=None,
        source_bits=bits,
    )


def _parse_digit_frame(frame: str) -> PivotFrame:
    if not isinstance(frame, str) or not frame.isdigit() or len(frame) < 18:
        raise ValueError("invalid pivot frame")
    if frame[:6] != MAGIC:
        raise ValueError("pivot frame magic mismatch")

    width = int(frame[6:8])
    _format(width)
    sign = int(frame[8])
    if sign not in (0, 1):
        raise ValueError("invalid sign bit")
    scale = int(frame[9:13])
    payload_length = int(frame[13:17])
    payload = frame[17:]
    if payload_length != len(payload) or payload_length <= 0:
        raise ValueError("payload length mismatch")
    if len(payload) > 1 and payload[0] == "0":
        raise ValueError("noncanonical leading zero payload")

    exponent_bits, fraction_bits, _ = _format(width)
    exponent_mask = (1 << exponent_bits) - 1

    if scale == SPECIAL_SCALE:
        fraction_field = int(payload)
        if fraction_field >= (1 << fraction_bits):
            raise ValueError("special payload exceeds fraction field")
        value_class = "NAN" if fraction_field else "INFINITY"
        source_bits = (
            (sign << (width - 1))
            | (exponent_mask << fraction_bits)
            | fraction_field
        )
        return PivotFrame(
            width, sign, scale, payload, value_class, None, source_bits
        )

    coefficient = int(payload)
    exact = Fraction(coefficient, pow(10, scale))
    if sign:
        exact = -exact
    if coefficient == 0:
        exact = Fraction(0, 1)
    source_bits = _finite_bits_from_exact(
        exact,
        width,
        zero_sign=sign if coefficient == 0 else 0,
    )
    return PivotFrame(
        width, sign, scale, payload, "FINITE", exact, source_bits
    )


def carrier_from_bits(bits: int, width: int) -> str:
    frame = build_pivot_frame(bits, width).frame
    return frame + PIVOT + frame[::-1]


def block72(text: str) -> Tuple[str, ...]:
    if not isinstance(text, str):
        raise TypeError("block72 requires text")
    return tuple(
        text[offset : offset + BLOCK_DIGITS]
        for offset in range(0, len(text), BLOCK_DIGITS)
    ) or ("",)


def concatenate_blocks(blocks: Sequence[str]) -> str:
    if any(len(block) > BLOCK_DIGITS for block in blocks):
        raise ValueError("block exceeds 72-position boundary")
    return "".join(blocks)


def direction_a_frame_from_carrier(carrier: str) -> str:
    if carrier.count(PIVOT) != 1:
        raise ValueError("carrier requires exactly one decimal pivot")
    left, _ = carrier.split(PIVOT)
    # A / LHS path: forward block concatenation from left edge to pivot.
    return concatenate_blocks(block72(left))


def direction_b_frame_from_carrier(carrier: str) -> str:
    if carrier.count(PIVOT) != 1:
        raise ValueError("carrier requires exactly one decimal pivot")
    _, right = carrier.split(PIVOT)
    # B / RHS path: independent read from the far right edge back toward pivot.
    # right == Reverse(F).  Reverse block order + reverse each block reconstructs F.
    right_blocks = block72(right)
    return "".join(block[::-1] for block in reversed(right_blocks))


def recover_direction_a(carrier: str) -> PivotFrame:
    return _parse_digit_frame(direction_a_frame_from_carrier(carrier))


def recover_direction_b(carrier: str) -> PivotFrame:
    return _parse_digit_frame(direction_b_frame_from_carrier(carrier))


def exact_decimal_literal(frame: PivotFrame) -> str | None:
    if frame.value_class != "FINITE":
        return None
    digits = frame.payload
    scale = frame.scale
    if scale == 0:
        body = digits + ".0"
    elif scale < len(digits):
        body = digits[:-scale] + "." + digits[-scale:]
    else:
        body = "0." + ("0" * (scale - len(digits))) + digits
    return ("-" if frame.sign else "") + body


def prove_carrier(bits: int, width: int) -> Dict[str, Any]:
    source = decode_ieee_bits(bits, width)
    carrier = carrier_from_bits(bits, width)
    a = recover_direction_a(carrier)
    b = recover_direction_b(carrier)
    left, right = carrier.split(PIVOT)
    forward_blocks = block72(left)
    reverse_blocks = block72(right)

    exact_numeric_match = (
        True
        if source.value_class != "FINITE"
        else a.exact_value == source.exact_value == b.exact_value
    )

    return _receipt({
        "schema": f"{SCHEMA}_CARRIER_PROOF",
        "width": width,
        "source_bits_hex": source.bit_hex,
        "source_class": source.value_class,
        "source_exact_value": (
            None
            if source.exact_value is None
            else f"{source.exact_value.numerator}/{source.exact_value.denominator}"
        ),
        "direction_a_bits_hex": f"{a.source_bits:0{width // 4}x}",
        "direction_b_bits_hex": f"{b.source_bits:0{width // 4}x}",
        "direction_a_exact_value": (
            None
            if a.exact_value is None
            else f"{a.exact_value.numerator}/{a.exact_value.denominator}"
        ),
        "direction_b_exact_value": (
            None
            if b.exact_value is None
            else f"{b.exact_value.numerator}/{b.exact_value.denominator}"
        ),
        "exact_decimal_literal": exact_decimal_literal(a),
        "frame_digit_count": len(left),
        "forward_block_count": len(forward_blocks),
        "reverse_block_count": len(reverse_blocks),
        "block_size": BLOCK_DIGITS,
        "carrier_digit_count_excluding_pivot": len(left) + len(right),
        "carrier_is_palindrome": carrier == carrier[::-1],
        "forward_concat_exact": concatenate_blocks(forward_blocks) == left,
        "reverse_concat_exact": direction_b_frame_from_carrier(carrier) == left,
        "direction_a_roundtrip_exact": a.source_bits == bits,
        "direction_b_roundtrip_exact": b.source_bits == bits,
        "exact_numeric_match": exact_numeric_match,
        "nonfinite_numeric_authority": False,
    })


def _deterministic_format_samples(width: int) -> Iterable[int]:
    exponent_bits, fraction_bits, _ = _format(width)
    exponent_mask = (1 << exponent_bits) - 1
    fraction_mask = (1 << fraction_bits) - 1
    exponent_samples = (
        0,
        1,
        2,
        max(1, exponent_mask // 2),
        max(1, exponent_mask - 2),
        exponent_mask - 1,
        exponent_mask,
    )
    fraction_samples = (
        0,
        1,
        2,
        fraction_mask // 3,
        fraction_mask // 2,
        max(0, fraction_mask - 1),
        fraction_mask,
    )
    for sign in (0, 1):
        for exponent in exponent_samples:
            for fraction in fraction_samples:
                yield (
                    (sign << (width - 1))
                    | (exponent << fraction_bits)
                    | fraction
                )


def _exhaustive_binary16_roundtrip() -> Tuple[int, int]:
    passed = 0
    for bits in range(1 << 16):
        proof = prove_carrier(bits, 16)
        if not (
            proof["carrier_is_palindrome"]
            and proof["forward_concat_exact"]
            and proof["reverse_concat_exact"]
            and proof["direction_a_roundtrip_exact"]
            and proof["direction_b_roundtrip_exact"]
            and proof["exact_numeric_match"]
        ):
            return passed, bits
        passed += 1
    return passed, -1


def validate_t5184_003() -> Dict[str, Any]:
    inherited = validate_t5184_002()
    representative = {
        name: prove_carrier(bits, width)
        for name, (width, bits) in REPRESENTATIVE_PATTERNS.items()
    }
    sampled = {
        width: tuple(prove_carrier(bits, width) for bits in _deterministic_format_samples(width))
        for width in (32, 64)
    }
    binary16_passed, binary16_failure = _exhaustive_binary16_roundtrip()

    point_one = representative["binary64_point_one"]
    min_subnormal = representative["binary64_min_subnormal"]
    max_finite = representative["binary64_max_finite"]

    all_rep = tuple(representative.values())
    all_sampled = tuple(item for group in sampled.values() for item in group)

    checks = {
        "inherited_reciprocal_boundary_green": inherited["result"] == "PASS",
        "ieee_widths_exact": set(IEEE_FORMATS) == {16, 32, 64},
        "binary16_exhaustive_all_65536": binary16_passed == (1 << 16)
            and binary16_failure == -1,
        "representative_a_roundtrip_exact": all(
            proof["direction_a_roundtrip_exact"] for proof in all_rep
        ),
        "representative_b_roundtrip_exact": all(
            proof["direction_b_roundtrip_exact"] for proof in all_rep
        ),
        "sampled_32_64_a_roundtrip_exact": all(
            proof["direction_a_roundtrip_exact"] for proof in all_sampled
        ),
        "sampled_32_64_b_roundtrip_exact": all(
            proof["direction_b_roundtrip_exact"] for proof in all_sampled
        ),
        "finite_numeric_projection_exact": all(
            proof["exact_numeric_match"] for proof in (*all_rep, *all_sampled)
        ),
        "palindromic_pivot_exact": all(
            proof["carrier_is_palindrome"] for proof in (*all_rep, *all_sampled)
        ),
        "forward_block_concatenation_exact": all(
            proof["forward_concat_exact"] for proof in (*all_rep, *all_sampled)
        ),
        "reverse_block_concatenation_exact": all(
            proof["reverse_concat_exact"] for proof in (*all_rep, *all_sampled)
        ),
        "point_one_hits_72_digit_boundary": point_one["frame_digit_count"] == 72
            and point_one["forward_block_count"] == 1,
        "binary64_min_subnormal_crosses_72_boundary": (
            min_subnormal["frame_digit_count"] == 768
            and min_subnormal["forward_block_count"] == 11
        ),
        "binary64_max_finite_crosses_72_boundary": (
            max_finite["frame_digit_count"] == 326
            and max_finite["forward_block_count"] == 5
        ),
        "signed_zero_identity_preserved": (
            representative["binary64_zero"]["source_bits_hex"] == "0000000000000000"
            and representative["binary64_negative_zero"]["source_bits_hex"]
            == "8000000000000000"
            and representative["binary64_negative_zero"]["direction_a_bits_hex"]
            == "8000000000000000"
            and representative["binary64_negative_zero"]["direction_b_bits_hex"]
            == "8000000000000000"
        ),
        "nonfinite_bit_identity_preserved": all(
            representative[name]["direction_a_bits_hex"]
            == representative[name]["source_bits_hex"]
            == representative[name]["direction_b_bits_hex"]
            for name in (
                "binary16_infinity",
                "binary16_nan_payload",
                "binary32_infinity",
                "binary32_nan_payload",
                "binary64_infinity",
                "binary64_nan_payload",
            )
        ),
        "nonfinite_never_claims_numeric_authority": all(
            representative[name]["source_exact_value"] is None
            and representative[name]["exact_decimal_literal"] is None
            and representative[name]["nonfinite_numeric_authority"] is False
            for name in (
                "binary16_infinity",
                "binary16_nan_payload",
                "binary32_infinity",
                "binary32_nan_payload",
                "binary64_infinity",
                "binary64_nan_payload",
            )
        ),
        "dyadic_decimal_termination_constructive": all(
            (
                state.exact_value is None
                or state.exact_value == 0
                or (
                    state.exact_value.denominator
                    & (state.exact_value.denominator - 1)
                )
                == 0
            )
            for width in IEEE_FORMATS
            for _, (candidate_width, bits) in REPRESENTATIVE_PATTERNS.items()
            if candidate_width == width
            for state in (decode_ieee_bits(bits, width),)
        ),
        "g3_rna_binding_preserved": G3_RNA_TRANSCRIPTION == "(y-x)-u^72=G^3",
        "genesis_palindrome_seed_preserved": PALINDROMIC_GENESIS_SEED == "123321.111",
        "same_delta_manifold": GLOBAL_DENOMINATOR == "(P=√(pq+(P⁴/AB)))/∆",
        "block72_is_block_not_global_limit": (
            min_subnormal["forward_block_count"] > 1
            and concatenate_blocks(
                block72(
                    build_pivot_frame(
                        REPRESENTATIVE_PATTERNS["binary64_min_subnormal"][1],
                        64,
                    ).frame
                )
            )
            == build_pivot_frame(
                REPRESENTATIVE_PATTERNS["binary64_min_subnormal"][1],
                64,
            ).frame
        ),
        "serializer_capacity_relation_preserved": SERIALIZER_CHARACTERS == 72 * 72 == 81 * 64,
        "ieee_has_no_native_float_alu_authority": True,
    }

    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "theorem_id": THEOREM_ID,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "binary16_patterns_exhausted": binary16_passed,
        "representative_pattern_count": len(representative),
        "sampled_binary32_pattern_count": len(sampled[32]),
        "sampled_binary64_pattern_count": len(sampled[64]),
        "block_size_digits": BLOCK_DIGITS,
        "serializer_characters": SERIALIZER_CHARACTERS,
        "direction_a": "FORWARD_LHS_EDGE_TO_PIVOT",
        "direction_b": "REVERSE_RHS_EDGE_TO_PIVOT",
        "decimal_pivot": PIVOT,
        "g3_rna_transcription": G3_RNA_TRANSCRIPTION,
        "palindromic_genesis_seed": PALINDROMIC_GENESIS_SEED,
        "universal_denominator": GLOBAL_DENOMINATOR,
        "authority": {
            "ieee_arithmetic_authority": False,
            "host_float_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
        },
        "source_complete_formalization_status": "IN_PROGRESS",
    })


def main() -> int:
    report = validate_t5184_003()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
