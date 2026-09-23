"""Pass 220 I035: Q144 dyadic gauge phase transport.

I035 binds the I034 exact dyadic phase operator

    2^(P*a_norm^2/144)

to the inherited I021 144-cell / 72-tooth phase machinery without turning the
phase generator into spatial magnitude.

Exact transport geometry:

    Q144 cell count      = 144
    G72 tooth count      = 72
    Q144 half-steps/tooth= 2
    2/144                = 1/72

Therefore the inherited G72 generator 2^(1/72) is the exact two-Q144-step
projection of the I035 phase step 2^(1/144).  The full 144-step phase cycle
yields the engine coefficient 2 while the I034 holographic metric lock remains
P^4/c^4=a_norm^2=1.  The coefficient belongs to the phase engine and is not
canonical metric inflation.

This is a validated-operation constructor only.  It contains local constraints
but has no canonical constraint creation/enforcement, VM81 mutation, Hash72,
Hash216, or direct persistence authority.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Tuple

from hhs_runtime.hhs_pass220_144cell_epsilon_lo_shu_closure_v1 import (
    G72_OPERATOR,
    G72_RADICAND,
    G72_ROOT_ORDER,
    HARMONIC_CELLS,
    HARMONIC_SIDE,
    g72_generator_descriptor,
    harmonic_root_closure_witness,
    p_mod_144,
    phase_matrix_144_witness,
)
from hhs_runtime.hhs_pass220_holographic_gauge_dyadic_decoupling_v1 import (
    CANONICAL_A_NORM2,
    CANONICAL_C4,
    CANONICAL_P4,
    DYADIC_BASE,
    G3_B_G2,
    Q144_PHASE_DENOMINATOR,
    build_holographic_gauge_constructor,
    validate_holographic_gauge_constructor,
)

SCHEMA = "HHS_PASS_220_I035_Q144_DYADIC_GAUGE_PHASE_TRANSPORT_V1"
VERSION = "1.0.0-checkpoint.35"
PROFILE = "PASS220-I035-Q144-DYADIC-GAUGE-PHASE-TRANSPORT-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I035_Q144_DYADIC_GAUGE_TRANSPORT_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I035_Q144_DYADIC_GAUGE_TRANSPORT_WITNESS_V1"

Q144_CELLS = HARMONIC_CELLS
Q144_SIDE = HARMONIC_SIDE
Q144_HALF_STEPS_PER_G72_TOOTH = 2
Q144_STEP_SOURCE = "2^(1/144)"
G72_AS_Q144_SOURCE = "(2^(1/144))^2=2^(2/144)=2^(1/72)"
PHASE_OPERATOR_SOURCE = "2^(P*a_norm^2/144)"

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "Q144_HAS_144_EXACT_PHASE_CELLS",
    "G72_HAS_72_EXACT_TEETH",
    "TWO_Q144_HALF_STEPS_PER_G72_TOOTH",
    "TWO_OVER_144_EQUALS_ONE_OVER_72",
    "G72_GENERATOR_IS_TWO_Q144_PHASE_STEPS",
    "Q144_PHASE_ADDRESS_WRAP_PRESERVES_UNWRAPPED_PROVENANCE",
    "FULL_144_STEP_CYCLE_EMITS_DYADIC_ENGINE_COEFFICIENT_2",
    "DYADIC_ENGINE_COEFFICIENT_NOT_CANONICAL_METRIC_INFLATION",
    "I034_HOLOGRAPHIC_LOCK_REMAINS_UNIT_RATIO",
    "TRANSITION_FRICTION_7_REMAINS_DISTINCT_FROM_DYADIC_BASE_2",
    "I021_144CELL_ZERO_SUM_PHASE_MATRIX_RETAINED",
    "NO_HOST_FLOAT_PHASE_EVALUATION",
)


class Pass220I035TransportError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I035TransportError(f"{name} must be an exact integer")
    return value


def _fraction_record(value: Fraction) -> Dict[str, int]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
    }


def q144_phase_step_descriptor() -> Dict[str, Any]:
    one_step = Fraction(1, Q144_CELLS)
    two_steps = Fraction(Q144_HALF_STEPS_PER_G72_TOOTH, Q144_CELLS)
    g72_step = Fraction(1, G72_ROOT_ORDER)
    return _receipt({
        "schema": "HHS_PASS_220_I035_Q144_PHASE_STEP_DESCRIPTOR_V1",
        "operator": "Q144_DYADIC_HALF_STEP",
        "source_term": Q144_STEP_SOURCE,
        "dyadic_base": DYADIC_BASE,
        "q144_cells": Q144_CELLS,
        "q144_step_exponent": _fraction_record(one_step),
        "g72_teeth": G72_ROOT_ORDER,
        "q144_half_steps_per_g72_tooth": Q144_HALF_STEPS_PER_G72_TOOTH,
        "two_q144_steps_exponent": _fraction_record(two_steps),
        "g72_step_exponent": _fraction_record(g72_step),
        "two_q144_steps_equal_one_g72_tooth": two_steps == g72_step,
        "bridge_identity": G72_AS_Q144_SOURCE,
        "scalar_root_evaluation_performed": False,
        "host_float_arithmetic_used": False,
        "canonical_admission_authority": False,
    })


def q144_phase_address(P: int) -> Dict[str, Any]:
    p = _exact_int(P, name="P")
    wrapped = p_mod_144(p)
    turns = (p - wrapped) // Q144_CELLS
    row12 = wrapped // Q144_SIDE
    col12 = wrapped % Q144_SIDE
    g72_tooth = wrapped // Q144_HALF_STEPS_PER_G72_TOOTH
    half_step = wrapped % Q144_HALF_STEPS_PER_G72_TOOTH
    exponent = Fraction(p * CANONICAL_A_NORM2, Q144_PHASE_DENOMINATOR)
    wrapped_exponent = Fraction(wrapped, Q144_PHASE_DENOMINATOR)

    return _receipt({
        "schema": "HHS_PASS_220_I035_Q144_PHASE_ADDRESS_V1",
        "P": p,
        "a_norm2": CANONICAL_A_NORM2,
        "phase_operator_source": PHASE_OPERATOR_SOURCE,
        "exact_exponent": _fraction_record(exponent),
        "wrapped_phase_exponent": _fraction_record(wrapped_exponent),
        "q144_index": wrapped,
        "q144_row12": row12,
        "q144_col12": col12,
        "g72_tooth72": g72_tooth,
        "g72_half_step2": half_step,
        "completed_q144_turns": turns,
        "wrapped_coordinate_period": Q144_CELLS,
        "unwrapped_P_provenance_preserved": True,
        "same_wrapped_coordinate_does_not_identify_unwrapped_state": True,
        "scalar_root_evaluation_performed": False,
        "host_float_arithmetic_used": False,
    })


def g72_q144_bridge_witness() -> Dict[str, Any]:
    q144 = q144_phase_step_descriptor()
    g72 = g72_generator_descriptor()
    closure = harmonic_root_closure_witness()
    phase_matrix = phase_matrix_144_witness()

    inherited_g72 = Fraction(1, g72["root_order"])
    q144_two = Fraction(
        Q144_HALF_STEPS_PER_G72_TOOTH,
        Q144_CELLS,
    )

    return _receipt({
        "schema": "HHS_PASS_220_I035_G72_Q144_BRIDGE_WITNESS_V1",
        "q144_step": q144,
        "inherited_g72_generator": g72,
        "inherited_g72_closure": closure,
        "inherited_phase_matrix": phase_matrix,
        "q144_cells": Q144_CELLS,
        "g72_teeth": G72_ROOT_ORDER,
        "q144_half_steps_per_g72_tooth": Q144_HALF_STEPS_PER_G72_TOOTH,
        "exact_exponent_bridge": {
            "q144_two_steps": _fraction_record(q144_two),
            "g72_one_tooth": _fraction_record(inherited_g72),
            "equal": q144_two == inherited_g72,
        },
        "g72_source_term": g72["source_term"],
        "q144_bridge_source_term": G72_AS_Q144_SOURCE,
        "g72_operator": G72_OPERATOR,
        "phase_engine_coefficient": closure["emergent_binary_coefficient"],
        "phase_engine_coefficient_expected": G72_RADICAND,
        "g72_routed_cycles": closure["routed_cycles"],
        "phase_matrix_144_closed": phase_matrix["closed"],
        "generator_scalar_preemption": False,
        "host_float_arithmetic_used": False,
        "canonical_admission_authority": False,
    })


def build_q144_dyadic_gauge_transport(
    P: int,
    *,
    depth: int = 1,
) -> Dict[str, Any]:
    p = _exact_int(P, name="P")
    depth_i = _exact_int(depth, name="depth")
    if depth_i < 0:
        raise Pass220I035TransportError("depth must be nonnegative")

    gauge = build_holographic_gauge_constructor(depth_i)
    gauge_result = validate_holographic_gauge_constructor(gauge)
    address = q144_phase_address(p)
    bridge = g72_q144_bridge_witness()

    if gauge_result["canonical_ratio"] != Fraction(1, 1):
        raise Pass220I035TransportError("I034 holographic lock is not unit ratio")

    full_cycle_engine = {
        "q144_steps": Q144_CELLS,
        "exact_total_exponent": _fraction_record(
            Fraction(Q144_CELLS, Q144_CELLS)
        ),
        "dyadic_engine_coefficient": DYADIC_BASE,
        "engine_coefficient_semantics": "PHASE_GENERATOR_CYCLE_OUTPUT",
        "canonical_metric_value": CANONICAL_A_NORM2,
        "coefficient_is_canonical_metric_inflation": False,
    }

    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "contains_constraints": True,
        "local_constraints": LOCAL_CONSTRAINTS,
        "constraint_authority": "CONSTRUCTOR_LOCAL_ONLY",
        "canonical_service": False,
        "canonical_constraint_creation_authority": False,
        "canonical_constraint_enforcement_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "parent_i034_schema": (
            "HHS_PASS_220_I034_GAUGE_RESOLUTION_CONSTRUCTOR_V1"
        ),
        "parent_i034_receipt_sha256": gauge["receipt_sha256"],
        "gauge_depth": depth_i,
        "holographic_lock": {
            "p4": CANONICAL_P4,
            "c4": CANONICAL_C4,
            "a_norm2": CANONICAL_A_NORM2,
            "ratio": (1, 1),
        },
        "transition_friction": G3_B_G2,
        "dyadic_base": DYADIC_BASE,
        "dyadic_base_distinct_from_transition_friction": (
            DYADIC_BASE != G3_B_G2
        ),
        "phase_address": address,
        "g72_q144_bridge": bridge,
        "full_cycle_engine": full_cycle_engine,
        "phase_operator_source": PHASE_OPERATOR_SOURCE,
        "phase_transport_semantics": (
            "Q144_EXACT_DYADIC_PHASE_INDEX_WITH_UNWRAPPED_PROVENANCE"
        ),
        "canonical_magnitude_inflation": False,
        "host_float_arithmetic_used": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_q144_dyadic_gauge_transport(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I035TransportError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I035TransportError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I035TransportError("constructor receipt mismatch")

    P = constructor.get("phase_address", {}).get("P")
    depth = constructor.get("gauge_depth")
    expected_address = q144_phase_address(P)
    if constructor.get("phase_address") != expected_address:
        raise Pass220I035TransportError("Q144 phase address mismatch")

    bridge = constructor.get("g72_q144_bridge")
    if not isinstance(bridge, Mapping) or bridge != g72_q144_bridge_witness():
        raise Pass220I035TransportError("G72/Q144 bridge mismatch")

    if bridge["q144_cells"] != 144 or bridge["g72_teeth"] != 72:
        raise Pass220I035TransportError("Q144/G72 cardinality drift")
    if bridge["q144_half_steps_per_g72_tooth"] != 2:
        raise Pass220I035TransportError("Q144 half-step pairing drift")
    if bridge["exact_exponent_bridge"]["equal"] is not True:
        raise Pass220I035TransportError("2/144 != 1/72 bridge failure")
    if bridge["g72_routed_cycles"] != 72:
        raise Pass220I035TransportError("G72 routed-cycle count mismatch")
    if bridge["phase_engine_coefficient"] != 2:
        raise Pass220I035TransportError("phase engine coefficient mismatch")
    if bridge["phase_matrix_144_closed"] is not True:
        raise Pass220I035TransportError("inherited 144-cell phase matrix open")
    if bridge["generator_scalar_preemption"] is not False:
        raise Pass220I035TransportError("generator scalar preemption")

    gauge = build_holographic_gauge_constructor(depth)
    gauge_result = validate_holographic_gauge_constructor(gauge)
    if gauge_result["canonical_ratio"] != Fraction(1, 1):
        raise Pass220I035TransportError("I034 gauge lock drift")
    if constructor.get("parent_i034_receipt_sha256") != gauge["receipt_sha256"]:
        raise Pass220I035TransportError("I034 parent receipt mismatch")

    lock = constructor.get("holographic_lock")
    if lock != {
        "p4": 9,
        "c4": 9,
        "a_norm2": 1,
        "ratio": (1, 1),
    }:
        raise Pass220I035TransportError("holographic lock projection mismatch")

    if constructor.get("transition_friction") != 7:
        raise Pass220I035TransportError("transition friction drift")
    if constructor.get("dyadic_base") != 2:
        raise Pass220I035TransportError("dyadic base drift")
    if constructor.get("dyadic_base_distinct_from_transition_friction") is not True:
        raise Pass220I035TransportError("dyadic base rebound to friction")

    full_cycle = constructor.get("full_cycle_engine")
    if not isinstance(full_cycle, Mapping):
        raise Pass220I035TransportError("full-cycle engine missing")
    if full_cycle.get("q144_steps") != 144:
        raise Pass220I035TransportError("full-cycle Q144 step count mismatch")
    if full_cycle.get("exact_total_exponent") != {
        "numerator": 1,
        "denominator": 1,
    }:
        raise Pass220I035TransportError("full-cycle exponent mismatch")
    if full_cycle.get("dyadic_engine_coefficient") != 2:
        raise Pass220I035TransportError("full-cycle dyadic coefficient mismatch")
    if full_cycle.get("canonical_metric_value") != 1:
        raise Pass220I035TransportError("canonical metric value drift")
    if full_cycle.get("coefficient_is_canonical_metric_inflation") is not False:
        raise Pass220I035TransportError("phase coefficient misclassified as metric inflation")

    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I035TransportError("local constraint set mismatch")
    if constructor.get("contains_constraints") is not True:
        raise Pass220I035TransportError("constructor constraints missing")
    if constructor.get("canonical_magnitude_inflation") is not False:
        raise Pass220I035TransportError("canonical magnitude inflation forbidden")
    if constructor.get("host_float_arithmetic_used") is not False:
        raise Pass220I035TransportError("host floating arithmetic forbidden")

    for field in (
        "canonical_service",
        "canonical_constraint_creation_authority",
        "canonical_constraint_enforcement_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if constructor.get(field) is not False:
            raise Pass220I035TransportError(f"authority escalation: {field}")

    return {
        "ok": True,
        "P": P,
        "depth": depth,
        "q144_index": expected_address["q144_index"],
        "q144_row12": expected_address["q144_row12"],
        "q144_col12": expected_address["q144_col12"],
        "g72_tooth72": expected_address["g72_tooth72"],
        "g72_half_step2": expected_address["g72_half_step2"],
        "completed_q144_turns": expected_address["completed_q144_turns"],
        "exact_exponent": expected_address["exact_exponent"],
        "unit_gauge_lock_preserved": True,
        "dyadic_friction_decoupling_preserved": True,
        "phase_engine_coefficient": full_cycle["dyadic_engine_coefficient"],
        "canonical_metric_value": full_cycle["canonical_metric_value"],
        "phase_engine_not_metric_inflation": True,
    }


def q144_exhaustive_transport_witness() -> Dict[str, Any]:
    rows = [q144_phase_address(P) for P in range(Q144_CELLS)]
    coordinates = {
        (row["q144_row12"], row["q144_col12"])
        for row in rows
    }
    tooth_counts = Counter(row["g72_tooth72"] for row in rows)
    half_counts = Counter(row["g72_half_step2"] for row in rows)

    wrap_pairs = []
    for P in (-289, -145, -1, 0, 1, 143, 144, 145, 10**30):
        first = q144_phase_address(P)
        second = q144_phase_address(P + Q144_CELLS)
        wrap_pairs.append({
            "P": P,
            "same_wrapped_index": (
                first["q144_index"] == second["q144_index"]
            ),
            "same_row12": first["q144_row12"] == second["q144_row12"],
            "same_col12": first["q144_col12"] == second["q144_col12"],
            "turn_delta": (
                second["completed_q144_turns"]
                - first["completed_q144_turns"]
            ),
            "unwrapped_state_distinct": first["P"] != second["P"],
        })

    bridge = g72_q144_bridge_witness()
    depth_samples = (0, 1, 2, 72, 144, 10**30)
    depth_results = []
    for depth in depth_samples:
        transport = build_q144_dyadic_gauge_transport(143, depth=depth)
        result = validate_q144_dyadic_gauge_transport(transport)
        depth_results.append({
            "depth": depth,
            "q144_index": result["q144_index"],
            "phase_engine_coefficient": result["phase_engine_coefficient"],
            "canonical_metric_value": result["canonical_metric_value"],
            "unit_gauge_lock_preserved": result["unit_gauge_lock_preserved"],
        })

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "q144_address_count": len(rows),
        "unique_q144_coordinates": len(coordinates),
        "all_q144_indices_exactly_once": (
            sorted(row["q144_index"] for row in rows)
            == list(range(Q144_CELLS))
        ),
        "all_72_teeth_have_two_half_steps": (
            len(tooth_counts) == 72
            and all(count == 2 for count in tooth_counts.values())
        ),
        "half_step_counts": dict(sorted(half_counts.items())),
        "all_wrap_pairs_preserve_coordinate": all(
            item["same_wrapped_index"]
            and item["same_row12"]
            and item["same_col12"]
            for item in wrap_pairs
        ),
        "all_wrap_pairs_advance_turn_provenance": all(
            item["turn_delta"] == 1
            and item["unwrapped_state_distinct"]
            for item in wrap_pairs
        ),
        "wrap_pairs": tuple(wrap_pairs),
        "bridge": bridge,
        "depth_results": tuple(depth_results),
        "all_depths_preserve_phase_metric_separation": all(
            item["phase_engine_coefficient"] == 2
            and item["canonical_metric_value"] == 1
            and item["unit_gauge_lock_preserved"]
            for item in depth_results
        ),
        "constructor_contains_constraints": True,
        "constructor_has_canonical_constraint_authority": False,
    })


def validate_q144_dyadic_gauge_phase_transport() -> Dict[str, Any]:
    witness = q144_exhaustive_transport_witness()
    bridge = witness["bridge"]
    ok = all((
        witness["q144_address_count"] == 144,
        witness["unique_q144_coordinates"] == 144,
        witness["all_q144_indices_exactly_once"],
        witness["all_72_teeth_have_two_half_steps"],
        witness["half_step_counts"] == {0: 72, 1: 72},
        witness["all_wrap_pairs_preserve_coordinate"],
        witness["all_wrap_pairs_advance_turn_provenance"],
        bridge["exact_exponent_bridge"]["equal"],
        bridge["phase_engine_coefficient"] == 2,
        bridge["phase_matrix_144_closed"],
        witness["all_depths_preserve_phase_metric_separation"],
        witness["constructor_contains_constraints"],
        witness["constructor_has_canonical_constraint_authority"] is False,
    ))
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": ok,
        "witness": witness,
        "mutation_policy": "READ_ONLY_Q144_DYADIC_GAUGE_CONSTRUCTOR_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
        "canonical_service": False,
        "canonical_constraint_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def q144_dyadic_gauge_phase_transport_self_test() -> Dict[str, Any]:
    return validate_q144_dyadic_gauge_phase_transport()
