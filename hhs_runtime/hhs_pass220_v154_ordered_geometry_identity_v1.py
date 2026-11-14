"""Pass 220 V154: ordered physical geometry identity for inherited GFX4 admission.

This module prepares *preadmission material*, not a VM81 receipt or physical
producer attestation. It composes with the existing GFX4 frame-state constructor;
a caller must still establish trusted producer lineage and submit the resulting
frame through the inherited singleton VM81 path.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping

from hhs_installer.canonical import hash216

SCHEMA = "HHS_PASS_220_V154_ORDERED_GEOMETRY_IDENTITY_V1"
DOMAIN = "HHS-P220-V154-ORDERED-PHYSICAL-GEOMETRY-V1"
PARTICLES = 10368
COMPONENTS = 3
POSITION_BYTES = PARTICLES * COMPONENTS * 4
RESERVED_KEY = "ordered_physical_geometry_observation"


class V154GeometryError(ValueError):
    pass


def _nonnegative_int(name: str, value: Any) -> int:
    if type(value) is not int or value < 0 or value > (1 << 64) - 1:
        raise V154GeometryError(f"V154_EXACT_U64_REQUIRED:{name}")
    return value


def geometry_identity(
    *, position_f32le: bytes, producer_tick: int, geometry_tick: int,
    render_tick: int, draw_resource_id: int, scene_resource_id: int,
    source_geometry_resource_id: int,
) -> dict[str, Any]:
    """Prepare ordered byte identity; never assert trusted physical origin."""
    if type(position_f32le) is not bytes or len(position_f32le) != POSITION_BYTES:
        raise V154GeometryError("V154_EXACT_POSITION_BYTES_REQUIRED")
    tick = _nonnegative_int("producer_tick", producer_tick)
    if (_nonnegative_int("geometry_tick", geometry_tick) != tick or
            _nonnegative_int("render_tick", render_tick) != tick):
        raise V154GeometryError("V154_TICK_MISMATCH")
    resource = _nonnegative_int("draw_resource_id", draw_resource_id)
    if (resource == 0 or
            _nonnegative_int("scene_resource_id", scene_resource_id) != resource or
            _nonnegative_int("source_geometry_resource_id", source_geometry_resource_id) != resource):
        raise V154GeometryError("V154_RESOURCE_MISMATCH")
    # Examine the IEEE-754 bit pattern directly: preserve both signed zeros.
    for i in range(0, POSITION_BYTES, 4):
        bits = int.from_bytes(position_f32le[i:i + 4], "little")
        if bits & 0x7f800000 == 0x7f800000:
            raise V154GeometryError("V154_NONFINITE_POSITION")
    payload = {
        "schema": SCHEMA,
        "producer_tick": tick,
        "particle_count": PARTICLES,
        "components": COMPONENTS,
        "position_byte_length": POSITION_BYTES,
        "position_sha256": sha256(position_f32le).hexdigest(),
        "draw_resource_id": resource,
    }
    return {
        **payload,
        "geometry_hash216": hash216(payload, domain=DOMAIN),
        "physical_source_provenance_verified": False,
        "native_vm81_admission": False,
        "physics_mutation_authority": False,
    }


def bind_geometry_frame_state(
    *, frame_state: Mapping[str, Any], geometry: Mapping[str, Any]
) -> dict[str, Any]:
    """Insert V154 geometry before GFX4 admission; no receipt is minted."""
    if not isinstance(frame_state, Mapping) or RESERVED_KEY in frame_state:
        raise V154GeometryError("V154_FRAME_STATE_COLLISION_OR_INVALID")
    if not isinstance(geometry, Mapping):
        raise V154GeometryError("V154_GEOMETRY_REQUIRED")
    if (geometry.get("schema") != SCHEMA or
            geometry.get("physical_source_provenance_verified") is not False or
            geometry.get("native_vm81_admission") is not False or
            geometry.get("physics_mutation_authority") is not False):
        raise V154GeometryError("V154_AUTHORITY_CLAIM_REJECTED")
    payload = {k: geometry[k] for k in (
        "schema", "producer_tick", "particle_count", "components",
        "position_byte_length", "position_sha256", "draw_resource_id"
    ) if k in geometry}
    if len(payload) != 7 or payload["particle_count"] != PARTICLES or (
            payload["components"] != COMPONENTS or
            payload["position_byte_length"] != POSITION_BYTES or
            type(payload["producer_tick"]) is not int or payload["producer_tick"] < 0 or
            type(payload["draw_resource_id"]) is not int or payload["draw_resource_id"] <= 0 or
            type(payload["position_sha256"]) is not str or
            len(payload["position_sha256"]) != 64 or
            any(ch not in "0123456789abcdef" for ch in payload["position_sha256"])):
        raise V154GeometryError("V154_GEOMETRY_SHAPE_INVALID")
    if geometry.get("geometry_hash216") != hash216(payload, domain=DOMAIN):
        raise V154GeometryError("V154_GEOMETRY_ROOT_MISMATCH")
    if set(geometry) != set(payload) | {
        "geometry_hash216", "physical_source_provenance_verified",
        "native_vm81_admission", "physics_mutation_authority"
    }:
        raise V154GeometryError("V154_UNEXPECTED_GEOMETRY_FIELDS")
    return {**frame_state, RESERVED_KEY: dict(geometry)}
