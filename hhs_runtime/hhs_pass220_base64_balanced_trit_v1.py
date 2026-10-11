"""Exact 3-bit <-> 2 balanced-trit, 6-bit <-> 4-trit radix bridge.

Two balanced trits have 9 states; exactly 8 are used for 3-bit inputs.
(+1,+1) is the reserved ninth state. Base64 sextets group two octets.
This source-exact ingress codec does not replace the native HNAN gate.
"""
from __future__ import annotations

from dataclasses import dataclass

FRAME_BITS = 5184
BINARY_GROUPS = 1728
BALANCED_TRITS = 3456
BASE64_SEXTETS = 864
ALPHABET64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
TRIT_VALUES = (-1, 0, 1)
RESERVED_PAIR = (1, 1)


class InvalidRadixState(ValueError):
    pass


def encode_three_bits(bits: str) -> tuple[int, int]:
    if (
        not isinstance(bits, str)
        or len(bits) != 3
        or any(c not in "01" for c in bits)
    ):
        raise InvalidRadixState("THREE_BIT_GROUP")
    n = int(bits, 2)
    return (n // 3 - 1, n % 3 - 1)


def decode_two_trits(pair: tuple[int, int]) -> str:
    if (
        not isinstance(pair, tuple)
        or len(pair) != 2
        or any(type(t) is not int or t not in TRIT_VALUES for t in pair)
    ):
        raise InvalidRadixState("BALANCED_TRIT_PAIR")
    n = 3 * (pair[0] + 1) + pair[1] + 1
    if n == 8:
        raise InvalidRadixState("RESERVED_NINTH_PAIR")
    return f"{n:03b}"


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
