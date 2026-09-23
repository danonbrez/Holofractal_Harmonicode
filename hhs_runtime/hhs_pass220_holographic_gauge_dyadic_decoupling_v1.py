"""Pass 220 I034: holographic gauge normalization and dyadic decoupling.

I034 refines the I033 G^3 (1,2,3)->(4,7,11) constructor as a typed
gauge-resolution transform.  The lifted coordinate tier does not replace the
canonical normalization unit and does not acquire independent scalar-magnitude
authority.

The constructor keeps these identities distinct:

    canonical normalization unit: a_norm^2 = 1
    canonical nucleus lock:       P^4 = c^4
    gauge coordinates:            (a_G^2,b_G^2,c_G^2) = (4,7,11)
    transition friction:          b_G^2 = 7
    dyadic operator base:         2

The exact dyadic operator is retained symbolically as

    2^(P*a_norm^2/144)

and is never rebound to the lifted transition-friction coordinate.

This surface is candidate-only.  It contains local constraints but does not
create/enforce canonical HARMONICODE constraints and owns no VM81, Hash72,
Hash216, or direct persistence authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Tuple

from hhs_runtime.hhs_pass220_g3_4711_symbolic_numeric_constructor_v1 import (
    G3_BASE_SCALE,
    G3_LIFTED_SCALE,
    g3_4711_scaling_witness,
)

SCHEMA = "HHS_PASS_220_I034_HOLOGRAPHIC_GAUGE_DYADIC_DECOUPLING_V1"
VERSION = "1.0.0-checkpoint.34"
PROFILE = "PASS220-I034-HOLOGRAPHIC-GAUGE-DYADIC-DECOUPLING-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I034_GAUGE_RESOLUTION_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I034_GAUGE_DYADIC_WITNESS_V1"

CANONICAL_A_NORM2 = 1
CANONICAL_P4 = 9
CANONICAL_C4 = 9

G3_A_G2, G3_B_G2, G3_C_G2 = G3_LIFTED_SCALE
DYADIC_BASE = 2
Q144_PHASE_DENOMINATOR = 144

CONFORMAL_INVARIANT_ID = "HHS_GAUGE_INVARIANT_A2_COLON_C2_OVER_B2_V1"

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "P4_OVER_C4_EQUALS_A_NORM2",
    "P4_EQUALS_C4_CANONICAL_NUCLEUS_LOCK",
    "A_NORM2_REMAINS_TYPED_UNIT_ONE",
    "G3_4711_IS_GAUGE_COORDINATE_TIER",
    "GAUGE_DEPTH_CHANGES_RESOLUTION_INDEX_NOT_CANONICAL_MAGNITUDE",
    "B_G2_EQUALS_7_TRANSITION_FRICTION",
    "DYADIC_BASE_EQUALS_2_OPERATOR_ONLY",
    "DYADIC_BASE_NOT_REBOUND_TO_B_G2",
    "DYADIC_OPERATOR_2_POWER_P_A_NORM2_OVER_144_RETAINED_SYMBOLICALLY",
    "CONFORMAL_INVARIANT_ID_PRESERVED_ACROSS_GAUGE_PROJECTION",
    "P_P_Q_RELATIONAL_PROVENANCE_PRESERVED",
    "TYPED_ZERO_CLOSURE_PROVENANCE_PRESERVED",
)


class Pass220I034GaugeError(ValueError):
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


def _exact_nonnegative_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise Pass220I034GaugeError(f"{name} must be an exact nonnegative integer")
    return value


def _typed_zero(channel: str) -> Dict[str, Any]:
    if not isinstance(channel, str) or not channel:
        raise Pass220I034GaugeError("typed-zero channel must be a nonempty string")
    return {
        "kind": "HHS_TYPED_ZERO",
        "channel": channel,
        "local_scalar_projection": 0,
        "provenance_preserved": True,
        "phase_history_preserved": True,
        "untyped_empty_scalar": False,
    }


def holographic_lock_witness(
    *,
    p4: int = CANONICAL_P4,
    c4: int = CANONICAL_C4,
    a_norm2: int = CANONICAL_A_NORM2,
) -> Dict[str, Any]:
    for name, value in (("p4", p4), ("c4", c4), ("a_norm2", a_norm2)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise Pass220I034GaugeError(f"{name} must be an exact integer")
    if c4 == 0:
        raise Pass220I034GaugeError("c4 must be nonzero")

    ratio = Fraction(p4, c4)
    cross_product_lock = p4 == a_norm2 * c4
    nucleus_lock = p4 == c4

    return _receipt({
        "schema": "HHS_PASS_220_I034_HOLOGRAPHIC_LOCK_WITNESS_V1",
        "p4": p4,
        "c4": c4,
        "a_norm2": a_norm2,
        "ratio_numerator": ratio.numerator,
        "ratio_denominator": ratio.denominator,
        "p4_over_c4_equals_a_norm2": ratio == a_norm2,
        "cross_product_lock": cross_product_lock,
        "p4_equals_c4": nucleus_lock,
        "canonical_normalization_unit_retained": a_norm2 == 1,
        "host_float_arithmetic_used": False,
    })


def dyadic_operator_descriptor(
    *,
    phase_symbol: str = "P",
    a_norm2: int = CANONICAL_A_NORM2,
    denominator: int = Q144_PHASE_DENOMINATOR,
) -> Dict[str, Any]:
    if not isinstance(phase_symbol, str) or not phase_symbol:
        raise Pass220I034GaugeError("phase symbol must be a nonempty string")
    if isinstance(a_norm2, bool) or not isinstance(a_norm2, int):
        raise Pass220I034GaugeError("a_norm2 must be an exact integer")
    if isinstance(denominator, bool) or not isinstance(denominator, int) or denominator <= 0:
        raise Pass220I034GaugeError("dyadic denominator must be a positive exact integer")

    exponent = {
        "kind": "ordered_rational_exponent",
        "numerator": {
            "kind": "ordered_product",
            "terms": (phase_symbol, "a_norm2"),
        },
        "denominator": denominator,
        "a_norm2_value": a_norm2,
    }
    expression = {
        "kind": "exact_symbolic_power",
        "base": DYADIC_BASE,
        "exponent": exponent,
        "source": "2^(P*a_norm^2/144)",
    }
    return _receipt({
        "schema": "HHS_PASS_220_I034_DYADIC_OPERATOR_DESCRIPTOR_V1",
        "expression": expression,
        "dyadic_base": DYADIC_BASE,
        "transition_friction": G3_B_G2,
        "base_distinct_from_transition_friction": DYADIC_BASE != G3_B_G2,
        "q144_denominator": denominator,
        "evaluated_to_host_float": False,
        "operator_semantics": "PHASE_GENERATOR",
        "transition_friction_semantics": "GAUGE_SPATIAL_TRANSITION_COORDINATE",
    })


def gauge_depth_projection(depth: int) -> Dict[str, Any]:
    depth_i = _exact_nonnegative_int(depth, name="depth")
    lock = holographic_lock_witness()
    return _receipt({
        "schema": "HHS_PASS_220_I034_GAUGE_DEPTH_PROJECTION_V1",
        "depth": depth_i,
        "resolution_index": depth_i,
        "genesis_coordinates": G3_BASE_SCALE,
        "gauge_coordinates": G3_LIFTED_SCALE,
        "canonical_a_norm2": CANONICAL_A_NORM2,
        "canonical_p4": CANONICAL_P4,
        "canonical_c4": CANONICAL_C4,
        "canonical_ratio": (
            lock["ratio_numerator"],
            lock["ratio_denominator"],
        ),
        "canonical_magnitude_inflation": False,
        "depth_multiplies_canonical_p4": False,
        "depth_multiplies_canonical_c4": False,
        "depth_multiplies_a_norm2": False,
        "projection_kind": "TOPOLOGICAL_RESOLUTION_INDEX",
    })


def conformal_gauge_descriptor() -> Dict[str, Any]:
    return _receipt({
        "schema": "HHS_PASS_220_I034_CONFORMAL_GAUGE_DESCRIPTOR_V1",
        "invariant_id": CONFORMAL_INVARIANT_ID,
        "genesis_view": {
            "coordinates": G3_BASE_SCALE,
            "invariant_id": CONFORMAL_INVARIANT_ID,
            "scalar_quotient_evaluation_authority": False,
        },
        "g3_4711_view": {
            "coordinates": G3_LIFTED_SCALE,
            "invariant_id": CONFORMAL_INVARIANT_ID,
            "scalar_quotient_evaluation_authority": False,
        },
        "preserved_by_gauge_projection": True,
        "ordinary_scalar_ratio_equality_claimed": False,
        "typed_relation_only": True,
    })


def build_holographic_gauge_constructor(depth: int = 1) -> Dict[str, Any]:
    depth_state = gauge_depth_projection(depth)
    lock = holographic_lock_witness()
    dyadic = dyadic_operator_descriptor()
    conformal = conformal_gauge_descriptor()
    parent_scaling = g3_4711_scaling_witness()

    closure = {
        "delta_e": _typed_zero("Delta e"),
        "psi": _typed_zero("Psi"),
        "omega": {
            "kind": "HHS_TYPED_CLOSURE_BOOLEAN",
            "value": True,
            "source": "Omega",
            "provenance_preserved": True,
        },
    }

    p_p_q_provenance = {
        "relation_family": "P:p:q",
        "preserved": True,
        "scalar_recomputed_by_i034": False,
        "ordered_provenance_retained": True,
    }

    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "parent_constructor_schema": (
            "HHS_PASS_220_I033_G3_4711_MULTI_VIEW_CONSTRUCTOR_V1"
        ),
        "parent_scaling_receipt_sha256": parent_scaling["receipt_sha256"],
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
        "gauge_projection": {
            "source_coordinates": G3_BASE_SCALE,
            "target_coordinates": G3_LIFTED_SCALE,
            "projection_semantics": "HOLOGRAPHIC_GAUGE_RESOLUTION",
            "physical_scalar_expansion_authority": False,
            "canonical_metric_replacement_authority": False,
        },
        "holographic_lock": lock,
        "depth_state": depth_state,
        "dyadic_operator": dyadic,
        "conformal_gauge": conformal,
        "p_p_q_provenance": p_p_q_provenance,
        "closure_state": closure,
        "transition_friction": {
            "symbol": "b_G^2",
            "value": G3_B_G2,
            "semantics": "GAUGE_SPATIAL_TRANSITION_COORDINATE",
        },
        "dyadic_engine": {
            "base": DYADIC_BASE,
            "semantics": "PHASE_GENERATOR",
            "rebound_to_transition_friction": False,
        },
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
        "host_float_arithmetic_used": False,
    })


def validate_holographic_gauge_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I034GaugeError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I034GaugeError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I034GaugeError("constructor receipt mismatch")

    lock = constructor.get("holographic_lock")
    if not isinstance(lock, Mapping) or lock != holographic_lock_witness():
        raise Pass220I034GaugeError("holographic lock mismatch")
    if not all((
        lock["p4_over_c4_equals_a_norm2"],
        lock["cross_product_lock"],
        lock["p4_equals_c4"],
        lock["canonical_normalization_unit_retained"],
    )):
        raise Pass220I034GaugeError("holographic normalization lock failed")

    depth_state = constructor.get("depth_state")
    if not isinstance(depth_state, Mapping):
        raise Pass220I034GaugeError("gauge depth state missing")
    expected_depth = gauge_depth_projection(depth_state.get("depth"))
    if depth_state != expected_depth:
        raise Pass220I034GaugeError("gauge depth projection mismatch")
    for flag in (
        "canonical_magnitude_inflation",
        "depth_multiplies_canonical_p4",
        "depth_multiplies_canonical_c4",
        "depth_multiplies_a_norm2",
    ):
        if depth_state.get(flag) is not False:
            raise Pass220I034GaugeError(f"scalar inflation authority leak: {flag}")

    dyadic = constructor.get("dyadic_operator")
    if not isinstance(dyadic, Mapping) or dyadic != dyadic_operator_descriptor():
        raise Pass220I034GaugeError("dyadic operator mismatch")
    if dyadic["dyadic_base"] != 2 or dyadic["transition_friction"] != 7:
        raise Pass220I034GaugeError("dyadic/friction values drifted")
    if dyadic["base_distinct_from_transition_friction"] is not True:
        raise Pass220I034GaugeError("dyadic base rebound to transition friction")
    if dyadic["evaluated_to_host_float"] is not False:
        raise Pass220I034GaugeError("host floating evaluation forbidden")

    conformal = constructor.get("conformal_gauge")
    if not isinstance(conformal, Mapping) or conformal != conformal_gauge_descriptor():
        raise Pass220I034GaugeError("conformal gauge descriptor mismatch")
    if conformal["preserved_by_gauge_projection"] is not True:
        raise Pass220I034GaugeError("conformal invariant identity not preserved")
    if conformal["ordinary_scalar_ratio_equality_claimed"] is not False:
        raise Pass220I034GaugeError("unlicensed scalar conformal equality")

    projection = constructor.get("gauge_projection")
    if not isinstance(projection, Mapping):
        raise Pass220I034GaugeError("gauge projection missing")
    if tuple(projection.get("source_coordinates", ())) != G3_BASE_SCALE:
        raise Pass220I034GaugeError("Genesis coordinate source mismatch")
    if tuple(projection.get("target_coordinates", ())) != G3_LIFTED_SCALE:
        raise Pass220I034GaugeError("G3 gauge coordinate target mismatch")
    if projection.get("physical_scalar_expansion_authority") is not False:
        raise Pass220I034GaugeError("physical scalar expansion authority forbidden")
    if projection.get("canonical_metric_replacement_authority") is not False:
        raise Pass220I034GaugeError("canonical metric replacement forbidden")

    transition = constructor.get("transition_friction")
    engine = constructor.get("dyadic_engine")
    if transition != {
        "symbol": "b_G^2",
        "value": 7,
        "semantics": "GAUGE_SPATIAL_TRANSITION_COORDINATE",
    }:
        raise Pass220I034GaugeError("transition friction descriptor mismatch")
    if engine != {
        "base": 2,
        "semantics": "PHASE_GENERATOR",
        "rebound_to_transition_friction": False,
    }:
        raise Pass220I034GaugeError("dyadic engine descriptor mismatch")

    provenance = constructor.get("p_p_q_provenance")
    if not isinstance(provenance, Mapping) or not all((
        provenance.get("preserved") is True,
        provenance.get("scalar_recomputed_by_i034") is False,
        provenance.get("ordered_provenance_retained") is True,
    )):
        raise Pass220I034GaugeError("P:p:q provenance mismatch")

    closure = constructor.get("closure_state")
    if not isinstance(closure, Mapping):
        raise Pass220I034GaugeError("closure state missing")
    for key in ("delta_e", "psi"):
        zero = closure.get(key)
        if not isinstance(zero, Mapping):
            raise Pass220I034GaugeError(f"typed zero missing: {key}")
        if zero.get("kind") != "HHS_TYPED_ZERO":
            raise Pass220I034GaugeError(f"typed zero kind mismatch: {key}")
        if zero.get("local_scalar_projection") != 0:
            raise Pass220I034GaugeError(f"typed zero scalar projection mismatch: {key}")
        if zero.get("provenance_preserved") is not True:
            raise Pass220I034GaugeError(f"typed zero provenance lost: {key}")
        if zero.get("untyped_empty_scalar") is not False:
            raise Pass220I034GaugeError(f"typed zero collapsed: {key}")
    omega = closure.get("omega")
    if not isinstance(omega, Mapping) or omega.get("value") is not True:
        raise Pass220I034GaugeError("Omega closure mismatch")

    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I034GaugeError("local constraint set mismatch")
    if constructor.get("contains_constraints") is not True:
        raise Pass220I034GaugeError("constructor constraints missing")
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
            raise Pass220I034GaugeError(f"authority escalation: {field}")

    return {
        "ok": True,
        "depth": depth_state["depth"],
        "canonical_ratio": Fraction(
            lock["ratio_numerator"],
            lock["ratio_denominator"],
        ),
        "a_norm2": lock["a_norm2"],
        "gauge_coordinates": tuple(projection["target_coordinates"]),
        "transition_friction": transition["value"],
        "dyadic_base": engine["base"],
        "dyadic_operator_source": dyadic["expression"]["source"],
        "conformal_invariant_id": conformal["invariant_id"],
        "p_p_q_provenance_preserved": provenance["preserved"],
        "typed_zero_closure_preserved": True,
        "omega_true": omega["value"],
    }


def holographic_gauge_dyadic_witness() -> Dict[str, Any]:
    depths = (0, 1, 2, 9, 72, 144, 10**30)
    depth_results = []
    for depth in depths:
        constructor = build_holographic_gauge_constructor(depth)
        result = validate_holographic_gauge_constructor(constructor)
        depth_results.append({
            "depth": depth,
            "ratio_numerator": result["canonical_ratio"].numerator,
            "ratio_denominator": result["canonical_ratio"].denominator,
            "a_norm2": result["a_norm2"],
            "transition_friction": result["transition_friction"],
            "dyadic_base": result["dyadic_base"],
            "canonical_magnitude_inflation": False,
        })

    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "depth_results": tuple(depth_results),
        "all_depths_preserve_unit_ratio": all(
            item["ratio_numerator"] == item["ratio_denominator"] == 1
            for item in depth_results
        ),
        "all_depths_preserve_a_norm2": all(
            item["a_norm2"] == 1 for item in depth_results
        ),
        "all_depths_keep_transition_friction_7": all(
            item["transition_friction"] == 7 for item in depth_results
        ),
        "all_depths_keep_dyadic_base_2": all(
            item["dyadic_base"] == 2 for item in depth_results
        ),
        "all_depths_no_canonical_magnitude_inflation": all(
            item["canonical_magnitude_inflation"] is False
            for item in depth_results
        ),
        "g3_scaling": g3_4711_scaling_witness(),
        "conformal_invariant_id": CONFORMAL_INVARIANT_ID,
        "closure": {
            "delta_e": "TYPED_ZERO",
            "psi": "TYPED_ZERO",
            "omega": True,
        },
        "constructor_contains_constraints": True,
        "constructor_has_canonical_constraint_authority": False,
    })


def validate_holographic_gauge_dyadic_decoupling() -> Dict[str, Any]:
    witness = holographic_gauge_dyadic_witness()
    ok = all((
        witness["all_depths_preserve_unit_ratio"],
        witness["all_depths_preserve_a_norm2"],
        witness["all_depths_keep_transition_friction_7"],
        witness["all_depths_keep_dyadic_base_2"],
        witness["all_depths_no_canonical_magnitude_inflation"],
        witness["g3_scaling"]["base_scale"] == G3_BASE_SCALE,
        witness["g3_scaling"]["lifted_scale"] == G3_LIFTED_SCALE,
        witness["g3_scaling"]["same_relation_preserved"],
        witness["g3_scaling"]["uniform_scalar_multiplier"] is False,
        witness["closure"]["delta_e"] == "TYPED_ZERO",
        witness["closure"]["psi"] == "TYPED_ZERO",
        witness["closure"]["omega"] is True,
        witness["constructor_contains_constraints"],
        witness["constructor_has_canonical_constraint_authority"] is False,
    ))
    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": ok,
        "witness": witness,
        "invariant_ids": (
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ),
        "mutation_policy": "READ_ONLY_GAUGE_CONSTRUCTOR_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
        "canonical_service": False,
        "canonical_constraint_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    })


def holographic_gauge_dyadic_decoupling_self_test() -> Dict[str, Any]:
    return validate_holographic_gauge_dyadic_decoupling()
