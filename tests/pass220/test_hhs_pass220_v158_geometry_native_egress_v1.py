"""V158: actual sealed Pass179 packet + ordered geometry bytes egress."""
from __future__ import annotations

from base64 import b64decode
from copy import deepcopy

import pytest

from hhs_installer.canonical import hash216, stable
from hhs_runtime.hhs_pass220_gfx4_decay_matrix_observation_v1 import (
    admit_decay_matrix_observation,
)
from hhs_runtime.hhs_pass220_native_observation_export_v1 import C11_LIBRARY
from hhs_runtime.hhs_pass220_v154_ordered_geometry_identity_v1 import (
    POSITION_BYTES, bind_geometry_frame_state, geometry_identity,
)
from hhs_runtime.hhs_pass220_v155_geometry_gfx4_receipt_binding_v1 import (
    COMMAND_DOMAIN, COMMAND_SCHEMA, V155GeometryBindingError,
)
from hhs_runtime.hhs_pass220_v158_geometry_native_egress_v1 import (
    V158GeometryEgressError, export_receipt_bound_geometry,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime


def admitted():
    vm81 = VMRCRuntime()
    raw = bytearray(POSITION_BYTES)
    raw[3] = 0x80
    positions = bytes(raw)
    commands = [
        {"opcode": 1}, {"opcode": 3, "resource_id": 7},
        {"opcode": 14, "resource_id": 9}, {"opcode": 24},
    ]
    normalized = [
        {k: c.get(k, 0) for k in ("opcode", "flags", "resource_id", "arg0", "arg1")}
        for c in commands
    ]
    command_root = hash216(
        stable({"schema": COMMAND_SCHEMA, "ordered": normalized}),
        domain=COMMAND_DOMAIN,
    )
    geom = geometry_identity(
        position_f32le=positions, producer_tick=9,
        geometry_tick=9, render_tick=9, draw_resource_id=9,
        scene_resource_id=9, source_geometry_resource_id=9,
    )
    frame = bind_geometry_frame_state(
        frame_state={"native_render_commands": {
            "schema": COMMAND_SCHEMA, "command_count": 4,
            "ordered_command_root_hash216": command_root,
        }}, geometry=geom,
    )
    matrix = b"abcd"
    scene = {"scene": "v158-test"}
    resources = {"geometry": "point-field", "resource_id": 9}
    camera = {"kind": "perspective"}
    bundle = admit_decay_matrix_observation(
        vm81=vm81, matrix_bytes=matrix, matrix_byte_length=4,
        matrix_version=1, scene_snapshot=scene,
        frame_state=frame, resource_manifest=resources,
        camera_state=camera, frame_index=9, exact_time_num=9,
        exact_time_den=120,
    )
    return dict(
        vm81=vm81, bundle=bundle, position_f32le=positions,
        producer_tick=9, draw_resource_id=9, commands=commands,
        matrix_bytes=matrix, scene_snapshot=scene,
        resource_manifest=resources, camera_state=camera,
        target_width=64, target_height=32,
    )


def test_sealed_packet_and_exact_geometry_egress_without_second_commit():
    assert C11_LIBRARY.is_file()
    args = admitted()
    epoch = args["vm81"].epoch
    exported = export_receipt_bound_geometry(**args)
    assert args["vm81"].epoch == epoch
    assert exported["native_vm81_frame_binding_verified"] is True
    assert exported["native_packet_sealed_and_validated"] is True
    assert exported["physical_source_provenance_verified"] is False
    assert exported["native_geometry_execution_verified"] is False
    assert b64decode(exported["position_base64"], validate=True) == args["position_f32le"]
    packet = b64decode(exported["packet_base64"], validate=True)
    assert packet[:8] == b"HHS179C1"
    assert packet[296:512].decode("ascii") == exported["frame_hash216"]
    assert exported["position_byte_length"] == 124416
    assert exported["draw_resource_id"] == 9


def test_changed_ordered_bytes_and_false_draw_rejected():
    args = admitted()
    changed = bytearray(args["position_f32le"])
    changed[3] = 0  # change negative zero into positive zero
    with pytest.raises(V155GeometryBindingError):
        export_receipt_bound_geometry(**{**args, "position_f32le": bytes(changed)})
    with pytest.raises(V155GeometryBindingError):
        export_receipt_bound_geometry(**{**args, "draw_resource_id": 10})
    with pytest.raises(V158GeometryEgressError, match="TARGET_BOUNDS"):
        export_receipt_bound_geometry(**{**args, "target_width": 0})
    assert args["vm81"].epoch == 1


def test_tampered_precommit_manifest_rejected():
    args = admitted()
    altered = deepcopy(args["bundle"])
    altered["frame_state"]["native_render_commands"]["command_count"] = 99
    with pytest.raises(V155GeometryBindingError):
        export_receipt_bound_geometry(**{**args, "bundle": altered})
    assert args["vm81"].epoch == 1
