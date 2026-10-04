"""Pass 220 I071 — shared-root phase-gear loop closure bridge.

I071 lowers the VM81 kernel's exact first-repeat orbit detector into the
72-position I070 tensor/Lo-Shu phase gear and lifts the same detector into
nested hydration descriptors. Geometry recurrence and lineage recurrence remain
distinct: a geometric loop may close while Hash216 ancestry continues.

This module is candidate/read-only. It does not create canonical mutation,
Hash72 commit, Hash216 commit, persistence, or external-egress authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, MutableSequence, Sequence

from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i070_i_tensor_lane5_vm81_bridge_v1 import (
    build_lane5_vm81_candidate,
    tensor_cell_witnesses,
)

SCHEMA = "HHS_PASS_220_I071_SHARED_ROOT_PHASE_GEAR_LOOP_CLOSURE_V1"
PROFILE = "PASS220-I071-SHARED-ROOT-PHASE-GEAR-LOOP-CLOSURE-v1"
ROOT_METADATA_SEED_TEXT = "179971.179971"
INVARIANT_GATE_TEXT = "1.001"
I042_SHARED_ROOT_SCHEMA = "HHS_PASS_220_I042_LANE5_MULTIMODAL_SHARED_ROOT_FABRIC_V1"
I070_SCHEMA = "HHS_PASS_220_I070_I_TENSOR_LANE5_VM81_BRIDGE_V1"

PHASE_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PHASE_CHANNELS = 8
LO_SHU_POSITIONS = 9
QUDIT_PHASE_SLOTS = PHASE_CHANNELS * LO_SHU_POSITIONS
VM81_CELLS = 81
VM81_NUCLEI = 9
HASH72_POSITIONS = 72
HASH216_POSITIONS = 216
MAX_SEEN = 8192
PHASE_LOCK_PERIOD = 5184

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "vm81_detector_semantics_preserved": True,
    "geometry_history_separated": True,
    "shared_root_required": True,
    "lower_lift_orbit_identity_preserved": True,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I071LoopError(ValueError):
    """Raised when I071 loop geometry or detector semantics diverge."""


@dataclass(frozen=True)
class SeenState:
    hash72_state: str
    step: int


@dataclass(frozen=True)
class PhaseGearGeometry:
    shared_root_sha256: str
    nucleus_index: int
    phase_slot: int
    phase_channel: int
    phase_symbol: str
    outcome: int
    row: int
    column: int
    lo_shu_value: int
    vm81_cell_id: int
    i070_binding_hash72: str
    geometry_hash72: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _exact_int(value: Any, name: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I071LoopError(f"{name} must be an exact integer")
    if not lower <= value <= upper:
        raise Pass220I071LoopError(
            f"{name} must satisfy {lower} <= {name} <= {upper}"
        )
    return value


def _sha256_hex(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass220I071LoopError(f"{name} must be a 64-character SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass220I071LoopError(f"{name} must be hexadecimal") from exc
    return value.lower()


def _hash72_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH72_POSITIONS:
        raise Pass220I071LoopError(f"{name} must be a 72-character Hash72 word")
    return value


def _hash216_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH216_POSITIONS:
        raise Pass220I071LoopError(f"{name} must be a 216-character Hash216 word")
    return value


def canonical_bytes(value: Any) -> bytes:
    def reject_float(node: Any, path: str = "root") -> None:
        if isinstance(node, float):
            raise Pass220I071LoopError(f"floating-point value forbidden at {path}")
        if isinstance(node, Mapping):
            for key, child in node.items():
                reject_float(child, f"{path}.{key}")
        elif isinstance(node, (list, tuple)):
            for index, child in enumerate(node):
                reject_float(child, f"{path}[{index}]")
    reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def kernel_orbit_contract() -> dict[str, Any]:
    return {
        "kernel_source": "hhs_runtime/HARMONICODE_VM_RUNTIME.c",
        "seen_capacity": MAX_SEEN,
        "detector_rule": "first matching Hash72 state returns cur-first_seen_step",
        "miss_rule": "append state+step when seen_count<MAX_SEEN; otherwise return 0",
        "transport_rule": "orbit_period>0 => W_ORBIT_DETECTED|W_CLOSE_TRANSPORT",
        "orbit_flag_rule": "orbit_period>0 => orbit_halted=1",
        "run_halt_rule": "halt_on_orbit && orbit_halted => break",
        "convergence_rule": (
            "W_CLOSE_TRANSPORT & W_CLOSE_ORIENTATION & "
            "W_CLOSE_CONSTRAINT => W_CONVERGED"
        ),
        "op_halt_is_distinct": True,
    }


def detect_orbit_exact(
    seen: MutableSequence[SeenState],
    state_hash72: str,
    current_step: int,
    *,
    max_seen: int = MAX_SEEN,
) -> int:
    """Exact semantic replica of VM81 detect_orbit()."""
    state = _hash72_word(state_hash72, "state_hash72")
    cur = _exact_int(current_step, "current_step", 0, (1 << 63) - 1)
    limit = _exact_int(max_seen, "max_seen", 1, MAX_SEEN)
    for prior in seen:
        if prior.hash72_state == state:
            if cur < prior.step:
                raise Pass220I071LoopError("current step precedes first-seen step")
            return cur - prior.step
    if len(seen) < limit:
        seen.append(SeenState(state, cur))
    return 0


def decode_phase_slot(phase_slot: int) -> tuple[int, int]:
    slot = _exact_int(phase_slot, "phase_slot", 0, QUDIT_PHASE_SLOTS - 1)
    return divmod(slot, LO_SHU_POSITIONS)


def encode_phase_slot(phase_channel: int, outcome: int) -> int:
    channel = _exact_int(phase_channel, "phase_channel", 0, PHASE_CHANNELS - 1)
    k = _exact_int(outcome, "outcome", 0, LO_SHU_POSITIONS - 1)
    return channel * LO_SHU_POSITIONS + k


def phase_successor(phase_slot: int) -> int:
    slot = _exact_int(phase_slot, "phase_slot", 0, QUDIT_PHASE_SLOTS - 1)
    return (slot + 1) % QUDIT_PHASE_SLOTS


def phase_gear_invariants() -> dict[str, Any]:
    return {
        "phase_channels": PHASE_CHANNELS,
        "lo_shu_positions": LO_SHU_POSITIONS,
        "qudit_phase_slots": QUDIT_PHASE_SLOTS,
        "vm81_cells": VM81_CELLS,
        "vm81_nuclei": VM81_NUCLEI,
        "64x81": 64 * 81,
        "72x72": 72 * 72,
        "144x36": 144 * 36,
        "phase_gear_determinant": 64 * 81 - 72 * 72,
        "phase_lock_period": PHASE_LOCK_PERIOD,
        "coordinate_closure": (
            64 * 81 == 72 * 72 == 144 * 36 == PHASE_LOCK_PERIOD
        ),
    }


def build_nucleus_qudit_surface(
    *,
    shared_root_sha256: str,
    nucleus_index: int,
) -> tuple[PhaseGearGeometry, ...]:
    root = _sha256_hex(shared_root_sha256, "shared_root_sha256")
    nucleus = _exact_int(nucleus_index, "nucleus_index", 0, VM81_NUCLEI - 1)
    i070 = build_lane5_vm81_candidate(nucleus)
    if i070.get("schema") != I070_SCHEMA:
        raise Pass220I071LoopError("I070 candidate schema mismatch")
    binding = _hash72_word(i070["binding_hash72"], "i070_binding_hash72")
    cells = tensor_cell_witnesses(nucleus)

    surface: list[PhaseGearGeometry] = []
    for slot in range(QUDIT_PHASE_SLOTS):
        channel, outcome = decode_phase_slot(slot)
        cell = cells[outcome]
        body = {
            "schema": SCHEMA,
            "shared_root_sha256": root,
            "i070_binding_hash72": binding,
            "nucleus_index": nucleus,
            "phase_slot": slot,
            "phase_channel": channel,
            "phase_symbol": PHASE_BASIS[channel],
            "outcome": outcome,
            "row": cell.row,
            "column": cell.column,
            "lo_shu_value": cell.lo_shu_value,
            "vm81_cell_id": cell.vm81_cell_id,
        }
        surface.append(
            PhaseGearGeometry(
                **body,
                geometry_hash72=hash72(body),
            )
        )
    if len(surface) != QUDIT_PHASE_SLOTS:
        raise Pass220I071LoopError("phase-gear surface must contain 72 states")
    if len({item.geometry_hash72 for item in surface}) != QUDIT_PHASE_SLOTS:
        raise Pass220I071LoopError("phase-gear geometry identities must be unique")
    return tuple(surface)


def lift_geometry(
    geometry: PhaseGearGeometry,
    *,
    nesting_depth: int,
    lineage_hash216: str,
    hydration_root_sha256: str,
) -> dict[str, Any]:
    depth = _exact_int(nesting_depth, "nesting_depth", 0, 1_000_000)
    lineage = _hash216_word(lineage_hash216, "lineage_hash216")
    hydration_root = _sha256_hex(hydration_root_sha256, "hydration_root_sha256")
    return {
        "schema": f"{SCHEMA}_LIFTED_GEOMETRY_V1",
        "nesting_depth": depth,
        "geometry": geometry.to_dict(),
        "lowered_geometry_hash72": geometry.geometry_hash72,
        "lineage_hash216": lineage,
        "hydration_root_sha256": hydration_root,
        "shared_root_sha256": geometry.shared_root_sha256,
        "canonical_mutation_authority": False,
    }


def lower_geometry(lifted: Mapping[str, Any]) -> str:
    geometry = lifted.get("geometry")
    if not isinstance(geometry, Mapping):
        raise Pass220I071LoopError("lifted geometry record missing geometry")
    claimed = _hash72_word(
        lifted.get("lowered_geometry_hash72"),
        "lowered_geometry_hash72",
    )
    if geometry.get("geometry_hash72") != claimed:
        raise Pass220I071LoopError("lift/lower geometry identity diverged")
    return claimed


def _hydration_root(i070: Mapping[str, Any]) -> str:
    payload = {
        "candidate_hash216": i070["candidate_hash216"],
        "candidate_hydration": i070["candidate_hydration"],
        "inherited_i069_hydration": i070["inherited_i069_hydration"],
        "metadata_optimization": i070["metadata_optimization"],
    }
    return sha256(canonical_bytes(payload)).hexdigest()


def advance_lineage(
    *,
    lineage_hash216: str,
    shared_root_sha256: str,
    from_geometry_hash72: str,
    to_geometry_hash72: str,
    step: int,
) -> str:
    lineage = _hash216_word(lineage_hash216, "lineage_hash216")
    root = _sha256_hex(shared_root_sha256, "shared_root_sha256")
    source = _hash72_word(from_geometry_hash72, "from_geometry_hash72")
    target = _hash72_word(to_geometry_hash72, "to_geometry_hash72")
    current_step = _exact_int(step, "step", 0, (1 << 63) - 1)

    previous_hash72 = lineage[-HASH72_POSITIONS:]
    change_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_LINEAGE_CHANGE_V1",
            "step": current_step,
            "from_geometry_hash72": source,
            "to_geometry_hash72": target,
        }
    )
    receipt_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_LINEAGE_RECEIPT_V1",
            "shared_root_sha256": root,
            "previous_lineage_hash216": lineage,
            "previous_hash72": previous_hash72,
            "change_hash72": change_hash72,
        }
    )
    result = previous_hash72 + change_hash72 + receipt_hash72
    return _hash216_word(result, "advanced_lineage_hash216")


def run_phase_gear_loop(
    *,
    shared_root_sha256: str,
    nucleus_index: int,
    nesting_depth: int = 0,
    halt_on_orbit: bool = True,
    orientation_closed: bool = False,
    constraint_closed: bool = False,
    max_steps: int = QUDIT_PHASE_SLOTS,
) -> dict[str, Any]:
    if not isinstance(halt_on_orbit, bool):
        raise Pass220I071LoopError("halt_on_orbit must be Boolean")
    if not isinstance(orientation_closed, bool) or not isinstance(
        constraint_closed, bool
    ):
        raise Pass220I071LoopError("closure flags must be Boolean")

    root = _sha256_hex(shared_root_sha256, "shared_root_sha256")
    nucleus = _exact_int(nucleus_index, "nucleus_index", 0, VM81_NUCLEI - 1)
    depth = _exact_int(nesting_depth, "nesting_depth", 0, 1_000_000)
    steps_limit = _exact_int(max_steps, "max_steps", 0, MAX_SEEN)

    i070 = build_lane5_vm81_candidate(nucleus)
    surface = build_nucleus_qudit_surface(
        shared_root_sha256=root,
        nucleus_index=nucleus,
    )
    lineage = _hash216_word(i070["candidate_hash216"], "initial_lineage_hash216")
    initial_lineage = lineage
    hydration_root = _hydration_root(i070)
    seen: list[SeenState] = []
    trace: list[dict[str, Any]] = []
    orbit_period = 0

    for step in range(steps_limit + 1):
        geometry = surface[step % QUDIT_PHASE_SLOTS]
        lifted = lift_geometry(
            geometry,
            nesting_depth=depth,
            lineage_hash216=lineage,
            hydration_root_sha256=hydration_root,
        )
        lowered = lower_geometry(lifted)
        orbit_period = detect_orbit_exact(seen, lowered, step)
        transport_closed = orbit_period > 0
        converged = (
            transport_closed and orientation_closed and constraint_closed
        )
        orbit_halted = transport_closed
        halted = halt_on_orbit and orbit_halted

        trace.append(
            {
                "step": step,
                "phase_slot": geometry.phase_slot,
                "phase_channel": geometry.phase_channel,
                "phase_symbol": geometry.phase_symbol,
                "outcome": geometry.outcome,
                "vm81_cell_id": geometry.vm81_cell_id,
                "lo_shu_value": geometry.lo_shu_value,
                "geometry_hash72": geometry.geometry_hash72,
                "lineage_hash216": lineage,
                "nesting_depth": depth,
                "orbit_period": orbit_period,
                "transport_closed": transport_closed,
                "orientation_closed": orientation_closed,
                "constraint_closed": constraint_closed,
                "converged": converged,
                "orbit_halted": orbit_halted,
                "halted": halted,
            }
        )
        if halted:
            break
        if step == steps_limit:
            break

        next_geometry = surface[(step + 1) % QUDIT_PHASE_SLOTS]
        lineage = advance_lineage(
            lineage_hash216=lineage,
            shared_root_sha256=root,
            from_geometry_hash72=geometry.geometry_hash72,
            to_geometry_hash72=next_geometry.geometry_hash72,
            step=step,
        )

    final = trace[-1]
    result = {
        "schema": SCHEMA,
        "profile": PROFILE,
        "shared_root_schema": I042_SHARED_ROOT_SCHEMA,
        "shared_root_sha256": root,
        "root_metadata_seed": ROOT_METADATA_SEED_TEXT,
        "invariant_gate": INVARIANT_GATE_TEXT,
        "nucleus_index": nucleus,
        "nesting_depth": depth,
        "phase_gear": phase_gear_invariants(),
        "kernel_orbit_contract": kernel_orbit_contract(),
        "initial_lineage_hash216": initial_lineage,
        "final_lineage_hash216": final["lineage_hash216"],
        "hydration_root_sha256": hydration_root,
        "visited_records": len(trace),
        "seen_unique_geometries": len(seen),
        "orbit_period": final["orbit_period"],
        "transport_closed": final["transport_closed"],
        "orientation_closed": final["orientation_closed"],
        "constraint_closed": final["constraint_closed"],
        "converged": final["converged"],
        "orbit_halted": final["orbit_halted"],
        "halt_on_orbit": halt_on_orbit,
        "halted": final["halted"],
        "geometry_returned": (
            trace[0]["geometry_hash72"] == final["geometry_hash72"]
        ),
        "lineage_advanced": (
            trace[0]["lineage_hash216"] != final["lineage_hash216"]
        ),
        "trace": trace,
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    result["receipt_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "shared_root_sha256": root,
            "nucleus_index": nucleus,
            "nesting_depth": depth,
            "orbit_period": result["orbit_period"],
            "geometry_returned": result["geometry_returned"],
            "lineage_advanced": result["lineage_advanced"],
            "converged": result["converged"],
            "authority": result["authority"],
        }
    )
    return result


def self_test() -> dict[str, Any]:
    root = sha256(
        canonical_bytes(
            {
                "schema": "HHS_PASS_220_I071_SELF_TEST_SHARED_ROOT",
                "root_metadata_seed": ROOT_METADATA_SEED_TEXT,
                "invariant_gate": INVARIANT_GATE_TEXT,
            }
        )
    ).hexdigest()
    local = run_phase_gear_loop(
        shared_root_sha256=root,
        nucleus_index=0,
        nesting_depth=0,
        halt_on_orbit=True,
        orientation_closed=False,
        constraint_closed=False,
        max_steps=QUDIT_PHASE_SLOTS,
    )
    lifted = run_phase_gear_loop(
        shared_root_sha256=root,
        nucleus_index=0,
        nesting_depth=7,
        halt_on_orbit=True,
        orientation_closed=True,
        constraint_closed=True,
        max_steps=QUDIT_PHASE_SLOTS,
    )
    checks = {
        "local_orbit_period_72": local["orbit_period"] == 72,
        "local_geometry_returned": local["geometry_returned"] is True,
        "local_lineage_advanced": local["lineage_advanced"] is True,
        "local_halts_on_orbit": local["halted"] is True,
        "local_not_converged_without_other_closures": local["converged"] is False,
        "lifted_orbit_period_72": lifted["orbit_period"] == 72,
        "lifted_geometry_returned": lifted["geometry_returned"] is True,
        "lifted_lineage_advanced": lifted["lineage_advanced"] is True,
        "lifted_converged_with_all_closures": lifted["converged"] is True,
        "lower_lift_period_invariant": local["orbit_period"] == lifted["orbit_period"],
        "phase_lock_5184": phase_gear_invariants()["phase_lock_period"] == 5184,
        "no_vm81_mutation_authority": (
            AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "sample_shared_root_sha256": root,
        "sample_receipt_hash72": lifted["receipt_hash72"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "MAX_SEEN",
    "PHASE_BASIS",
    "QUDIT_PHASE_SLOTS",
    "Pass220I071LoopError",
    "PhaseGearGeometry",
    "SeenState",
    "advance_lineage",
    "build_nucleus_qudit_surface",
    "decode_phase_slot",
    "detect_orbit_exact",
    "encode_phase_slot",
    "kernel_orbit_contract",
    "lift_geometry",
    "lower_geometry",
    "phase_gear_invariants",
    "phase_successor",
    "run_phase_gear_loop",
    "self_test",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
