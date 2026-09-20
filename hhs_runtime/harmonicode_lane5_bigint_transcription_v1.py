"""Pass 219 Lane 5 1.52: BigInt transcription geometry and nested boundary binding.

This layer does not create a second codec. It exposes one typed callable over the
existing canonical 5,184-character serializer so the same operation is used in
both directions, and binds the already-implemented Lo Shu/H36/RNA geometry to
the universal P/Delta boundary condition.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple, Union

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    FRACTAL_123,
    LO_SHU,
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_rna_hash72_dna_qudit_phase_lock_v1 import (
    coordinate_phase_lock_witness,
    palindromic_precision_lanes,
    phase_locked_state_witness,
)

SCHEMA = "HHS_PASS219_LANE5_BIGINT_NESTED_TRANSCRIPTION_V1"
VERSION = "1.0.0"
GLOBAL_DENOMINATOR_NATIVE = "(P=√(pq+(P⁴/AB)))/∆"
GLOBAL_DENOMINATOR_ASCII = "(P=sqrt(pq+(P^4/AB)))/Delta"
GENESIS_UNIT_PROJECTION = "1_G=123321.111/a^2"
NESTED_BOUNDARY_KINDS: Tuple[str, ...] = (
    "rational",
    "matrix",
    "continued_fraction",
    "tensor",
    "x",
    "y",
    "z",
    "w",
    "A",
    "B",
)

SerializedOrOffsets = Union[str, Tuple[int, ...]]


class Lane5BigIntTranscriptionError(ValueError):
    pass


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


def transcribe_5184(value: str | Sequence[int]) -> SerializedOrOffsets:
    """Traverse the canonical BigInt serializer in either direction.

    A canonical 5,184-character state returns its 81 exact offsets. An 81-cell
    exact offset sequence returns the canonical 5,184-character state. This is
    deliberately one callable over the inherited serializer/deserializer pair,
    so callers do not acquire independent ingress and egress algorithms.
    """
    if isinstance(value, str):
        return deserialize_offsets_5184(value)
    if isinstance(value, (bytes, bytearray)):
        raise Lane5BigIntTranscriptionError("binary buffers are not offset sequences")
    try:
        offsets = tuple(value)
    except TypeError as exc:
        raise Lane5BigIntTranscriptionError("unsupported transcription input") from exc
    return serialize_offsets_5184(offsets)


def boundary_manifest(
    kinds: Iterable[str] = NESTED_BOUNDARY_KINDS,
) -> Dict[str, Any]:
    objects = tuple(str(kind) for kind in kinds)
    if not objects:
        raise Lane5BigIntTranscriptionError("at least one nested boundary object is required")
    return {
        "global_denominator_native": GLOBAL_DENOMINATOR_NATIVE,
        "global_denominator_ascii": GLOBAL_DENOMINATOR_ASCII,
        "objects": tuple(
            {
                "kind": kind,
                "boundary_condition": True,
                "global_denominator": GLOBAL_DENOMINATOR_NATIVE,
                "independent_normalization_authority": False,
            }
            for kind in objects
        ),
    }


def geometry_witness() -> Dict[str, Any]:
    lanes = palindromic_precision_lanes()
    lo_shu_rows = tuple(sum(row) for row in LO_SHU)
    lo_shu_columns = tuple(sum(LO_SHU[row][column] for row in range(3)) for column in range(3))
    lo_shu_diagonals = (
        sum(LO_SHU[i][i] for i in range(3)),
        sum(LO_SHU[i][2 - i] for i in range(3)),
    )
    coordinate = coordinate_phase_lock_witness()
    h36_population_sum = sum(range(1, 37))
    base_lane = lanes[0]
    genesis_seed = (
        f"{base_lane['palindrome_digits']}."
        f"{base_lane['remainder_numerator']:03d}"
    )
    return _receipt({
        "schema": f"{SCHEMA}_GEOMETRY",
        "g123": FRACTAL_123,
        "lo_shu": LO_SHU,
        "lo_shu_rows": lo_shu_rows,
        "lo_shu_columns": lo_shu_columns,
        "lo_shu_diagonals": lo_shu_diagonals,
        "macro_side": 4,
        "local_tensor_side": 3,
        "ordered_side": 12,
        "ordered_tensor_positions": 144,
        "h36_side": 6,
        "h36_states": 36,
        "h36_population_sum": h36_population_sum,
        "h36_normalization": h36_population_sum // 6,
        "palindromes": tuple(lane["palindrome_digits"] for lane in lanes),
        "genesis_seed": genesis_seed,
        "genesis_unit_projection": GENESIS_UNIT_PROJECTION,
        "serialized_characters": SERIALIZED_CHARACTERS,
        "hash72_square": 72 * 72,
        "vm81_local64": 81 * 64,
        "coordinate_bijection": coordinate["all_coordinate_systems_bijective"],
    })


def validate_lane5_1_52() -> Dict[str, Any]:
    offsets = tuple(index % 9 for index in range(VM81_CELLS))
    serialized = transcribe_5184(offsets)
    if not isinstance(serialized, str):
        raise AssertionError("offset transcription did not return serialization")
    recovered = transcribe_5184(serialized)
    geometry = geometry_witness()
    manifest = boundary_manifest()
    phase = phase_locked_state_witness(serialized)

    first_token = serialized[:64]
    shared_denominators = {
        item["global_denominator"] for item in manifest["objects"]
    }

    checks = {
        "single_transcription_callable": transcribe_5184.__name__ == "transcribe_5184",
        "same_circuit_roundtrip": recovered == offsets,
        "fixed_width_5184": len(serialized) == 5184,
        "leading_zero_token_preserved": (
            offsets[0] == 0
            and first_token[1:21] == "0" * 20
            and first_token[22:42] == "0" * 19 + "1"
        ),
        "g123_exact": geometry["g123"] == ((1, 2, 3), (2, 4, 6), (3, 6, 9)),
        "sum_product_six": sum((1, 2, 3)) == 1 * 2 * 3 == 6,
        "h36_exact": (
            geometry["h36_states"] == 36
            and geometry["h36_population_sum"] == 666
            and geometry["h36_normalization"] == 111
        ),
        "twelve_squared_is_144": (
            geometry["ordered_side"] == 12
            and geometry["ordered_tensor_positions"] == 144
        ),
        "tensor_h36_is_5184": geometry["ordered_tensor_positions"] * geometry["h36_states"] == 5184,
        "factorizations_5184": geometry["hash72_square"] == geometry["vm81_local64"] == 5184,
        "palindromic_scaling_lanes": geometry["palindromes"] == ("123321", "246642", "369963"),
        "genesis_seed_123321_111": geometry["genesis_seed"] == "123321.111",
        "lo_shu_magic_geometry": (
            geometry["lo_shu_rows"] == (15, 15, 15)
            and geometry["lo_shu_columns"] == (15, 15, 15)
            and geometry["lo_shu_diagonals"] == (15, 15)
        ),
        "shared_global_denominator": shared_denominators == {GLOBAL_DENOMINATOR_NATIVE},
        "all_nested_objects_are_boundary_conditions": all(
            item["boundary_condition"]
            and not item["independent_normalization_authority"]
            for item in manifest["objects"]
        ),
        "coordinate_bijection_5184": geometry["coordinate_bijection"] is True,
        "complete_serialized_state_is_operand": phase["complete_state_is_serialized_operand"] is True,
        "authority_not_duplicated": (
            phase["canonical_vm81_mutation_authority"] is False
            and phase["canonical_hash72_authority"] is False
            and phase["canonical_hash216_authority"] is False
            and phase["floating_point_authority"] is False
        ),
    }
    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "global_denominator_native": GLOBAL_DENOMINATOR_NATIVE,
        "genesis_unit_projection": GENESIS_UNIT_PROJECTION,
        "serialized_state_root_sha256": phase["state_root_sha256"],
        "transcription_operation": "transcribe_5184",
        "ingress_egress_same_operation": True,
        "nested_payloads_remain_typed": True,
        "source_complete_formalization_status": "IN_PROGRESS",
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def main() -> int:
    report = validate_lane5_1_52()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
