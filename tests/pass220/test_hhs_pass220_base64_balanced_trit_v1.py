"""Exhaustive 3-bit/2-trit and Base64 sextet tests and full raw-frame checks."""
from dataclasses import replace
from hashlib import sha256

import pytest

from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import (
    ALPHABET64,
    BINARY_GROUPS,
    BALANCED_TRITS,
    BASE64_SEXTETS,
    HNAN_PAIR,
    OUTER_PAIRS,
    BINARY_ADDRESSES,
    LO_SHU,
    tensor_cell_for_pair,
    tensor_address_for_pair,
    InvalidRadixState,
    encode_three_bits,
    decode_two_trits,
    encode_frame,
    decode_frame,
)


def test_all_three_bit_and_two_trit_pairs() -> None:
    pairs = [encode_three_bits(f"{i:03b}") for i in range(8)]
    assert len(set(pairs)) == 8
    assert pairs == list(OUTER_PAIRS)
    assert HNAN_PAIR not in pairs
    assert all(decode_two_trits(pair) == f"{i:03b}" for i, pair in enumerate(pairs))
    # HNAN is a valid ninth tensor state, not a binary input.
    assert tensor_cell_for_pair(HNAN_PAIR)[0] == "Quotient"
    assert tensor_address_for_pair(HNAN_PAIR) == (
        "HNAN", 5, "x+y-z-w+xy+yx-zw-wz",
    )
    with pytest.raises(InvalidRadixState, match="HNAN_CENTER_REQUIRES_NATIVE_GATE"):
        decode_two_trits(HNAN_PAIR)


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


def test_hnan_center_routing_and_base64_mismatch_fail_closed() -> None:
    carrier = encode_frame("0" * 5184)
    with pytest.raises(InvalidRadixState, match="HNAN_CENTER_REQUIRES_NATIVE_GATE"):
        decode_frame(replace(carrier, trits=HNAN_PAIR + carrier.trits[2:]))
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
        "hnanCenterDecoded",
        "allNineTensorStatesRoundTrip",
        "base64DomainCardinality",
    ):
        assert token in lean
    assert "TestReport" in wl
    assert "Full5184" in wl
    assert "64" in wl



def test_tensor_pair_codebook_exact_hnan_loshu_geometry() -> None:
    from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
        HNAN_LO_SHU_TENSOR,
        HNAN_LO_SHU_TENSOR_SOURCE,
        hnan_gate,
    )
    expected = (
        ("000", "001", "010"),
        ("011", "HNAN", "100"),
        ("101", "110", "111"),
    )
    assert BINARY_ADDRESSES == expected
    assert LO_SHU == ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    for r in (-1, 0, 1):
        for c in (-1, 0, 1):
            pair = (r, c)
            addr, loshu, source = tensor_address_for_pair(pair)
            assert addr == expected[r + 1][c + 1]
            assert loshu == LO_SHU[r + 1][c + 1]
            assert source == HNAN_LO_SHU_TENSOR_SOURCE[r + 1][c + 1]
            expected_ast = (
                hnan_gate(1, 0)
                if pair == HNAN_PAIR else HNAN_LO_SHU_TENSOR[r + 1][c + 1]
            )
            assert tensor_cell_for_pair(pair) == expected_ast
            if pair != HNAN_PAIR:
                assert decode_two_trits(pair) == addr
