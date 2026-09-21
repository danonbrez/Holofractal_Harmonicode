"""Pass 220 checkpoint 1: Lo Shu zero-calibrated normalization and 1,2,3 fractal geometry.

This module is additive witness/reference infrastructure.  It does not widen
canonical VM81/Hash72/Hash216 mutation authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

SCHEMA = "HHS_PASS_220_LO_SHU_NORMALIZATION_V1"
VERSION = "1.0.0-checkpoint.1"
PROFILE = "PASS220-I001-LO-SHU-NORMALIZED-BIGINT-v1"

LO_SHU: Tuple[Tuple[int, ...], ...] = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
LO_SHU_FLAT: Tuple[int, ...] = tuple(cell for row in LO_SHU for cell in row)
VM81_CELLS = 81
NUCLEUS_CELLS = 9
NUCLEUS_COUNT = VM81_CELLS // NUCLEUS_CELLS
HASH72_BASE = 72
SCALAR_RADIX = HASH72_BASE * HASH72_BASE  # 5184; inherited Pass 033 carrier radix.
SERIALIZED_CHARACTERS = 5184
CELL_TOKEN_CHARACTERS = 64
HASH216_OBJECT_COUNT = 3

FRACTAL_123: Tuple[Tuple[int, ...], ...] = tuple(
    tuple((row + 1) * (column + 1) for column in range(3)) for row in range(3)
)


class Pass220NormalizationError(ValueError):
    pass


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220NormalizationError(f"{name} must be an exact integer")
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(_stable_json(record).encode("utf-8")).hexdigest()
    return record


def repeated_lo_shu_reference() -> Tuple[int, ...]:
    """Checkpoint reference: nine local Lo Shu nuclei, 81 cells total."""
    return LO_SHU_FLAT * NUCLEUS_COUNT


def normalize_offsets(
    state: Sequence[int],
    *,
    reference: Sequence[int] | None = None,
    modulus: int = 9,
) -> Tuple[int, ...]:
    """Return non-negative normalization offsets relative to a closure reference."""
    modulus_i = _exact_int(modulus, name="modulus")
    if modulus_i <= 1:
        raise Pass220NormalizationError("modulus must be greater than one")
    ref = tuple(reference if reference is not None else repeated_lo_shu_reference())
    values = tuple(state)
    if len(values) != len(ref):
        raise Pass220NormalizationError("state/reference length mismatch")
    offsets = []
    for index, (value, anchor) in enumerate(zip(values, ref)):
        v = _exact_int(value, name=f"state[{index}]")
        a = _exact_int(anchor, name=f"reference[{index}]")
        offsets.append((v - a) % modulus_i)
    return tuple(offsets)


def reconstruct_from_offsets(
    offsets: Sequence[int],
    *,
    reference: Sequence[int] | None = None,
    modulus: int = 9,
) -> Tuple[int, ...]:
    """Reconstruct the residue-class state from normalized offsets."""
    modulus_i = _exact_int(modulus, name="modulus")
    if modulus_i <= 1:
        raise Pass220NormalizationError("modulus must be greater than one")
    ref = tuple(reference if reference is not None else repeated_lo_shu_reference())
    delta = tuple(offsets)
    if len(delta) != len(ref):
        raise Pass220NormalizationError("offset/reference length mismatch")
    result = []
    for index, (offset, anchor) in enumerate(zip(delta, ref)):
        d = _exact_int(offset, name=f"offsets[{index}]")
        a = _exact_int(anchor, name=f"reference[{index}]")
        if not 0 <= d < modulus_i:
            raise Pass220NormalizationError("offset outside canonical residue range")
        residue = (a + d) % modulus_i
        result.append(modulus_i if residue == 0 else residue)
    return tuple(result)


def offsets_to_bigint(offsets: Sequence[int], *, radix: int = SCALAR_RADIX) -> int:
    """Injectively project a normalized offset vector to a non-negative scalar integer."""
    radix_i = _exact_int(radix, name="radix")
    if radix_i <= 9:
        raise Pass220NormalizationError("radix must exceed the 0..8 offset alphabet")
    scalar = 0
    multiplier = 1
    for index, offset in enumerate(offsets):
        digit = _exact_int(offset, name=f"offsets[{index}]")
        if not 0 <= digit <= 8:
            raise Pass220NormalizationError("offset must be in 0..8")
        scalar += digit * multiplier
        multiplier *= radix_i
    return scalar


def bigint_to_offsets(value: int, *, length: int = VM81_CELLS, radix: int = SCALAR_RADIX) -> Tuple[int, ...]:
    """Decode the scalar projection back to the fixed-length offset vector."""
    n = _exact_int(value, name="value")
    length_i = _exact_int(length, name="length")
    radix_i = _exact_int(radix, name="radix")
    if n < 0 or length_i <= 0 or radix_i <= 9:
        raise Pass220NormalizationError("invalid bigint decode parameters")
    digits = []
    remaining = n
    for _ in range(length_i):
        digit = remaining % radix_i
        remaining //= radix_i
        if digit > 8:
            raise Pass220NormalizationError("bigint contains a non-offset radix digit")
        digits.append(digit)
    if remaining:
        raise Pass220NormalizationError("bigint exceeds requested offset-vector length")
    return tuple(digits)


def _encode_rational_scientific_token(value: Fraction) -> str:
    """Encode one exact rational as a fixed 64-character HARMONICODE carrier token.

    Layout: sign + 20-digit numerator + '/' + 20-digit denominator + 'e' +
    exponent sign + 20-digit decimal exponent.  Checkpoint 1 normalizes the
    rational itself and therefore uses exponent zero; the exponent field is kept
    explicit so the token remains a scientific-notation carrier rather than a
    plain decimal string.
    """
    q = Fraction(value)
    sign = "+" if q >= 0 else "-"
    numerator = abs(q.numerator)
    denominator = q.denominator
    exponent = 0
    if numerator >= 10**20 or denominator >= 10**20:
        raise Pass220NormalizationError("rational token field overflow")
    token = f"{sign}{numerator:020d}/{denominator:020d}e+{exponent:020d}"
    if len(token) != CELL_TOKEN_CHARACTERS:
        raise AssertionError("internal 64-character token invariant failed")
    return token


def _decode_rational_scientific_token(token: str) -> Fraction:
    if len(token) != CELL_TOKEN_CHARACTERS:
        raise Pass220NormalizationError("rational token must be exactly 64 characters")
    if token[0] not in "+-" or token[21] != "/" or token[42] != "e" or token[43] not in "+-":
        raise Pass220NormalizationError("invalid rational scientific token layout")
    numerator_text = token[1:21]
    denominator_text = token[22:42]
    exponent_text = token[44:64]
    if not numerator_text.isdigit() or not denominator_text.isdigit() or not exponent_text.isdigit():
        raise Pass220NormalizationError("invalid rational scientific token digits")
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    if denominator == 0:
        raise Pass220NormalizationError("zero rational denominator")
    if token[0] == "-":
        numerator = -numerator
    exponent = int(exponent_text)
    if token[43] == "-":
        exponent = -exponent
    q = Fraction(numerator, denominator)
    if exponent >= 0:
        return q * (10**exponent)
    return q / (10 ** (-exponent))


def serialize_offsets_5184(offsets: Sequence[int]) -> str:
    """Serialize exactly 81 normalization offsets into the fixed 5184-character ABI."""
    values = tuple(offsets)
    if len(values) != VM81_CELLS:
        raise Pass220NormalizationError("5184-character serializer requires exactly 81 offsets")
    tokens = []
    for index, offset in enumerate(values):
        digit = _exact_int(offset, name=f"offsets[{index}]")
        if not 0 <= digit <= 8:
            raise Pass220NormalizationError("offset must be in 0..8")
        tokens.append(_encode_rational_scientific_token(Fraction(digit, 1)))
    encoded = "".join(tokens)
    if len(encoded) != SERIALIZED_CHARACTERS:
        raise AssertionError("internal 5184-character serialization invariant failed")
    return encoded


def deserialize_offsets_5184(serialized: str) -> Tuple[int, ...]:
    if not isinstance(serialized, str) or len(serialized) != SERIALIZED_CHARACTERS:
        raise Pass220NormalizationError("serialized object must be exactly 5184 characters")
    offsets = []
    for start in range(0, SERIALIZED_CHARACTERS, CELL_TOKEN_CHARACTERS):
        q = _decode_rational_scientific_token(serialized[start : start + CELL_TOKEN_CHARACTERS])
        if q.denominator != 1 or not 0 <= q.numerator <= 8:
            raise Pass220NormalizationError("serialized token is not a canonical normalization offset")
        offsets.append(q.numerator)
    if len(offsets) != VM81_CELLS:
        raise AssertionError("internal VM81 decode invariant failed")
    return tuple(offsets)


def compose_fixed_objects(*objects: str) -> str:
    """Concatenate fixed-width objects without delimiters; boundaries are intrinsic."""
    if not objects:
        raise Pass220NormalizationError("at least one object is required")
    for index, obj in enumerate(objects):
        if not isinstance(obj, str) or len(obj) != SERIALIZED_CHARACTERS:
            raise Pass220NormalizationError(f"object[{index}] is not a 5184-character canonical object")
    return "".join(objects)


def split_fixed_objects(payload: str) -> Tuple[str, ...]:
    if not isinstance(payload, str) or len(payload) == 0 or len(payload) % SERIALIZED_CHARACTERS:
        raise Pass220NormalizationError("payload length is not an integral 5184-character object count")
    return tuple(
        payload[start : start + SERIALIZED_CHARACTERS]
        for start in range(0, len(payload), SERIALIZED_CHARACTERS)
    )


def lo_shu_positions() -> Dict[int, Tuple[int, int]]:
    return {
        value: (row, column)
        for row, values in enumerate(LO_SHU)
        for column, value in enumerate(values)
    }


def squared_distance(left: Tuple[int, int], right: Tuple[int, int]) -> int:
    dr = left[0] - right[0]
    dc = left[1] - right[1]
    return dr * dr + dc * dc


def triangle_squared_distance_spectrum(values: Sequence[int]) -> Tuple[int, int, int]:
    if len(values) != 3:
        raise Pass220NormalizationError("triangle requires exactly three Lo Shu values")
    positions = lo_shu_positions()
    try:
        points = [positions[_exact_int(value, name="triangle value")] for value in values]
    except KeyError as exc:
        raise Pass220NormalizationError("triangle value is not a Lo Shu address") from exc
    distances = (
        squared_distance(points[0], points[1]),
        squared_distance(points[1], points[2]),
        squared_distance(points[2], points[0]),
    )
    return tuple(sorted(distances))


def fractal_123_geometry_witness() -> Dict[str, Any]:
    rows = FRACTAL_123
    positions = lo_shu_positions()
    row_spectra = tuple(triangle_squared_distance_spectrum(row) for row in rows)
    reciprocal_pairs = {
        "12_21": rows[0][1] == rows[1][0] == 2,
        "13_31": rows[0][2] == rows[2][0] == 3,
        "23_32": rows[1][2] == rows[2][1] == 6,
    }
    middle = row_spectra[1]
    if middle != (4, 4, 8):
        raise Pass220NormalizationError("2,4,6 right-isosceles Lo Shu geometry mismatch")
    if row_spectra[0] != (2, 5, 5) or row_spectra[2] != row_spectra[0]:
        raise Pass220NormalizationError("1,2,3 / 3,6,9 Lo Shu distance-spectrum mirror mismatch")
    return _receipt({
        "schema": "HHS_PASS_220_123_FRACTAL_LO_SHU_GEOMETRY_WITNESS_V1",
        "profile": PROFILE,
        "fractal_matrix": rows,
        "lo_shu_positions": {str(key): value for key, value in positions.items()},
        "triangles": rows,
        "squared_distance_spectra": row_spectra,
        "reciprocal_source_pairs_share_scalar_and_address": reciprocal_pairs,
        "diagonal_square_channel": (rows[0][0], rows[1][1], rows[2][2]),
        "off_diagonal_reciprocal_channel": (2, 3, 6),
        "middle_triangle_right_isosceles": True,
        "outer_triangle_distance_spectrum_preserved": True,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })


def normalization_witness(state: Sequence[int] | None = None) -> Dict[str, Any]:
    reference = repeated_lo_shu_reference()
    actual = tuple(reference if state is None else state)
    offsets = normalize_offsets(actual, reference=reference)
    scalar = offsets_to_bigint(offsets)
    encoded = serialize_offsets_5184(offsets)
    roundtrip_offsets = deserialize_offsets_5184(encoded)
    scalar_roundtrip = bigint_to_offsets(scalar, length=VM81_CELLS)
    if roundtrip_offsets != offsets or scalar_roundtrip != offsets:
        raise Pass220NormalizationError("normalization roundtrip mismatch")
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "vm81_cells": VM81_CELLS,
        "nucleus_count": NUCLEUS_COUNT,
        "scalar_radix": SCALAR_RADIX,
        "serialized_characters": SERIALIZED_CHARACTERS,
        "cell_token_characters": CELL_TOKEN_CHARACTERS,
        "offsets": offsets,
        "scalar_bigint": scalar,
        "closed": scalar == 0 and all(offset == 0 for offset in offsets),
        "serialization_roundtrip": True,
        "scalar_roundtrip": True,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    })
