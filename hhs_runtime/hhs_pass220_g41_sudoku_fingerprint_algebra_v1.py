"""Pass 220 I014: exact G41 reciprocal Sudoku fingerprint algebra.

Read-only witness/reference implementation. It derives the 41 reciprocal
nine-cell fingerprint classes of the canonical 81-cell Sudoku seed, binds
those classes to the inherited Lo Shu normalization/bigint carrier, and
provides an exhaustive finite reachability codec. It does not widen canonical
VM81, Hash72, Hash216, persistence, receipt, or mutation authority.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    LO_SHU_FLAT,
    SCALAR_RADIX,
    deserialize_offsets_5184,
    normalize_offsets,
    offsets_to_bigint,
    repeated_lo_shu_reference,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_220_G41_SUDOKU_FINGERPRINT_ALGEBRA_V1"
VERSION = "1.0.0-checkpoint.14"
PROFILE = "PASS220-I014-G41-SUDOKU-FINGERPRINT-ALGEBRA-v1"
REACHABILITY_SCHEMA = "HHS_PASS_220_G41_SURFACE_REACHABILITY_WITNESS_V1"

LO_SHU: Tuple[Tuple[int, ...], ...] = (
    (4, 9, 2),
    (3, 5, 7),
    (8, 1, 6),
)

SUDOKU81: Tuple[Tuple[int, ...], ...] = (
    (7, 3, 5, 2, 4, 9, 6, 8, 1),
    (6, 8, 1, 7, 3, 5, 2, 4, 9),
    (2, 4, 9, 6, 8, 1, 7, 3, 5),
    (3, 5, 7, 4, 9, 2, 8, 1, 6),
    (8, 1, 6, 3, 5, 7, 4, 9, 2),
    (4, 9, 2, 8, 1, 6, 3, 5, 7),
    (5, 7, 3, 9, 2, 4, 1, 6, 8),
    (1, 6, 8, 5, 7, 3, 9, 2, 4),
    (9, 2, 4, 1, 6, 8, 5, 7, 3),
)

# Four wrapped directional families. Center + +/- of each = nine local slots.
DIRECTION_OFFSETS: Dict[str, Tuple[int, int]] = {
    "z_minus": (-1, -1),
    "y_minus": (-1, 0),
    "w_plus": (-1, 1),
    "x_minus": (0, -1),
    "center": (0, 0),
    "x_plus": (0, 1),
    "w_minus": (1, -1),
    "y_plus": (1, 0),
    "z_plus": (1, 1),
}

CELL_EQUATIONS: Dict[int, str] = {
    0: "SX-SZ-WZ+XY+YX-ZW",
    1: "a2",
    2: "b2",
    3: "c2",
    4: "b2^2",
    5: "b2+c2",
    6: "b2*c2",
    7: "b2^2+c2",
    8: "b2^3",
    9: "c2^2",
}


class Pass220G41FingerprintError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220G41FingerprintError(f"{name} must be an exact integer")
    return value


def zero_cell_value(
    *,
    sx: int = 0,
    sz: int = 0,
    xy: int = 1,
    yx: int = -1,
    zw: int = 1,
    wz: int = -1,
) -> int:
    """Evaluate C0 from typed additive/ordered phase composites.

    sx denotes x+y and sz denotes z+w. xy/yx/zw/wz stay independently
    supplied ordered composites; this function does not commute them.
    """
    values = {"sx": sx, "sz": sz, "xy": xy, "yx": yx, "zw": zw, "wz": wz}
    for name, value in values.items():
        _exact_int(value, name=name)
    return sx - sz - wz + xy + yx - zw


def derived_cell_values(
    *, a2: int = 1, b2: int = 2, c2: int = 3, c0: int | None = None
) -> Dict[int, int]:
    a = _exact_int(a2, name="a2")
    b = _exact_int(b2, name="b2")
    c = _exact_int(c2, name="c2")
    zero = zero_cell_value() if c0 is None else _exact_int(c0, name="c0")
    return {
        0: zero,
        1: a,
        2: b,
        3: c,
        4: b**2,
        5: b + c,
        6: b * c,
        7: b**2 + c,
        8: b**3,
        9: c**2,
    }


def symbol_radix() -> int:
    cells = derived_cell_values()
    return cells[9] + cells[1]


def validate_sudoku_seed(seed: Sequence[Sequence[int]] = SUDOKU81) -> bool:
    rows = tuple(tuple(row) for row in seed)
    if len(rows) != 9 or any(len(row) != 9 for row in rows):
        return False
    target = tuple(range(1, 10))
    for row in rows:
        if any(isinstance(v, bool) or not isinstance(v, int) for v in row):
            return False
        if tuple(sorted(row)) != target:
            return False
    for c in range(9):
        if tuple(sorted(rows[r][c] for r in range(9))) != target:
            return False
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            block = tuple(
                sorted(rows[br + dr][bc + dc] for dr in range(3) for dc in range(3))
            )
            if block != target:
                return False
    return True


def _anchor(row: int, column: int) -> Tuple[int, int]:
    r = _exact_int(row, name="row")
    c = _exact_int(column, name="column")
    if not 0 <= r < 9 or not 0 <= c < 9:
        raise Pass220G41FingerprintError("anchor outside 9x9 torus")
    return r, c


def anchor_position(row: int, column: int) -> int:
    r, c = _anchor(row, column)
    return 9 * r + c + 1


def position_anchor(position: int) -> Tuple[int, int]:
    p = _exact_int(position, name="position")
    if not 1 <= p <= 81:
        raise Pass220G41FingerprintError("position outside 1..81")
    return divmod(p - 1, 9)


def opposite_anchor(row: int, column: int) -> Tuple[int, int]:
    r, c = _anchor(row, column)
    return 8 - r, 8 - c


def fingerprint(
    row: int,
    column: int,
    *,
    seed: Sequence[Sequence[int]] = SUDOKU81,
) -> Tuple[Tuple[int, ...], ...]:
    if not validate_sudoku_seed(seed):
        raise Pass220G41FingerprintError("invalid canonical Sudoku seed")
    r, c = _anchor(row, column)
    rows = tuple(tuple(values) for values in seed)
    return tuple(
        tuple(rows[(r + dr) % 9][(c + dc) % 9] for dc in (-1, 0, 1))
        for dr in (-1, 0, 1)
    )


def directional_fingerprint(
    row: int,
    column: int,
    *,
    seed: Sequence[Sequence[int]] = SUDOKU81,
) -> Dict[str, int]:
    if not validate_sudoku_seed(seed):
        raise Pass220G41FingerprintError("invalid canonical Sudoku seed")
    r, c = _anchor(row, column)
    rows = tuple(tuple(values) for values in seed)
    return {
        name: rows[(r + dr) % 9][(c + dc) % 9]
        for name, (dr, dc) in DIRECTION_OFFSETS.items()
    }


def reciprocal_fingerprint(
    matrix: Sequence[Sequence[int]],
) -> Tuple[Tuple[int, ...], ...]:
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220G41FingerprintError("fingerprint must be 3x3")
    for row in rows:
        for value in row:
            v = _exact_int(value, name="fingerprint value")
            if not 1 <= v <= 9:
                raise Pass220G41FingerprintError("fingerprint value outside 1..9")
    return tuple(
        tuple(10 - rows[2 - r][2 - c] for c in range(3))
        for r in range(3)
    )


def flatten_fingerprint(matrix: Sequence[Sequence[int]]) -> Tuple[int, ...]:
    rows = tuple(tuple(row) for row in matrix)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise Pass220G41FingerprintError("fingerprint must be 3x3")
    values = tuple(value for row in rows for value in row)
    for value in values:
        v = _exact_int(value, name="fingerprint value")
        if not 1 <= v <= 9:
            raise Pass220G41FingerprintError("fingerprint value outside 1..9")
    return values


def canonical_fingerprint_key(matrix: Sequence[Sequence[int]]) -> Tuple[int, ...]:
    direct = flatten_fingerprint(matrix)
    reciprocal = flatten_fingerprint(reciprocal_fingerprint(matrix))
    return min(direct, reciprocal)


def fingerprint_class_id(row: int, column: int) -> int:
    """Return the 1..41 reciprocal-anchor class.

    This position involution has the same p <-> 82-p arithmetic shape as the
    inherited order-nine reciprocal anchor, but does not replace its magic
    magnitude identity.
    """
    p = anchor_position(row, column)
    return min(p, 82 - p)


def encode_anchor_reachability(row: int, column: int) -> Tuple[int, int]:
    """Encode one of 81 anchors as (class_id, reciprocal_orientation)."""
    p = anchor_position(row, column)
    class_id = min(p, 82 - p)
    orientation = 0 if p <= 41 else 1
    return class_id, orientation


def decode_anchor_reachability(class_id: int, orientation: int) -> Tuple[int, int]:
    k = _exact_int(class_id, name="class_id")
    o = _exact_int(orientation, name="orientation")
    if not 1 <= k <= 41 or o not in (0, 1):
        raise Pass220G41FingerprintError("invalid reachability address")
    if k == 41 and o != 0:
        raise Pass220G41FingerprintError(
            "center class has no reciprocal orientation"
        )
    p = k if o == 0 else 82 - k
    return position_anchor(p)


def local_bigint_projection(matrix: Sequence[Sequence[int]]) -> int:
    values = flatten_fingerprint(matrix)
    offsets = normalize_offsets(values, reference=LO_SHU_FLAT, modulus=9)
    return offsets_to_bigint(offsets, radix=SCALAR_RADIX)


def enumerate_fingerprint_classes(
    seed: Sequence[Sequence[int]] = SUDOKU81,
) -> Tuple[Dict[str, Any], ...]:
    if not validate_sudoku_seed(seed):
        raise Pass220G41FingerprintError("invalid canonical Sudoku seed")
    records = []
    seen_keys = set()
    for class_id in range(1, 42):
        row, column = position_anchor(class_id)
        reciprocal_position = 82 - class_id
        rr, rc = position_anchor(reciprocal_position)
        direct = fingerprint(row, column, seed=seed)
        reciprocal = fingerprint(rr, rc, seed=seed)
        if reciprocal_fingerprint(direct) != reciprocal:
            raise Pass220G41FingerprintError("reciprocal fingerprint mismatch")
        key = canonical_fingerprint_key(direct)
        if key in seen_keys:
            raise Pass220G41FingerprintError(
                "duplicate reciprocal fingerprint class"
            )
        seen_keys.add(key)
        records.append({
            "class_id": class_id,
            "anchor_position": class_id,
            "anchor": (row, column),
            "reciprocal_position": reciprocal_position,
            "reciprocal_anchor": (rr, rc),
            "fixed_center": class_id == 41,
            "fingerprint": direct,
            "reciprocal_fingerprint": reciprocal,
            "canonical_key": key,
            "local_bigint": local_bigint_projection(direct),
            "reciprocal_local_bigint": local_bigint_projection(reciprocal),
        })
    return tuple(records)


def full_sudoku_serialization_witness(
    seed: Sequence[Sequence[int]] = SUDOKU81,
) -> Dict[str, Any]:
    if not validate_sudoku_seed(seed):
        raise Pass220G41FingerprintError("invalid canonical Sudoku seed")
    flat = tuple(value for row in seed for value in row)
    reference = repeated_lo_shu_reference()
    offsets = normalize_offsets(flat, reference=reference, modulus=9)
    bigint = offsets_to_bigint(offsets, radix=SCALAR_RADIX)
    serialized = serialize_offsets_5184(offsets)
    if deserialize_offsets_5184(serialized) != offsets:
        raise Pass220G41FingerprintError(
            "5184-character serialization roundtrip failed"
        )
    return {
        "offset_count": len(offsets),
        "scalar_radix": SCALAR_RADIX,
        "scalar_bigint": bigint,
        "serialized_characters": len(serialized),
        "roundtrip": True,
    }


def quadratic3_mul(
    left: Tuple[int, int],
    right: Tuple[int, int],
) -> Tuple[int, int]:
    a, b = left
    c, d = right
    for name, value in (("a", a), ("b", b), ("c", c), ("d", d)):
        _exact_int(value, name=name)
    return a * c + 3 * b * d, a * d + b * c


def quadratic3_pow(exponent: int) -> Tuple[int, int]:
    n = _exact_int(exponent, name="exponent")
    if n < 0:
        raise Pass220G41FingerprintError(
            "negative exponent not admitted by integer-pair power"
        )
    result = (1, 0)
    base = (2, 1)  # G = C2 + C1*P, P^2 = C3.
    while n:
        if n & 1:
            result = quadratic3_mul(result, base)
        base = quadratic3_mul(base, base)
        n >>= 1
    return result


def quadratic3_norm(value: Tuple[int, int]) -> int:
    a, b = value
    return a * a - 3 * b * b


def number_theory_witness(depth: int = 8) -> Dict[str, Any]:
    n = _exact_int(depth, name="depth")
    if n < 3:
        raise Pass220G41FingerprintError("depth must include G^3")
    powers = tuple(quadratic3_pow(k) for k in range(n + 1))
    norms = tuple(quadratic3_norm(value) for value in powers)
    recurrence = all(
        powers[k + 1][lane]
        == 4 * powers[k][lane] - powers[k - 1][lane]
        for k in range(1, n)
        for lane in (0, 1)
    )
    cells = derived_cell_values()
    return {
        "basis_relation": "P^2=C3",
        "G": powers[1],
        "G2": powers[2],
        "G3": powers[3],
        "G2_is_C7_plus_C4P": powers[2] == (cells[7], cells[4]),
        "C7_plus_C4": cells[7] + cells[4],
        "G3_P_coefficient_is_magic_sum": powers[3][1] == 15,
        "powers": powers,
        "norms": norms,
        "all_norms_C1": all(value == cells[1] for value in norms),
        "recurrence_Xn1_eq_C4_Xn_minus_Xn1": recurrence,
    }


def g41_surface_reachability_witness(
    seed: Sequence[Sequence[int]] = SUDOKU81,
) -> Dict[str, Any]:
    if not validate_sudoku_seed(seed):
        raise Pass220G41FingerprintError("invalid canonical Sudoku seed")
    oriented = tuple(
        fingerprint(*position_anchor(position), seed=seed)
        for position in range(1, 82)
    )
    unique_oriented = len({flatten_fingerprint(item) for item in oriented})
    reciprocal_ok = all(
        reciprocal_fingerprint(fingerprint(r, c, seed=seed))
        == fingerprint(8 - r, 8 - c, seed=seed)
        for r in range(9)
        for c in range(9)
    )
    involution_ok = all(
        reciprocal_fingerprint(reciprocal_fingerprint(item)) == item
        for item in oriented
    )
    class_buckets: Dict[Tuple[int, ...], list[int]] = {}
    for position, item in enumerate(oriented, start=1):
        class_buckets.setdefault(
            canonical_fingerprint_key(item), []
        ).append(position)
    class_sizes = tuple(sorted(len(value) for value in class_buckets.values()))
    reachability_roundtrip = all(
        decode_anchor_reachability(
            *encode_anchor_reachability(*position_anchor(position))
        )
        == position_anchor(position)
        for position in range(1, 82)
    )
    center = fingerprint(4, 4, seed=seed)
    local_bigints = tuple(local_bigint_projection(item) for item in oriented)
    return _receipt({
        "schema": REACHABILITY_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "canonical_path": [
            "SUDOKU81",
            "anchor_position_1_81",
            "wrapped_4D_9_slot_fingerprint",
            "reciprocal_class_1_41_plus_orientation",
            "Lo_Shu_relative_offsets",
            "radix_5184_bigint_projection",
        ],
        "four_dimensions": ("x", "y", "z", "w"),
        "local_degrees_of_freedom": 9,
        "oriented_fingerprint_count": 81,
        "unique_oriented_fingerprint_count": unique_oriented,
        "entangled_fingerprint_class_count": len(class_buckets),
        "class_size_histogram": {
            "size_1": class_sizes.count(1),
            "size_2": class_sizes.count(2),
        },
        "single_fixed_class_position": 41,
        "center_fingerprint": center,
        "center_is_lo_shu": center == LO_SHU,
        "center_self_reciprocal": reciprocal_fingerprint(center) == center,
        "reciprocal_relation_all_81": reciprocal_ok,
        "reciprocal_involution_all_81": involution_ok,
        "reachability_codec_roundtrip_all_81": reachability_roundtrip,
        "local_bigint_unique_all_81": len(set(local_bigints)) == 81,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
        "mutation_performed": False,
    })


def validate_g41_surface_reachability() -> Dict[str, Any]:
    witness = g41_surface_reachability_witness()
    classes = enumerate_fingerprint_classes()
    serialization = full_sudoku_serialization_witness()
    number_theory = number_theory_witness()
    ok = all((
        validate_sudoku_seed(),
        derived_cell_values() == {index: index for index in range(10)},
        zero_cell_value() == 0,
        symbol_radix() == 10,
        len(classes) == 41,
        witness["unique_oriented_fingerprint_count"] == 81,
        witness["entangled_fingerprint_class_count"] == 41,
        witness["class_size_histogram"] == {"size_1": 1, "size_2": 40},
        witness["center_is_lo_shu"],
        witness["center_self_reciprocal"],
        witness["reciprocal_relation_all_81"],
        witness["reciprocal_involution_all_81"],
        witness["reachability_codec_roundtrip_all_81"],
        witness["local_bigint_unique_all_81"],
        serialization["roundtrip"],
        serialization["serialized_characters"] == 5184,
        number_theory["G2_is_C7_plus_C4P"],
        number_theory["C7_plus_C4"] == 11,
        number_theory["G3_P_coefficient_is_magic_sum"],
        number_theory["all_norms_C1"],
        number_theory["recurrence_Xn1_eq_C4_Xn_minus_Xn1"],
    ))
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": ok,
        "reachability": witness,
        "class_count": len(classes),
        "serialization": serialization,
        "number_theory": number_theory,
        "invariant_ids": (
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
        ),
        "mutation_policy":
            "READ_ONLY_REFERENCE_WITNESS_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def g41_fingerprint_self_test() -> Dict[str, Any]:
    return validate_g41_surface_reachability()
