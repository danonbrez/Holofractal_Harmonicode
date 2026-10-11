"""Pass 220 universal 5184-address witnessed state preservation (candidate).

Exhaustive local 2 x 3 x 3 state encoding extended pointwise to 5184
addresses; the Lean proof quantifies over all 2^5184 * 3^10368
possible unconstrained combined binary and paired-trinary assignments.

The full raw frame and two trinary witness planes are retained. This
representation is NOT a substitute for HNAN gate semantics, HHS ordered
octonion products, canonical Hash72, or native VM81 admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    bitstring_to_words,
    words_to_bitstring,
    words_to_le_bytes,
    le_bytes_to_words,
)

WIDTH = 5184
BYTES_PER_BINARY_FRAME = 648
BYTES_PER_TRINARY_LANE = WIDTH // 4
ROLE_TO_CODE = {-1: 0, 0: 1, 1: 2}
CODE_TO_ROLE = (-1, 0, 1)


class StateSpaceError(ValueError):
    pass


@dataclass(frozen=True)
class FullState:
    binary: str
    xy_lane: tuple[int, ...]
    zw_lane: tuple[int, ...]


@dataclass(frozen=True)
class EncodedWitness:
    vm81_le_bytes: bytes
    xy_two_bit_plane: bytes
    zw_two_bit_plane: bytes
    relative_phase_sha256: str
    address_count: int = WIDTH
    authority: str = "CANDIDATE_WITNESS_ONLY"


def _validate_trits(values: Sequence[int], name: str) -> None:
    if len(values) != WIDTH:
        raise StateSpaceError(f"{name}:TRINARY_WIDTH")
    if any(type(value) is not int or value not in ROLE_TO_CODE for value in values):
        raise StateSpaceError(f"{name}:TRINARY_ALPHABET")


def pack_trinary_plane(values: Sequence[int]) -> bytes:
    """2-bit packing, four exact balanced-trinary roles per byte."""
    _validate_trits(values, "PACK")
    out = bytearray(BYTES_PER_TRINARY_LANE)
    for i, role in enumerate(values):
        out[i >> 2] |= ROLE_TO_CODE[role] << ((i & 3) * 2)
    return bytes(out)


def unpack_trinary_plane(packed: bytes) -> tuple[int, ...]:
    if not isinstance(packed, bytes) or len(packed) != BYTES_PER_TRINARY_LANE:
        raise StateSpaceError("TRINARY_PACKED_WIDTH")
    out: list[int] = []
    for i in range(WIDTH):
        code = (packed[i >> 2] >> ((i & 3) * 2)) & 3
        if code == 3:
            raise StateSpaceError("NONCANONICAL_11_TRIT_CODE")
        out.append(CODE_TO_ROLE[code])
    return tuple(out)


def _phase_digest(left: Sequence[int], right: Sequence[int]) -> str:
    # The signed phase role difference lies in [-2,+2].
    # Shift by +2 for a deterministic exact-byte witness.
    return sha256(bytes(l - r + 2 for l, r in zip(left, right, strict=True))).hexdigest()


def encode_full_state(state: FullState) -> EncodedWitness:
    """Exact source-bound representation; no independent Hash72 inversion."""
    if not isinstance(state, FullState):
        raise StateSpaceError("STATE_TYPE")
    raw = state.binary
    if not isinstance(raw, str) or len(raw) != WIDTH or set(raw) - {"0", "1"}:
        raise StateSpaceError("BINARY_5184")
    _validate_trits(state.xy_lane, "XY")
    _validate_trits(state.zw_lane, "ZW")
    raw_bytes = words_to_le_bytes(bitstring_to_words(raw))
    if len(raw_bytes) != BYTES_PER_BINARY_FRAME:
        raise StateSpaceError("RAW648")
    result = EncodedWitness(
        vm81_le_bytes=raw_bytes,
        xy_two_bit_plane=pack_trinary_plane(state.xy_lane),
        zw_two_bit_plane=pack_trinary_plane(state.zw_lane),
        relative_phase_sha256=_phase_digest(state.xy_lane, state.zw_lane),
    )
    if decode_full_state(result) != state:
        raise StateSpaceError("FULL_STATE_ROUNDTRIP")
    return result


def decode_full_state(witness: EncodedWitness) -> FullState:
    if (
        not isinstance(witness, EncodedWitness)
        or witness.address_count != WIDTH
        or witness.authority != "CANDIDATE_WITNESS_ONLY"
        or not isinstance(witness.vm81_le_bytes, bytes)
        or len(witness.vm81_le_bytes) != BYTES_PER_BINARY_FRAME
    ):
        raise StateSpaceError("WITNESS_ADMISSION")
    binary = words_to_bitstring(le_bytes_to_words(witness.vm81_le_bytes))
    left = unpack_trinary_plane(witness.xy_two_bit_plane)
    right = unpack_trinary_plane(witness.zw_two_bit_plane)
    if _phase_digest(left, right) != witness.relative_phase_sha256:
        raise StateSpaceError("PHASE_DIFFERENCE_WITNESS_DRIFT")
    return FullState(binary=binary, xy_lane=left, zw_lane=right)


def vm_hash72_address(index: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """The two exact addresses designate the same linear position."""
    if type(index) is not int or not 0 <= index < WIDTH:
        raise StateSpaceError("ADDRESS_5184")
    vm = divmod(index, 64)
    h72 = divmod(index, 72)
    if vm[0] * 64 + vm[1] != h72[0] * 72 + h72[1]:
        raise StateSpaceError("COORDINATE_IDENTITY")
    return vm, h72
