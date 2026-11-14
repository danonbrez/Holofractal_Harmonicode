from __future__ import annotations

import base64
import ctypes
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass220_native_observation_export_v1 import (
    C11_LIBRARY,
    Init,
    Command,
    NativeObservationExportError,
    _native_packet,
    _preflight_commands,
    native_observation_export,
)


def _identity():
    return {
        "classification": "HHS_PASS_220_GFX4_GRAPHICS_FRAME_VM81_ADMITTED",
        "packet_identity_vm81_admitted": True,
        "scene_snapshot_hash216": "a" * 216,
        "frame_hash216": "b" * 216,
        "prior_frame_hash216": "",
        "resource_manifest_hash216": "c" * 216,
        "camera_hash72": "d" * 72,
    }


def test_ctypes_layout_and_native_shared_library_exists():
    assert ctypes.sizeof(Command) == 32
    assert ctypes.sizeof(Init) >= 1016
    assert C11_LIBRARY.is_file()


def test_c11_native_packet_round_trip_and_identity_lanes():
    raw = _native_packet(
        _identity(), frame_index=9, time_num=9, time_den=120,
        width=128, height=64,
        commands=[{"opcode": 1}, {"opcode": 24}],
    )
    assert raw[:8] == b"HHS179C1"
    assert len(raw) == 1088 + 2 * 32
    assert raw[80:296] == b"a" * 216
    assert raw[296:512] == b"b" * 216
    assert raw[512:728] == bytes(216)
    assert raw[728:944] == b"c" * 216
    assert raw[944:1016] == b"d" * 72
    assert int.from_bytes(raw[32:36], "little") & 1  # sealed
    assert not (int.from_bytes(raw[32:36], "little") & 4)  # admitted


@pytest.mark.parametrize("commands,classification", [
    ([{"opcode": 24}, {"opcode": 1}], "COMMAND_SEQUENCE"),
    ([{"opcode": 1}, {"opcode": 3}, {"opcode": 24}], "RESOURCE_REQUIRED"),
    ([{"opcode": 1}, {"opcode": 19}, {"opcode": 24}], "COMMAND_SEQUENCE"),
    ([{"opcode": 1}, {"opcode": 21}, {"opcode": 24}], "COMMAND_SEQUENCE"),
    ([{"opcode": 1}, {"opcode": 1}, {"opcode": 24}], "COMMAND_SEQUENCE"),
    ([{"opcode": 1}, {"opcode": 25}, {"opcode": 24}], "EXACT_OPCODE"),
    ([{"opcode": 1}, {"opcode": 24, "arg0": -1}], "EXACT_ARG0"),
])
def test_invalid_command_rejected_before_mutation(commands, classification):
    with pytest.raises(NativeObservationExportError, match=classification):
        _preflight_commands(commands)


def test_browser_may_not_supply_native_receipt():
    with pytest.raises(NativeObservationExportError, match="CLIENT_AUTHORITY_CLAIM"):
        native_observation_export({"identity": {"forged": True}})


def test_noncanonical_matrix_egress_fails_closed():
    with pytest.raises(NativeObservationExportError, match="MATRIX_NONCANONICAL"):
        native_observation_export({"matrix_hex": "ABCD"})


def test_guarded_native_export_admits_decayed_observation_and_emits_sealed_c11_packet():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    result = native_observation_export({
        "matrix_hex": "010200ff",
        "matrix_byte_length": 4,
        "matrix_version": before + 1,
        "scene_snapshot": {"scene_id": "p220-native-egress-test"},
        "frame_state": {"physics_tick": before + 1},
        "resource_manifest": {"type": "rgba8"},
        "camera_state": {"kind": "perspective", "z": 128},
        "frame_index": before + 1,
        "exact_time_num": before + 1,
        "exact_time_den": 120,
        "target_width": 64,
        "target_height": 64,
        "commands": [{"opcode": 1}, {"opcode": 24}],
    })
    assert VMRC.epoch == before + 1
    assert result["schema"] == "HHS_PASS_220_NATIVE_OBSERVATION_EGRESS_V1"
    assert result["native_receipt_verified"] is True
    assert result["native_decay_binding_verified"] is True
    assert result["packet_identity_verified"] is True
    assert result["command_manifest_bound_before_vm81_admission"] is True
    assert len(result["command_manifest_hash216"]) == 216
    packet = base64.b64decode(result["observation"]["packet_base64"], validate=True)
    assert packet[:8] == b"HHS179C1"
    assert packet[296:512].decode("ascii") == result["observation"]["frameHash216"]
    assert int.from_bytes(packet[56:64], "little") == result["observation"]["frameIndex"]
    assert int.from_bytes(packet[64:72], "little") == result["observation"]["timeNum"]
    assert int.from_bytes(packet[72:80], "little") == result["observation"]["timeDen"]
    assert int.from_bytes(packet[32:36], "little") & 4 == 0


