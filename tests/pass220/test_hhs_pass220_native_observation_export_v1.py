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
