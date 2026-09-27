from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass220_gfx4_vm81_graphics_packet_identity_v1 import (
    CLASSIFICATION,
    GFX4GraphicsIdentityError,
    build_vm81_admitted_graphics_packet_identity,
    gfx4_vm81_graphics_packet_identity_self_test,
    packet_identity_bytes,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime


def _kwargs():
    return {
        "scene_snapshot": {
            "scene_id": "test-scene",
            "node_count": 5184,
            "layout": [72, 72],
        },
        "frame_state": {
            "tick": 9,
            "phase": {"numerator": 9, "denominator": 144},
        },
        "resource_manifest": {
            "geometry": "HHS_NATIVE_5184_POINT_FIELD",
            "postprocess": "HHS_NATIVE_RGBA8_COMPOSITOR",
        },
        "camera_state": {
            "kind": "perspective",
            "fov": {"numerator": 62, "denominator": 1},
            "position": [0, 0, 128],
        },
        "frame_index": 9,
        "exact_time_num": 9,
        "exact_time_den": 60,
    }


def test_gfx4_vm81_admitted_packet_identity_advances_singleton_authority():
    vm81 = VMRCRuntime()
    before_hash72 = vm81.state_hash72
    identity = build_vm81_admitted_graphics_packet_identity(
        vm81=vm81,
        **_kwargs(),
    )
    assert identity["classification"] == CLASSIFICATION
    assert identity["packet_identity_vm81_admitted"] is True
    assert identity["packet_compatibility_unadmitted"] is False
    assert identity["singleton_vm81_authority"] is True
    assert identity["independent_vm81_authority"] is False
    assert len(identity["scene_snapshot_hash216"]) == 216
    assert len(identity["frame_hash216"]) == 216
    assert len(identity["resource_manifest_hash216"]) == 216
    assert len(identity["camera_hash72"]) == 72
    assert len(identity["packet_identity_hash216"]) == 216
    assert vm81.epoch == 1
    assert vm81.state_hash72 != before_hash72
    admission = identity["vm81_admission"]
    assert len(admission["receipt_hash72"]) == 72
    assert len(admission["operation_hash216"]) == 216
    assert admission["output_hash72"] == vm81.state_hash72


def test_gfx4_identity_is_replay_deterministic_from_equal_vm81_genesis():
    a = build_vm81_admitted_graphics_packet_identity(
        vm81=VMRCRuntime(),
        **_kwargs(),
    )
    b = build_vm81_admitted_graphics_packet_identity(
        vm81=VMRCRuntime(),
        **_kwargs(),
    )
    for key in (
        "scene_snapshot_hash216",
        "frame_hash216",
        "resource_manifest_hash216",
        "camera_hash72",
        "packet_identity_hash216",
    ):
        assert a[key] == b[key]
    assert a["vm81_admission"]["receipt_hash72"] == b["vm81_admission"]["receipt_hash72"]
    assert a["vm81_admission"]["operation_hash216"] == b["vm81_admission"]["operation_hash216"]


def test_gfx4_packet_identity_bytes_match_native_wasm_slot_widths():
    identity = build_vm81_admitted_graphics_packet_identity(
        vm81=VMRCRuntime(),
        **_kwargs(),
    )
    lanes = packet_identity_bytes(identity)
    assert len(lanes["scene"]) == 216
    assert len(lanes["frame"]) == 216
    assert len(lanes["prior"]) == 216
    assert len(lanes["resources"]) == 216
    assert len(lanes["camera"]) == 72


def test_gfx4_rejects_float_descriptor_before_vm81_mutation():
    vm81 = VMRCRuntime()
    kwargs = _kwargs()
    kwargs["camera_state"] = {
        "kind": "perspective",
        "fov": 62.0,
        "position": [0, 0, 128],
    }
    with pytest.raises(Exception):
        build_vm81_admitted_graphics_packet_identity(vm81=vm81, **kwargs)
    assert vm81.epoch == 0


def test_gfx4_rejects_invalid_time_before_vm81_mutation():
    vm81 = VMRCRuntime()
    kwargs = _kwargs()
    kwargs["exact_time_den"] = 0
    with pytest.raises(GFX4GraphicsIdentityError, match="TIME_DENOMINATOR"):
        build_vm81_admitted_graphics_packet_identity(vm81=vm81, **kwargs)
    assert vm81.epoch == 0


def test_gfx4_self_test_closes():
    receipt = gfx4_vm81_graphics_packet_identity_self_test()
    assert receipt["status"] == "PASS"
    assert receipt["deterministic_replay"] is True
    assert receipt["packet_compatibility_unadmitted"] is False
    assert receipt["scene_bytes"] == 216
    assert receipt["camera_bytes"] == 72
