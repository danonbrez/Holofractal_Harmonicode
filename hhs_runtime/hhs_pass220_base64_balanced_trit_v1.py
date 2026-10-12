"""HNAN-addressed 3-bit -> 2-balanced-trit / Base64 lossless ingress.

The nine balanced-trit pairs are the complete ordered 3x3 HNAN tensor:
the eight outer positions carry 000..111, the (0,0) center is the inherited
HNAN gate. Neither the binary mapping nor HNAN ordering is a free Base3 choice.
Source frame: 5184 bits -> 1728 tensor pairs -> 864 Base64 sextets.
This source-exact candidate ingress never replaces the native VM81/HNAN gate.
"""
from __future__ import annotations

from dataclasses import dataclass

from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    HNAN_LO_SHU_TENSOR,
    HNAN_LO_SHU_TENSOR_SOURCE,
    HNAN_CENTER_EXPRESSION,
    HNAN_GATE_10,
    hnan_gate,
)

FRAME_BITS = 5184
BINARY_GROUPS = 1728
BALANCED_TRITS = 3456
BASE64_SEXTETS = 864
ALPHABET64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
TRIT_VALUES = (-1, 0, 1)
HNAN_PAIR = (0, 0)
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
BINARY_ADDRESSES = (
    ("000", "001", "010"),
    ("011", "HNAN", "100"),
    ("101", "110", "111"),
)
# The binary->trit codebook IS the row-major HNAN tensor boundary,
# not ordinary decimal base-3 enumeration with a final unused ninth pair.
OUTER_PAIRS = tuple(
    (row, col)
    for row in TRIT_VALUES
    for col in TRIT_VALUES
    if (row, col) != HNAN_PAIR
)
PAIR_TO_BITS = {pair: f"{n:03b}" for n, pair in enumerate(OUTER_PAIRS)}


class InvalidRadixState(ValueError):
    pass


def _validate_pair(pair: tuple[int, int]) -> None:
    if (
        not isinstance(pair, tuple)
        or len(pair) != 2
        or any(type(t) is not int or t not in TRIT_VALUES for t in pair)
    ):
        raise InvalidRadixState("BALANCED_TRIT_PAIR")


def encode_three_bits(bits: str) -> tuple[int, int]:
    if (
        not isinstance(bits, str)
        or len(bits) != 3
        or any(c not in "01" for c in bits)
    ):
        raise InvalidRadixState("THREE_BIT_GROUP")
    return OUTER_PAIRS[int(bits, 2)]


def decode_two_trits(pair: tuple[int, int]) -> str:
    """Return binary from one of eight outer cells, not from HNAN center."""
    _validate_pair(pair)
    if pair == HNAN_PAIR:
        raise InvalidRadixState("HNAN_CENTER_REQUIRES_NATIVE_GATE")
    return PAIR_TO_BITS[pair]


def tensor_cell_for_pair(pair: tuple[int, int]) -> tuple:
    """Resolve all nine valid pair addresses to *existing* native HNAN ASTs.

    The center uses the inherited hnan_gate(1,0), not a new synthetic value.
    Every outer state retains its ordered x/y/z/w tensor expression.
    """
    _validate_pair(pair)
    row = pair[0] + 1
    col = pair[1] + 1
    if HNAN_LO_SHU_TENSOR_SOURCE[1][1] != HNAN_CENTER_EXPRESSION:
        raise InvalidRadixState("HNAN_CENTER_SOURCE_DRIFT")
    if pair == HNAN_PAIR:
        if HNAN_GATE_10 != hnan_gate(1, 0):
            raise InvalidRadixState("HNAN_GATE_DRIFT")
        return HNAN_GATE_10
    return HNAN_LO_SHU_TENSOR[row][col]


def tensor_address_for_pair(pair: tuple[int, int]) -> tuple[str, int, str]:
    """Return (binary address or HNAN, Lo Shu cell, source expression)."""
    _validate_pair(pair)
    r, c = pair[0] + 1, pair[1] + 1
    return (
        BINARY_ADDRESSES[r][c],
        LO_SHU[r][c],
        HNAN_LO_SHU_TENSOR_SOURCE[r][c],
    )


@dataclass(frozen=True)
class Base64TritCarrier:
    alphabet64: str
    trits: tuple[int, ...]
    source_bit_count: int = FRAME_BITS
    authority: str = "CANDIDATE_RADIX_PROJECTION_ONLY"


def encode_frame(bits: str) -> Base64TritCarrier:
    if (
        not isinstance(bits, str)
        or len(bits) != FRAME_BITS
        or any(c not in "01" for c in bits)
    ):
        raise InvalidRadixState("BINARY5184")
    trits = tuple(
        t
        for i in range(0, FRAME_BITS, 3)
        for t in encode_three_bits(bits[i:i + 3])
    )
    alphabet64 = "".join(
        ALPHABET64[int(bits[i:i + 6], 2)]
        for i in range(0, FRAME_BITS, 6)
    )
    assert len(trits) == BALANCED_TRITS
    assert len(alphabet64) == BASE64_SEXTETS
    carrier = Base64TritCarrier(alphabet64, trits)
    if decode_frame(carrier) != bits:
        raise InvalidRadixState("SOURCE_ROUNDTRIP")
    return carrier


def decode_frame(carrier: Base64TritCarrier) -> str:
    if (
        not isinstance(carrier, Base64TritCarrier)
        or carrier.source_bit_count != FRAME_BITS
        or carrier.authority != "CANDIDATE_RADIX_PROJECTION_ONLY"
    ):
        raise InvalidRadixState("RADIX_CARRIER_AUTHORITY")
    if len(carrier.trits) != BALANCED_TRITS:
        raise InvalidRadixState("TRIT_FRAME_WIDTH")
    bits = "".join(
        decode_two_trits(carrier.trits[i:i + 2])
        for i in range(0, BALANCED_TRITS, 2)
    )
    if (
        len(carrier.alphabet64) != BASE64_SEXTETS
        or any(c not in ALPHABET64 for c in carrier.alphabet64)
    ):
        raise InvalidRadixState("BASE64_FRAME_WIDTH_OR_ALPHABET")
    expected = "".join(
        ALPHABET64[int(bits[i:i + 6], 2)]
        for i in range(0, FRAME_BITS, 6)
    )
    if expected != carrier.alphabet64:
        raise InvalidRadixState("BASE64_TRIT_WITNESS_DISAGREEMENT")
    return bits
