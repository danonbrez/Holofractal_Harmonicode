"""Pass 219 RML4 eight-channel dynamic octonion gyroscope.

RML4 is an additive successor to the frozen RML2/RML3 phase geometry.  It
models x,y,z,w,xy,yx,zw,wz as eight continuously addressable u^72 imaginary
phase rotations on one gyroscope.

The four primitive channels retain the inherited orthogonal-plane geometry.
The four ordered product channels are not a second gyroscope: each is a
quarter-turn image of its generating primitive in the direction of the ordered
reciprocal operand.  The signed direction of that quarter turn remains an
explicit witness because orientation is semantic state and must not be guessed
from a scalar projection.

The ambient address space is exactly 72^8 states.  Product quarter-turn
constraints select admissible states/trajectories from that ambient manifold;
the implementation does not claim that all 72^8 ambient tuples are mutually
admissible.

Addition, multiplication and exponentiation are represented as typed modes of
one underlying SIGNED_IMAGINARY_PHASE_ROTATION primitive.  Original operator,
operand order, nesting and ancestry remain receipt-visible.

RML4 is read-only with respect to canonical VM81/Hash authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.pass219.phase_geometry_learning import (
    CCW,
    CW,
    HALF_CYCLE,
    ORTHOGONAL_PLANE,
    PHASE_MODULUS,
    PRIMARY_PLANE,
    QUARTER_CYCLE,
)
from hhs_runtime.pass219.production_phase_geometry_binding import SOURCE_SCHEMA as RML3_SOURCE_SCHEMA

PASS = 219
ITERATION = "RML4_DYNAMIC_OCTONION_GYROSCOPE"

CHANNELS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PRIMITIVES = ("x", "y", "z", "w")
PRODUCTS = ("xy", "yx", "zw", "wz")
FULL_CYCLE_DEGREES = 360
DEGREES_PER_PHASE_STEP = FULL_CYCLE_DEGREES // PHASE_MODULUS
AMBIENT_STATE_COUNT = PHASE_MODULUS ** len(CHANNELS)

GYROSCOPE_SCHEMA = "HHS_PASS219_RML4_EIGHT_CHANNEL_DYNAMIC_GYROSCOPE_V1"
TRANSITION_SCHEMA = "HHS_PASS219_RML4_DYNAMIC_GYROSCOPE_TRANSITION_V1"
OPERATION_SCHEMA = "HHS_PASS219_RML4_UNIFIED_PHASE_OPERATION_V1"
RML3_BINDING_SCHEMA = "HHS_PASS219_RML4_RML3_DYNAMIC_GYROSCOPE_BINDING_V1"

PRIMITIVE_GEOMETRY = {
    "x": {"plane": PRIMARY_PLANE, "direction": CW, "signed_orientation": 1},
    "y": {"plane": ORTHOGONAL_PLANE, "direction": CCW, "signed_orientation": -1},
    "z": {"plane": PRIMARY_PLANE, "direction": CCW, "signed_orientation": -1},
    "w": {"plane": ORTHOGONAL_PLANE, "direction": CW, "signed_orientation": 1},
}

# Ordered product = same gyroscope after a directed quarter turn toward the
# reciprocal operand.  The scalar sign of that turn is supplied explicitly by
# the caller and is never inferred by swapping operands.
PRODUCT_RELATIONS = {
    "xy": {"generator": "x", "reciprocal": "y"},
    "yx": {"generator": "y", "reciprocal": "x"},
    "zw": {"generator": "z", "reciprocal": "w"},
    "wz": {"generator": "w", "reciprocal": "z"},
}

UNIFIED_ROTATION_PRIMITIVE = "SIGNED_IMAGINARY_PHASE_ROTATION"


class DynamicGyroscopeError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise DynamicGyroscopeError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DynamicGyroscopeError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _phase(value: Any, label: str) -> int:
    integer = _exact_int(value, label)
    if integer < 0 or integer >= PHASE_MODULUS:
        raise DynamicGyroscopeError(f"{label}_PHASE72_OUT_OF_RANGE")
    return integer


def _normalize_phases(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping) or tuple(value.keys()) != CHANNELS:
        raise DynamicGyroscopeError("ORDERED_EIGHT_CHANNEL_PHASE_STATE_REQUIRED")
    return {channel: _phase(value[channel], channel.upper()) for channel in CHANNELS}


def _normalize_quarter_turn_signs(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping) or tuple(value.keys()) != PRODUCTS:
        raise DynamicGyroscopeError("ORDERED_PRODUCT_QUARTER_TURN_SIGNS_REQUIRED")
    result: dict[str, int] = {}
    for product in PRODUCTS:
        sign = _exact_int(value[product], f"{product.upper()}_QUARTER_TURN_SIGN")
        if sign not in (-1, 1):
            raise DynamicGyroscopeError(f"{product.upper()}_QUARTER_TURN_SIGN_MUST_BE_PLUS_OR_MINUS_ONE")
        result[product] = sign
    return result


def phase_to_exact_angle(phase72: int) -> dict[str, Any]:
    phase = _phase(phase72, "PHASE")
    return {
        "phase72": phase,
        "u_phase": f"u^{phase}",
        "angle_degrees": phase * DEGREES_PER_PHASE_STEP,
        "degrees_per_phase_step": DEGREES_PER_PHASE_STEP,
        "full_cycle_degrees": FULL_CYCLE_DEGREES,
        "half_circle_index": phase // HALF_CYCLE,
        "phase_within_half_circle": phase % HALF_CYCLE,
        "typed_u0_is_scalar_zero": False,
    }


def encode_ambient_state(phases: Mapping[str, Any]) -> int:
    normalized = _normalize_phases(phases)
    index = 0
    for channel in CHANNELS:
        index = index * PHASE_MODULUS + normalized[channel]
    if index < 0 or index >= AMBIENT_STATE_COUNT:
        raise AssertionError("RML4_AMBIENT_STATE_INDEX_INTERNAL_RANGE")
    return index


def decode_ambient_state(index: int) -> dict[str, int]:
    value = _exact_int(index, "AMBIENT_STATE_INDEX")
    if value < 0 or value >= AMBIENT_STATE_COUNT:
        raise DynamicGyroscopeError("AMBIENT_STATE_INDEX_OUT_OF_RANGE")
    digits = [0] * len(CHANNELS)
    remainder = value
    for position in range(len(CHANNELS) - 1, -1, -1):
        digits[position] = remainder % PHASE_MODULUS
        remainder //= PHASE_MODULUS
    return {channel: digits[i] for i, channel in enumerate(CHANNELS)}


def _cyclic_distance(a: int, b: int) -> int:
    forward = (a - b) % PHASE_MODULUS
    reverse = (b - a) % PHASE_MODULUS
    return min(forward, reverse)


def expected_product_phase(
    generator_phase72: int,
    quarter_turn_sign: int,
) -> int:
    generator = _phase(generator_phase72, "GENERATOR_PHASE")
    sign = _exact_int(quarter_turn_sign, "QUARTER_TURN_SIGN")
    if sign not in (-1, 1):
        raise DynamicGyroscopeError("QUARTER_TURN_SIGN_MUST_BE_PLUS_OR_MINUS_ONE")
    return (generator + sign * QUARTER_CYCLE) % PHASE_MODULUS


def evaluate_product_constraints(
    phases: Mapping[str, Any],
    quarter_turn_signs: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = _normalize_phases(phases)
    signs = _normalize_quarter_turn_signs(quarter_turn_signs)
    rows: list[dict[str, Any]] = []
    total = 0
    for product in PRODUCTS:
        relation = PRODUCT_RELATIONS[product]
        generator = relation["generator"]
        reciprocal = relation["reciprocal"]
        expected = expected_product_phase(normalized[generator], signs[product])
        actual = normalized[product]
        distance = _cyclic_distance(actual, expected)
        total += distance
        rows.append(
            {
                "product": product,
                "generator": generator,
                "reciprocal": reciprocal,
                "quarter_turn_direction": "TOWARD_ORDERED_RECIPROCAL",
                "quarter_turn_sign": signs[product],
                "quarter_turn_magnitude_steps": QUARTER_CYCLE,
                "quarter_turn_magnitude_degrees": QUARTER_CYCLE * DEGREES_PER_PHASE_STEP,
                "expected_product_phase72": expected,
                "actual_product_phase72": actual,
                "disequilibrium_units": distance,
                "satisfied": distance == 0,
                "same_gyroscope_not_second_gyroscope": True,
            }
        )
    return {
        "relations": rows,
        "quarter_turn_disequilibrium_units": total,
        "all_product_quarter_turn_relations_satisfied": total == 0,
        "commutative_product_collapse_permitted": False,
        "scalar_projection_substitution_authority": False,
    }


def build_gyroscope_state(
    phases: Mapping[str, Any],
    quarter_turn_signs: Mapping[str, Any],
    *,
    state_id: str,
    ancestry_root_sha256: str | None = None,
    legacy_i148_product_phase72: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _reject_float(phases)
    normalized = _normalize_phases(phases)
    signs = _normalize_quarter_turn_signs(quarter_turn_signs)
    constraints = evaluate_product_constraints(normalized, signs)

    channels: dict[str, dict[str, Any]] = {}
    for channel in CHANNELS:
        base = phase_to_exact_angle(normalized[channel])
        if channel in PRIMITIVES:
            channels[channel] = {
                **base,
                "channel": channel,
                "role": "ORTHOGONAL_GYROSCOPE_PRIMITIVE",
                "imaginary_3d_frame": dict(PRIMITIVE_GEOMETRY[channel]),
                "continuously_rotating": True,
            }
        else:
            relation = PRODUCT_RELATIONS[channel]
            channels[channel] = {
                **base,
                "channel": channel,
                "role": "RECIPROCAL_QUARTER_TURN_IMAGE_OF_SAME_GYROSCOPE",
                "generator": relation["generator"],
                "reciprocal": relation["reciprocal"],
                "quarter_turn_sign": signs[channel],
                "quarter_turn_steps": QUARTER_CYCLE,
                "quarter_turn_degrees": QUARTER_CYCLE * DEGREES_PER_PHASE_STEP,
                "quarter_turn_direction": "TOWARD_ORDERED_RECIPROCAL",
                "continuously_rotating": True,
            }

    legacy: dict[str, int] | None = None
    if legacy_i148_product_phase72 is not None:
        if not isinstance(legacy_i148_product_phase72, Mapping):
            raise DynamicGyroscopeError("LEGACY_I148_PRODUCT_PHASE_MAPPING_REQUIRED")
        legacy = {
            product: _phase(legacy_i148_product_phase72.get(product), f"LEGACY_{product.upper()}")
            for product in PRODUCTS
        }

    state = {
        "schema": GYROSCOPE_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "state_id": str(state_id),
        "channel_order": list(CHANNELS),
        "phase_modulus": PHASE_MODULUS,
        "full_cycle_degrees": FULL_CYCLE_DEGREES,
        "ambient_state_count": AMBIENT_STATE_COUNT,
        "ambient_state_index": encode_ambient_state(normalized),
        "phases": normalized,
        "quarter_turn_signs": signs,
        "channels": channels,
        "product_constraints": constraints,
        "admissible_product_geometry": constraints["all_product_quarter_turn_relations_satisfied"],
        "legacy_i148_product_phase72": legacy,
        "legacy_i148_product_phase_is_dynamic_product_identity": False if legacy is not None else None,
        "ancestry_root_sha256": ancestry_root_sha256,
        "eight_channels_are_one_gyroscope": True,
        "product_channels_are_reciprocal_quarter_turn_images": True,
        "ambient_72_pow_8_is_admissible_cardinality_claim": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    state["state_sha256"] = _sha256(state)
    return state


def advance_gyroscope(
    state: Mapping[str, Any],
    signed_steps: Mapping[str, Any],
    *,
    transition_id: str,
) -> dict[str, Any]:
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise DynamicGyroscopeError("RML4_GYROSCOPE_STATE_SCHEMA_MISMATCH")
    phases = _normalize_phases(state.get("phases"))
    signs = _normalize_quarter_turn_signs(state.get("quarter_turn_signs"))
    if not isinstance(signed_steps, Mapping) or tuple(signed_steps.keys()) != CHANNELS:
        raise DynamicGyroscopeError("ORDERED_EIGHT_CHANNEL_SIGNED_STEPS_REQUIRED")
    deltas = {channel: _exact_int(signed_steps[channel], f"{channel.upper()}_SIGNED_STEP") for channel in CHANNELS}
    next_phases = {
        channel: (phases[channel] + deltas[channel]) % PHASE_MODULUS
        for channel in CHANNELS
    }
    next_state = build_gyroscope_state(
        next_phases,
        signs,
        state_id=f"{state.get('state_id')}->{transition_id}",
        ancestry_root_sha256=state.get("state_sha256"),
        legacy_i148_product_phase72=state.get("legacy_i148_product_phase72"),
    )
    transition = {
        "schema": TRANSITION_SCHEMA,
        "transition_id": str(transition_id),
        "prior_state_sha256": state.get("state_sha256"),
        "prior_ambient_state_index": state.get("ambient_state_index"),
        "signed_steps": deltas,
        "rotation_directions": {
            channel: "PLUS" if deltas[channel] > 0 else "MINUS" if deltas[channel] < 0 else "HOLD"
            for channel in CHANNELS
        },
        "next_state": next_state,
        "all_eight_local_phase_coordinates_updated_by_same_rotation_primitive": True,
        "underlying_primitive": UNIFIED_ROTATION_PRIMITIVE,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    transition["transition_sha256"] = _sha256(transition)
    return transition


def unified_phase_operation(
    state: Mapping[str, Any],
    *,
    operator: str,
    ordered_operands: list[str],
    signed_step: int = 0,
    repetitions: int = 1,
    product_channel: str | None = None,
) -> dict[str, Any]:
    """Express +, *, and ^ as typed modes of one phase-rotation primitive.

    This is an execution witness, not ordinary scalar algebra.  It intentionally
    preserves the source operator and operand order.
    """
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise DynamicGyroscopeError("RML4_GYROSCOPE_STATE_SCHEMA_MISMATCH")
    if operator not in ("+", "*", "^"):
        raise DynamicGyroscopeError("RML4_UNIFIED_OPERATOR_UNSUPPORTED")
    if not isinstance(ordered_operands, list) or not ordered_operands or any(ch not in CHANNELS for ch in ordered_operands):
        raise DynamicGyroscopeError("RML4_ORDERED_OPERANDS_REQUIRED")
    step = _exact_int(signed_step, "SIGNED_STEP")
    repeat = _exact_int(repetitions, "REPETITIONS")
    if repeat < 1:
        raise DynamicGyroscopeError("REPETITIONS_MUST_BE_POSITIVE")

    phases = _normalize_phases(state.get("phases"))
    signs = _normalize_quarter_turn_signs(state.get("quarter_turn_signs"))
    mode: str
    witness: dict[str, Any]

    if operator == "+":
        mode = "COUPLED_PHASE_ROTATION"
        witness = {
            "coupled_channels": list(ordered_operands),
            "rotated_phase72": {
                channel: (phases[channel] + step) % PHASE_MODULUS
                for channel in ordered_operands
            },
            "operand_identity_preserved": True,
            "scalar_sum_materialized": False,
        }
    elif operator == "*":
        mode = "ORDERED_RECIPROCAL_QUARTER_TURN"
        if product_channel not in PRODUCTS:
            raise DynamicGyroscopeError("RML4_PRODUCT_CHANNEL_REQUIRED")
        relation = PRODUCT_RELATIONS[str(product_channel)]
        if ordered_operands != [relation["generator"], relation["reciprocal"]]:
            raise DynamicGyroscopeError("RML4_PRODUCT_OPERAND_ORDER_DRIFT")
        witness = {
            "product_channel": product_channel,
            "generator": relation["generator"],
            "reciprocal": relation["reciprocal"],
            "quarter_turn_sign": signs[str(product_channel)],
            "quarter_turn_steps": QUARTER_CYCLE,
            "product_phase72": expected_product_phase(
                phases[relation["generator"]],
                signs[str(product_channel)],
            ),
            "same_gyroscope": True,
            "scalar_product_materialized": False,
        }
    else:
        mode = "RECURSIVE_PHASE_ORBIT"
        if len(ordered_operands) != 1:
            raise DynamicGyroscopeError("RML4_POWER_SINGLE_ORDERED_OPERAND_REQUIRED")
        channel = ordered_operands[0]
        orbit = [phases[channel]]
        phase = phases[channel]
        for _ in range(repeat):
            phase = (phase + step) % PHASE_MODULUS
            orbit.append(phase)
        witness = {
            "channel": channel,
            "signed_step": step,
            "repetitions": repeat,
            "phase_orbit72": orbit,
            "recursive_nesting_preserved": True,
            "scalar_power_materialized": False,
        }

    result = {
        "schema": OPERATION_SCHEMA,
        "source_operator": operator,
        "mode": mode,
        "underlying_primitive": UNIFIED_ROTATION_PRIMITIVE,
        "ordered_operands": list(ordered_operands),
        "source_state_sha256": state.get("state_sha256"),
        "witness": witness,
        "operator_identity_preserved": True,
        "operand_order_preserved": True,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["operation_sha256"] = _sha256(result)
    return result


def build_dynamic_gyroscopes_from_rml3_source(
    source: Mapping[str, Any],
    quarter_turn_signs: Mapping[str, Any],
) -> dict[str, Any]:
    """Lift a frozen RML3 physical phase source into RML4 dynamic geometry.

    Primitive x/y/z/w phase coordinates are inherited exactly from I148.
    Existing I148 xy/yx/zw/wz values remain provenance evidence, while the new
    RML4 product coordinates are generated as reciprocal quarter-turn images.
    This explicitly avoids reinterpreting frozen I148 products in place.
    """
    _reject_float(source)
    if source.get("schema") != RML3_SOURCE_SCHEMA:
        raise DynamicGyroscopeError("RML3_PHASE_SOURCE_SCHEMA_MISMATCH")
    if source.get("phase_ring") != PHASE_MODULUS:
        raise DynamicGyroscopeError("RML3_PHASE_RING_DRIFT")
    ledger = source.get("channel_ledger")
    if not isinstance(ledger, list) or len(ledger) != 20:
        raise DynamicGyroscopeError("RML3_TWENTY_PHASE_QUADS_REQUIRED")
    signs = _normalize_quarter_turn_signs(quarter_turn_signs)

    states: list[dict[str, Any]] = []
    for row in ledger:
        if not isinstance(row, Mapping):
            raise DynamicGyroscopeError("RML3_PHASE_LEDGER_ROW_MAPPING_REQUIRED")
        legacy = row.get("ordered_channel_phase72")
        if not isinstance(legacy, Mapping) or tuple(legacy.keys()) != CHANNELS:
            raise DynamicGyroscopeError("RML3_ORDERED_EIGHT_CHANNEL_LEDGER_REQUIRED")
        primitives = {channel: _phase(legacy[channel], f"RML3_{channel.upper()}") for channel in PRIMITIVES}
        dynamic_phases = {
            "x": primitives["x"],
            "y": primitives["y"],
            "z": primitives["z"],
            "w": primitives["w"],
            "xy": expected_product_phase(primitives["x"], signs["xy"]),
            "yx": expected_product_phase(primitives["y"], signs["yx"]),
            "zw": expected_product_phase(primitives["z"], signs["zw"]),
            "wz": expected_product_phase(primitives["w"], signs["wz"]),
        }
        quad_index = _exact_int(row.get("quad_index"), "RML3_QUAD_INDEX")
        states.append(
            build_gyroscope_state(
                dynamic_phases,
                signs,
                state_id=f"rml3:{source.get('raw5184_sha256')}:quad:{quad_index}",
                ancestry_root_sha256=source.get("source_receipt_sha256"),
                legacy_i148_product_phase72={product: legacy[product] for product in PRODUCTS},
            )
        )

    binding = {
        "schema": RML3_BINDING_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "rml3_raw5184_sha256": source.get("raw5184_sha256"),
        "rml3_source_receipt_sha256": source.get("source_receipt_sha256"),
        "rml3_phase_circuit_root_sha256": source.get("phase_circuit_root_sha256"),
        "quarter_turn_signs": signs,
        "gyroscope_count": len(states),
        "ambient_state_count_per_gyroscope": AMBIENT_STATE_COUNT,
        "gyroscopes": states,
        "primitive_phase_coordinates_inherited_exactly_from_rml3": True,
        "legacy_i148_products_preserved_as_provenance_not_reinterpreted": True,
        "rml4_products_generated_as_reciprocal_quarter_turn_images": True,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    binding["binding_sha256"] = _sha256(binding)
    return binding


__all__ = [
    "AMBIENT_STATE_COUNT",
    "CHANNELS",
    "DEGREES_PER_PHASE_STEP",
    "FULL_CYCLE_DEGREES",
    "GYROSCOPE_SCHEMA",
    "OPERATION_SCHEMA",
    "PRIMITIVES",
    "PRODUCTS",
    "PRODUCT_RELATIONS",
    "RML3_BINDING_SCHEMA",
    "TRANSITION_SCHEMA",
    "UNIFIED_ROTATION_PRIMITIVE",
    "DynamicGyroscopeError",
    "advance_gyroscope",
    "build_dynamic_gyroscopes_from_rml3_source",
    "build_gyroscope_state",
    "decode_ambient_state",
    "encode_ambient_state",
    "evaluate_product_constraints",
    "expected_product_phase",
    "phase_to_exact_angle",
    "unified_phase_operation",
]
