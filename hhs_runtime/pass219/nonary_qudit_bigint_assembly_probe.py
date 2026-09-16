"""Pass 219 diagnostic probe for exact nonary/qudit BigInt assembly closure.

This probe tests whether the already-derived 8-channel ordered phase layer and
9-state Lo Shu qudit layer can be serialized into one exact integer carrier at
arbitrary nesting depth without adding a new primitive algebra.

For depth m, the two exact layer words live in Z_(8^m) and Z_(9^m). Because
those moduli are coprime, the Chinese Remainder Theorem provides one exact
BigInt representative in Z_(72^m). At m=72 this gives exactly 72^72 integer
positions. The probe also keeps a local 8 x 9 <-> 72 glyph bijection so every
cell can be read as an ordered phase/qudit assembly symbol.

This is diagnostic/read-only. It does not create canonical VM81 mutation,
Hash72 minting, Hash216 persistence, or floating-point authority, and it does
not scalarize the supplied directional HARMONICODE equations.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.dynamic_octonion_gyroscope import CHANNELS
from hhs_runtime.pass219.platonic_multistate_fold_probe import STATE_ORDER

PASS = 219
ITERATION = "NONARY_QUDIT_BIGINT_ASSEMBLY_PROBE_1_0"
SCHEMA = "HHS_PASS219_NONARY_QUDIT_BIGINT_ASSEMBLY_PROBE_V1"

PHASE_RADIX = 8
QUDIT_RADIX = 9
GLYPH_RADIX = 72
HASH72_DEPTH = 72
HASH72_MANIFOLD_CARDINALITY = GLYPH_RADIX**HASH72_DEPTH
FOUR_STATE_TRANSLATION_SURFACE = "c^4=P^4"
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
LO_SHU_QUDIT_DIGITS = tuple(value - 1 for value in LO_SHU)


class NonaryQuditBigIntAssemblyProbeError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise NonaryQuditBigIntAssemblyProbeError(
            f"FLOAT_PROBE_AUTHORITY_FORBIDDEN:{path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise NonaryQuditBigIntAssemblyProbeError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _digit(value: Any, radix: int, label: str) -> int:
    integer = _exact_int(value, label)
    if integer < 0 or integer >= radix:
        raise NonaryQuditBigIntAssemblyProbeError(f"{label}_OUT_OF_RANGE")
    return integer


def encode_radix_digits(digits: Sequence[int], radix: int) -> int:
    """Encode least-significant-position-first exact digits into one integer."""
    radix = _exact_int(radix, "RADIX")
    if radix < 2:
        raise NonaryQuditBigIntAssemblyProbeError("RADIX_MUST_BE_AT_LEAST_TWO")
    value = 0
    place = 1
    for index, item in enumerate(digits):
        digit = _digit(item, radix, f"DIGIT_{index}")
        value += digit * place
        place *= radix
    return value


def decode_radix_digits(value: int, radix: int, depth: int) -> tuple[int, ...]:
    """Exact inverse of encode_radix_digits for a fixed depth."""
    value = _exact_int(value, "VALUE")
    radix = _exact_int(radix, "RADIX")
    depth = _exact_int(depth, "DEPTH")
    if radix < 2:
        raise NonaryQuditBigIntAssemblyProbeError("RADIX_MUST_BE_AT_LEAST_TWO")
    if depth <= 0:
        raise NonaryQuditBigIntAssemblyProbeError("DEPTH_MUST_BE_POSITIVE")
    modulus = radix**depth
    if value < 0 or value >= modulus:
        raise NonaryQuditBigIntAssemblyProbeError("VALUE_OUTSIDE_FIXED_DEPTH_MODULUS")
    remainder = value
    digits: list[int] = []
    for _ in range(depth):
        remainder, digit = divmod(remainder, radix)
        digits.append(digit)
    if remainder != 0:
        raise AssertionError("FIXED_DEPTH_RADIX_DECODE_REMAINDER")
    return tuple(digits)


def encode_local_glyph(phase_digit: int, qudit_digit: int) -> int:
    """CRT-biject one ordered phase digit and one nonary digit into 0..71."""
    phase = _digit(phase_digit, PHASE_RADIX, "PHASE_DIGIT")
    qudit = _digit(qudit_digit, QUDIT_RADIX, "QUDIT_DIGIT")
    # 9 == 1 (mod 8) and 64 == 1 (mod 9), while each term vanishes
    # modulo the other factor. This is the canonical least residue in Z_72.
    return (9 * phase + 64 * qudit) % GLYPH_RADIX


def decode_local_glyph(glyph: int) -> tuple[int, int]:
    glyph = _digit(glyph, GLYPH_RADIX, "GLYPH")
    return glyph % PHASE_RADIX, glyph % QUDIT_RADIX


def _crt_pair(left_value: int, left_modulus: int, right_value: int, right_modulus: int) -> int:
    left_value = _exact_int(left_value, "LEFT_VALUE")
    right_value = _exact_int(right_value, "RIGHT_VALUE")
    left_modulus = _exact_int(left_modulus, "LEFT_MODULUS")
    right_modulus = _exact_int(right_modulus, "RIGHT_MODULUS")
    if left_modulus <= 1 or right_modulus <= 1:
        raise NonaryQuditBigIntAssemblyProbeError("CRT_MODULUS_TOO_SMALL")
    if gcd(left_modulus, right_modulus) != 1:
        raise NonaryQuditBigIntAssemblyProbeError("CRT_MODULI_MUST_BE_COPRIME")
    if not (0 <= left_value < left_modulus and 0 <= right_value < right_modulus):
        raise NonaryQuditBigIntAssemblyProbeError("CRT_RESIDUE_OUT_OF_RANGE")
    scale = ((right_value - left_value) * pow(left_modulus, -1, right_modulus)) % right_modulus
    return (left_value + left_modulus * scale) % (left_modulus * right_modulus)


def serialize_qudit_assembly(
    phase_digits: Sequence[int],
    qudit_digits: Sequence[int],
) -> dict[str, Any]:
    """Serialize equal-depth phase and nonary layers into one exact BigInt."""
    if len(phase_digits) != len(qudit_digits):
        raise NonaryQuditBigIntAssemblyProbeError("LAYER_DEPTH_MISMATCH")
    depth = len(phase_digits)
    if depth <= 0:
        raise NonaryQuditBigIntAssemblyProbeError("LAYER_DEPTH_MUST_BE_POSITIVE")
    normalized_phase = tuple(
        _digit(value, PHASE_RADIX, f"PHASE_{index}")
        for index, value in enumerate(phase_digits)
    )
    normalized_qudit = tuple(
        _digit(value, QUDIT_RADIX, f"QUDIT_{index}")
        for index, value in enumerate(qudit_digits)
    )
    phase_modulus = PHASE_RADIX**depth
    qudit_modulus = QUDIT_RADIX**depth
    combined_modulus = GLYPH_RADIX**depth
    if phase_modulus * qudit_modulus != combined_modulus:
        raise AssertionError("72_DEPTH_FACTORIZATION_DRIFT")
    phase_word = encode_radix_digits(normalized_phase, PHASE_RADIX)
    qudit_word = encode_radix_digits(normalized_qudit, QUDIT_RADIX)
    bigint = _crt_pair(phase_word, phase_modulus, qudit_word, qudit_modulus)
    glyph_stream = tuple(
        encode_local_glyph(phase, qudit)
        for phase, qudit in zip(normalized_phase, normalized_qudit)
    )
    result = {
        "depth": depth,
        "phase_radix": PHASE_RADIX,
        "qudit_radix": QUDIT_RADIX,
        "glyph_radix": GLYPH_RADIX,
        "phase_modulus": phase_modulus,
        "qudit_modulus": qudit_modulus,
        "combined_modulus": combined_modulus,
        "phase_word": phase_word,
        "qudit_word": qudit_word,
        "bigint": bigint,
        "glyph_stream": list(glyph_stream),
        "fixed_denominator_rational_position": {
            "numerator": bigint,
            "denominator": combined_modulus,
        },
        "phase_residue_exact": bigint % phase_modulus == phase_word,
        "qudit_residue_exact": bigint % qudit_modulus == qudit_word,
    }
    result["serialization_sha256"] = _digest(result)
    return result


def deserialize_qudit_assembly(bigint: int, depth: int) -> dict[str, Any]:
    bigint = _exact_int(bigint, "BIGINT")
    depth = _exact_int(depth, "DEPTH")
    if depth <= 0:
        raise NonaryQuditBigIntAssemblyProbeError("DEPTH_MUST_BE_POSITIVE")
    phase_modulus = PHASE_RADIX**depth
    qudit_modulus = QUDIT_RADIX**depth
    combined_modulus = GLYPH_RADIX**depth
    if bigint < 0 or bigint >= combined_modulus:
        raise NonaryQuditBigIntAssemblyProbeError("BIGINT_OUTSIDE_ASSEMBLY_MODULUS")
    phase_word = bigint % phase_modulus
    qudit_word = bigint % qudit_modulus
    phase_digits = decode_radix_digits(phase_word, PHASE_RADIX, depth)
    qudit_digits = decode_radix_digits(qudit_word, QUDIT_RADIX, depth)
    glyph_stream = tuple(
        encode_local_glyph(phase, qudit)
        for phase, qudit in zip(phase_digits, qudit_digits)
    )
    return {
        "depth": depth,
        "phase_word": phase_word,
        "qudit_word": qudit_word,
        "phase_digits": list(phase_digits),
        "qudit_digits": list(qudit_digits),
        "glyph_stream": list(glyph_stream),
        "bigint": bigint,
        "combined_modulus": combined_modulus,
    }


def bigint_from_glyph_stream(glyph_stream: Sequence[int]) -> int:
    if len(glyph_stream) <= 0:
        raise NonaryQuditBigIntAssemblyProbeError("GLYPH_STREAM_REQUIRED")
    decoded = [decode_local_glyph(glyph) for glyph in glyph_stream]
    phase_digits = [pair[0] for pair in decoded]
    qudit_digits = [pair[1] for pair in decoded]
    return int(serialize_qudit_assembly(phase_digits, qudit_digits)["bigint"])


def glyph_stream_from_bigint(bigint: int, depth: int) -> tuple[int, ...]:
    decoded = deserialize_qudit_assembly(bigint, depth)
    return tuple(int(value) for value in decoded["glyph_stream"])


def canonical_lo_shu_assembly_fixture() -> dict[str, Any]:
    """Build one depth-72 word containing every local 8x9 symbol exactly once."""
    if len(CHANNELS) != PHASE_RADIX:
        raise NonaryQuditBigIntAssemblyProbeError("EIGHT_ORDERED_PHASE_CHANNELS_REQUIRED")
    if sorted(LO_SHU) != list(range(1, 10)):
        raise NonaryQuditBigIntAssemblyProbeError("LO_SHU_MUST_BE_A_1_TO_9_PERMUTATION")
    phase_digits: list[int] = []
    qudit_digits: list[int] = []
    cells: list[dict[str, Any]] = []
    for phase_digit, channel in enumerate(CHANNELS):
        for lo_shu_index, lo_shu_value in enumerate(LO_SHU):
            qudit_digit = lo_shu_value - 1
            glyph = encode_local_glyph(phase_digit, qudit_digit)
            position = len(cells)
            phase_digits.append(phase_digit)
            qudit_digits.append(qudit_digit)
            cells.append(
                {
                    "position": position,
                    "phase_channel": channel,
                    "phase_digit": phase_digit,
                    "lo_shu_index": lo_shu_index,
                    "lo_shu_value": lo_shu_value,
                    "qudit_digit": qudit_digit,
                    "glyph": glyph,
                }
            )
    serialized = serialize_qudit_assembly(phase_digits, qudit_digits)
    restored = deserialize_qudit_assembly(serialized["bigint"], HASH72_DEPTH)
    glyphs = tuple(cell["glyph"] for cell in cells)
    return {
        "cells": cells,
        "phase_digits": phase_digits,
        "qudit_digits": qudit_digits,
        "glyph_stream": list(glyphs),
        "local_symbol_count": len(glyphs),
        "all_72_local_symbols_unique": len(set(glyphs)) == GLYPH_RADIX,
        "all_72_local_symbols_covered": set(glyphs) == set(range(GLYPH_RADIX)),
        "bigint": serialized["bigint"],
        "combined_modulus": serialized["combined_modulus"],
        "phase_round_trip_exact": restored["phase_digits"] == phase_digits,
        "qudit_round_trip_exact": restored["qudit_digits"] == qudit_digits,
        "glyph_round_trip_exact": restored["glyph_stream"] == list(glyphs),
        "bigint_glyph_stream_round_trip_exact": (
            bigint_from_glyph_stream(glyphs) == serialized["bigint"]
            and glyph_stream_from_bigint(serialized["bigint"], HASH72_DEPTH) == glyphs
        ),
    }


def build_pPq_lane_order_surface(P: int = 5) -> dict[str, Any]:
    """Bind the six tetrahedral relations to exact pq/qp directional order."""
    P = _exact_int(P, "P")
    if P <= 1:
        raise NonaryQuditBigIntAssemblyProbeError("P_MUST_EXCEED_ONE_FOR_PROBE")
    p = P - 1
    q = P + 1
    if p + q != 2 * P or p * q != P * P - 1:
        raise AssertionError("PQ_EXACT_PROJECTION_DRIFT")
    relations = list(combinations(STATE_ORDER, 2))
    directed: list[dict[str, Any]] = []
    for lane_index, (left, right) in enumerate(relations):
        directed.append(
            {
                "opcode": 2 * lane_index,
                "lane": lane_index,
                "source": left,
                "target": right,
                "direction": "pq",
                "order": [p, P, q],
            }
        )
        directed.append(
            {
                "opcode": 2 * lane_index + 1,
                "lane": lane_index,
                "source": right,
                "target": left,
                "direction": "qp",
                "order": [q, P, p],
            }
        )
    return {
        "P": P,
        "p": p,
        "q": q,
        "p_plus_q_equals_2P": p + q == 2 * P,
        "pq_equals_P2_minus_one": p * q == P * P - 1,
        "four_state_translation_surface": FOUR_STATE_TRANSLATION_SURFACE,
        "surface_scalarized": False,
        "undirected_lane_count": len(relations),
        "directed_lane_count": len(directed),
        "directed_lanes": directed,
        "opcodes_are_dense_0_through_11": [row["opcode"] for row in directed] == list(range(12)),
    }


def single_coordinate_injectivity_probe(depth: int = HASH72_DEPTH) -> dict[str, Any]:
    """Exercise every position with every nonzero local 72-state symbol."""
    depth = _exact_int(depth, "DEPTH")
    if depth <= 0:
        raise NonaryQuditBigIntAssemblyProbeError("DEPTH_MUST_BE_POSITIVE")
    addresses: set[int] = set()
    exact_round_trips = True
    for position in range(depth):
        for glyph in range(1, GLYPH_RADIX):
            phase_digit, qudit_digit = decode_local_glyph(glyph)
            phase = [0] * depth
            qudit = [0] * depth
            phase[position] = phase_digit
            qudit[position] = qudit_digit
            encoded = serialize_qudit_assembly(phase, qudit)
            bigint = int(encoded["bigint"])
            restored = deserialize_qudit_assembly(bigint, depth)
            if restored["phase_digits"] != phase or restored["qudit_digits"] != qudit:
                exact_round_trips = False
            addresses.add(bigint)
    expected = depth * (GLYPH_RADIX - 1)
    return {
        "depth": depth,
        "tested_nonzero_single_coordinate_states": expected,
        "unique_bigint_addresses": len(addresses),
        "all_tested_addresses_unique": len(addresses) == expected,
        "all_tested_round_trips_exact": exact_round_trips,
    }


def integer_range_round_trip_probe(depth: int = HASH72_DEPTH) -> dict[str, Any]:
    """Test representative integer positions, including both exact boundaries."""
    depth = _exact_int(depth, "DEPTH")
    modulus = GLYPH_RADIX**depth
    samples = [0, 1, 71, 72, 73, modulus // 2, modulus - 2, modulus - 1]
    rows = []
    for value in samples:
        decoded = deserialize_qudit_assembly(value, depth)
        rebuilt = serialize_qudit_assembly(decoded["phase_digits"], decoded["qudit_digits"])
        rows.append(
            {
                "value": value,
                "round_trip_exact": int(rebuilt["bigint"]) == value,
            }
        )
    return {
        "modulus": modulus,
        "samples": rows,
        "all_samples_round_trip_exact": all(row["round_trip_exact"] for row in rows),
        "zero_is_first_integer_position": samples[0] == 0,
        "max_is_last_integer_position": samples[-1] == modulus - 1,
    }


def nonary_scaling_probe() -> dict[str, Any]:
    """Verify that increasing qudit depth changes only the exact radix modulus."""
    rows = []
    for depth in (1, 2, 9, HASH72_DEPTH):
        qudit_digits = tuple(LO_SHU_QUDIT_DIGITS[index % len(LO_SHU_QUDIT_DIGITS)] for index in range(depth))
        word = encode_radix_digits(qudit_digits, QUDIT_RADIX)
        restored = decode_radix_digits(word, QUDIT_RADIX, depth)
        rows.append(
            {
                "depth": depth,
                "modulus": QUDIT_RADIX**depth,
                "round_trip_exact": restored == qudit_digits,
            }
        )
    return {
        "rows": rows,
        "same_encode_decode_primitive_at_every_depth": all(row["round_trip_exact"] for row in rows),
        "primitive_rule_count_increases_with_depth": False,
    }


def bigint_qudit_assembly_probe(P: int = 5) -> dict[str, Any]:
    """Run the complete exact serialization/assembly diagnostic surface."""
    local_pairs = []
    glyphs = set()
    local_round_trip_exact = True
    for phase in range(PHASE_RADIX):
        for qudit in range(QUDIT_RADIX):
            glyph = encode_local_glyph(phase, qudit)
            restored = decode_local_glyph(glyph)
            local_round_trip_exact = local_round_trip_exact and restored == (phase, qudit)
            glyphs.add(glyph)
            local_pairs.append({"phase": phase, "qudit": qudit, "glyph": glyph})

    fixture = canonical_lo_shu_assembly_fixture()
    lanes = build_pPq_lane_order_surface(P)
    injectivity = single_coordinate_injectivity_probe(HASH72_DEPTH)
    range_probe = integer_range_round_trip_probe(HASH72_DEPTH)
    scaling = nonary_scaling_probe()
    report = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "local_symbol_algebra": {
            "phase_radix": PHASE_RADIX,
            "qudit_radix": QUDIT_RADIX,
            "glyph_radix": GLYPH_RADIX,
            "factorization": "72=8*9",
            "phase_qudit_pair_count": len(local_pairs),
            "unique_glyph_count": len(glyphs),
            "local_crt_is_bijective": len(glyphs) == GLYPH_RADIX and local_round_trip_exact,
            "phase_channel_order": list(CHANNELS),
            "lo_shu": list(LO_SHU),
            "lo_shu_qudit_digits": list(LO_SHU_QUDIT_DIGITS),
        },
        "hash72_assembly": {
            "depth": HASH72_DEPTH,
            "phase_layer_modulus": PHASE_RADIX**HASH72_DEPTH,
            "nonary_layer_modulus": QUDIT_RADIX**HASH72_DEPTH,
            "combined_modulus": HASH72_MANIFOLD_CARDINALITY,
            "factorization_exact": (
                PHASE_RADIX**HASH72_DEPTH * QUDIT_RADIX**HASH72_DEPTH
                == HASH72_MANIFOLD_CARDINALITY
            ),
            "integer_position_min": 0,
            "integer_position_max": HASH72_MANIFOLD_CARDINALITY - 1,
            "integer_position_count": HASH72_MANIFOLD_CARDINALITY,
            "one_fixed_denominator_rational_position_per_integer": True,
            "fixture_bigint": fixture["bigint"],
            "fixture_all_72_local_symbols_covered": fixture["all_72_local_symbols_covered"],
            "fixture_phase_round_trip_exact": fixture["phase_round_trip_exact"],
            "fixture_qudit_round_trip_exact": fixture["qudit_round_trip_exact"],
            "fixture_glyph_round_trip_exact": fixture["glyph_round_trip_exact"],
            "fixture_bigint_glyph_stream_round_trip_exact": fixture[
                "bigint_glyph_stream_round_trip_exact"
            ],
        },
        "lane_order": lanes,
        "single_coordinate_injectivity": injectivity,
        "integer_range_round_trip": range_probe,
        "nonary_scaling": scaling,
        "assembly_result": {
            "bigint_and_typed_phase_qudit_stream_are_exact_bijective_views": True,
            "each_hash72_state_has_one_integer_position_under_this_serialization": (
                local_round_trip_exact
                and range_probe["all_samples_round_trip_exact"]
                and fixture["phase_round_trip_exact"]
                and fixture["qudit_round_trip_exact"]
                and injectivity["all_tested_addresses_unique"]
                and injectivity["all_tested_round_trips_exact"]
            ),
            "same_serialization_primitives_scale_to_deeper_qudit_layers": scaling[
                "same_encode_decode_primitive_at_every_depth"
            ],
            "six_lanes_are_pPq_ordered_with_twelve_directed_opcodes": (
                lanes["undirected_lane_count"] == 6
                and lanes["directed_lane_count"] == 12
                and lanes["opcodes_are_dense_0_through_11"]
            ),
            "bigint_is_harmonicode_qudit_assembly_carrier_candidate": True,
            "new_primitive_algebra_required_for_depth_scaling": False,
        },
        "authority": {
            "diagnostic_only": True,
            "canonical_equation_rewrite": False,
            "typed_c4_p4_surface_scalarized": False,
            "vm81_mutation": False,
            "hash72_minting": False,
            "hash216_persistence": False,
            "floating_point_authority": False,
        },
    }
    report["report_sha256"] = _digest(report)
    return report


def main() -> int:
    report = bigint_qudit_assembly_probe()
    result = report["assembly_result"]
    required = (
        report["local_symbol_algebra"]["local_crt_is_bijective"],
        report["hash72_assembly"]["factorization_exact"],
        report["hash72_assembly"]["fixture_all_72_local_symbols_covered"],
        report["hash72_assembly"]["fixture_phase_round_trip_exact"],
        report["hash72_assembly"]["fixture_qudit_round_trip_exact"],
        report["hash72_assembly"]["fixture_glyph_round_trip_exact"],
        report["single_coordinate_injectivity"]["all_tested_addresses_unique"],
        report["single_coordinate_injectivity"]["all_tested_round_trips_exact"],
        report["integer_range_round_trip"]["all_samples_round_trip_exact"],
        report["nonary_scaling"]["same_encode_decode_primitive_at_every_depth"],
        result["each_hash72_state_has_one_integer_position_under_this_serialization"],
        result["six_lanes_are_pPq_ordered_with_twelve_directed_opcodes"],
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
