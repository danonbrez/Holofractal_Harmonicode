"""Cross-verify the Pass 220 expanded trinary memory view with native HNAN codec.

Both views reconstruct the identical 5,184-bit binary egress; neither is a
substitute for a typed symbolic Delta execution or new VM81 authority.
"""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import (
    BALANCED_TRITS, BASE64_SEXTETS, FRAME_BITS, HNAN_PAIR,
    decode_frame, decode_two_trits, encode_frame, encode_three_bits,
    tensor_address_for_pair, tensor_cell_for_pair,
)
from test_binary_trinary_egress_memory_lift import (
    _bits, _lift_bit, _pack, _recover_bit,
)


@pytest.mark.parametrize("pattern", [0, 1, 2, 3])
def test_expanded_register_and_hnan_native_codec_agree(pattern: int) -> None:
    sources = (
        bytes(648),
        bytes([0xFF]) * 648,
        bytes([0xA5, 0x5A]) * 324,
        bytes((i * 73 + 19) % 256 for i in range(648)),
    )
    source = sources[pattern]
    bits = _bits(source, "MSB0")
    lifted = tuple(_lift_bit(bit) for bit in bits)
    recovered_bits = tuple(_recover_bit(block) for block in lifted)
    assert len(lifted) * 9 == 46656
    assert len(recovered_bits) == FRAME_BITS
    assert _pack(recovered_bits, "MSB0") == source

    recovered_binary = "".join(str(bit) for bit in recovered_bits)
    native_carrier = encode_frame(recovered_binary)
    assert len(native_carrier.trits) == BALANCED_TRITS
    assert len(native_carrier.alphabet64) == BASE64_SEXTETS
    assert decode_frame(native_carrier) == recovered_binary
    assert bytes(int(recovered_binary[i:i + 8], 2)
                 for i in range(0, FRAME_BITS, 8)) == source
    assert source == sources[pattern]


def test_eight_outer_tensor_addresses_are_exhaustively_reversible() -> None:
    seen = set()
    for n in range(8):
        binary = f"{n:03b}"
        pair = encode_three_bits(binary)
        assert pair != HNAN_PAIR
        assert decode_two_trits(pair) == binary
        address, cell, expression = tensor_address_for_pair(pair)
        assert address == binary
        assert isinstance(cell, int) and 1 <= cell <= 9
        assert isinstance(expression, str) and expression
        assert tensor_cell_for_pair(pair) is not None
        seen.add(pair)
    assert len(seen) == 8
    assert HNAN_PAIR not in seen
    # Ninth state is the inherited center gate; binary-only decoding
    # must not coerce it to an arbitrary 3-bit word.
    from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import InvalidRadixState
    with pytest.raises(InvalidRadixState, match="HNAN_CENTER"):
        decode_two_trits(HNAN_PAIR)
    assert tensor_cell_for_pair(HNAN_PAIR) is not None
