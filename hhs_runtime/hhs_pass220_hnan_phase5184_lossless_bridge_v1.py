"""Pass 220 read-only HNAN phase5184 bridge.

Combines existing I148 raw bit-preserving VM81 ingress, the inherited ordered
HNAN witness, and I065 Hash72 generator hydration without inventing a new
canonical mutation/hash authority. It is NOT a codec from arbitrary 5184 raw
bits into 72 hash symbols: the raw carrier is retained for exact recovery.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any

from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import (
    encode_frame as encode_base64_trits,
    decode_frame as decode_base64_trits,
)
from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    pipeline as raw5184_pipeline,
    words_to_bitstring,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_CENTER_EXPRESSION,
    HNAN_LO_SHU_TENSOR_SOURCE,
    HNAN_TERMINAL_SOURCE,
    invariant_receipt,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    HASH72_ALPHABET,
    HASH72_POSITIONS,
    hash72_vertex_geometry,
    compress_hash72_vertex_geometry,
    validate_binary5184,
)

SCHEMA = "HHS_PASS220_HNAN_PHASE5184_LOSSLESS_BRIDGE_V1"
EXPECTED_TENSOR = (
    ("xy", "x+y", "yx"),
    ("xy-zw", "x+y-z-w+xy+yx-zw-wz", "wz-yx"),
    ("wz", "z+w", "zw"),
)
ADDRESSES = (
    ("000", "001", "010"),
    ("011", "HNAN", "100"),
    ("101", "110", "111"),
)


class Phase5184BridgeError(ValueError):
    pass


def validate_generator(word: str) -> str:
    if not isinstance(word, str) or len(word) != HASH72_POSITIONS:
        raise Phase5184BridgeError("HASH72_GENERATOR_WIDTH")
    if any(ch not in HASH72_ALPHABET for ch in word):
        raise Phase5184BridgeError("HASH72_GENERATOR_ALPHABET")
    return word


def phase_difference_witnesses(source: Any) -> tuple[tuple[tuple[int, int, int], ...], ...]:
    """Three ordered, reversible modular phase differences per octonion quad.

    For every (left, right) phase pair, delta = (left-right) mod 72.
    Reconstruct left from (right, delta), retaining role/order provenance.
    This additive projection is not native tensor scalarization.
    """
    witnesses = tuple(
        tuple(
            (left, right, (left - right) % 72)
            for left, right in zip(
                quad.stereo_ternary.left_mono_phase72,
                quad.stereo_ternary.right_mono_phase72,
                strict=True,
            )
        )
        for quad in source.quads
    )
    if len(witnesses) != 20 or any(len(row) != 3 for row in witnesses):
        raise Phase5184BridgeError("THREE_PERSPECTIVES_PER_QUAD")
    if not all((right + delta) % 72 == left for row in witnesses
               for left, right, delta in row):
        raise Phase5184BridgeError("PHASE_DIFFERENCE_NOT_REVERSIBLE")
    return witnesses


def candidate_bridge(
    raw_bits: str,
    generator: str,
    *,
    require_i065_palindrome: bool = False,
    expand_generator: bool = False,
) -> dict[str, Any]:
    """Execute an exact read-only bridge with optional full Hash72 hydration.

    Preserves all 5184 source bits independently of the Hash72 generator.
    The generator may be independently supplied; no invented link to raw bits.
    """
    source = raw5184_pipeline(raw_bits)
    if words_to_bitstring(source.pcm64_bits) != raw_bits:
        raise Phase5184BridgeError("RAW5184_RECOVERY_FAILURE")
    if require_i065_palindrome:
        validate_binary5184(raw_bits)
    word = validate_generator(generator)

    if HNAN_LO_SHU_TENSOR_SOURCE != EXPECTED_TENSOR:
        raise Phase5184BridgeError("HNAN_ORDERED_PHASE_DRIFT")
    if HNAN_CENTER_EXPRESSION != EXPECTED_TENSOR[1][1]:
        raise Phase5184BridgeError("HNAN_CENTER_DRIFT")
    if HNAN_TERMINAL_SOURCE != "xy+epsilon":
        raise Phase5184BridgeError("HNAN_EPSILON_ELIDED")
    hnan = invariant_receipt()
    if hnan["status"] != "PASS":
        raise Phase5184BridgeError("HNAN_INVARIANT_FAILURE")

    stereo_views = tuple(quad.stereo_ternary for quad in source.quads)
    if len(stereo_views) != 20 or any(
        view.numerator_roles != (-1, 0, 1)
        or view.denominator_roles != (-1, 0, 1)
        or not view.typed_quotient_only
        for view in stereo_views
    ):
        raise Phase5184BridgeError("TRINARY_LANE_ROLE_FAILURE")

    differences = phase_difference_witnesses(source)
    radix_carrier = encode_base64_trits(raw_bits)
    if decode_base64_trits(radix_carrier) != raw_bits:
        raise Phase5184BridgeError("BASE64_TRINARY_ROUNDTRIP")

    roundtrip = None
    materialized = 0
    if expand_generator:
        vertices = hash72_vertex_geometry(word)
        recovered = compress_hash72_vertex_geometry(vertices)
        if recovered != word:
            raise Phase5184BridgeError("HASH72_GENERATOR_RECOVERY_FAILURE")
        roundtrip = True
        materialized = len(vertices)

    return {
        "schema": SCHEMA,
        "raw_bits": raw_bits,  # retained full source, not replaced by a digest
        "raw_sha256": sha256(raw_bits.encode("ascii")).hexdigest(),
        "raw_width": len(raw_bits),
        "vm81_cells": len(source.pcm64_bits),
        "quad_count": len(source.quads),
        "pilot_word": source.pilot_pcm64_bits,
        "hnan_tensor": HNAN_LO_SHU_TENSOR_SOURCE,
        "phase_difference_witnesses": differences,
        "phase_difference_exact": True,
        "radix_binary3_groups": 1728,
        "radix_balanced_trits": len(radix_carrier.trits),
        "radix_base64_sextets": len(radix_carrier.alphabet64),
        "base64_trinary_roundtrip_exact": True,
        "hnan_binary_addresses": ADDRESSES,
        "hnan_center_source": HNAN_CENTER_EXPRESSION,
        "hnan_terminal_source": HNAN_TERMINAL_SOURCE,
        "hnan_invariants_pass": True,
        "hash72_generator": word,
        "hash72_hydrated_vertex_count": materialized,
        "hash72_admitted_generator_roundtrip": roundtrip,
        "i065_palindrome_enforced": require_i065_palindrome,
        "raw_roundtrip_exact": True,
        "candidate_only": True,
        "new_vm81_mutation_authority": False,
        "new_hash72_commit_authority": False,
        "new_hash216_persistence_authority": False,
        "generic_5184_to_72_compression_claim": False,
    }


def recover_raw(receipt: dict[str, Any]) -> str:
    """Lossless reconstruction from retained source, not from hash alone."""
    if receipt.get("schema") != SCHEMA:
        raise Phase5184BridgeError("BRIDGE_SCHEMA")
    raw = receipt.get("raw_bits")
    if (
        not isinstance(raw, str)
        or len(raw) != 5184
        or any(bit not in "01" for bit in raw)
        or receipt.get("raw_sha256") != sha256(raw.encode("ascii")).hexdigest()
    ):
        raise Phase5184BridgeError("RAW5184_WITNESS_CORRUPTED")
    source = raw5184_pipeline(raw)
    if receipt.get("phase_difference_witnesses") != phase_difference_witnesses(source):
        raise Phase5184BridgeError("PHASE_DIFFERENCE_WITNESS_DRIFT")
    return raw
