"""Native GFX4 admission of fixed-size ordered decay-matrix observations.

Extends the inherited GFX4 constructor by composition: the observed matrix
content identity and exact version are embedded in the *admitted* frame_state,
not attached by browser assertions. Uses inherited Hash216, VMRC and GFX4.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping

from hhs_installer.canonical import hash216
from hhs_runtime.hhs_pass220_gfx4_vm81_graphics_packet_identity_v1 import (
    build_vm81_admitted_graphics_packet_identity,
)
from hhs_runtime.hhs_pass220_gfx4_observation_witness_v1 import (
    verify_gfx4_vm81_observation_witness,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime

SCHEMA = "HHS_PASS_220_GFX4_DECAY_MATRIX_OBSERVATION_V1"
DECAY_DOMAIN = "HHS-P220-GFX4-ORDERED-DECAY-MATRIX-V1"


class GFX4DecayObservationError(ValueError):
    pass


def _matrix_bytes(value: bytes | bytearray | memoryview, *, byte_length: int) -> bytes:
    if type(byte_length) is not int or byte_length <= 0:
        raise GFX4DecayObservationError("P220_DECAY_FIXED_SIZE_REQUIRED")
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise GFX4DecayObservationError("P220_DECAY_SERIALIZED_BYTES_REQUIRED")
    raw = bytes(value)
    if len(raw) != byte_length:
        raise GFX4DecayObservationError("P220_DECAY_FIXED_SIZE_MISMATCH")
    return raw


def decay_matrix_identity(raw: bytes, *, matrix_version: int, byte_length: int) -> dict[str, Any]:
    if type(matrix_version) is not int or matrix_version < 0:
        raise GFX4DecayObservationError("P220_DECAY_EXACT_VERSION_REQUIRED")
    data = _matrix_bytes(raw, byte_length=byte_length)
    digest = sha256(data).hexdigest()
    # Hash216 uses the existing native canonical domain-separated constructor.
    native_hash216 = hash216(
        {"schema": SCHEMA, "matrix_version": matrix_version,
         "byte_length": byte_length, "ordered_bytes_hex": data.hex()},
        domain=DECAY_DOMAIN,
    )
    return {
        "schema": SCHEMA,
        "matrix_version": matrix_version,
        "byte_length": byte_length,
        "content_sha256": digest,
        "decay_hash216": native_hash216,
    }


def admit_decay_matrix_observation(
    *,
    vm81: VMRCRuntime,
    matrix_bytes: bytes | bytearray | memoryview,
    matrix_byte_length: int,
    matrix_version: int,
    scene_snapshot: Mapping[str, Any],
    frame_state: Mapping[str, Any],
    resource_manifest: Mapping[str, Any],
    camera_state: Mapping[str, Any],
    frame_index: int,
    exact_time_num: int,
    exact_time_den: int,
    prior_frame_hash216: str | None = None,
) -> dict[str, Any]:
    """Admit a frame whose own native dependency root includes decay content.

    The matrix is observational input; this does not mutate or invent the
    decay-pool physics, nor does it allocate a second VM81 runtime.
    """
    if not isinstance(vm81, VMRCRuntime):
        raise GFX4DecayObservationError("P220_DECAY_INHERITED_VM81_REQUIRED")
    if not isinstance(frame_state, Mapping):
        raise GFX4DecayObservationError("P220_DECAY_FRAME_STATE_REQUIRED")
    if "decay_matrix_observation" in frame_state:
        raise GFX4DecayObservationError("P220_DECAY_OBSERVATION_COLLISION")
    observation = decay_matrix_identity(
        matrix_bytes, matrix_version=matrix_version,
        byte_length=matrix_byte_length,
    )
    bound_frame_state = dict(frame_state)
    bound_frame_state["decay_matrix_observation"] = observation
    identity = build_vm81_admitted_graphics_packet_identity(
        vm81=vm81,
        scene_snapshot=scene_snapshot,
        frame_state=bound_frame_state,
        resource_manifest=resource_manifest,
        camera_state=camera_state,
        frame_index=frame_index,
        exact_time_num=exact_time_num,
        exact_time_den=exact_time_den,
        prior_frame_hash216=prior_frame_hash216,
    )
    witness = verify_gfx4_vm81_observation_witness(vm81=vm81, identity=identity)
    return {
        "schema": SCHEMA,
        "classification": identity["classification"],
        "identity": identity,
        "observation": observation,
        "frame_state": bound_frame_state,
        "witness": witness,
        "nativeAdmission": True,
        "decayHash216": observation["decay_hash216"],
        "matrixVersion": matrix_version,
        "frameHash216": identity["frame_hash216"],
        "frameIndex": frame_index,
        "timeNum": exact_time_num,
        "timeDen": exact_time_den,
        "canonical_mutation_authority": False,
    }
