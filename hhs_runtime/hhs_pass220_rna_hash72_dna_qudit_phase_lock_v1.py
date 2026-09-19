"""Pass 220 I019: phase-lock the 5184-character BigInt state across RNA,
Hash72 chunk folding, x/y/z/w Digital DNA, H36 precision, and the 81-cell qudit.

This is a read-only exact witness layer.  The complete 5184-character
HARMONICODE rational-scientific serialization remains the state.  I019 scans
that same state as 72 x 72 characters and as 81 x 64-character qudit cells,
reads it bidirectionally through exact 3-character RNA windows, and binds the
already-proven 1/2/3 palindromic H36 precision constructor to the full state.

No canonical VM81 mutation, Hash72 mint, Hash216 persistence, or floating-point
authority is introduced.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH72_LEN,
    coordinate_5184,
    hash72_rows_from_5184,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    CELL_TOKEN_CHARACTERS,
    FRACTAL_123,
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
    PHASE_MATRIX,
    PHASE_PATH,
    Q_MINUS_ONE_PROJECTION,
)

SCHEMA = "HHS_PASS_220_RNA_HASH72_DNA_QUDIT_PHASE_LOCK_V1"
VERSION = "1.0.0-checkpoint.19"
PROFILE = "PASS220-I019-RNA-HASH72-DNA-QUDIT-PHASE-LOCK-v1"

RNA_WINDOW_CHARACTERS = 3
HASH72_CHUNKS = 72
RNA_WINDOWS_PER_HASH72_CHUNK = HASH72_LEN // RNA_WINDOW_CHARACTERS
RNA_WINDOWS_TOTAL = SERIALIZED_CHARACTERS // RNA_WINDOW_CHARACTERS
H36_CELLS = 36
H36_SIDE = 6
H36_MAGIC_LINE = 111
PRECISION_DENOMINATOR = 1000
SCALE_ROWS: Tuple[Tuple[int, int, int], ...] = FRACTAL_123


class Pass220RNAHash72DNAPhaseLockError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _root(value: Any) -> str:
    payload = value if isinstance(value, str) else _stable_json(value)
    return sha256(payload.encode("utf-8")).hexdigest()


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = _root(record)
    return record


def _require_serialized(serialized: str) -> Tuple[int, ...]:
    if not isinstance(serialized, str) or len(serialized) != SERIALIZED_CHARACTERS:
        raise Pass220RNAHash72DNAPhaseLockError(
            "state must be the exact 5184-character HARMONICODE serialization"
        )
    try:
        offsets = deserialize_offsets_5184(serialized)
    except Exception as exc:
        raise Pass220RNAHash72DNAPhaseLockError(
            "state is not a canonical 5184-character normalization carrier"
        ) from exc
    if serialize_offsets_5184(offsets) != serialized:
        raise Pass220RNAHash72DNAPhaseLockError(
            "state failed canonical deserialize/serialize identity"
        )
    return offsets


def _chunk_windows(chunk: str) -> Tuple[str, ...]:
    if len(chunk) != HASH72_LEN:
        raise Pass220RNAHash72DNAPhaseLockError("Hash72 chunk must contain 72 characters")
    windows = tuple(
        chunk[start : start + RNA_WINDOW_CHARACTERS]
        for start in range(0, HASH72_LEN, RNA_WINDOW_CHARACTERS)
    )
    if len(windows) != RNA_WINDOWS_PER_HASH72_CHUNK or any(
        len(window) != RNA_WINDOW_CHARACTERS for window in windows
    ):
        raise AssertionError("internal 72/3 RNA partition failed")
    return windows


def bidirectional_rna_windows(serialized: str) -> Dict[str, Any]:
    _require_serialized(serialized)
    rows = hash72_rows_from_5184(serialized)
    forward = tuple(
        window
        for chunk in rows
        for window in _chunk_windows(chunk)
    )
    reverse = tuple(
        window[::-1]
        for chunk in reversed(rows)
        for window in reversed(_chunk_windows(chunk))
    )
    forward_text = "".join(forward)
    reverse_text = "".join(reverse)
    if forward_text != serialized:
        raise AssertionError("forward RNA windows did not reconstruct the state")
    if reverse_text != serialized[::-1]:
        raise AssertionError("reverse RNA windows did not reconstruct the reverse state")
    if "".join(window[::-1] for window in reversed(reverse)) != serialized:
        raise AssertionError("double reverse RNA traversal did not restore the state")
    return {
        "hash72_chunks": len(rows),
        "hash72_chunk_characters": HASH72_LEN,
        "rna_window_characters": RNA_WINDOW_CHARACTERS,
        "rna_windows_per_chunk": RNA_WINDOWS_PER_HASH72_CHUNK,
        "rna_windows_total": len(forward),
        "forward_characters": len(forward_text),
        "reverse_characters": len(reverse_text),
        "forward_root_sha256": _root(forward_text),
        "reverse_root_sha256": _root(reverse_text),
        "double_reverse_exact": True,
    }


def coordinate_phase_lock_witness() -> Dict[str, Any]:
    seen_rna = set()
    seen_hash72 = set()
    seen_vm81 = set()
    for index in range(SERIALIZED_CHARACTERS):
        coordinate = coordinate_5184(index)
        chunk, within_chunk = divmod(index, HASH72_LEN)
        triplet, rna_symbol = divmod(within_chunk, RNA_WINDOW_CHARACTERS)
        if 72 * chunk + within_chunk != index:
            raise AssertionError("72x72 coordinate reconstruction failed")
        if (
            HASH72_LEN * coordinate["hash72_row"] + coordinate["hash72_column"]
            != index
        ):
            raise AssertionError("Hash72 coordinate drift")
        if (
            CELL_TOKEN_CHARACTERS * coordinate["vm81_cell"] + coordinate["local64"]
            != index
        ):
            raise AssertionError("VM81 coordinate drift")
        seen_rna.add((chunk, triplet, rna_symbol))
        seen_hash72.add((coordinate["hash72_row"], coordinate["hash72_column"]))
        seen_vm81.add((coordinate["vm81_cell"], coordinate["local64"]))
    return {
        "linear_positions": SERIALIZED_CHARACTERS,
        "rna_coordinates": len(seen_rna),
        "hash72_coordinates": len(seen_hash72),
        "vm81_local64_coordinates": len(seen_vm81),
        "all_coordinate_systems_bijective": (
            len(seen_rna)
            == len(seen_hash72)
            == len(seen_vm81)
            == SERIALIZED_CHARACTERS
        ),
        "factorizations": {
            "72x72": HASH72_CHUNKS * HASH72_LEN,
            "72x24x3": (
                HASH72_CHUNKS
                * RNA_WINDOWS_PER_HASH72_CHUNK
                * RNA_WINDOW_CHARACTERS
            ),
            "81x64": VM81_CELLS * CELL_TOKEN_CHARACTERS,
        },
        "coordinate_rule": "k=72*chunk+3*triplet+symbol=64*cell+local64",
    }


def palindromic_precision_lanes() -> Tuple[Dict[str, Any], ...]:
    lanes = []
    for scale, row in enumerate(SCALE_ROWS, start=1):
        palindrome = tuple(row) + tuple(reversed(row))
        remainder = Fraction(H36_MAGIC_LINE * scale, PRECISION_DENOMINATOR)
        if palindrome != tuple(reversed(palindrome)):
            raise AssertionError("1/2/3 precision word lost palindrome symmetry")
        if remainder / scale != Fraction(H36_MAGIC_LINE, PRECISION_DENOMINATOR):
            raise AssertionError("H36 precision remainder lost scale covariance")
        lanes.append({
            "scale": scale,
            "tensor_row": tuple(row),
            "palindrome": palindrome,
            "palindrome_digits": "".join(str(value) for value in palindrome),
            "remainder_numerator": remainder.numerator,
            "remainder_denominator": remainder.denominator,
            "remainder_exact": f"{remainder.numerator}/{remainder.denominator}",
            "base_remainder_exact": "111/1000",
            "mod2": tuple(value % 2 for value in row),
            "mod3": tuple(value % 3 for value in row),
        })
    return tuple(lanes)


def _scaled_state_palindrome_root(
    offsets: Sequence[int],
    *,
    scale: int,
) -> str:
    row = SCALE_ROWS[scale - 1]
    expanded = []
    for offset in offsets:
        left = tuple(offset * factor for factor in row)
        expanded.append(left + tuple(reversed(left)))
    return _root({
        "scale": scale,
        "palindromic_scaled_offsets": expanded,
        "remainder": (
            H36_MAGIC_LINE * scale,
            PRECISION_DENOMINATOR,
        ),
    })


def phase_locked_state_witness(serialized: str) -> Dict[str, Any]:
    offsets = _require_serialized(serialized)
    rna = bidirectional_rna_windows(serialized)
    coordinates = coordinate_phase_lock_witness()
    lanes = palindromic_precision_lanes()
    chunks = hash72_rows_from_5184(serialized)
    state_root = _root(serialized)

    lane_bindings = tuple({
        **lane,
        "full_state_palindrome_root_sha256": _scaled_state_palindrome_root(
            offsets, scale=lane["scale"]
        ),
        "bound_state_root_sha256": state_root,
    } for lane in lanes)

    q_minus_one = tuple(
        (name, Q_MINUS_ONE_PROJECTION[name])
        for name in ("xy", "yx", "zw", "wz")
    )

    checks = {
        "canonical_5184_roundtrip": serialize_offsets_5184(offsets) == serialized,
        "hash72_chunk_partition": len(chunks) == HASH72_CHUNKS,
        "rna_bidirectional_exact": (
            rna["rna_windows_total"] == RNA_WINDOWS_TOTAL
            and rna["double_reverse_exact"]
        ),
        "coordinate_phase_lock": coordinates["all_coordinate_systems_bijective"],
        "palindromic_precision_three_lanes": (
            tuple(lane["palindrome_digits"] for lane in lanes)
            == ("123321", "246642", "369963")
        ),
        "h36_scaled_remainders": (
            tuple(
                Fraction(
                    lane["remainder_numerator"],
                    lane["remainder_denominator"],
                )
                for lane in lanes
            )
            == (
                Fraction(111, 1000),
                Fraction(222, 1000),
                Fraction(333, 1000),
            )
        ),
        "ordered_xyzw_phase_present": q_minus_one == (
            ("xy", 1),
            ("yx", -1),
            ("zw", 1),
            ("wz", -1),
        ),
        "vm81_qudit_cells": len(offsets) == VM81_CELLS,
    }
    if not all(checks.values()):
        raise Pass220RNAHash72DNAPhaseLockError(
            "RNA/Hash72/DNA/qudit phase-lock witness failed"
        )

    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "state_root_sha256": state_root,
        "serialized_characters": len(serialized),
        "offset_count": len(offsets),
        "hash72_chunk_roots_sha256": tuple(_root(chunk) for chunk in chunks),
        "rna": rna,
        "coordinates": coordinates,
        "precision_lanes": lane_bindings,
        "digital_dna": {
            "phase_path": PHASE_PATH,
            "phase_matrix": PHASE_MATRIX,
            "q_minus_one_ordered_products": q_minus_one,
            "ordered_products_collapsed": False,
        },
        "qudit": {
            "cells": VM81_CELLS,
            "characters_per_cell": CELL_TOKEN_CHARACTERS,
            "same_state_index_required": True,
        },
        "checks": checks,
        "phase_locked": True,
        "complete_state_is_serialized_operand": True,
        "hash72_chunks_are_state_slices_not_minted_hashes": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    })


def validate_phase_locked_state(serialized: str) -> Dict[str, Any]:
    witness = phase_locked_state_witness(serialized)
    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "ok": witness["phase_locked"] and all(witness["checks"].values()),
        "state_root_sha256": witness["state_root_sha256"],
        "witness_receipt_sha256": witness["receipt_sha256"],
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "floating_point_authority": False,
    })


def phase_lock_self_test() -> Dict[str, Any]:
    offsets = tuple(index % 9 for index in range(VM81_CELLS))
    serialized = serialize_offsets_5184(offsets)
    return validate_phase_locked_state(serialized)
