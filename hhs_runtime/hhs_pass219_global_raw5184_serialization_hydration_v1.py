"""Pass 219 I150 global raw5184 compatibility serialization hydration.

This module binds inherited Python 5,184-bit / 648-byte VM81-compatible
serialization surfaces to the already-authoritative I148 integer-only
x,y,z,w octonion dual-stereo ternary PCM64 hydration law.

The projection remains derived and non-authoritative.  Returned bytes are
bit-identical to the supplied carrier.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    AudioHydration,
    CELLS,
    H36,
    PCM64_NOISE_FLOOR,
    PCM64_SATURATION_CEILING,
    PCM64_ZERO_CROSSING,
    PHASE_CHANNELS,
    PHASE_QUADS,
    RAW_BITS,
    RAW_BYTES,
    SINE_Q62,
    WORD_BITS,
    hydrate_words,
    le_bytes_to_words,
    words_to_le_bytes,
)

SCHEMA = "HHS_PASS219_I150_GLOBAL_RAW5184_COMPATIBILITY_HYDRATION_V1"
VERSION = "1.0.0"
TERNARY_ROLES = (-1, 0, 1)
TERNARY_PCM64 = (
    PCM64_NOISE_FLOOR,
    PCM64_ZERO_CROSSING,
    PCM64_SATURATION_CEILING,
)


@dataclass(frozen=True)
class Raw5184CompatibilityDescriptor:
    schema: str = SCHEMA
    version: str = VERSION
    raw_bits: int = RAW_BITS
    raw_bytes: int = RAW_BYTES
    vm81_cells: int = CELLS
    word_bits: int = WORD_BITS
    phase_quads: int = PHASE_QUADS
    phase_channels: int = len(PHASE_CHANNELS)
    h36: int = H36
    exact_bit_identity: bool = True
    little_endian_word_transport: bool = True
    dual_stereo_hydration_required: bool = True
    ternary_pcm64_required: bool = True
    zero_over_zero_u0_mod_u72_required: bool = True
    scalar_projection_runtime_authority: bool = False
    floating_point_authority: bool = False
    vm81_mutation_authority: bool = False
    hash72_commit_authority: bool = False
    hash216_commit_authority: bool = False
    canonical_persistence_authority: bool = False


def descriptor() -> Raw5184CompatibilityDescriptor:
    return Raw5184CompatibilityDescriptor()


def _validate_hydration(hydration: AudioHydration) -> None:
    if len(hydration.pcm64_bits) != CELLS:
        raise ValueError("I150_PCM64_CELL_COUNT")
    if len(hydration.quads) != PHASE_QUADS:
        raise ValueError("I150_PHASE_QUAD_COUNT")
    if len(hydration.sine_pcm64) != PHASE_QUADS * len(PHASE_CHANNELS):
        raise ValueError("I150_SINE_SAMPLE_COUNT")

    for quad in hydration.quads:
        if tuple(channel.basis for channel in quad.channels) != PHASE_CHANNELS:
            raise ValueError("I150_ORDERED_OCTONION_CHANNELS")
        q = quad.stereo_ternary
        if q.numerator_roles != TERNARY_ROLES:
            raise ValueError("I150_LEFT_TERNARY_ROLES")
        if q.denominator_roles != TERNARY_ROLES:
            raise ValueError("I150_RIGHT_TERNARY_ROLES")
        if q.quotient_identity != (1, 1, 1):
            raise ValueError("I150_TERNARY_QUOTIENT_IDENTITY")
        if q.quotient_phase72 != (0, 0, 0):
            raise ValueError("I150_TERNARY_QUOTIENT_PHASE")
        if q.role_pcm64 != TERNARY_PCM64:
            raise ValueError("I150_TERNARY_PCM64_BOUNDS")
        if not (
            q.left_mono_yx_sum_xy
            and q.right_mono_wz_sum_zw
            and q.center_mono_xy_sum_colon_zw_sum
            and q.exact_pcm64_role_bounds
            and q.center_zero_over_zero_u0_mod_u72
            and q.center_xy_sum_over_zw_sum_u0
            and q.typed_quotient_only
        ):
            raise ValueError("I150_STEREO_TERNARY_INVARIANT")
        if q.scalar_division_attempted or q.scalar_projection_runtime_authority:
            raise ValueError("I150_SCALAR_PROJECTION_AUTHORITY")

        by_basis = {channel.basis: channel.phase72 for channel in quad.channels}
        expected_left = (
            by_basis["yx"],
            (by_basis["x"] + by_basis["y"]) % 72,
            by_basis["xy"],
        )
        expected_right = (
            by_basis["wz"],
            (by_basis["z"] + by_basis["w"]) % 72,
            by_basis["zw"],
        )
        if q.left_mono_phase72 != expected_left:
            raise ValueError("I150_LEFT_MONO_ORDER")
        if q.right_mono_phase72 != expected_right:
            raise ValueError("I150_RIGHT_MONO_ORDER")

        for channel in quad.channels:
            if channel.sine_pcm64 != SINE_Q62[channel.phase72]:
                raise ValueError("I150_PCM64_SINE_Q62")

    if (
        hydration.canonical_mutation_authority
        or hydration.canonical_hash72_authority
        or hydration.canonical_hash216_authority
        or hydration.canonical_persistence_authority
        or hydration.scalar_projection_runtime_authority
        or hydration.floating_point_authority
    ):
        raise ValueError("I150_PROJECTION_AUTHORITY")


def hydrate_raw5184_bytes(payload: bytes | bytearray | memoryview) -> AudioHydration:
    raw = bytes(payload)
    if len(raw) != RAW_BYTES:
        raise ValueError("I150_RAW5184_BYTE_COUNT")
    words = le_bytes_to_words(raw)
    hydration = hydrate_words(words)
    _validate_hydration(hydration)
    replay = words_to_le_bytes(hydration.pcm64_bits)
    if replay != raw:
        raise AssertionError("I150_RAW5184_BIT_IDENTITY")
    return hydration


def serialize_raw5184_bytes(payload: bytes | bytearray | memoryview) -> bytes:
    raw = bytes(payload)
    hydrate_raw5184_bytes(raw)
    return raw


def deserialize_raw5184_bytes(payload: bytes | bytearray | memoryview) -> bytes:
    raw = bytes(payload)
    hydrate_raw5184_bytes(raw)
    return raw


def validation_receipt(payload: bytes | bytearray | memoryview) -> dict[str, Any]:
    raw = bytes(payload)
    hydration = hydrate_raw5184_bytes(raw)
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "raw_bits": RAW_BITS,
        "raw_bytes": len(raw),
        "vm81_cells": len(hydration.pcm64_bits),
        "phase_quads": len(hydration.quads),
        "pcm64_waveform_samples": len(hydration.sine_pcm64),
        "left_mono": ["yx", "x+y", "xy"],
        "right_mono": ["wz", "z+w", "zw"],
        "center_relation": "x+y:z+w",
        "ternary_roles": list(TERNARY_ROLES),
        "ternary_pcm64": list(TERNARY_PCM64),
        "center_closure": "0/0=u^0 mod(u^72)=1",
        "center_native_relation": "(x+y)/(z+w)=u^0",
        "exact_bit_identity": True,
        "scalar_projection_runtime_authority": False,
        "floating_point_authority": False,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
        "canonical_persistence_authority": False,
    }


__all__ = [
    "SCHEMA",
    "VERSION",
    "Raw5184CompatibilityDescriptor",
    "descriptor",
    "hydrate_raw5184_bytes",
    "serialize_raw5184_bytes",
    "deserialize_raw5184_bytes",
    "validation_receipt",
]
