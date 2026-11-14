"""V155 exact native GFX4 geometry/command/replay binding regressions."""
from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_installer.canonical import hash216, stable
from hhs_runtime.hhs_pass220_gfx4_decay_matrix_observation_v1 import (
    admit_decay_matrix_observation,
)
from hhs_runtime.hhs_pass220_v154_ordered_geometry_identity_v1 import (
    POSITION_BYTES, bind_geometry_frame_state, geometry_identity,
)
from hhs_runtime.hhs_pass220_v155_geometry_gfx4_receipt_binding_v1 import (
    COMMAND_DOMAIN, COMMAND_SCHEMA, V155GeometryBindingError,
    verify_geometry_gfx4_receipt_binding,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime


def fixture():
    vm81 = VMRCRuntime()
    positions = bytes(POSITION_BYTES)
    commands = [
        {"opcode": 1}, {"opcode": 3, "resource_id": 7},
        {"opcode": 14, "resource_id": 9}, {"opcode": 24},
    ]
    normalized = [
        {k: c.get(k, 0) for k in ("opcode", "flags", "resource_id", "arg0", "arg1")}
        for c in commands
    ]
    root = hash216(stable({"schema": COMMAND_SCHEMA, "ordered": normalized}),
                   domain=COMMAND_DOMAIN)
    geometry = geometry_identity(
        position_f32le=positions, producer_tick=9, geometry_tick=9,
        render_tick=9, draw_resource_id=9, scene_resource_id=9,
        source_geometry_resource_id=9,
    )
    frame = bind_geometry_frame_state(frame_state={
        "native_render_commands": {
            "schema": COMMAND_SCHEMA, "command_count": len(commands),
            "ordered_command_root_hash216": root,
        }
    }, geometry=geometry)
    scene = {"scene": "v155-snapshot"}
    resources = {"geometry": "v155-point-field", "resource_id": 9}
    camera = {"kind": "perspective"}
    matrix = bytes((1, 2, 3, 4))
    bundle = admit_decay_matrix_observation(
        vm81=vm81, matrix_bytes=matrix, matrix_byte_length=len(matrix),
        matrix_version=1, scene_snapshot=scene, frame_state=frame,
        resource_manifest=resources, camera_state=camera,
        frame_index=9, exact_time_num=9, exact_time_den=120,
    )
    kwargs = dict(vm81=vm81, bundle=bundle, position_f32le=positions,
                  producer_tick=9, draw_resource_id=9, commands=commands,
                  matrix_bytes=matrix, scene_snapshot=scene,
                  resource_manifest=resources, camera_state=camera)
    return kwargs


def test_live_receipt_binds_v154_geometry_and_exact_draw_manifest():
    kw = fixture()
    before = kw["vm81"].epoch
    proof = verify_geometry_gfx4_receipt_binding(**kw)
    assert kw["vm81"].epoch == before
    assert proof["verified_vm81_frame_binding"] is True
    assert proof["verified_geometry_draw_binding"] is True
    assert proof["physical_source_provenance_verified"] is False
    assert proof["native_packet_execution_verified"] is False
    assert len(proof["geometry_hash216"]) == 216


def test_geometry_bytes_tick_and_resource_tampering_rejected():
    kw = fixture()
    changed = bytearray(kw["position_f32le"])
    changed[3] = 0x80  # negative zero must change source identity
    for altered in (
        {"position_f32le": bytes(changed)},
        {"producer_tick": 10},
        {"draw_resource_id": 10},
        {"commands": [{"opcode": 1}, {"opcode": 3, "resource_id": 7},
                      {"opcode": 14, "resource_id": 10}, {"opcode": 24}]},
    ):
        with pytest.raises(V155GeometryBindingError):
            verify_geometry_gfx4_receipt_binding(**{**kw, **altered})


def test_manifest_and_vm81_commit_tampering_fail_closed():
    kw = fixture()
    forged = deepcopy(kw["bundle"])
    forged["frame_state"]["native_render_commands"]["command_count"] = 5
    with pytest.raises(V155GeometryBindingError, match="COMMAND_MANIFEST"):
        verify_geometry_gfx4_receipt_binding(**{**kw, "bundle": forged})
    forged = deepcopy(kw["bundle"])
    forged["frame_state"]["fake"] = 1
    with pytest.raises(ValueError, match="DEPENDENCY_MISMATCH"):
        verify_geometry_gfx4_receipt_binding(**{**kw, "bundle": forged})


def test_missing_draw_and_fake_unchanged_geometry_rejected():
    kw = fixture()
    no_draw = [{"opcode": 1}, {"opcode": 3, "resource_id": 7}, {"opcode": 24}]
    with pytest.raises(V155GeometryBindingError, match="BOUND_DRAW_RESOURCE_MISSING"):
        verify_geometry_gfx4_receipt_binding(**{**kw, "commands": no_draw})
    forged = deepcopy(kw["bundle"])
    forged["frame_state"]["ordered_physical_geometry_observation"]["native_vm81_admission"] = True
    with pytest.raises(V155GeometryBindingError, match="GEOMETRY_CONTENT"):
        verify_geometry_gfx4_receipt_binding(**{**kw, "bundle": forged})
