"""Exact Pass 220 I001 normalization-offset <-> native VM81 frame membrane.

This is NOT a generic tensor-to-scalar compiler or a replacement for VM81.
The existing fixed 5184-character rational-scientific serialization is
authoritative for the I001 81-cell offset profile (cell values 0..8).
The native 81x64 binary frame is only its reversible ingress/egress carrier
under this explicitly typed profile, never the universal HARMONICODE state.
Cell addresses, ordering and external constraint ancestry must be retained
by the caller; no VM81 mutation or Hash72/Hash216 minting occurs here.
"""
from __future__ import annotations

import ctypes
import struct
from dataclasses import dataclass
from typing import Any

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    Pass220NormalizationError,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)

OFFSET_PROFILE = "PASS220-I001-LO-SHU-NORMALIZED-BIGINT-v1"
NATIVE_FRAME_PROFILE = "HHS_VM81_I001_OFFSETS_UINT64_LE_V1"
FRAME_BYTES = 648
CANONICAL_CHARACTERS = 5184
CELL_COUNT = 81

# Derive the ONLY nine admitted offset token spellings directly from the
# original Pass 220 I001 serializer. Validate lexically BEFORE entering the
# rational decoder: an untrusted 20-digit exponent must never trigger a
# 10**huge allocation or turn a source-identity failure into a DoS.
_I001_CANONICAL_TOKENS = {
    serialize_offsets_5184((value,) * CELL_COUNT)[:64]: value
    for value in range(9)
}


class NativeOffsetFrameError(ValueError):
    pass


@dataclass(frozen=True)
class NativeOffsetFrame:
    """Retains full original exact form and its verified reversible projection.

    Keep this carrier in the guarded runtime, never expose canonical source
    text through ordinary model-facing status or API telemetry.
    """
    canonical_5184: str
    raw_frame_le: bytes
    offsets: tuple[int, ...]
    profile: str = NATIVE_FRAME_PROFILE

    def public_status(self) -> dict[str, Any]:
        return {
            "schema": "HHS_NATIVE_OFFSET_VM81_FRAME_PROFILE_V1",
            "serialization_profile": OFFSET_PROFILE,
            "native_frame_profile": self.profile,
            "canonical_characters": len(self.canonical_5184),
            "native_frame_bytes": len(self.raw_frame_le),
            "ordered_cell_count": len(self.offsets),
            "source_state_exposed": False,
            "exact_profile_roundtrip_verified": True,
            "universal_tensor_codec_claimed": False,
            "commutation_or_scalarization_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_mint_authority": False,
        }


def _native_frame_abi() -> tuple[Any, type]:
    # Load the inherited C runtime once through its existing singleton
    # loader. Never build an alternative VM81 or substitute a pure Python
    # semantic authority for the C binary ingress/egress boundary.
    from hhs_python.runtime.hhs_exact_ctypes_bridge import (
        HHSExactVM81Frame,
        _RUNTIME_LIB,
    )
    return _RUNTIME_LIB, HHSExactVM81Frame


def _verify_through_native_frame(raw: bytes) -> tuple[int, ...]:
    if not isinstance(raw, bytes) or len(raw) != FRAME_BYTES:
        raise NativeOffsetFrameError("native VM81 ingress needs exactly 648 bytes")
    lib, NativeFrame = _native_frame_abi()
    source = (ctypes.c_uint8 * FRAME_BYTES).from_buffer_copy(raw)
    frame = NativeFrame()
    status = int(lib.hhs_exact_vm81_frame_import_le(
        source, FRAME_BYTES, ctypes.byref(frame)
    ))
    if status != 0:
        raise NativeOffsetFrameError(f"native VM81 import rejected: {status}")
    exported = (ctypes.c_uint8 * FRAME_BYTES)()
    written = ctypes.c_size_t()
    status = int(lib.hhs_exact_vm81_frame_export_le(
        ctypes.byref(frame), exported, FRAME_BYTES, ctypes.byref(written)
    ))
    if status != 0 or written.value != FRAME_BYTES:
        raise NativeOffsetFrameError("native VM81 exact frame export failed")
    if bytes(exported) != raw:
        raise NativeOffsetFrameError("native VM81 byte roundtrip diverged")
    return tuple(int(value) for value in frame.words)


def from_canonical_offset_object(serialized: str) -> NativeOffsetFrame:
    """Encode only native I001 normalized offsets, retaining full source."""
    if not isinstance(serialized, str) or len(serialized) != CANONICAL_CHARACTERS:
        raise NativeOffsetFrameError("5184-character exact rational carrier required")
    # Fail closed on noncanonical or adversarial token structures before
    # the generic Fraction/scientific exponent parser performs arithmetic.
    tokens = tuple(serialized[i:i + 64] for i in range(0, CANONICAL_CHARACTERS, 64))
    if any(token not in _I001_CANONICAL_TOKENS for token in tokens):
        raise NativeOffsetFrameError("noncanonical rational scientific spelling")
    try:
        offsets = deserialize_offsets_5184(serialized)
        canonical = serialize_offsets_5184(offsets)
    except (Pass220NormalizationError, ValueError) as exc:
        raise NativeOffsetFrameError("not a valid I001 offset serialization") from exc
    # The I001 decoder accepts equivalent rational spellings. This boundary
    # requires the exact canonical 64-character-per-cell representation;
    # accepting arbitrary textual variants would violate source identity.
    if canonical != serialized:
        raise NativeOffsetFrameError("noncanonical rational scientific spelling")
    if len(offsets) != CELL_COUNT or any(
        isinstance(digit, bool) or not isinstance(digit, int) or not 0 <= digit <= 8
        for digit in offsets
    ):
        raise NativeOffsetFrameError("81 native I001 offset cells required")
    raw = struct.pack("<81Q", *offsets)
    if _verify_through_native_frame(raw) != offsets:
        raise NativeOffsetFrameError("I001 cell order changed in VM81 ingress")
    return NativeOffsetFrame(canonical, raw, offsets)


def from_native_offset_frame(raw: bytes) -> NativeOffsetFrame:
    """Decode only exact 0..8 offset words; reject arbitrary VM81 bit states."""
    offsets = _verify_through_native_frame(raw)
    if len(offsets) != CELL_COUNT or any(value > 8 for value in offsets):
        raise NativeOffsetFrameError("VM81 words outside I001 normalized offset profile")
    canonical = serialize_offsets_5184(offsets)
    inverse = struct.pack("<81Q", *deserialize_offsets_5184(canonical))
    if inverse != raw:
        raise NativeOffsetFrameError("VM81 offset inverse projection failed")
    return NativeOffsetFrame(canonical, raw, offsets)


def assert_bidirectional_offset_identity(serialized: str) -> NativeOffsetFrame:
    """Check BOTH exact canonical string and native binary roundtrips."""
    original = from_canonical_offset_object(serialized)
    reconstructed = from_native_offset_frame(original.raw_frame_le)
    if (
        reconstructed.canonical_5184 != serialized
        or reconstructed.offsets != original.offsets
        or reconstructed.raw_frame_le != original.raw_frame_le
    ):
        raise NativeOffsetFrameError("bidirectional exact offset identity failed")
    return original
