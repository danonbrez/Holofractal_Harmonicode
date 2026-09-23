"""Pass 220 I036: Genesis / reverse-offset holographic Lo Shu nucleus.

I036 freezes three exact, mutually reconstructible coordinate views of the
same Lo Shu nucleus:

    Genesis offset : {-4,-3,-2,-1,0,1,2,3,4}
    Lo Shu magnitude: {1,2,3,4,5,6,7,8,9}
    reverse offset : {-3,-1,1,3,5,7,9,11,13}

For a Lo Shu magnitude m:

    epsilon = m - 5
    m       = epsilon + 5
    r       = 5 + 2*epsilon = 2*m - 5

The three layers retain the same Lo Shu address and are carried
co-residently.  No layer replaces the others.  The signed Genesis layer
has zero line sums; the magnitude and reverse-offset layers each retain
line sum 15.  All three preserve the same center and reflection pairing.

This is a validated-operation constructor only.  It contains local
constraints but has no canonical mutation, Hash72/Hash216, or persistence
authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    CELL_TOKEN_CHARACTERS,
    HASH72_BASE,
    LO_SHU,
    LO_SHU_FLAT,
    NUCLEUS_CELLS,
    SCALAR_RADIX,
    VM81_CELLS,
    lo_shu_positions,
    repeated_lo_shu_reference,
)

SCHEMA = "HHS_PASS_220_I036_GENESIS_REVERSE_OFFSET_HOLOGRAPHIC_NUCLEUS_V1"
VERSION = "1.0.0-checkpoint.36"
PROFILE = "PASS220-I036-GENESIS-REVERSE-OFFSET-HOLOGRAPHIC-NUCLEUS-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I036_HOLOGRAPHIC_NUCLEUS_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I036_HOLOGRAPHIC_NUCLEUS_WITNESS_V1"

CENTER_MAGNITUDE = 5
GENESIS_OFFSET_ALPHABET = tuple(range(-4, 5))
LO_SHU_MAGNITUDE_ALPHABET = tuple(range(1, 10))
REVERSE_OFFSET_ALPHABET = tuple(range(-3, 14, 2))
OPERATION64 = 8 * 8
VM5184 = VM81_CELLS * OPERATION64

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "GENESIS_OFFSET_EQUALS_MAGNITUDE_MINUS_5",
    "MAGNITUDE_EQUALS_GENESIS_OFFSET_PLUS_5",
    "REVERSE_OFFSET_EQUALS_5_PLUS_2_TIMES_GENESIS_OFFSET",
    "REVERSE_OFFSET_EQUALS_2_TIMES_MAGNITUDE_MINUS_5",
    "ALL_THREE_LAYERS_PRESERVE_LO_SHU_CELL_ADDRESS",
    "ALL_THREE_LAYERS_ARE_MUTUALLY_RECONSTRUCTIBLE",
    "GENESIS_LAYER_LINE_SUMS_ZERO",
    "MAGNITUDE_LAYER_LINE_SUMS_FIFTEEN",
    "REVERSE_OFFSET_LAYER_LINE_SUMS_FIFTEEN",
    "CENTER_ZERO_FIVE_FIVE_COINCIDENCE_PRESERVED",
    "REFLECTION_PAIRS_PRESERVE_SUM_TEN",
    "NINE_NUCLEI_FORM_VM81",
    "VM81_TIMES_64_EQUALS_72_SQUARED_EQUALS_5184",
    "NO_HOST_FLOAT_ARITHMETIC",
)


class Pass220I036NucleusError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I036NucleusError(f"{name} must be an exact integer")
    return value


def genesis_offset_from_magnitude(magnitude: int) -> int:
    m = _exact_int(magnitude, name="magnitude")
    if m not in LO_SHU_MAGNITUDE_ALPHABET:
        raise Pass220I036NucleusError("magnitude must be in 1..9")
    return m - CENTER_MAGNITUDE


def magnitude_from_genesis_offset(offset: int) -> int:
    e = _exact_int(offset, name="genesis offset")
    if e not in GENESIS_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("genesis offset must be in -4..4")
    return e + CENTER_MAGNITUDE


def reverse_offset_from_genesis_offset(offset: int) -> int:
    e = _exact_int(offset, name="genesis offset")
    if e not in GENESIS_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("genesis offset must be in -4..4")
    return CENTER_MAGNITUDE + 2 * e


def reverse_offset_from_magnitude(magnitude: int) -> int:
    m = _exact_int(magnitude, name="magnitude")
    if m not in LO_SHU_MAGNITUDE_ALPHABET:
        raise Pass220I036NucleusError("magnitude must be in 1..9")
    return 2 * m - CENTER_MAGNITUDE


def genesis_offset_from_reverse_offset(reverse_offset: int) -> int:
    r = _exact_int(reverse_offset, name="reverse offset")
    if r not in REVERSE_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("reverse offset outside canonical alphabet")
    numerator = r - CENTER_MAGNITUDE
    if numerator % 2:
        raise Pass220I036NucleusError("reverse offset does not map to an exact Genesis offset")
    e = numerator // 2
    if e not in GENESIS_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("decoded Genesis offset outside canonical alphabet")
    return e


def magnitude_from_reverse_offset(reverse_offset: int) -> int:
    return magnitude_from_genesis_offset(
        genesis_offset_from_reverse_offset(reverse_offset)
    )


def _matrix_map(function):
    return tuple(tuple(function(value) for value in row) for row in LO_SHU)


def genesis_offset_matrix() -> Tuple[Tuple[int, ...], ...]:
    return _matrix_map(genesis_offset_from_magnitude)


def reverse_offset_matrix() -> Tuple[Tuple[int, ...], ...]:
    return _matrix_map(reverse_offset_from_magnitude)


def _line_sums(matrix: Sequence[Sequence[int]]) -> Dict[str, Tuple[int, ...]]:
    rows = tuple(tuple(_exact_int(v, name="matrix cell") for v in row) for row in matrix)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220I036NucleusError("matrix must be 3x3")
    return {
        "rows": tuple(sum(row) for row in rows),
        "columns": tuple(sum(rows[r][c] for r in range(3)) for c in range(3)),
        "diagonals": (
            sum(rows[i][i] for i in range(3)),
            sum(rows[i][2 - i] for i in range(3)),
        ),
    }


def coordinate_triplet(magnitude: int) -> Dict[str, Any]:
    m = _exact_int(magnitude, name="magnitude")
    if m not in LO_SHU_MAGNITUDE_ALPHABET:
        raise Pass220I036NucleusError("magnitude must be in 1..9")
    e = genesis_offset_from_magnitude(m)
    r = reverse_offset_from_magnitude(m)
    position = lo_shu_positions()[m]
    return _receipt({
        "schema": "HHS_PASS_220_I036_CELL_COORDINATE_TRIPLET_V1",
        "lo_shu_position": position,
        "genesis_offset": e,
        "magnitude": m,
        "reverse_offset": r,
        "relations": (
            "epsilon=m-5",
            "m=epsilon+5",
            "r=5+2*epsilon",
            "r=2*m-5",
        ),
        "mutually_reconstructible": (
            magnitude_from_genesis_offset(e) == m
            and genesis_offset_from_reverse_offset(r) == e
            and magnitude_from_reverse_offset(r) == m
        ),
        "co_resident_views": True,
        "projection_does_not_erase_provenance": True,
    })


def reflection_pairs_witness() -> Dict[str, Any]:
    pairs = []
    for magnitude in range(1, 6):
        mirror = 10 - magnitude
        left = coordinate_triplet(magnitude)
        right = coordinate_triplet(mirror)
        pairs.append({
            "magnitude_pair": (magnitude, mirror),
            "genesis_pair": (left["genesis_offset"], right["genesis_offset"]),
            "reverse_pair": (left["reverse_offset"], right["reverse_offset"]),
            "magnitude_sum": magnitude + mirror,
            "genesis_sum": left["genesis_offset"] + right["genesis_offset"],
            "reverse_sum": left["reverse_offset"] + right["reverse_offset"],
        })
    return _receipt({
        "schema": "HHS_PASS_220_I036_REFLECTION_PAIRS_V1",
        "pairs": tuple(pairs),
        "all_magnitude_pairs_sum_10": all(p["magnitude_sum"] == 10 for p in pairs),
        "all_genesis_pairs_sum_0": all(p["genesis_sum"] == 0 for p in pairs),
        "all_reverse_pairs_sum_10": all(p["reverse_sum"] == 10 for p in pairs),
        "center_pair": pairs[-1],
    })


def nucleus_layers_witness() -> Dict[str, Any]:
    genesis = genesis_offset_matrix()
    magnitude = LO_SHU
    reverse = reverse_offset_matrix()
    genesis_sums = _line_sums(genesis)
    magnitude_sums = _line_sums(magnitude)
    reverse_sums = _line_sums(reverse)

    triplets = tuple(coordinate_triplet(m) for m in LO_SHU_FLAT)
    reconstruct_from_genesis = tuple(
        magnitude_from_genesis_offset(cell["genesis_offset"]) for cell in triplets
    )
    reconstruct_from_reverse = tuple(
        magnitude_from_reverse_offset(cell["reverse_offset"]) for cell in triplets
    )

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "profile": PROFILE,
        "genesis_alphabet": GENESIS_OFFSET_ALPHABET,
        "magnitude_alphabet": LO_SHU_MAGNITUDE_ALPHABET,
        "reverse_offset_alphabet": REVERSE_OFFSET_ALPHABET,
        "genesis_matrix": genesis,
        "magnitude_matrix": magnitude,
        "reverse_offset_matrix": reverse,
        "genesis_line_sums": genesis_sums,
        "magnitude_line_sums": magnitude_sums,
        "reverse_offset_line_sums": reverse_sums,
        "genesis_all_lines_zero": all(
            value == 0 for group in genesis_sums.values() for value in group
        ),
        "magnitude_all_lines_fifteen": all(
            value == 15 for group in magnitude_sums.values() for value in group
        ),
        "reverse_all_lines_fifteen": all(
            value == 15 for group in reverse_sums.values() for value in group
        ),
        "cell_triplets": triplets,
        "genesis_reconstructs_lo_shu": reconstruct_from_genesis == LO_SHU_FLAT,
        "reverse_reconstructs_lo_shu": reconstruct_from_reverse == LO_SHU_FLAT,
        "center": {
            "genesis_offset": genesis[1][1],
            "magnitude": magnitude[1][1],
            "reverse_offset": reverse[1][1],
        },
        "reflection": reflection_pairs_witness(),
        "all_three_layers_same_cell_addresses": all(
            cell["lo_shu_position"] == lo_shu_positions()[cell["magnitude"]]
            for cell in triplets
        ),
        "co_resident_holographic_redundancy": True,
        "floating_point_authority": False,
        "canonical_admission_authority": False,
    })


def vm81_holographic_frame_witness() -> Dict[str, Any]:
    reference = repeated_lo_shu_reference()
    if len(reference) != VM81_CELLS:
        raise Pass220I036NucleusError("inherited VM81 reference cardinality mismatch")
    cells = tuple(coordinate_triplet(value) for value in reference)
    nuclei = tuple(
        cells[start : start + NUCLEUS_CELLS]
        for start in range(0, VM81_CELLS, NUCLEUS_CELLS)
    )
    return _receipt({
        "schema": "HHS_PASS_220_I036_VM81_HOLOGRAPHIC_FRAME_V1",
        "vm81_cells": VM81_CELLS,
        "nucleus_cells": NUCLEUS_CELLS,
        "nucleus_count": len(nuclei),
        "all_nuclei_have_nine_cells": all(len(nucleus) == 9 for nucleus in nuclei),
        "all_cells_mutually_reconstructible": all(
            cell["mutually_reconstructible"] for cell in cells
        ),
        "operation64": OPERATION64,
        "vm5184": VM5184,
        "hash72_squared": HASH72_BASE * HASH72_BASE,
        "vm81_times_64_equals_5184": VM81_CELLS * OPERATION64 == 5184,
        "hash72_squared_equals_5184": HASH72_BASE * HASH72_BASE == 5184,
        "cell_token_characters": CELL_TOKEN_CHARACTERS,
        "scalar_radix": SCALAR_RADIX,
        "same_vm81_geometry_three_coordinate_views": True,
        "canonical_vm81_mutation_authority": False,
    })


def build_genesis_reverse_offset_constructor() -> Dict[str, Any]:
    nucleus = nucleus_layers_witness()
    vm81 = vm81_holographic_frame_witness()
    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "contains_constraints": True,
        "local_constraints": LOCAL_CONSTRAINTS,
        "constraint_authority": "CONSTRUCTOR_LOCAL_ONLY",
        "canonical_service": False,
        "canonical_constraint_creation_authority": False,
        "canonical_constraint_enforcement_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "parent_i001_schema": "HHS_PASS_220_LO_SHU_NORMALIZATION_V1",
        "nucleus": nucleus,
        "vm81_frame": vm81,
        "holographic_semantics": (
            "THREE_CO_RESIDENT_EXACT_COORDINATE_VIEWS_OF_SAME_LO_SHU_NUCLEUS"
        ),
        "host_float_arithmetic_used": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_genesis_reverse_offset_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I036NucleusError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I036NucleusError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I036NucleusError("constructor receipt mismatch")
    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I036NucleusError("local constraint set mismatch")

    nucleus = constructor.get("nucleus")
    vm81 = constructor.get("vm81_frame")
    if nucleus != nucleus_layers_witness():
        raise Pass220I036NucleusError("nucleus witness mismatch")
    if vm81 != vm81_holographic_frame_witness():
        raise Pass220I036NucleusError("VM81 holographic frame mismatch")

    if nucleus["genesis_alphabet"] != GENESIS_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("Genesis alphabet drift")
    if nucleus["magnitude_alphabet"] != LO_SHU_MAGNITUDE_ALPHABET:
        raise Pass220I036NucleusError("magnitude alphabet drift")
    if nucleus["reverse_offset_alphabet"] != REVERSE_OFFSET_ALPHABET:
        raise Pass220I036NucleusError("reverse-offset alphabet drift")
    if nucleus["center"] != {
        "genesis_offset": 0, "magnitude": 5, "reverse_offset": 5
    }:
        raise Pass220I036NucleusError("center correspondence drift")

    required_true = (
        nucleus["genesis_all_lines_zero"],
        nucleus["magnitude_all_lines_fifteen"],
        nucleus["reverse_all_lines_fifteen"],
        nucleus["genesis_reconstructs_lo_shu"],
        nucleus["reverse_reconstructs_lo_shu"],
        nucleus["all_three_layers_same_cell_addresses"],
        nucleus["reflection"]["all_magnitude_pairs_sum_10"],
        nucleus["reflection"]["all_genesis_pairs_sum_0"],
        nucleus["reflection"]["all_reverse_pairs_sum_10"],
        vm81["all_nuclei_have_nine_cells"],
        vm81["all_cells_mutually_reconstructible"],
        vm81["vm81_times_64_equals_5184"],
        vm81["hash72_squared_equals_5184"],
        vm81["same_vm81_geometry_three_coordinate_views"],
    )
    if not all(required_true):
        raise Pass220I036NucleusError("holographic nucleus closure failed")

    for field in (
        "canonical_service",
        "canonical_constraint_creation_authority",
        "canonical_constraint_enforcement_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if constructor.get(field) is not False:
            raise Pass220I036NucleusError(f"authority escalation: {field}")

    if constructor.get("host_float_arithmetic_used") is not False:
        raise Pass220I036NucleusError("host floating arithmetic forbidden")

    return {
        "ok": True,
        "genesis_matrix": nucleus["genesis_matrix"],
        "magnitude_matrix": nucleus["magnitude_matrix"],
        "reverse_offset_matrix": nucleus["reverse_offset_matrix"],
        "center": nucleus["center"],
        "three_exact_views": True,
        "same_lo_shu_addresses": True,
        "vm81_cells": vm81["vm81_cells"],
        "vm5184": vm81["vm5184"],
    }


def genesis_reverse_offset_holographic_nucleus_self_test() -> Dict[str, Any]:
    constructor = build_genesis_reverse_offset_constructor()
    result = validate_genesis_reverse_offset_constructor(constructor)
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "constructor_receipt_sha256": constructor["receipt_sha256"],
        "mutation_policy": "READ_ONLY_HOLOGRAPHIC_NUCLEUS_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
        "canonical_service": False,
        "canonical_constraint_authority": False,
    })
