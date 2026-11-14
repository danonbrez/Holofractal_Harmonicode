"""V154 regression: bit-exact ordered geometry remains non-authoritative."""
from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_v154_ordered_geometry_identity_v1 import (
    POSITION_BYTES, RESERVED_KEY, V154GeometryError,
    bind_geometry_frame_state, geometry_identity,
)


def candidate(data=None, **overrides):
    args = dict(
        position_f32le=bytes(POSITION_BYTES) if data is None else data,
        producer_tick=72, geometry_tick=72, render_tick=72,
        draw_resource_id=9, scene_resource_id=9,
        source_geometry_resource_id=9,
    )
    args.update(overrides)
    return geometry_identity(**args)


def test_ordered_content_and_signed_zero_are_distinct():
    zero = candidate()
    data = bytearray(POSITION_BYTES)
    data[3] = 0x80
    negative_zero = candidate(bytes(data))
    assert zero["geometry_hash216"] != negative_zero["geometry_hash216"]
    assert zero["position_sha256"] != negative_zero["position_sha256"]
    assert negative_zero["particle_count"] == 10368
    assert negative_zero["position_byte_length"] == 124416
    assert negative_zero["native_vm81_admission"] is False
    assert negative_zero["physical_source_provenance_verified"] is False


def test_tick_resource_and_shape_fail_closed():
    for changes in (
        {"producer_tick": -1},
        {"geometry_tick": 73},
        {"render_tick": 73},
        {"draw_resource_id": 0},
        {"scene_resource_id": 10},
        {"source_geometry_resource_id": 10},
        {"position_f32le": bytearray(POSITION_BYTES)},
        {"position_f32le": bytes(POSITION_BYTES - 4)},
    ):
        with pytest.raises(V154GeometryError):
            candidate(**changes)


def test_nonfinite_bits_rejected_and_tiny_subnormal_allowed():
    for bits in (0x7f800000, 0xff800000, 0x7fc00001):
        data = bytearray(POSITION_BYTES)
        data[0:4] = bits.to_bytes(4, "little")
        with pytest.raises(V154GeometryError, match="NONFINITE"):
            candidate(bytes(data))
    data = bytearray(POSITION_BYTES)
    data[0:4] = (1).to_bytes(4, "little")
    assert candidate(bytes(data))["producer_tick"] == 72


def test_binding_precedes_inherited_gfx4_without_new_authority():
    geometry = candidate()
    original = {"phase": {"numerator": 1, "denominator": 72}}
    bound = bind_geometry_frame_state(frame_state=original, geometry=geometry)
    assert original == {"phase": {"numerator": 1, "denominator": 72}}
    assert bound[RESERVED_KEY]["geometry_hash216"] == geometry["geometry_hash216"]
    assert bound[RESERVED_KEY]["native_vm81_admission"] is False
    with pytest.raises(V154GeometryError):
        bind_geometry_frame_state(frame_state=bound, geometry=geometry)
    for mutation in (
        {"native_vm81_admission": True},
        {"physical_source_provenance_verified": True},
        {"geometry_hash216": "0" * 216},
        {"draw_resource_id": 10},
        {"unexpected": "claim"},
    ):
        forged = {**geometry, **mutation}
        with pytest.raises(V154GeometryError):
            bind_geometry_frame_state(frame_state=original, geometry=forged)
