"""Exact Pass 220 I001 rational-offset <-> native C VM81 frame regression.

Tests run ONLY after building the real C ABI. No authority is borrowed from
synthetic frame bytes or used to commit any native state.
"""
from __future__ import annotations

import struct

import pytest

from hhs_backend.runtime.hhs_lane5_exact_offset_vm81_codec_v1 import (
    NativeOffsetFrameError,
    from_canonical_offset_object,
    from_native_offset_frame,
    assert_bidirectional_offset_identity,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    serialize_offsets_5184,
    deserialize_offsets_5184,
    offsets_to_bigint,
    bigint_to_offsets,
)


@pytest.mark.parametrize("offsets", [
    (0,) * 81,
    (8,) * 81,
    tuple(i % 9 for i in range(81)),
    tuple(8 - i % 9 for i in range(81)),
    tuple(0 if i != 80 else 8 for i in range(81)),
])
def test_original_i001_roundtrips_through_actual_native_c_frame(offsets):
    source = serialize_offsets_5184(offsets)
    carrier = assert_bidirectional_offset_identity(source)
    assert carrier.canonical_5184 == source
    assert len(source) == 5184
    assert len(carrier.raw_frame_le) == 648
    assert tuple(struct.unpack("<81Q", carrier.raw_frame_le)) == offsets
    assert carrier.offsets == offsets
    assert bigint_to_offsets(offsets_to_bigint(offsets)) == offsets
    assert deserialize_offsets_5184(carrier.canonical_5184) == offsets
    public = carrier.public_status()
    assert public["exact_profile_roundtrip_verified"] is True
    assert public["universal_tensor_codec_claimed"] is False
    assert public["source_state_exposed"] is False
    assert public["canonical_vm81_mutation_authority"] is False
    assert "raw_frame_le" not in public
    assert "canonical_5184" not in public


def test_full_81_position_address_provenance_is_not_reordered():
    positions = tuple((i * 7 + 2) % 9 for i in range(81))
    carrier = assert_bidirectional_offset_identity(serialize_offsets_5184(positions))
    assert list(struct.unpack("<81Q", carrier.raw_frame_le)) == list(positions)


@pytest.mark.parametrize("raw,reason", [
    (b"\x00" * 647, "exactly 648 bytes"),
    (b"\x00" * 649, "exactly 648 bytes"),
    (struct.pack("<81Q", *([0] * 80 + [9])), "outside I001"),
    (struct.pack("<81Q", *([0] * 80 + [(1 << 64) - 1])), "outside I001"),
])
def test_refuse_unsupported_or_lossy_native_binary_egress(raw, reason):
    with pytest.raises(NativeOffsetFrameError, match=reason):
        from_native_offset_frame(raw)


def test_refuse_equivalent_but_noncanonical_rational_spelling():
    source = serialize_offsets_5184((1,) * 81)
    # Correct rational value but different scientific exponent and numerator.
    # I001 canonicalizer must reject rather than erase the source spelling.
    alternative = "+00000000000000000010/00000000000000000001e-00000000000000000001"
    assert len(alternative) == 64
    modified = alternative + source[64:]
    assert deserialize_offsets_5184(modified) == (1,) * 81
    with pytest.raises(NativeOffsetFrameError, match="noncanonical"):
        from_canonical_offset_object(modified)


def test_refuse_zero_denominator_and_non_offset_rationals():
    good = serialize_offsets_5184((0,) * 81)
    invalid = good[:22] + "0" * 20 + good[42:]
    with pytest.raises(NativeOffsetFrameError, match="not a valid I001"):
        from_canonical_offset_object(invalid)
    non_offset = "+00000000000000000009/00000000000000000001e+00000000000000000000"
    assert len(non_offset) == 64
    with pytest.raises(NativeOffsetFrameError, match="not a valid I001"):
        from_canonical_offset_object(non_offset + good[64:])


@pytest.mark.parametrize("invalid", ["", "0" * 5183, "0" * 5185, 0.1, None])
def test_refuse_wrong_width_or_ordinary_float_input(invalid):
    with pytest.raises(NativeOffsetFrameError, match="5184-character"):
        from_canonical_offset_object(invalid)
