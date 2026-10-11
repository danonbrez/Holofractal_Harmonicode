"""Pointwise-complete HNAN witness-carrier regression; native authority unchanged."""
from dataclasses import replace
from hashlib import sha256
from itertools import product

import pytest

from hhs_runtime.hhs_pass220_hnan_full_state_space_preservation_v1 import (
    BYTES_PER_BINARY_FRAME,
    BYTES_PER_TRINARY_LANE,
    FullState,
    StateSpaceError,
    decode_full_state,
    encode_full_state,
    pack_trinary_plane,
    unpack_trinary_plane,
    vm_hash72_address,
)


def full_frame(seed: int = 0) -> FullState:
    # All 18 local binary/xy/zw triples appear in every 18-position window.
    return FullState(
        binary="".join(str(((i + seed) % 2)) for i in range(5184)),
        xy_lane=tuple((((i // 2 + seed) % 3) - 1) for i in range(5184)),
        zw_lane=tuple((((i // 6 + seed) % 3) - 1) for i in range(5184)),
    )


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 17, 64])
def test_all_5184_positions_exact_full_witness(seed: int) -> None:
    source = full_frame(seed)
    witness = encode_full_state(source)
    assert len(witness.vm81_le_bytes) == BYTES_PER_BINARY_FRAME == 648
    assert len(witness.xy_two_bit_plane) == BYTES_PER_TRINARY_LANE == 1296
    assert len(witness.zw_two_bit_plane) == BYTES_PER_TRINARY_LANE == 1296
    assert decode_full_state(witness) == source
    assert witness.authority == "CANDIDATE_WITNESS_ONLY"


def test_all_18_local_binary_and_complete_trinary_combinations() -> None:
    triples = tuple(
        (binary, xy, zw)
        for binary, xy, zw in product((0, 1), (-1, 0, 1), (-1, 0, 1))
    )
    assert len(triples) == 18
    for b, l, r in triples:
        source = FullState(str(b) * 5184, (l,) * 5184, (r,) * 5184)
        assert decode_full_state(encode_full_state(source)) == source


def test_every_5184_coordinate_dual_address_is_exact() -> None:
    seen_vm = set()
    seen_hash = set()
    for i in range(5184):
        vm, h72 = vm_hash72_address(i)
        assert vm[0] * 64 + vm[1] == i
        assert h72[0] * 72 + h72[1] == i
        seen_vm.add(vm)
        seen_hash.add(h72)
    assert len(seen_vm) == len(seen_hash) == 5184


def test_all_three_trits_roundtrip_at_each_address() -> None:
    for role in (-1, 0, 1):
        packed = pack_trinary_plane((role,) * 5184)
        assert unpack_trinary_plane(packed) == (role,) * 5184


def test_invalid_11_code_is_rejected_not_coerced() -> None:
    source = full_frame()
    witness = encode_full_state(source)
    corrupted = bytes([witness.xy_two_bit_plane[0] | 3]) + witness.xy_two_bit_plane[1:]
    with pytest.raises(StateSpaceError, match="NONCANONICAL"):
        decode_full_state(replace(witness, xy_two_bit_plane=corrupted))


def test_tampered_valid_phase_code_is_rejected_by_difference_witness() -> None:
    witness = encode_full_state(full_frame())
    first = witness.xy_two_bit_plane[0]
    old_code = first & 3
    new_code = (old_code + 1) % 3
    corrupted = bytes([(first & 252) | new_code]) + witness.xy_two_bit_plane[1:]
    with pytest.raises(StateSpaceError, match="PHASE_DIFFERENCE_WITNESS_DRIFT"):
        decode_full_state(replace(witness, xy_two_bit_plane=corrupted))


def test_invalid_source_trit_is_rejected() -> None:
    good = full_frame()
    bad = list(good.xy_lane)
    bad[17] = 3
    with pytest.raises(StateSpaceError, match="XY:TRINARY_ALPHABET"):
        encode_full_state(replace(good, xy_lane=tuple(bad)))


def test_invalid_binary_width_is_rejected() -> None:
    good = full_frame()
    with pytest.raises(StateSpaceError, match="BINARY_5184"):
        encode_full_state(replace(good, binary=good.binary[:-1]))


def test_phase_difference_sha256_is_deterministic() -> None:
    state = full_frame()
    a = encode_full_state(state)
    b = encode_full_state(state)
    assert a == b
    expected = sha256(bytes(l - r + 2 for l, r in zip(
        state.xy_lane, state.zw_lane, strict=True
    ))).hexdigest()
    assert a.relative_phase_sha256 == expected


def test_full_state_symbols_present_in_lean_wolfram() -> None:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    lean = (root / "formal/lean/HHS/Pass220/HNANFullStateSpacePreservation.lean").read_text()
    wl = (root / "formal/wolfram/pass220_hnan_full_5184_state_space_preservation_v1.wl").read_text()
    for token in (
        "fullStateRoundTrip", "fullStateEncodingInjective",
        "allTritAddressesRoundTrip", "allXYCodesAdmitted",
        "allRelativePhaseWitnessesRetained",
        "vm81AndHash72SharePosition",
    ):
        assert token in lean
    assert wl.count("VerificationTest[") == 21
    assert "AllTestsSucceeded" in wl
    assert "ArbitraryHash72DigestInversionClaimed" in wl
