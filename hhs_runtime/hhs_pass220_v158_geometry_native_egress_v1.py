"""Pass 220 V158 — receipt-bound ordered geometry packet egress.

A trusted server-side *caller* supplies the VMRC instance and its already
admitted GFX4 bundle, not a browser-supplied admission object. V155 verifies
the receipt, geometry bytes, resource, command root and decay binding. Pass179
C11 then creates and validates the corresponding sealed native packet.

This module does not attest the physical producer or expose an API route:
that requires separately verified native producer / Lane 5 ownership.
"""
from __future__ import annotations

from base64 import b64encode
from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_native_observation_export_v1 import (
    _native_packet, _preflight_commands,
)
from hhs_runtime.hhs_pass220_v155_geometry_gfx4_receipt_binding_v1 import (
    verify_geometry_gfx4_receipt_binding,
)
from hhs_runtime.hhs_pass220_v154_ordered_geometry_identity_v1 import POSITION_BYTES
from hhs_runtime.pass163.vmrc import VMRCRuntime

SCHEMA = "HHS_PASS_220_V158_ORDERED_GEOMETRY_NATIVE_EGRESS_V1"


class V158GeometryEgressError(ValueError):
    pass


def export_receipt_bound_geometry(
    *, vm81: VMRCRuntime, bundle: Mapping[str, Any],
    position_f32le: bytes, producer_tick: int,
    draw_resource_id: int, commands: Sequence[Mapping[str, Any]],
    matrix_bytes: bytes, scene_snapshot: Mapping[str, Any],
    resource_manifest: Mapping[str, Any], camera_state: Mapping[str, Any],
    target_width: int, target_height: int,
) -> dict[str, Any]:
    if not isinstance(vm81, VMRCRuntime):
        raise V158GeometryEgressError("V158_EXISTING_VM81_REQUIRED")
    if not isinstance(bundle, Mapping) or not isinstance(bundle.get("identity"), Mapping):
        raise V158GeometryEgressError("V158_ADMITTED_BUNDLE_REQUIRED")
    if type(position_f32le) is not bytes or len(position_f32le) != POSITION_BYTES:
        raise V158GeometryEgressError("V158_ORDERED_BYTES_REQUIRED")
    if type(target_width) is not int or type(target_height) is not int or not (
        1 <= target_width <= 16384 and 1 <= target_height <= 16384
    ):
        raise V158GeometryEgressError("V158_TARGET_BOUNDS")
    if not isinstance(commands, (list, tuple)):
        raise V158GeometryEgressError("V158_COMMANDS_REQUIRED")
    # The exact Pass179/native sequence gate executes before any packet build.
    _preflight_commands(list(commands))
    proof = verify_geometry_gfx4_receipt_binding(
        vm81=vm81, bundle=bundle, position_f32le=position_f32le,
        producer_tick=producer_tick, draw_resource_id=draw_resource_id,
        commands=commands, matrix_bytes=matrix_bytes,
        scene_snapshot=scene_snapshot, resource_manifest=resource_manifest,
        camera_state=camera_state,
    )
    identity = bundle["identity"]
    if identity.get("frame_hash216") != proof["frame_hash216"]:
        raise V158GeometryEgressError("V158_FRAME_IDENTITY_MISMATCH")
    index, num, den = (
        bundle.get("frameIndex"), bundle.get("timeNum"), bundle.get("timeDen")
    )
    if (type(index) is not int or type(num) is not int or
            type(den) is not int or index < 0 or
            not -(1 << 63) <= num < (1 << 63) or
            not 0 < den < (1 << 64)):
        raise V158GeometryEgressError("V158_EXACT_TIME_INVALID")
    # Inherited native C11 builder validates and seals the actual packet.
    packet = _native_packet(
        identity, frame_index=index, time_num=num, time_den=den,
        width=target_width, height=target_height, commands=list(commands),
    )
    payload = bytes(position_f32le)
    return {
        "schema": SCHEMA,
        "source_classification": "RECEIPT_BOUND_GEOMETRY_PROJECTION",
        "physical_source_provenance_verified": False,
        "native_vm81_frame_binding_verified": True,
        "native_packet_sealed_and_validated": True,
        "native_geometry_execution_verified": False,
        "frame_hash216": proof["frame_hash216"],
        "dependency_root_hash216": proof["dependency_root_hash216"],
        "geometry_hash216": proof["geometry_hash216"],
        "command_manifest_hash216": proof["ordered_command_root_hash216"],
        "producer_tick": producer_tick,
        "draw_resource_id": draw_resource_id,
        "particle_count": 10368,
        "position_byte_length": POSITION_BYTES,
        "position_sha256": sha256(payload).hexdigest(),
        "position_base64": b64encode(payload).decode("ascii"),
        "packet_base64": b64encode(packet).decode("ascii"),
        "physics_mutation_authority": False,
        "vm81_mutation_authority": False,
    }
