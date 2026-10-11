"""Exhaustive 3-bit/2-trit and Base64 sextet tests and full raw-frame checks."""
from dataclasses import replace
from hashlib import sha256

import pytest

from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import (
    ALPHABET64,
    BINARY_GROUPS,
    BALANCED_TRITS,
    BASE64_SEXTETS,
    RESERVED_PAIR,
    InvalidRadixState,
    encode_three_bits,
    decode_two_trits,
    encode_frame,
    decode_frame,
)


def test_all_three_bit_and_two_trit_pairs() -> None:
    pairs = [encode_three_bits(f"{i:03b}") for i in range(8)]
    assert len(set(pairs)) == 8
    assert RESERVED_PAIR not in pairs
    assert all(decode_two_trits(pair) == f"{i:03b}" for i, pair in enumerate(pairs))
    with pytest.raises(InvalidRadixState, match="RESERVED_NINTH_PAIR"):
        decode_two_trits(RESERVED_PAIR)


def test_all_base64_64_sextets() -> None:
    symbols = set()
    for i in range(64):
        bits = f"{i:06b}"
        first = encode_three_bits(bits[:3])
        second = encode_three_bits(bits[3:])
        assert decode_two_trits(first) + decode_two_trits(second) == bits
        symbols.add(ALPHABET64[i])
    assert len(symbols) == 64


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 31, 63, 127, 255])
def test_5184_bit_full_frame_roundtrip(seed: int) -> None:
    data = bytearray()
    n = 0
    while len(data) < 648:
        data.extend(sha256(bytes([seed]) + n.to_bytes(4, "big")).digest())
        n += 1
    bits = "".join(f"{value:08b}" for value in data[:648])
    carrier = encode_frame(bits)
    assert len(carrier.trits) == BALANCED_TRITS == 3456
    assert len(carrier.alphabet64) == BASE64_SEXTETS == 864
    assert BINARY_GROUPS == 1728
    assert decode_frame(carrier) == bits
    assert carrier.authority == "CANDIDATE_RADIX_PROJECTION_ONLY"


def test_unused_pair_and_base64_mismatch_fail_closed() -> None:
    carrier = encode_frame("0" * 5184)
    with pytest.raises(InvalidRadixState, match="RESERVED_NINTH_PAIR"):
        decode_frame(replace(carrier, trits=RESERVED_PAIR + carrier.trits[2:]))
    with pytest.raises(InvalidRadixState, match="BASE64_TRIT_WITNESS_DISAGREEMENT"):
        decode_frame(replace(
            carrier, alphabet64="B" + carrier.alphabet64[1:]))


def test_binary_width_and_alphabet_rejected() -> None:
    with pytest.raises(InvalidRadixState, match="BINARY5184"):
        encode_frame("1" * 5183)
    with pytest.raises(InvalidRadixState, match="BINARY5184"):
        encode_frame("1" * 5183 + "x")


def test_lean_and_wolfram_proof_surfaces() -> None:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    lean = (root / "formal/lean/HHS/Pass220/Base64BalancedTrit5184.lean").read_text()
    wl = (root / "formal/wolfram/pass220_base64_balanced_trit5184_v1.wl").read_text()
    for token in (
        "allThreeBitTriplesRoundTrip",
        "full5184RadixRoundTrip",
        "reservedNinthRejected",
        "base64DomainCardinality",
    ):
        assert token in lean
    assert "TestReport" in wl
    assert "Full5184" in wl
    assert "64" in wl
