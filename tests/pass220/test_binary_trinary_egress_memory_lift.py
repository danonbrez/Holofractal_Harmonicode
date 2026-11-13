"""Pass 220 additive binary-egress/trinary-memory-lift composition tests.

This is a read-only verification surface, not a new VM81 authority or Delta ABI.
It reuses the inherited Lo Shu seed, Pass 070 reversible binary/trinary
translation and Pass 175 permanent address mapping. The expanded 3x3 positions
are auxiliary memory coordinates, NOT newly minted VM5184 addresses.
"""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_loshu_phase_embedding_v1 import LO_SHU_3X3
from hhs_runtime.pass175.runtime import InstructionAddress
from hhs_backend.runtime.hhs_universal_binary_trinary_translation_v1 import (
    make_binary_pair_state,
    reconstruct_pair,
    translate_pair,
)


def _trit(value: int) -> int:
    """Inherited Pass 219 trit(s)=(s mod 3)-1, balanced residue."""
    return value % 3 - 1


KERNEL = tuple(tuple(_trit(s) for s in row) for row in LO_SHU_3X3)


def _balanced_add(a: int, b: int) -> int:
    return (a + b + 1) % 3 - 1


def _lift_bit(bit: int) -> tuple[tuple[int, ...], ...]:
    if type(bit) is not int or bit not in (0, 1):
        raise ValueError("binary egress bit required")
    return tuple(tuple(_balanced_add(bit, k) for k in row) for row in KERNEL)


def _recover_bit(block: tuple[tuple[int, ...], ...]) -> int:
    if len(block) != 3 or any(len(row) != 3 for row in block):
        raise ValueError("3x3 lift required")
    candidates = set()
    for r in range(3):
        for c in range(3):
            trit = block[r][c]
            if type(trit) is not int or trit not in (-1, 0, 1):
                raise ValueError("nontrinary lift state")
            candidates.add((trit - KERNEL[r][c]) % 3)
    if len(candidates) != 1 or next(iter(candidates)) not in (0, 1):
        raise ValueError("inconsistent or corrupted lift")
    return next(iter(candidates))


def _bits(data: bytes, bit_order: str) -> tuple[int, ...]:
    if bit_order not in ("MSB0", "LSB0"):
        raise ValueError("explicit bit-order selection required")
    shifts = range(7, -1, -1) if bit_order == "MSB0" else range(8)
    return tuple((byte >> shift) & 1 for byte in data for shift in shifts)


def _pack(bits: tuple[int, ...], bit_order: str) -> bytes:
    shifts = range(7, -1, -1) if bit_order == "MSB0" else range(8)
    out = bytearray()
    for offset in range(0, len(bits), 8):
        out.append(sum(bits[offset + i] << shift for i, shift in enumerate(shifts)))
    return bytes(out)


@pytest.mark.parametrize("bit_order", ["MSB0", "LSB0"])
@pytest.mark.parametrize("pattern", [0, 1, 2, 3])
def test_full_648_byte_egress_trinary_lift_recovers_exact_payload(
    bit_order: str, pattern: int
) -> None:
    sources = (
        bytes(648),
        bytes([255]) * 648,
        bytes([0xA5, 0x5A]) * 324,
        bytes((i * 73 + 19) % 256 for i in range(648)),
    )
    binary = sources[pattern]
    original = bytes(binary)
    bits = _bits(binary, bit_order)
    assert len(bits) == 5184
    lift = tuple(_lift_bit(bit) for bit in bits)
    assert len(lift) * 9 == 46656
    assert all(len({t for row in block for t in row}) == 3 for block in lift)
    recovered = tuple(_recover_bit(block) for block in lift)
    assert recovered == bits
    assert _pack(recovered, bit_order) == original
    assert binary == original  # immutable egress source
    for address, bit in enumerate(bits):
        cell = InstructionAddress.from_state(address)
        assert address == 64 * cell.cell + cell.operation
        assert _recover_bit(lift[address]) == bit


def test_lift_is_not_new_native_address_or_inversion_authority() -> None:
    assert len(LO_SHU_3X3) == 3
    assert len(KERNEL) == 3
    assert all(sum(row) == 0 for row in KERNEL)
    assert sorted(sum((list(row) for row in KERNEL), [])) == [-1, -1, -1, 0, 0, 0, 1, 1, 1]
    with pytest.raises(ValueError):
        _lift_bit(-1)
    block = [list(row) for row in _lift_bit(1)]
    block[0][0] = _balanced_add(block[0][0], 1)
    with pytest.raises(ValueError, match="inconsistent"):
        _recover_bit(tuple(tuple(row) for row in block))


def test_existing_pass070_pair_translation_unchanged() -> None:
    for a in (0, 1):
        for b in (0, 1):
            source = make_binary_pair_state((a, b))
            translation = translate_pair(source)
            result = reconstruct_pair(translation)
            assert result["source_identity_recovered"] is True
            assert result["reconstructed_bits"] == [a, b]


# Out of scope until bound to the repository's typed Delta / UCE execution:
#   native F(Delta=B, theta) -> B' -> compare B' with B;
#   VM81 admission, Hash72/Hash216 receipts, RML15 reverse replay.
# A 3x3 memory lift alone must not claim those admission results.
