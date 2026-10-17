"""Pass 220 I086: Conway's Life is the sole new transition logic.

The 81 occupancy positions are a typed projection over existing VM81 cells.
Native Lo Shu/HNAN tensors and Hash216 lineage remain inherited and untouched.
"""
from __future__ import annotations

from hashlib import sha256
import json

from hhs_runtime.hhs_pass220_i085_two_sweep_hash216_clock_v1 import (
    address_tick, compose_single_hash216_array,
)

SCHEMA = "HHS_PASS220_I086_CONWAY_81_CELL_NATIVE_PROJECTION_V1"
MASK = (1 << 81) - 1


def conway_step(occupancy: int) -> int:
    """Exact B3/S23 transition on the existing 9x9 toroidal cell addresses."""
    if type(occupancy) is not int or occupancy < 0 or occupancy > MASK:
        raise ValueError("occupancy must be an exact 81-bit nonnegative integer")
    next_state = 0
    for row in range(9):
        for col in range(9):
            index = 9 * row + col
            neighbors = sum(
                (occupancy >> (9 * ((row + dr) % 9) + ((col + dc) % 9))) & 1
                for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if dr != 0 or dc != 0
            )
            alive = (occupancy >> index) & 1
            if neighbors == 3 or (alive and neighbors == 2):
                next_state |= 1 << index
    return next_state


def compose_conway_frame(*, occupancy: int, frame_id: int) -> dict:
    """Bind one Conway projection to the inherited I085 two-sweep Hash216 clock.

    Projection receipts are NOT new Hash216 roots or canonical VM81 mutations.
    """
    updated = conway_step(occupancy)
    inherited = compose_single_hash216_array(frame_id=frame_id)
    addresses = [
        {
            "cell": i,
            "row": i // 9,
            "column": i % 9,
            "previous_alive": (occupancy >> i) & 1,
            "next_alive": (updated >> i) & 1,
            "native_address": address_tick(
                frame_id=frame_id, sweep=0, position5184=i * 64
            ),
        }
        for i in range(81)
    ]
    body = {
        "schema": SCHEMA,
        "frame_id": frame_id,
        "occupancy_before": str(occupancy),
        "occupancy_after": str(updated),
        "cell_addresses": addresses,
        "inherited_hash216_index_root_sha256":
            inherited["hash216_array_index_root_sha256"],
        "inherited_hash216_logical_identity_sha256":
            inherited["hash216_array_logical_identity_sha256"],
    }
    digest = sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()
    return {
        **body,
        "projection_receipt_sha256": digest,
        "new_logic": "CONWAY_B3_S23_TOROIDAL_9X9",
        "inherited_two_sweep_hash216_array": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "native_tensor_redefined": False,
    }
