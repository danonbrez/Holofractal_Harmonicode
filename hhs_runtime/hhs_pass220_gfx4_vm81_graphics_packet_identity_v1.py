"""Pass 220 GFX4: VM81-admitted graphics render-packet identity binding.

This module does not create a peer VM81 authority. Callers must provide the
already-authoritative VMRCRuntime instance. Exact graphics descriptors are
canonicalized, identified with inherited Hash216/Hash72, committed through the
singleton VM81 transition path, and only then exposed as an admitted frame
identity bundle suitable for the Pass 179 native render-packet ABI.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Dict, Mapping

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable
from hhs_runtime.pass163.vmrc import VMRCRuntime, VMRCError

SCHEMA = "HHS_PASS_220_GFX4_VM81_GRAPHICS_PACKET_IDENTITY_V1"
CLASSIFICATION = "HHS_PASS_220_GFX4_GRAPHICS_FRAME_VM81_ADMITTED"
CAPABILITY_SCOPE = "P220_GFX4_GRAPHICS_FRAME_ADMISSION"
SOURCE_ARCHITECTURE = "PASS220_GFX4_NATIVE_GRAPHICS_STATE"
SCENE_DOMAIN = "HHS-P220-GFX4-SCENE-SNAPSHOT-V1"
RESOURCE_DOMAIN = "HHS-P220-GFX4-RESOURCE-MANIFEST-V1"
CAMERA_DOMAIN = "HHS-P220-GFX4-CAMERA-V1"
DEPENDENCY_DOMAIN = "HHS-P220-GFX4-VM81-DEPENDENCY-V1"
FRAME_DOMAIN = "HHS-P220-GFX4-ADMITTED-FRAME-V1"
PACKET_DOMAIN = "HHS-P220-GFX4-PACKET-IDENTITY-V1"
THREAD = 63


class GFX4GraphicsIdentityError(ValueError):
    pass


def _exact_int(name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GFX4GraphicsIdentityError(f"P220_GFX4_EXACT_INTEGER_REQUIRED:{name}")
    return value


def _mapping(name: str, value: Any) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise GFX4GraphicsIdentityError(f"P220_GFX4_MAPPING_REQUIRED:{name}")
    return value


def _hash_len(name: str, value: str, expected: int) -> str:
    if not isinstance(value, str) or len(value) != expected:
        raise GFX4GraphicsIdentityError(f"P220_GFX4_IDENTITY_LENGTH_INVALID:{name}")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise GFX4GraphicsIdentityError(
            f"P220_GFX4_IDENTITY_ASCII_REQUIRED:{name}"
        ) from exc
    return value


def _writes_from_material(material: bytes) -> Dict[int, int]:
    digest = sha256(material).digest()
    writes: Dict[int, int] = {}
    for offset, byte in enumerate(digest[:24]):
        position = int((byte + offset * 17) % 81)
        trit = 1 if (byte & 1) else -1
        writes[position] = trit
    if not writes:
        raise GFX4GraphicsIdentityError("P220_GFX4_EMPTY_VM81_WRITE_SET")
    return writes


def build_vm81_admitted_graphics_packet_identity(
    *,
    vm81: VMRCRuntime,
    scene_snapshot: Mapping[str, Any],
    frame_state: Mapping[str, Any],
    resource_manifest: Mapping[str, Any],
    camera_state: Mapping[str, Any],
    frame_index: int,
    exact_time_num: int,
    exact_time_den: int,
    prior_frame_hash216: str | None = None,
) -> Dict[str, Any]:
    """Admit one exact graphics frame through the inherited VM81 authority."""

    if not isinstance(vm81, VMRCRuntime):
        raise GFX4GraphicsIdentityError("P220_GFX4_INHERITED_VM81_REQUIRED")

    frame_index = _exact_int("frame_index", frame_index)
    exact_time_num = _exact_int("exact_time_num", exact_time_num)
    exact_time_den = _exact_int("exact_time_den", exact_time_den)
    if frame_index < 0:
        raise GFX4GraphicsIdentityError("P220_GFX4_FRAME_INDEX_NEGATIVE")
    if exact_time_den <= 0:
        raise GFX4GraphicsIdentityError("P220_GFX4_TIME_DENOMINATOR_INVALID")

    scene = stable(_mapping("scene_snapshot", scene_snapshot))
    frame = stable(_mapping("frame_state", frame_state))
    resources = stable(_mapping("resource_manifest", resource_manifest))
    camera = stable(_mapping("camera_state", camera_state))

    # canonical_bytes performs the recursive no-float/type gate.
    canonical_bytes(scene)
    canonical_bytes(frame)
    canonical_bytes(resources)
    canonical_bytes(camera)

    scene_hash216 = _hash_len(
        "scene_snapshot_hash216",
        hash216(scene, domain=SCENE_DOMAIN),
        216,
    )
    resource_hash216 = _hash_len(
        "resource_manifest_hash216",
        hash216(resources, domain=RESOURCE_DOMAIN),
        216,
    )
    camera_hash72 = _hash_len(
        "camera_hash72",
        hash72(camera, domain=CAMERA_DOMAIN),
        72,
    )
    prior = (
        _hash_len("prior_frame_hash216", prior_frame_hash216, 216)
        if prior_frame_hash216 is not None
        else ""
    )

    admission_material = {
        "schema": SCHEMA,
        "scene_snapshot_hash216": scene_hash216,
        "resource_manifest_hash216": resource_hash216,
        "camera_hash72": camera_hash72,
        "frame_state": frame,
        "frame_index": frame_index,
        "exact_time": {
            "numerator": exact_time_num,
            "denominator": exact_time_den,
        },
        "prior_frame_hash216": prior,
    }
    dependency_root = _hash_len(
        "dependency_root",
        hash216(admission_material, domain=DEPENDENCY_DOMAIN),
        216,
    )
    material = canonical_bytes(admission_material)

    input_hash72 = vm81.state_hash72
    epoch_before = vm81.epoch
    try:
        candidate = vm81.submit_candidate(
            thread=THREAD,
            writes=_writes_from_material(material),
            operation="VMRC_COMMIT",
            expected_input_hash72=input_hash72,
            dependency_root=dependency_root,
            capability_scope=CAPABILITY_SCOPE,
            source_architecture=SOURCE_ARCHITECTURE,
            target_architecture="VM81",
        )
        result = vm81.execute(candidate)
    except VMRCError as exc:
        raise GFX4GraphicsIdentityError(
            f"P220_GFX4_VM81_ADMISSION_REJECTED:{exc}"
        ) from exc

    commit = result.get("commit") or {}
    receipt = commit.get("receipt") or {}
    if commit.get("classification") != "HHS_PASS_163_COMMIT_ADMITTED":
        raise GFX4GraphicsIdentityError("P220_GFX4_VM81_COMMIT_NOT_ADMITTED")

    receipt_hash72 = _hash_len(
        "vm81_receipt_hash72",
        str(receipt.get("receipt_hash72") or ""),
        72,
    )
    # Pass 163 names this root operation_hash216 because it commits a
    # 216-position Hash216Genome, while Hash216Genome.root() deliberately
    # serializes that position manifold to one SHA-256 hex root (64 chars).
    operation_hash216 = _hash_len(
        "vm81_operation_hash216_root",
        str(receipt.get("operation_hash216") or ""),
        64,
    )
    try:
        bytes.fromhex(operation_hash216)
    except ValueError as exc:
        raise GFX4GraphicsIdentityError(
            "P220_GFX4_VM81_OPERATION_ROOT_HEX_INVALID"
        ) from exc
    output_hash72 = _hash_len(
        "vm81_output_hash72",
        str(receipt.get("output_hash72") or ""),
        72,
    )
    if vm81.epoch != epoch_before + 1:
        raise GFX4GraphicsIdentityError("P220_GFX4_VM81_EPOCH_DID_NOT_ADVANCE")
    if output_hash72 != vm81.state_hash72:
        raise GFX4GraphicsIdentityError("P220_GFX4_VM81_OUTPUT_ROOT_MISMATCH")

    frame_identity_payload = {
        **admission_material,
        "dependency_root_hash216": dependency_root,
        "vm81_admission": {
            "candidate_id": candidate.candidate_id,
            "receipt_hash72": receipt_hash72,
            "operation_hash216": operation_hash216,
            "input_hash72": input_hash72,
            "output_hash72": output_hash72,
            "epoch_before": epoch_before,
            "epoch_after": vm81.epoch,
            "capability_scope": CAPABILITY_SCOPE,
        },
    }
    frame_hash216 = _hash_len(
        "frame_hash216",
        hash216(frame_identity_payload, domain=FRAME_DOMAIN),
        216,
    )
    packet_identity_hash216 = _hash_len(
        "packet_identity_hash216",
        hash216(
            {
                "scene_snapshot_hash216": scene_hash216,
                "frame_hash216": frame_hash216,
                "prior_frame_hash216": prior,
                "resource_manifest_hash216": resource_hash216,
                "camera_hash72": camera_hash72,
                "vm81_operation_hash216": operation_hash216,
            },
            domain=PACKET_DOMAIN,
        ),
        216,
    )

    return {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "scene_snapshot_hash216": scene_hash216,
        "frame_hash216": frame_hash216,
        "prior_frame_hash216": prior,
        "resource_manifest_hash216": resource_hash216,
        "camera_hash72": camera_hash72,
        "packet_identity_hash216": packet_identity_hash216,
        "vm81_admission": frame_identity_payload["vm81_admission"],
        "packet_compatibility_unadmitted": False,
        "packet_identity_vm81_admitted": True,
        "singleton_vm81_authority": True,
        "independent_vm81_authority": False,
        "independent_hash72_authority": False,
        "independent_hash216_mutation_authority": False,
        "gpu_or_renderer_mutation_authority": False,
    }


def packet_identity_bytes(identity: Mapping[str, Any]) -> Dict[str, bytes]:
    """Return exact ASCII byte lanes for the native/WASM packet identity slots."""
    record = _mapping("identity", identity)
    if record.get("classification") != CLASSIFICATION:
        raise GFX4GraphicsIdentityError("P220_GFX4_ADMITTED_IDENTITY_REQUIRED")
    if record.get("packet_identity_vm81_admitted") is not True:
        raise GFX4GraphicsIdentityError("P220_GFX4_VM81_ADMISSION_FLAG_REQUIRED")
    scene = _hash_len(
        "scene_snapshot_hash216",
        str(record.get("scene_snapshot_hash216") or ""),
        216,
    )
    frame = _hash_len(
        "frame_hash216",
        str(record.get("frame_hash216") or ""),
        216,
    )
    resources = _hash_len(
        "resource_manifest_hash216",
        str(record.get("resource_manifest_hash216") or ""),
        216,
    )
    camera = _hash_len(
        "camera_hash72",
        str(record.get("camera_hash72") or ""),
        72,
    )
    prior = str(record.get("prior_frame_hash216") or "")
    if prior:
        _hash_len("prior_frame_hash216", prior, 216)
    return {
        "scene": scene.encode("ascii"),
        "frame": frame.encode("ascii"),
        "prior": prior.encode("ascii") if prior else bytes(216),
        "resources": resources.encode("ascii"),
        "camera": camera.encode("ascii"),
    }


def gfx4_vm81_graphics_packet_identity_self_test() -> Dict[str, Any]:
    vm81_a = VMRCRuntime()
    vm81_b = VMRCRuntime()
    kwargs = {
        "scene_snapshot": {
            "scene_id": "gfx4-self-test",
            "node_count": 5184,
            "layout": [72, 72],
        },
        "frame_state": {
            "tick": 144,
            "phase": {"numerator": 1, "denominator": 144},
        },
        "resource_manifest": {
            "geometry": "HHS_NATIVE_5184_POINT_FIELD",
            "compositor": "HHS_NATIVE_RGBA8_POSTPROCESS",
        },
        "camera_state": {
            "kind": "perspective",
            "fov": {"numerator": 62, "denominator": 1},
            "position": [0, 0, 128],
        },
        "frame_index": 144,
        "exact_time_num": 144,
        "exact_time_den": 60,
    }
    first = build_vm81_admitted_graphics_packet_identity(vm81=vm81_a, **kwargs)
    replay = build_vm81_admitted_graphics_packet_identity(vm81=vm81_b, **kwargs)
    lanes = packet_identity_bytes(first)
    deterministic = all(
        first[key] == replay[key]
        for key in (
            "scene_snapshot_hash216",
            "frame_hash216",
            "resource_manifest_hash216",
            "camera_hash72",
            "packet_identity_hash216",
        )
    )
    if not deterministic:
        raise GFX4GraphicsIdentityError("P220_GFX4_DETERMINISTIC_REPLAY_FAILED")
    return {
        "schema": "HHS_PASS_220_GFX4_VM81_GRAPHICS_PACKET_IDENTITY_SELF_TEST_V1",
        "status": "PASS",
        "classification": first["classification"],
        "deterministic_replay": True,
        "vm81_epoch": vm81_a.epoch,
        "scene_bytes": len(lanes["scene"]),
        "frame_bytes": len(lanes["frame"]),
        "resource_bytes": len(lanes["resources"]),
        "camera_bytes": len(lanes["camera"]),
        "packet_compatibility_unadmitted": first[
            "packet_compatibility_unadmitted"
        ],
    }
