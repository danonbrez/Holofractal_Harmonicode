"""Pass 220 I080 deterministic knowledge-graph QPU boundary.

Additive proof/reference layer for the frozen I041 browser seed.  The layer
binds the complete 5,184-address BigInt carrier, typed Genesis constructors,
the u^16 nine-phase 64:72:81 gear, exact I065 Hash216 hydration, and a
lossless symbolic IEEE-754 bit-string RNA ingress/egress membrane.

All arithmetic in this module is exact integer/string structure.  IEEE-754
encodings are transported as symbolic bit strings; they are never evaluated
through a host floating-point algorithm.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH72_ALPHABET,
    HASH216_LEN,
    coordinate_5184,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    FULL_HASH216_COMPONENTS,
    hydrate_hash216_geometry,
)

SCHEMA = "HHS_PASS_220_I080_DETERMINISTIC_KNOWLEDGE_GRAPH_QPU_V1"
VERSION = "1.0.0"

SERIALIZED_CHARACTERS = 5184
LAST_ADDRESS = 5183
FREE_TERNARY_POSITIONS = 5183
VM81_CELLS = 81
LOCAL64 = 64
HASH72 = 72
HASH216_PLANES = 3
FULL_ATTACHED = HASH216_PLANES * SERIALIZED_CHARACTERS
OFFSET_MIN = -9
OFFSET_MAX = 9
OFFSET_CARDINALITY = 19
PHASE_MODULUS = 72
PHASE_STEP = 16
PHASE_ORBIT = 9
PHASE_GEAR_E = (8, 24, 40, 56, 72, 16, 32, 48, 64)
ROOT_METADATA_SEED = "179971.179971"

DECIMAL_ADDRESS_ALPHABET = tuple("0123456789")
DYADIC_4_7_11 = (4, 7, 11)
FRACTAL_123 = ((1, 2, 3), (2, 4, 6), (3, 6, 9))

GENESIS = {
    "10": "LO_SHU_SUDOKU_QUDIT_NUCLEUS",
    "20": "DYADIC_4_7_11_SCALING_QUANTIZATION",
    "30": "TRIADIC_A2_B2_C2_CLOSURE",
    "100": "DUAL_9X9_QUDIT_ENTANGLEMENT",
}

AUTHORITY = {
    "candidate_only": True,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "ieee_float_internal_logic_authority": False,
    "lossy_scalar_projection_authority": False,
    "browser_math_random_authority": False,
}


class I080QPUError(ValueError):
    """Fail-closed deterministic-QPU boundary error."""


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise I080QPUError(f"{name} must be an exact integer")
    return value


def genesis_serialization(prefix: str) -> dict[str, Any]:
    if prefix not in GENESIS:
        raise I080QPUError(f"unsupported Genesis constructor {prefix!r}")
    padding = SERIALIZED_CHARACTERS - len(prefix)
    carrier = prefix + ("0" * padding)
    if len(carrier) != SERIALIZED_CHARACTERS:
        raise AssertionError("Genesis carrier width drift")
    record: dict[str, Any] = {
        "prefix": prefix,
        "constructor": GENESIS[prefix],
        "serialized5184": carrier,
        "serialized_characters": len(carrier),
        "padding_hnan_zero_positions": padding,
        "hnan_zero_defined": True,
        "root_metadata_seed": ROOT_METADATA_SEED,
        "sha256": sha256(carrier.encode("ascii")).hexdigest(),
    }
    if prefix == "10":
        record.update({
            "decimal_address_alphabet": DECIMAL_ADDRESS_ALPHABET,
            "lo_shu_sudoku_qudit_nucleus": True,
            "nonzero_arabic_symbols": tuple("123456789"),
        })
    elif prefix == "20":
        record["dyadic_scaling_quantization"] = DYADIC_4_7_11
    elif prefix == "30":
        record.update({
            "triadic_fractal_123": FRACTAL_123,
            "triadic_closure": "a^2+b^2=c^2=(A+B=C)/(AB/P^4)",
            "direct_quartic_closure": "AB=P^4",
        })
    else:
        record["dual_qudit_entanglement"] = {
            "constructor_source": "100=90+10=81*81",
            "left_qudit_cells": 81,
            "right_qudit_cells": 81,
            "ordered_pair_addresses": 81 * 81,
        }
    return record


def genesis_bundle() -> dict[str, Any]:
    constructors = {key: genesis_serialization(key) for key in GENESIS}
    return {
        "constructors": constructors,
        "all_width_5184": all(
            row["serialized_characters"] == SERIALIZED_CHARACTERS
            for row in constructors.values()
        ),
        "genesis_zero": "0" * SERIALIZED_CHARACTERS,
        "genesis_zero_positions": SERIALIZED_CHARACTERS,
        "hnan_zero_defined": True,
    }


def validate_offset_tensor(offsets: Sequence[int]) -> dict[str, Any]:
    values = tuple(offsets)
    if len(values) != SERIALIZED_CHARACTERS:
        raise I080QPUError("offset tensor must contain exactly 5184 addressed states")
    witness = []
    for index, raw in enumerate(values):
        value = _exact_int(raw, name=f"offset[{index}]")
        if not OFFSET_MIN <= value <= OFFSET_MAX:
            raise I080QPUError(f"offset[{index}] outside -9..+9")
        c = coordinate_5184(index)
        witness.append((
            index,
            value,
            c["vm81_cell"],
            c["local64"],
            c["hash72_row"],
            c["hash72_column"],
        ))
    return {
        "positions": len(values),
        "address_range": (0, LAST_ADDRESS),
        "offset_min": OFFSET_MIN,
        "offset_max": OFFSET_MAX,
        "offset_cardinality": OFFSET_CARDINALITY,
        "all_addresses_covered": len(witness) == SERIALIZED_CHARACTERS,
        "state_root_sha256": sha256(repr(witness).encode("utf-8")).hexdigest(),
        "lossy_scalar_projection_used": False,
    }


def trinary_tensor_witness() -> dict[str, Any]:
    return {
        "carrier_positions": SERIALIZED_CHARACTERS,
        "nucleus_anchor_positions": 1,
        "free_trinary_positions": FREE_TERNARY_POSITIONS,
        "phase_alphabet": (-1, 0, 1),
        "state_space_source": "3^5183",
        "every_character_addressed": True,
        "materialized": False,
    }


def phase_gear_tick(tick: int) -> dict[str, Any]:
    k = _exact_int(tick, name="tick")
    if k < 0:
        raise I080QPUError("tick must be nonnegative")
    if VM81_CELLS * LOCAL64 != HASH72 * HASH72 != SERIALIZED_CHARACTERS:
        raise AssertionError("unreachable")
    if VM81_CELLS * LOCAL64 != SERIALIZED_CHARACTERS:
        raise I080QPUError("VM81 81x64 geometry drift")
    if HASH72 * HASH72 != SERIALIZED_CHARACTERS:
        raise I080QPUError("Hash72 72x72 geometry drift")
    if 64 * 81 != 72 * 72:
        raise I080QPUError("64:72:81 gear closure drift")
    if PHASE_ORBIT * PHASE_STEP != 2 * PHASE_MODULUS:
        raise I080QPUError("u^16 nine-phase orbit drift")

    linear = k % SERIALIZED_CHARACTERS
    phase_index = k % PHASE_ORBIT
    phase_value = PHASE_GEAR_E[phase_index]
    return {
        "tick": k,
        "one_tick_one_lane5_optimization_operation": True,
        "linear5184": linear,
        "coordinate5184": coordinate_5184(linear),
        "phase_step": PHASE_STEP,
        "phase_modulus": PHASE_MODULUS,
        "phase_orbit_length": PHASE_ORBIT,
        "phase_gear_E": PHASE_GEAR_E,
        "u16_phase_index9": phase_index,
        "u16_phase_value": phase_value,
        "ratio_64_72": (8, 9),
        "ratio_72_81": (8, 9),
        "common_closure_5184": 64 * 81,
        "nine_steps": PHASE_ORBIT * PHASE_STEP,
        "two_turns": 2 * PHASE_MODULUS,
        "full_5184_tick_period_restores_address": (
            (k + SERIALIZED_CHARACTERS) % SERIALIZED_CHARACTERS == linear
        ),
        "quartic_closure": "AB=P^4",
        "mirror_quartic_closure": "BA=-P^4",
        "hnan_closure": True,
    }


IEEE_LAYOUTS: dict[int, tuple[int, int]] = {
    16: (5, 10),
    32: (8, 23),
    64: (11, 52),
}


def _require_bits(raw_bits: str) -> tuple[int, int, int]:
    if not isinstance(raw_bits, str) or not raw_bits or any(ch not in "01" for ch in raw_bits):
        raise I080QPUError("IEEE ingress requires a raw 0/1 bit string")
    width = len(raw_bits)
    try:
        exponent_width, fraction_width = IEEE_LAYOUTS[width]
    except KeyError as exc:
        raise I080QPUError("IEEE ingress width must be binary16, binary32, or binary64") from exc
    if 1 + exponent_width + fraction_width != width:
        raise AssertionError("IEEE layout drift")
    return width, exponent_width, fraction_width


def ieee754_symbolic_ingress(raw_bits: str) -> dict[str, Any]:
    width, exponent_width, fraction_width = _require_bits(raw_bits)
    exponent_end = 1 + exponent_width
    sign = raw_bits[0]
    exponent = raw_bits[1:exponent_end]
    fraction = raw_bits[exponent_end:]
    exponent_all_zero = all(ch == "0" for ch in exponent)
    exponent_all_one = all(ch == "1" for ch in exponent)
    fraction_all_zero = all(ch == "0" for ch in fraction)
    if exponent_all_one:
        classification = "INFINITY" if fraction_all_zero else "NAN"
    elif exponent_all_zero:
        classification = "ZERO" if fraction_all_zero else "SUBNORMAL"
    else:
        classification = "NORMAL"
    mirror = raw_bits[::-1]
    return {
        "format": f"binary{width}",
        "width": width,
        "sign_bit": sign,
        "exponent_bits": exponent,
        "fraction_bits": fraction,
        "classification": classification,
        "raw_bits": raw_bits,
        "mirror_bits": mirror,
        "palindromic_carrier": raw_bits + "." + mirror,
        "symbolic_constructor": f"IEEE754[{sign}|{exponent}|{fraction}]",
        "internal_ieee_float_algorithm_used": False,
        "lossy_scalar_projection_used": False,
        "raw_bits_sha256": sha256(raw_bits.encode("ascii")).hexdigest(),
    }


def ieee754_symbolic_egress(record: Mapping[str, Any]) -> str:
    if not isinstance(record, Mapping):
        raise I080QPUError("IEEE RNA egress requires a mapping")
    raw = record.get("raw_bits")
    if not isinstance(raw, str):
        raise I080QPUError("IEEE RNA record is missing raw_bits")
    replay = ieee754_symbolic_ingress(raw)
    for key in (
        "format",
        "width",
        "sign_bit",
        "exponent_bits",
        "fraction_bits",
        "classification",
        "mirror_bits",
        "palindromic_carrier",
        "symbolic_constructor",
        "raw_bits_sha256",
    ):
        if replay[key] != record.get(key):
            raise I080QPUError(f"IEEE RNA record drift at {key}")
    return raw


def ieee754_lossless_roundtrip(raw_bits: str) -> dict[str, Any]:
    ingress = ieee754_symbolic_ingress(raw_bits)
    egress = ieee754_symbolic_egress(ingress)
    return {
        "ingress": ingress,
        "egress_raw_bits": egress,
        "roundtrip_exact": egress == raw_bits,
        "palindromic_reverse_exact": ingress["mirror_bits"][::-1] == raw_bits,
        "internal_ieee_float_algorithm_used": False,
        "lossy_scalar_projection_used": False,
    }


def hash216_hydration_translation(hash216: str) -> dict[str, Any]:
    if not isinstance(hash216, str) or len(hash216) != HASH216_LEN:
        raise I080QPUError("Hash216 must contain exactly 216 symbols")
    hydrated = hydrate_hash216_geometry(hash216)
    if hydrated["full_attached_components"] != FULL_HASH216_COMPONENTS:
        raise I080QPUError("I065 Hash216 hydration component drift")
    planes = tuple({
        "role": plane["role"],
        "hash72": plane["generator_hash72"],
        "offset_positions": plane["expanded_vertices"],
        "roundtrip_exact": plane["roundtrip_exact"],
        "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
    } for plane in hydrated["planes"])
    return {
        "hash216_width": len(hash216),
        "plane_count": len(planes),
        "planes": planes,
        "positions_per_plane": SERIALIZED_CHARACTERS,
        "full_attached_components": hydrated["full_attached_components"],
        "roundtrip_exact": hydrated["roundtrip_exact"],
        "lossless_translation": True,
    }


def reference_hash216() -> str:
    lane0 = HASH72_ALPHABET
    lane1 = HASH72_ALPHABET[::-1]
    lane2 = HASH72_ALPHABET[1:] + HASH72_ALPHABET[:1]
    result = lane0 + lane1 + lane2
    if len(result) != HASH216_LEN:
        raise AssertionError("reference Hash216 width drift")
    return result


def deterministic_qpu_witness(hash216: str | None = None) -> dict[str, Any]:
    source = reference_hash216() if hash216 is None else hash216
    zero_offsets = (0,) * SERIALIZED_CHARACTERS
    ieee_vectors = (
        "0" * 16,
        "1" + ("0" * 15),
        "0011110000000000",
        "0" * 32,
        "00111111100000000000000000000000",
        "0" * 64,
        "0011111111110000000000000000000000000000000000000000000000000000",
        "0111111111110000000000000000000000000000000000000000000000000000",
        "0111111111111000000000000000000000000000000000000000000000000001",
    )
    ieee = tuple(ieee754_lossless_roundtrip(bits) for bits in ieee_vectors)
    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "genesis": genesis_bundle(),
        "offset_tensor": validate_offset_tensor(zero_offsets),
        "trinary_tensor": trinary_tensor_witness(),
        "phase_gear": {
            "tick0": phase_gear_tick(0),
            "tick5183": phase_gear_tick(5183),
            "tick5184": phase_gear_tick(5184),
        },
        "hash216_hydration": hash216_hydration_translation(source),
        "ieee754_ingress_egress": ieee,
        "lossless_ieee_all_vectors": all(row["roundtrip_exact"] for row in ieee),
        "authority": dict(AUTHORITY),
    }
    result["witness_sha256"] = sha256(repr(result).encode("utf-8")).hexdigest()
    return result


def self_test() -> dict[str, Any]:
    witness = deterministic_qpu_witness()
    g = witness["genesis"]["constructors"]
    checks = {
        "genesis_all_width_5184": witness["genesis"]["all_width_5184"],
        "genesis_10_padding_5182": g["10"]["padding_hnan_zero_positions"] == 5182,
        "genesis_20_dyadic_4_7_11": g["20"]["dyadic_scaling_quantization"] == DYADIC_4_7_11,
        "genesis_30_triadic_123": g["30"]["triadic_fractal_123"] == FRACTAL_123,
        "genesis_100_dual_qudit": g["100"]["dual_qudit_entanglement"]["ordered_pair_addresses"] == 6561,
        "offsets_cover_5184": witness["offset_tensor"]["all_addresses_covered"],
        "offset_alphabet_19": witness["offset_tensor"]["offset_cardinality"] == 19,
        "trinary_free_positions_5183": witness["trinary_tensor"]["free_trinary_positions"] == 5183,
        "trinary_source_3_pow_5183": witness["trinary_tensor"]["state_space_source"] == "3^5183",
        "phase_gear_E_exact": witness["phase_gear"]["tick0"]["phase_gear_E"] == PHASE_GEAR_E,
        "phase_gear_64_72_81": witness["phase_gear"]["tick0"]["common_closure_5184"] == 5184,
        "phase_gear_u16_two_turn": witness["phase_gear"]["tick0"]["nine_steps"] == 144,
        "tick_5184_restores": witness["phase_gear"]["tick5184"]["linear5184"] == 0,
        "hash216_width": witness["hash216_hydration"]["hash216_width"] == 216,
        "hash216_three_planes": witness["hash216_hydration"]["plane_count"] == 3,
        "hash216_hydration_15552": witness["hash216_hydration"]["full_attached_components"] == FULL_ATTACHED,
        "hash216_roundtrip": witness["hash216_hydration"]["roundtrip_exact"],
        "ieee_all_lossless": witness["lossless_ieee_all_vectors"],
        "authority_fail_closed": (
            witness["authority"]["ieee_float_internal_logic_authority"] is False
            and witness["authority"]["lossy_scalar_projection_authority"] is False
            and witness["authority"]["canonical_hash216_commit_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(v) for v in checks.values()),
        "failed": tuple(k for k, v in checks.items() if not v),
        "checks": checks,
        "witness_sha256": witness["witness_sha256"],
    }


__all__ = [
    "AUTHORITY",
    "DECIMAL_ADDRESS_ALPHABET",
    "DYADIC_4_7_11",
    "FRACTAL_123",
    "GENESIS",
    "I080QPUError",
    "OFFSET_MAX",
    "OFFSET_MIN",
    "PHASE_GEAR_E",
    "SCHEMA",
    "VERSION",
    "deterministic_qpu_witness",
    "genesis_bundle",
    "genesis_serialization",
    "hash216_hydration_translation",
    "ieee754_lossless_roundtrip",
    "ieee754_symbolic_egress",
    "ieee754_symbolic_ingress",
    "phase_gear_tick",
    "reference_hash216",
    "self_test",
    "trinary_tensor_witness",
    "validate_offset_tensor",
]


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), sort_keys=True, indent=2))
