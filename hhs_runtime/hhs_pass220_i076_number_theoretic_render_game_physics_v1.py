"""Pass 220 I076 — number-theoretic render/game physics.

This layer makes the browser renderer's existing 64/72 label precise without
reinterpreting it as a count of skipped frames.

The exact scheduler is:

    rskip = 64/72 = 8/9        (phase-bias ratio)
    Q4                           (projection quantization)
    local64                      (operation coordinate)
    phase72                      (Hash72 phase coordinate)
    VM81                         (cell coordinate)
    5184 = lcm(64,72,81,4)      (high-precision supercycle)

Physics/state construction advances on every simulation tick.  Q4 controls
projection writes.  The 64/72 value remains an exact phase-bias accumulator
that is attached to each projected state.  No canonical state is deleted when
the renderer does not write a frame.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from math import lcm
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_holofractal_relativistic_game_engine_v1 import (
    H36_FRAME_BITS,
    HASH72_SIDE,
    H36_RULE_COUNT,
    HOLOGRAPHIC_NODE_COUNT,
    QUARTIC_RENDER_PERIOD,
    VM81_CELLS,
    holographic_animation_state,
)

SCHEMA = "HHS_PASS_220_I076_NUMBER_THEORETIC_RENDER_GAME_PHYSICS_V1"
PROFILE = "PASS220-I076-NUMBER-THEORETIC-RENDER-GAME-PHYSICS-v1"
VERSION = "1.0.0"

RSKIP_NUMERATOR = 64
RSKIP_DENOMINATOR = 72
RSKIP_REDUCED = Fraction(8, 9)
GLOBAL_RENDER_CLOSURE_TICKS = 5184
QUARTIC_PROJECTION_PERIOD = 4
QUARTIC_WRITES_PER_SUPERCYCLE = GLOBAL_RENDER_CLOSURE_TICKS // QUARTIC_PROJECTION_PERIOD

AUTHORITY_BOUNDARY = {
    "projection_only": True,
    "rskip_is_phase_bias": True,
    "rskip_is_skipped_frame_count": False,
    "physics_tick_always_advances": True,
    "quartic_quantizes_projection_writes": True,
    "global_closure_is_exact_integer_state": True,
    "browser_bigint_scheduler_required": True,
    "gpu_float_is_projection_only": True,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_authority": False,
    "canonical_hash216_authority": False,
    "canonical_persistence_authority": False,
}


class Pass220I076RenderPhysicsError(ValueError):
    pass


def _exact_nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I076RenderPhysicsError(f"{name} must be an exact integer")
    if value < 0:
        raise Pass220I076RenderPhysicsError(f"{name} must be nonnegative")
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["receipt_sha256"] = sha256(
        _stable_json(out).encode("utf-8")
    ).hexdigest()
    return out


def number_theoretic_render_phase(tick: int) -> dict[str, Any]:
    """Return the exact projection scheduler state for one simulation tick."""
    t = _exact_nonnegative_int(tick, "tick")
    scaled = t * RSKIP_NUMERATOR
    closure = t % GLOBAL_RENDER_CLOSURE_TICKS
    hash72_row, hash72_col = divmod(closure, HASH72_SIDE)

    return _receipt({
        "schema": f"{SCHEMA}_PHASE_STATE_V1",
        "tick": t,
        "rskip": {
            "numerator": RSKIP_NUMERATOR,
            "denominator": RSKIP_DENOMINATOR,
            "reduced_numerator": RSKIP_REDUCED.numerator,
            "reduced_denominator": RSKIP_REDUCED.denominator,
            "meaning": "PHASE_BIAS_NOT_FRAME_SKIP_COUNT",
        },
        "bias_accumulator": {
            "whole": scaled // RSKIP_DENOMINATOR,
            "remainder72": scaled % RSKIP_DENOMINATOR,
            "denominator": RSKIP_DENOMINATOR,
        },
        "coordinates": {
            "local64": t % H36_RULE_COUNT,
            "phase72": t % HASH72_SIDE,
            "vm81": t % VM81_CELLS,
            "quartic4": t % QUARTIC_PROJECTION_PERIOD,
            "linear5184": closure,
            "hash72_row72": hash72_row,
            "hash72_col72": hash72_col,
        },
        "projection": {
            "quartic_render": (t % QUARTIC_PROJECTION_PERIOD) == 0,
            "quartic_period": QUARTIC_PROJECTION_PERIOD,
            "simulation_tick_continues": True,
            "skipped_projection_writes_delete_no_state": True,
        },
        "supercycle": {
            "period_ticks": GLOBAL_RENDER_CLOSURE_TICKS,
            "index": t // GLOBAL_RENDER_CLOSURE_TICKS,
            "phase": closure,
            "high_precision_closure": closure == 0,
        },
        "canonical_mutation_authority": False,
        "gpu_float_is_canonical_authority": False,
    })


def validate_render_phase(state: Mapping[str, Any]) -> bool:
    if not isinstance(state, Mapping):
        raise Pass220I076RenderPhysicsError("state must be a mapping")
    if state.get("schema") != f"{SCHEMA}_PHASE_STATE_V1":
        raise Pass220I076RenderPhysicsError("phase-state schema mismatch")
    tick = _exact_nonnegative_int(state.get("tick"), "tick")
    expected = number_theoretic_render_phase(tick)
    if state != expected:
        raise Pass220I076RenderPhysicsError("phase-state replay mismatch")
    return True


def render_supercycle_witness() -> dict[str, Any]:
    """Exhaustively prove the exact 5,184-tick scheduler cycle."""
    states = tuple(
        number_theoretic_render_phase(tick)
        for tick in range(GLOBAL_RENDER_CLOSURE_TICKS)
    )
    coords = tuple(state["coordinates"] for state in states)
    bias_remainders = tuple(
        state["bias_accumulator"]["remainder72"]
        for state in states
    )
    quartic_writes = tuple(
        state["tick"]
        for state in states
        if state["projection"]["quartic_render"]
    )

    vm81_local64 = {
        (item["vm81"], item["local64"])
        for item in coords
    }
    hash72_surface = {
        (item["hash72_row72"], item["hash72_col72"])
        for item in coords
    }
    full_closures_before_end = tuple(
        state["tick"]
        for state in states[1:]
        if (
            state["coordinates"]["local64"] == 0
            and state["coordinates"]["phase72"] == 0
            and state["coordinates"]["vm81"] == 0
            and state["coordinates"]["quartic4"] == 0
        )
    )
    next_state = number_theoretic_render_phase(
        GLOBAL_RENDER_CLOSURE_TICKS
    )

    checks = {
        "rskip_exact_64_72": Fraction(
            RSKIP_NUMERATOR, RSKIP_DENOMINATOR
        ) == RSKIP_REDUCED,
        "rskip_reduced_8_9": RSKIP_REDUCED == Fraction(8, 9),
        "quartic_period_4": QUARTIC_PROJECTION_PERIOD == 4,
        "global_lcm_5184": lcm(
            H36_RULE_COUNT,
            HASH72_SIDE,
            VM81_CELLS,
            QUARTIC_PROJECTION_PERIOD,
        ) == GLOBAL_RENDER_CLOSURE_TICKS,
        "h36_frame_5184": H36_FRAME_BITS == GLOBAL_RENDER_CLOSURE_TICKS,
        "holographic_nodes_5184": (
            HOLOGRAPHIC_NODE_COUNT == GLOBAL_RENDER_CLOSURE_TICKS
        ),
        "vm81_local64_bijection_5184": (
            len(vm81_local64) == GLOBAL_RENDER_CLOSURE_TICKS
        ),
        "hash72_surface_bijection_5184": (
            len(hash72_surface) == GLOBAL_RENDER_CLOSURE_TICKS
        ),
        "bias_remainder_has_9_exact_states": (
            len(set(bias_remainders)) == RSKIP_REDUCED.denominator
        ),
        "quartic_writes_1296": (
            len(quartic_writes) == QUARTIC_WRITES_PER_SUPERCYCLE
        ),
        "no_early_full_precision_closure": (
            full_closures_before_end == ()
        ),
        "tick_5184_returns_all_scheduler_residues": (
            next_state["coordinates"]["local64"] == 0
            and next_state["coordinates"]["phase72"] == 0
            and next_state["coordinates"]["vm81"] == 0
            and next_state["coordinates"]["quartic4"] == 0
            and next_state["coordinates"]["linear5184"] == 0
            and next_state["bias_accumulator"]["remainder72"] == 0
            and next_state["supercycle"]["high_precision_closure"] is True
        ),
    }
    if not all(checks.values()):
        raise Pass220I076RenderPhysicsError(
            f"render supercycle failed: {checks}"
        )

    return _receipt({
        "schema": f"{SCHEMA}_SUPERCYCLE_WITNESS_V1",
        "checks": checks,
        "rskip": {
            "numerator": 64,
            "denominator": 72,
            "reduced": {"numerator": 8, "denominator": 9},
        },
        "quartic_projection_period": QUARTIC_PROJECTION_PERIOD,
        "quartic_projection_writes": len(quartic_writes),
        "bias_remainder_states": tuple(sorted(set(bias_remainders))),
        "vm81_local64_states": len(vm81_local64),
        "hash72_surface_states": len(hash72_surface),
        "closure_ticks": GLOBAL_RENDER_CLOSURE_TICKS,
        "next_after_closure": next_state,
        "authority": dict(AUTHORITY_BOUNDARY),
    })


def game_projection_state(
    tick: int,
    *,
    seed: str = "HHS-I076-RENDER-GAME-PHYSICS",
) -> dict[str, Any]:
    """Bind I076 scheduling to the inherited I041 exact animation state."""
    t = _exact_nonnegative_int(tick, "tick")
    if not isinstance(seed, str) or not seed:
        raise Pass220I076RenderPhysicsError("seed must be non-empty")

    scheduler = number_theoretic_render_phase(t)
    animation = holographic_animation_state(t, seed)
    inherited_gate = animation["quartic_render_gate"]

    if inherited_gate["period"] != QUARTIC_PROJECTION_PERIOD:
        raise Pass220I076RenderPhysicsError("I041 quartic period drift")
    if inherited_gate["render"] != scheduler["projection"]["quartic_render"]:
        raise Pass220I076RenderPhysicsError("I041/I076 quartic gate mismatch")
    if inherited_gate["simulation_tick_continues"] is not True:
        raise Pass220I076RenderPhysicsError("I041 simulation clock was gated")

    return _receipt({
        "schema": f"{SCHEMA}_GAME_PROJECTION_STATE_V1",
        "tick": t,
        "seed": seed,
        "scheduler": scheduler,
        "i041_animation_receipt_sha256": animation["receipt_sha256"],
        "i041_path_linear5184": animation["pathway_node"]["linear5184"],
        "i041_quartic_render_gate": inherited_gate,
        "same_quartic_projection_decision": True,
        "rskip_bias_attached_without_deleting_physics": True,
        "render_backend_may_project_float": True,
        "canonical_float_authority": False,
        "canonical_mutation_authority": False,
    })


def self_test() -> dict[str, Any]:
    cycle = render_supercycle_witness()
    probes = (0, 1, 4, 63, 64, 71, 72, 80, 81, 5183, 5184)
    projected = tuple(game_projection_state(tick) for tick in probes)
    checks = {
        "cycle_closed": all(cycle["checks"].values()),
        "probe_count": len(projected) == len(probes),
        "quartic_match": all(
            item["same_quartic_projection_decision"]
            for item in projected
        ),
        "tick_5184_high_precision_closure": (
            projected[-1]["scheduler"]["supercycle"][
                "high_precision_closure"
            ]
            is True
        ),
        "authority_candidate_only": (
            AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"]
            is False
            and AUTHORITY_BOUNDARY["canonical_hash72_authority"] is False
            and AUTHORITY_BOUNDARY["canonical_hash216_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [key for key, value in checks.items() if not value],
        "checks": checks,
        "cycle_receipt_sha256": cycle["receipt_sha256"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "GLOBAL_RENDER_CLOSURE_TICKS",
    "Pass220I076RenderPhysicsError",
    "QUARTIC_PROJECTION_PERIOD",
    "RSKIP_DENOMINATOR",
    "RSKIP_NUMERATOR",
    "RSKIP_REDUCED",
    "game_projection_state",
    "number_theoretic_render_phase",
    "render_supercycle_witness",
    "self_test",
    "validate_render_phase",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))