def test_native_snapshot_source_is_server_owned_and_bound_to_existing_vmrc():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    result = native_observation_export({
        "source_mode": "VMRC_RAW5184_SNAPSHOT",
        "scene_snapshot": {"scene_id": "p220-server-owned-observation"},
        "frame_state": {"camera_phase": 1},
        "resource_manifest": {"format": "rgba8"},
        "camera_state": {"kind": "perspective"},
        "target_width": 64,
        "target_height": 64,
        "commands": [{"opcode": 1}, {"opcode": 24}],
    })
    assert result["native_source_verified"] is True
    assert result["observation_source"] == "VMRC_RAW5184_SNAPSHOT"
    assert result["physical_decay_pool_provenance"] is False
    assert result["native_receipt_verified"] is True
    assert result["native_decay_binding_verified"] is True
    assert VMRC.epoch == before + 1
    assert result["observation"]["matrixVersion"] == before


def test_native_snapshot_rejects_client_supplied_matrix_bytes_before_commit():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    with pytest.raises(NativeObservationExportError, match="CLIENT_MATRIX_OVERRIDE"):
        native_observation_export({
            "source_mode": "VMRC_RAW5184_SNAPSHOT",
            "matrix_hex": "aabb",
        })
    assert VMRC.epoch == before


def test_client_matrix_is_diagnostic_not_verified_producer():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    result = native_observation_export({
        "source_mode": "CLIENT_MATRIX_DIAGNOSTIC",
        "matrix_hex": "010200ff",
        "matrix_byte_length": 4,
        "matrix_version": before + 1,
        "scene_snapshot": {"scene_id": "p220-client-diagnostic"},
        "frame_state": {"physics_tick": before + 1},
        "resource_manifest": {"format": "rgba8"},
        "camera_state": {"kind": "perspective"},
        "frame_index": before + 1,
        "exact_time_num": before + 1,
        "exact_time_den": 120,
        "target_width": 64,
        "target_height": 64,
        "commands": [{"opcode": 1}, {"opcode": 24}],
    })
    assert result["native_source_verified"] is False
    assert result["observation_source"] == "CLIENT_MATRIX_DIAGNOSTIC"
    assert result["physical_decay_pool_provenance"] is False


def test_native_snapshot_rejects_untrusted_display_time():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    with pytest.raises(NativeObservationExportError, match="CLIENT_TIMESTAMP_OVERRIDE"):
        native_observation_export({
            "source_mode": "VMRC_RAW5184_SNAPSHOT",
            "frame_index": 999,
        })
    assert VMRC.epoch == before


def test_native_render_command_order_changes_admitted_gfx4_frame_identity():
    from hhs_runtime.hhs_pass220_native_observation_export_v1 import native_observation_export
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    args = dict(
        source_mode="CLIENT_MATRIX_DIAGNOSTIC",
        matrix_hex="01020304",
        matrix_byte_length=4,
        scene_snapshot={"scene": "native-ordered-command-proof"},
        frame_state={"tick": 3},
        resource_manifest={"type": "points"},
        camera_state={"kind": "perspective"},
        exact_time_den=120,
        target_width=64,
        target_height=64,
    )
    before = VMRC.epoch
    one = native_observation_export({
        **args, "matrix_version":before+1, "frame_index":1,
        "exact_time_num":1,
        "commands":[{"opcode":1}, {"opcode":2,"arg0":32,"arg1":64},{"opcode":24}],
    })
    two = native_observation_export({
        **args, "matrix_version":before+2, "frame_index":2,
        "exact_time_num":2,
        "commands":[{"opcode":1}, {"opcode":2,"arg0":64,"arg1":32},{"opcode":24}],
    })
    assert one["command_manifest_hash216"] != two["command_manifest_hash216"]
    assert one["observation"]["frameHash216"] != two["observation"]["frameHash216"]
    assert one["command_manifest_bound_before_vm81_admission"] is True


def test_reserved_frame_command_manifest_cannot_be_overridden_before_mutation():
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    before = VMRC.epoch
    with pytest.raises(NativeObservationExportError, match="FRAME_STATE_MANIFEST_COLLISION"):
        native_observation_export({
            "source_mode":"CLIENT_MATRIX_DIAGNOSTIC",
            "matrix_hex":"01020304", "matrix_byte_length":4,
            "matrix_version":before + 1,
            "scene_snapshot":{},
            "frame_state":{"native_render_commands":{"forged":True}},
            "resource_manifest":{}, "camera_state":{},
            "frame_index":1, "exact_time_num":1, "exact_time_den":120,
            "target_width":64, "target_height":64,
            "commands":[{"opcode":1},{"opcode":24}],
        })
    assert VMRC.epoch == before
