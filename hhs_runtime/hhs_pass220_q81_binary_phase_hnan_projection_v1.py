"""Pass220 Q81 binary phase receipt projection over the inherited HNAN gate.

Additive read-only candidate. The 81 receipt bits are NOT the native tensor.
The accompanying orientation witness is required for the exact ordered-pair
inverse; it must be supplied by admitted upstream context, never guessed.
This projection does not calculate the course-wide closure, grant VM81
admission, or mint Hash72/Hash216 receipts.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_LO_SHU_TENSOR_SOURCE,
    HNAN_TERMINAL_SOURCE,
    hnan_loshu_resolution_receipt,
)

SCHEMA = "HHS_PASS220_Q81_BINARY_PHASE_HNAN_PROJECTION_V1"
DIM = 9
PHASE_TABLE = (
    ((0, 1), (1, 0)),
    ((-1, 1), (1, -1)),
)
PAIR_TO_CODE = {
    pair: (bit, orientation)
    for bit, orientations in enumerate(PHASE_TABLE)
    for orientation, pair in enumerate(orientations)
}


class Q81PhaseProjectionError(ValueError):
    """Typed, deterministic candidate rejection."""


def _square(value: Any, name: str, allowed: set[int]) -> tuple[tuple[int, ...], ...]:
    if not isinstance(value, (tuple, list)) or len(value) != DIM:
        raise Q81PhaseProjectionError(f"{name}_ROWS")
    rows: list[tuple[int, ...]] = []
    for row in value:
        if not isinstance(row, (tuple, list)) or len(row) != DIM:
            raise Q81PhaseProjectionError(f"{name}_COLS")
        if any(type(cell) is not int or cell not in allowed for cell in row):
            raise Q81PhaseProjectionError(f"{name}_DOMAIN")
        rows.append(tuple(row))
    return tuple(rows)


def _gate_source() -> dict[str, Any]:
    """Reuse an inherited ordered-source witness, never substitute a new gate."""
    source = hnan_loshu_resolution_receipt()
    if (
        source.get("status") != "PASS"
        or HNAN_TERMINAL_SOURCE != "xy+epsilon"
        or source.get("terminal_source") != HNAN_TERMINAL_SOURCE
        or source.get("tensor_source") != [list(row) for row in HNAN_LO_SHU_TENSOR_SOURCE]
        or source.get("epsilon_elision_authorized") is not False
        or source.get("ordered_product_commutation_authorized") is not False
    ):
        raise Q81PhaseProjectionError("HNAN_SOURCE_NOT_VERIFIED")
    return source


def decode_candidate(
    binary: Sequence[Sequence[int]],
    *,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    """Decode ordered pairs with supplied native orientation context.

    Context must contain an exact 9x9 `orientation` matrix plus unchanged
    `source_identity` and `provenance` from the calling native candidate.
    Neither source identity nor provenance is reconstructed from 81 bits.
    """
    bits = _square(binary, "BINARY", {0, 1})
    if not isinstance(context, Mapping):
        raise Q81PhaseProjectionError("CONTEXT_REQUIRED")
    orientation = _square(context.get("orientation"), "ORIENTATION", {0, 1})
    if not isinstance(context.get("source_identity"), str) or not context["source_identity"]:
        raise Q81PhaseProjectionError("SOURCE_IDENTITY_REQUIRED")
    if not isinstance(context.get("provenance"), Mapping):
        raise Q81PhaseProjectionError("PROVENANCE_REQUIRED")
    _gate_source()
    pairs = tuple(
        tuple(PHASE_TABLE[bits[i][j]][orientation[i][j]] for j in range(DIM))
        for i in range(DIM)
    )
    return {
        "schema": SCHEMA,
        "native_ordered_pairs": pairs,
        "orientation": orientation,
        "source_identity": context["source_identity"],
        "provenance": dict(context["provenance"]),
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }


def encode_candidate(native: Mapping[str, Any]) -> dict[str, Any]:
    """Encode ordered phase pairs, preserving orientation and source context."""
    if not isinstance(native, Mapping) or native.get("schema") != SCHEMA:
        raise Q81PhaseProjectionError("NATIVE_SCHEMA")
    if (
        native.get("candidate_only") is not True
        or native.get("canonical_vm81_mutation_authority") is not False
        or native.get("canonical_hash72_commit_authority") is not False
        or native.get("canonical_hash216_persistence_authority") is not False
    ):
        raise Q81PhaseProjectionError("CANDIDATE_AUTHORITY")
    raw = native.get("native_ordered_pairs")
    if not isinstance(raw, (list, tuple)) or len(raw) != DIM:
        raise Q81PhaseProjectionError("PAIR_ROWS")
    rows: list[tuple[tuple[int, int], ...]] = []
    for row in raw:
        if not isinstance(row, (list, tuple)) or len(row) != DIM:
            raise Q81PhaseProjectionError("PAIR_COLS")
        new_row = []
        for pair in row:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise Q81PhaseProjectionError("PAIR_SHAPE")
            if any(type(x) is not int for x in pair) or tuple(pair) not in PAIR_TO_CODE:
                raise Q81PhaseProjectionError("PAIR_DOMAIN")
            new_row.append(tuple(pair))
        rows.append(tuple(new_row))
    pairs = tuple(rows)
    claimed = _square(native.get("orientation"), "ORIENTATION", {0, 1})
    binary = tuple(
        tuple(PAIR_TO_CODE[pairs[i][j]][0] for j in range(DIM))
        for i in range(DIM)
    )
    actual = tuple(
        tuple(PAIR_TO_CODE[pairs[i][j]][1] for j in range(DIM))
        for i in range(DIM)
    )
    if actual != claimed:
        raise Q81PhaseProjectionError("ORIENTATION_WITNESS_MISMATCH")
    if not isinstance(native.get("source_identity"), str) or not native["source_identity"]:
        raise Q81PhaseProjectionError("SOURCE_IDENTITY_REQUIRED")
    if not isinstance(native.get("provenance"), Mapping):
        raise Q81PhaseProjectionError("PROVENANCE_REQUIRED")
    _gate_source()
    context = {
        "orientation": actual,
        "source_identity": native["source_identity"],
        "provenance": dict(native["provenance"]),
    }
    check = decode_candidate(binary, context=context)
    if check != native:
        raise Q81PhaseProjectionError("NATIVE_ROUNDTRIP_MISMATCH")
    return {
        "schema": SCHEMA,
        "binary": binary,
        "context": context,
        "candidate_only": True,
        "native_roundtrip_exact": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }


def verify_receipt(receipt: Mapping[str, Any]) -> bool:
    if not isinstance(receipt, Mapping) or receipt.get("schema") != SCHEMA:
        raise Q81PhaseProjectionError("RECEIPT_SCHEMA")
    if (
        receipt.get("candidate_only") is not True
        or receipt.get("canonical_vm81_mutation_authority") is not False
        or receipt.get("canonical_hash72_commit_authority") is not False
        or receipt.get("canonical_hash216_persistence_authority") is not False
    ):
        raise Q81PhaseProjectionError("RECEIPT_AUTHORITY")
    decoded = decode_candidate(receipt.get("binary"), context=receipt.get("context"))
    encoded = encode_candidate(decoded)
    if encoded != receipt:
        raise Q81PhaseProjectionError("RECEIPT_ROUNDTRIP_MISMATCH")
    return True
