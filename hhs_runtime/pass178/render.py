from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

from .exact import ExactPhysicsError, ExactRational, reject_float

Q32 = 1 << 32


def q32_32(value: ExactRational) -> tuple[int, ExactRational]:
    scaled_num = value.num * Q32
    if scaled_num >= 0:
        integer = scaled_num // value.den
    else:
        integer = -((-scaled_num) // value.den)
    projected = ExactRational(integer, Q32)
    return integer, (value - projected).abs()


def render_packet(
    *,
    step_index: int,
    world_time: ExactRational,
    position3: Iterable[ExactRational],
    phase_index_mod_72: int,
    state_hash216: str,
    transition_hash216: str,
) -> dict[str, Any]:
    if step_index < 0 or not 0 <= phase_index_mod_72 < 72:
        raise ExactPhysicsError("P178_RENDER_PACKET_INDEX_RANGE")
    if len(state_hash216) != 216 or len(transition_hash216) != 216:
        raise ExactPhysicsError("P178_RENDER_PACKET_HASH216_LENGTH")
    p = tuple(position3)
    if len(p) != 3:
        raise ExactPhysicsError("P178_RENDER_PACKET_POSITION_ARITY")
    projected = [q32_32(v) for v in p]
    errors = [pair[1] for pair in projected]
    max_error = max(errors, default=ExactRational(0))
    packet = {
        "schema": "HHS_PASS_178_IMMUTABLE_RENDER_PACKET_V1",
        "step_index": step_index,
        "world_time_num": world_time.num,
        "world_time_den": world_time.den,
        "position_q32_32": [pair[0] for pair in projected],
        "phase_index_mod_72": phase_index_mod_72,
        "state_hash216": state_hash216,
        "transition_hash216": transition_hash216,
        "render_projection_error_bound": max_error.as_pair(),
        "authoritative_snapshot_reference": state_hash216,
        "immutable": True,
        "renderer_feedback_authority": False,
        "simulation_mutation_authority": False,
        "floating_point_authority": False,
    }
    packet["packet_sha256"] = hashlib.sha256(
        json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return packet
