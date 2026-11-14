"""Pass 220 V155: verify geometry-bearing GFX4 frame against inherited VM81.

This is a postcommit *binding witness*. The preadmitted V154 geometry is checked
against original bytes, exact draw-command identity, and the existing GFX4
dependency/replay verifier. It does not attest a native physical producer,
replace C11 packet validation, or mint receipts.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_installer.canonical import hash216, stable
from hhs_runtime.hhs_pass220_gfx4_decay_matrix_observation_v1 import (
    verify_decay_matrix_observation,
)
from hhs_runtime.hhs_pass220_v154_ordered_geometry_identity_v1 import (
    RESERVED_KEY, geometry_identity,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime

SCHEMA = "HHS_PASS_220_V155_GEOMETRY_GFX4_RECEIPT_BINDING_V1"
COMMAND_SCHEMA = "HHS_PASS_220_NATIVE_RENDER_COMMAND_MANIFEST_V1"
COMMAND_DOMAIN = "HHS-P220-NATIVE-RENDER-COMMANDS-V1"
DRAW_OPCODES = frozenset((14, 16))


class V155GeometryBindingError(ValueError):
    pass


def verify_geometry_gfx4_receipt_binding(
    *, vm81: VMRCRuntime, bundle: Mapping[str, Any],
    position_f32le: bytes, producer_tick: int,
    draw_resource_id: int, commands: Sequence[Mapping[str, Any]],
    matrix_bytes: bytes, scene_snapshot: Mapping[str, Any],
    resource_manifest: Mapping[str, Any], camera_state: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(vm81, VMRCRuntime):
        raise V155GeometryBindingError("V155_INHERITED_VM81_REQUIRED")
    if not isinstance(bundle, Mapping) or not isinstance(bundle.get("frame_state"), Mapping):
        raise V155GeometryBindingError("V155_FRAME_STATE_REQUIRED")
    frame = bundle["frame_state"]
    geom = frame.get(RESERVED_KEY)
    if not isinstance(geom, Mapping):
        raise V155GeometryBindingError("V155_GEOMETRY_NOT_BOUND")
    try:
        expected = geometry_identity(
            position_f32le=position_f32le,
            producer_tick=producer_tick,
            geometry_tick=producer_tick,
            render_tick=producer_tick,
            draw_resource_id=draw_resource_id,
            scene_resource_id=draw_resource_id,
            source_geometry_resource_id=draw_resource_id,
        )
    except (TypeError, ValueError) as exc:
        raise V155GeometryBindingError("V155_GEOMETRY_INPUT_REJECTED") from exc
    if dict(geom) != expected:
        raise V155GeometryBindingError("V155_GEOMETRY_CONTENT_OR_TICK_MISMATCH")
    if (not isinstance(commands, (list, tuple)) or len(commands) < 3 or
            any(not isinstance(item, Mapping) for item in commands)):
        raise V155GeometryBindingError("V155_COMMANDS_REQUIRED")
    normalized = []
    for command in commands:
        row = {}
        for key, default in (("opcode", None), ("flags", 0), ("resource_id", 0),
                             ("arg0", 0), ("arg1", 0)):
            val = command.get(key, default)
            if type(val) is not int or val < 0 or val > (1 << 64) - 1:
                raise V155GeometryBindingError("V155_COMMAND_TYPE_INVALID")
            row[key] = val
        if set(command) - set(row):
            raise V155GeometryBindingError("V155_COMMAND_EXTRA_FIELDS")
        normalized.append(row)
    if normalized[0]["opcode"] != 1 or normalized[-1]["opcode"] != 24:
        raise V155GeometryBindingError("V155_COMMAND_SEQUENCE_INVALID")
    if not any(c["opcode"] in DRAW_OPCODES and
               c["resource_id"] == draw_resource_id for c in normalized[1:-1]):
        raise V155GeometryBindingError("V155_BOUND_DRAW_RESOURCE_MISSING")
    manifest = {"schema": COMMAND_SCHEMA, "ordered": normalized}
    expected_root = hash216(stable(manifest), domain=COMMAND_DOMAIN)
    bound = frame.get("native_render_commands")
    if not isinstance(bound, Mapping) or dict(bound) != {
        "command_count": len(normalized),
        "ordered_command_root_hash216": expected_root,
        "schema": COMMAND_SCHEMA,
    }:
        raise V155GeometryBindingError("V155_COMMAND_MANIFEST_MISMATCH")
    # This inherited verification compares ordered matrix bytes, scene,
    # resource, camera and the entire frame_state to the committed VM81
    # dependency root, then verifies the live journal and replay witness.
    verification = verify_decay_matrix_observation(
        vm81=vm81, bundle=bundle, matrix_bytes=matrix_bytes,
        scene_snapshot=scene_snapshot, resource_manifest=resource_manifest,
        camera_state=camera_state,
    )
    if (verification.get("verified_live_vm81_commit") is not True or
            verification.get("verified_decay_matrix_binding") is not True):
        raise V155GeometryBindingError("V155_INHERITED_RECEIPT_REJECTED")
    return {
        "schema": SCHEMA,
        "frame_hash216": verification["frame_hash216"],
        "dependency_root_hash216": verification["dependency_root_hash216"],
        "geometry_hash216": expected["geometry_hash216"],
        "ordered_command_root_hash216": expected_root,
        "draw_resource_id": draw_resource_id,
        "verified_vm81_frame_binding": True,
        "verified_geometry_draw_binding": True,
        "physical_source_provenance_verified": False,
        "native_packet_execution_verified": False,
        "physics_mutation_authority": False,
    }
