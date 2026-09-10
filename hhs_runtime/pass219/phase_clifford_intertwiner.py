"""Pass 219 RML11 exact phase-transport / Clifford-module intertwiner bridge.

RML11 binds the validated RML4 SIGNED_IMAGINARY_PHASE_ROTATION surface to the
constructive RML10 Cl_(0,8) ~= M16(R) witness without replacing the native
u^72 phase state with a matrix state.

The bridge preserves the one-gyroscope semantics:

    x,y,z,w        -> primitive Clifford actions e_x,e_y,e_z,e_w
    xy,yx,zw,wz   -> ordered dependent bivectors
                       e_x e_y, e_y e_x, e_z e_w, e_w e_z

so the executable matrix projection proves

    xy = -yx
    zw = -wz

while ordered channel identity, reciprocal direction, quarter-turn sign, and
full phase72 state remain receipt-visible.

One exact Clifford application corresponds only to one native quarter-cycle
u^18.  An arbitrary signed phase displacement is decomposed exactly as

    delta = 18*q + r,  |r| < 18,

with q lifted into the discrete Clifford action and r preserved as residual
u^72 phase.  The residual is never rounded, discarded, or treated as a matrix
coefficient.  Therefore a complete Clifford lift is claimed only when every
residual is zero.

For a complete lift T, RML11 distinguishes:

* FULL_CL08_MODULE_INTERTWINER: T commutes with all eight RML10 generators;
* EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING: T commutes with the Cl_(0,8)
  volume/chirality operator but is not a full module endomorphism;
* ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING: T anticommutes with the volume
  operator and therefore swaps its +/- chirality sectors.

For partial lifts, the exact quarter-cycle component is classified while the
remaining phase state stays authoritative in RML4.

No VM81 mutation, Hash72 mint, Hash216 persistence, floating-point canonical
state, or scalar-projection substitution authority is introduced.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from typing import Any, Mapping

from hhs_runtime.pass219.bott8_native_correspondence import PASS188_B8_ORDER
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PHASE_MODULUS,
    PRODUCTS,
    PRODUCT_RELATIONS,
    TRANSITION_SCHEMA,
    advance_gyroscope,
    unified_phase_operation,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    CHIRAL_PAIRS,
    flip_chiral_pair_half_turn,
)
from hhs_runtime.pass219.real_clifford_morita_witness import (
    Matrix,
    audit_rml5_generators_on_clifford_morita_bridge,
    build_cl08_generators,
    build_cl08_isomorphism_witness,
    build_clifford_morita_native_packet,
)

PASS = 219
ITERATION = "RML11_PHASE_CLIFFORD_INTERTWINER"

CHANNEL_ACTION_SCHEMA = "HHS_PASS219_RML11_ONE_GYROSCOPE_CLIFFORD_CHANNEL_ACTIONS_V1"
TRANSPORT_SCHEMA = "HHS_PASS219_RML11_PHASE_CLIFFORD_TRANSPORT_LIFT_V1"
OPERATION_BRIDGE_SCHEMA = "HHS_PASS219_RML11_UNIFIED_PHASE_OPERATION_CLIFFORD_BRIDGE_V1"
COUPLED_CLASS_SCHEMA = "HHS_PASS219_RML11_COUPLED_GENERATOR_CLIFFORD_CLASS_V1"
PAIR_FLIP_CLASS_SCHEMA = "HHS_PASS219_RML11_CHIRAL_PAIR_FLIP_CLIFFORD_CLASS_V1"
AUDIT_SCHEMA = "HHS_PASS219_RML11_PHASE_CLIFFORD_GENERATOR_AUDIT_V1"

QUARTER_CYCLE_STEPS = PHASE_MODULUS // 4
PRIMITIVE_CHANNELS = ("x", "y", "z", "w")
GENERATOR_INDEX = {channel: index for index, channel in enumerate(PRIMITIVE_CHANNELS)}
GENERATOR_TO_PRODUCT = {
    relation["generator"]: product for product, relation in PRODUCT_RELATIONS.items()
}


class PhaseCliffordIntertwinerError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise PhaseCliffordIntertwinerError(f"FLOAT_PHASE_CLIFFORD_AUTHORITY_FORBIDDEN:{path}")
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
        raise PhaseCliffordIntertwinerError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _identity(order: int = 16) -> Matrix:
    n = _exact_int(order, "IDENTITY_ORDER")
    if n <= 0:
        raise PhaseCliffordIntertwinerError("POSITIVE_MATRIX_ORDER_REQUIRED")
    return tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))


def _zero(order: int = 16) -> Matrix:
    n = _exact_int(order, "ZERO_ORDER")
    if n <= 0:
        raise PhaseCliffordIntertwinerError("POSITIVE_MATRIX_ORDER_REQUIRED")
    return tuple(tuple(0 for _ in range(n)) for _ in range(n))


def _scale(matrix: Matrix, scalar: int) -> Matrix:
    k = _exact_int(scalar, "MATRIX_SCALAR")
    return tuple(tuple(k * value for value in row) for row in matrix)


def _add(left: Matrix, right: Matrix) -> Matrix:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise PhaseCliffordIntertwinerError("MATRIX_ADD_SHAPE_MISMATCH")
    return tuple(
        tuple(left[i][j] + right[i][j] for j in range(len(left[i])))
        for i in range(len(left))
    )


def _matmul(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise PhaseCliffordIntertwinerError("MATRIX_PRODUCT_SHAPE_MISMATCH")
    rows = len(left)
    inner = len(right)
    cols = len(right[0])
    if any(len(row) != inner for row in left) or any(len(row) != cols for row in right):
        raise PhaseCliffordIntertwinerError("RECTANGULAR_MATRIX_REQUIRED")
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(inner)) for j in range(cols))
        for i in range(rows)
    )


def _matrix_hash(matrix: Matrix) -> str:
    return _sha256([list(row) for row in matrix])


def _commutes(left: Matrix, right: Matrix) -> bool:
    return _matmul(left, right) == _matmul(right, left)


def _anticommutes(left: Matrix, right: Matrix) -> bool:
    return _matmul(left, right) == _scale(_matmul(right, left), -1)


def _matrix_power_order4(matrix: Matrix, exponent: int) -> Matrix:
    """Exact signed power for an action whose square is -I and fourth power I."""
    power = _exact_int(exponent, "CLIFFORD_QUARTER_EXPONENT") % 4
    result = _identity(16)
    for _ in range(power):
        result = _matmul(result, matrix)
    return result


def decompose_signed_phase_step(signed_steps: int) -> tuple[int, int]:
    """Return q,r with delta=18*q+r and a sign-symmetric |r|<18 remainder."""
    delta = _exact_int(signed_steps, "SIGNED_PHASE_STEPS")
    if delta == 0:
        return 0, 0
    sign = 1 if delta > 0 else -1
    quarter_units = sign * (abs(delta) // QUARTER_CYCLE_STEPS)
    residual = delta - QUARTER_CYCLE_STEPS * quarter_units
    if abs(residual) >= QUARTER_CYCLE_STEPS:
        raise AssertionError("RML11_PHASE_QUARTER_DECOMPOSITION_RANGE_DRIFT")
    if delta != QUARTER_CYCLE_STEPS * quarter_units + residual:
        raise AssertionError("RML11_PHASE_QUARTER_DECOMPOSITION_IDENTITY_DRIFT")
    return quarter_units, residual


@lru_cache(maxsize=1)
def _channel_action_matrices() -> dict[str, Matrix]:
    """Build the one-gyroscope channel action inside the RML10 Cl_(0,8) carrier."""
    generators = build_cl08_generators()
    primitives = {
        channel: generators[GENERATOR_INDEX[channel]]
        for channel in PRIMITIVE_CHANNELS
    }
    actions: dict[str, Matrix] = dict(primitives)
    for product in PRODUCTS:
        relation = PRODUCT_RELATIONS[product]
        actions[product] = _matmul(
            primitives[relation["generator"]],
            primitives[relation["reciprocal"]],
        )
    return actions


@lru_cache(maxsize=1)
def _chirality_volume() -> Matrix:
    value = _identity(16)
    for generator in build_cl08_generators():
        value = _matmul(value, generator)
    return value


@lru_cache(maxsize=1)
def build_one_gyroscope_clifford_channel_actions() -> dict[str, Any]:
    generators = build_cl08_generators()
    actions = _channel_action_matrices()
    identity = _identity(16)
    negative_identity = _scale(identity, -1)
    volume = _chirality_volume()
    if _matmul(volume, volume) != identity:
        raise AssertionError("RML11_CL08_VOLUME_NOT_INVOLUTIVE")

    rows: list[dict[str, Any]] = []
    for channel in CHANNELS:
        action = actions[channel]
        if _matmul(action, action) != negative_identity:
            raise AssertionError(f"RML11_CHANNEL_ACTION_SQUARE_DRIFT:{channel}")
        role = "PRIMITIVE_GENERATOR" if channel in PRIMITIVE_CHANNELS else "ORDERED_DEPENDENT_BIVECTOR"
        row: dict[str, Any] = {
            "channel": channel,
            "role": role,
            "action_matrix_sha256": _matrix_hash(action),
            "action_squares_to_minus_identity": True,
            "commutes_with_cl08_chirality_volume": _commutes(action, volume),
            "anticommutes_with_cl08_chirality_volume": _anticommutes(action, volume),
        }
        if channel in PRODUCTS:
            relation = PRODUCT_RELATIONS[channel]
            row.update(
                {
                    "generator": relation["generator"],
                    "reciprocal": relation["reciprocal"],
                    "ordered_bivector_expression": f"e_{relation['generator']}*e_{relation['reciprocal']}",
                    "same_gyroscope_dependent_product_view": True,
                }
            )
        rows.append(row)

    if actions["xy"] != _scale(actions["yx"], -1):
        raise AssertionError("RML11_XY_YX_CHIRALITY_MATRIX_IDENTITY_FAILED")
    if actions["zw"] != _scale(actions["wz"], -1):
        raise AssertionError("RML11_ZW_WZ_CHIRALITY_MATRIX_IDENTITY_FAILED")

    result = {
        "schema": CHANNEL_ACTION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "rml10_cl08_witness_sha256": build_cl08_isomorphism_witness()["witness_sha256"],
        "rml10_generator_count": len(generators),
        "rml10_matrix_order": 16,
        "channel_order": list(CHANNELS),
        "native_b8_grade_order": list(PASS188_B8_ORDER),
        "primitive_action_generators": list(PRIMITIVE_CHANNELS),
        "rows": rows,
        "xy_equals_negative_yx_matrix_projection": True,
        "zw_equals_negative_wz_matrix_projection": True,
        "product_channels_constructed_from_primitive_actions": True,
        "product_channels_are_not_promoted_to_independent_gyroscope_axes": True,
        "native_b8_grade_tag_is_not_reinterpreted_as_channel_action_generator_index": True,
        "cl08_chirality_volume_sha256": _matrix_hash(volume),
        "cl08_chirality_volume_squared_is_identity": True,
        "ordered_channel_identity_survives_coincident_matrix_projection": True,
        "phase_state_reinterpreted_as_clifford_matrix_state": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def _require_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_float(state)
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise PhaseCliffordIntertwinerError("RML4_GYROSCOPE_STATE_SCHEMA_REQUIRED")
    phases = state.get("phases")
    signs = state.get("quarter_turn_signs")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != CHANNELS:
        raise PhaseCliffordIntertwinerError("RML4_ORDERED_PHASES_REQUIRED")
    if not isinstance(signs, Mapping) or tuple(signs.keys()) != PRODUCTS:
        raise PhaseCliffordIntertwinerError("RML4_ORDERED_PRODUCT_SIGNS_REQUIRED")
    return state


def _normalize_signed_steps(signed_steps: Mapping[str, Any]) -> dict[str, int]:
    if not isinstance(signed_steps, Mapping) or tuple(signed_steps.keys()) != CHANNELS:
        raise PhaseCliffordIntertwinerError("ORDERED_EIGHT_CHANNEL_SIGNED_STEPS_REQUIRED")
    return {
        channel: _exact_int(signed_steps[channel], f"{channel.upper()}_SIGNED_STEP")
        for channel in CHANNELS
    }


def build_phase_transport_clifford_lift(
    state: Mapping[str, Any],
    signed_steps: Mapping[str, Any],
    *,
    transport_id: str,
) -> dict[str, Any]:
    """Lift exact u^18 components of one RML4 phase transport into Cl_(0,8)."""
    state = _require_state(state)
    deltas = _normalize_signed_steps(signed_steps)
    actions = _channel_action_matrices()
    generators = build_cl08_generators()
    volume = _chirality_volume()
    identity = _identity(16)

    matrix = identity
    factors: list[dict[str, Any]] = []
    factor_matrices: list[Matrix] = []
    all_residual_zero = True
    for channel in CHANNELS:
        quarter_units, residual = decompose_signed_phase_step(deltas[channel])
        factor = _matrix_power_order4(actions[channel], quarter_units)
        factor_matrices.append(factor)
        matrix = _matmul(matrix, factor)
        all_residual_zero = all_residual_zero and residual == 0
        row: dict[str, Any] = {
            "channel": channel,
            "signed_phase_steps": deltas[channel],
            "quarter_cycle_steps": QUARTER_CYCLE_STEPS,
            "signed_quarter_units": quarter_units,
            "residual_phase_steps": residual,
            "exact_decomposition_verified": deltas[channel] == QUARTER_CYCLE_STEPS * quarter_units + residual,
            "factor_matrix_sha256": _matrix_hash(factor),
            "channel_action_role": (
                "PRIMITIVE_GENERATOR" if channel in PRIMITIVE_CHANNELS else "ORDERED_DEPENDENT_BIVECTOR"
            ),
        }
        if channel in PRODUCTS:
            relation = PRODUCT_RELATIONS[channel]
            row.update(
                {
                    "product_generator": relation["generator"],
                    "product_reciprocal": relation["reciprocal"],
                    "construction_quarter_turn_sign": state["quarter_turn_signs"][channel],
                    "ordered_product_identity_preserved": True,
                }
            )
        factors.append(row)

    # Because the Clifford action is noncommutative, the inverse of the ordered
    # lift reverses factor order.  It is not silently replaced by same-order
    # negated exponents.
    inverse_matrix = identity
    for factor in reversed(factor_matrices):
        inverse_factor = _matrix_power_order4(factor, -1)
        inverse_matrix = _matmul(inverse_matrix, inverse_factor)
    inverse_exact = _matmul(matrix, inverse_matrix) == identity and _matmul(inverse_matrix, matrix) == identity
    if not inverse_exact:
        raise AssertionError("RML11_ORDERED_CLIFFORD_INVERSE_FAILED")

    commutes_all = all(_commutes(matrix, generator) for generator in generators)
    commutes_volume = _commutes(matrix, volume)
    anticommutes_volume = _anticommutes(matrix, volume)
    if not commutes_volume and not anticommutes_volume:
        raise AssertionError("RML11_CLIFFORD_GRADING_CLASSIFICATION_FAILED")

    if commutes_all:
        quarter_classification = "FULL_CL08_MODULE_INTERTWINER"
    elif commutes_volume:
        quarter_classification = "EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING"
    else:
        quarter_classification = "ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING"

    if all_residual_zero:
        full_classification = quarter_classification
    else:
        full_classification = "RESIDUAL_U72_PHASE_PRESERVED_NO_COMPLETE_CLIFFORD_LIFT"

    result = {
        "schema": TRANSPORT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "transport_id": str(transport_id),
        "source_state_sha256": state.get("state_sha256"),
        "source_ambient_state_index": state.get("ambient_state_index"),
        "underlying_phase_primitive": "SIGNED_IMAGINARY_PHASE_ROTATION",
        "channel_action_witness_sha256": build_one_gyroscope_clifford_channel_actions()["witness_sha256"],
        "ordered_channel_composition": list(CHANNELS),
        "signed_steps": deltas,
        "factors": factors,
        "quarter_component_matrix_sha256": _matrix_hash(matrix),
        "inverse_quarter_component_matrix_sha256": _matrix_hash(inverse_matrix),
        "ordered_reverse_factor_inverse_verified": inverse_exact,
        "same_order_negated_factor_sequence_is_inverse_claimed": False,
        "complete_clifford_lift": all_residual_zero,
        "residual_u72_phase_preserved": not all_residual_zero,
        "quarter_component_classification": quarter_classification,
        "full_phase_transform_classification": full_classification,
        "quarter_component_commutes_with_all_cl08_generators": commutes_all,
        "quarter_component_commutes_with_cl08_chirality_volume": commutes_volume,
        "quarter_component_anticommutes_with_cl08_chirality_volume": anticommutes_volume,
        "full_cl08_module_intertwiner": all_residual_zero and commutes_all,
        "full_transform_chirality_sector_preserving": all_residual_zero and commutes_volume,
        "full_transform_chirality_sector_swapping": all_residual_zero and anticommutes_volume,
        "phase72_state_retained": True,
        "clifford_lift_replaces_phase_state": False,
        "residual_phase_rounded_or_discarded": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["transport_sha256"] = _sha256(result)
    return result


def classify_rml4_transition_clifford(transition: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(transition)
    if transition.get("schema") != TRANSITION_SCHEMA:
        raise PhaseCliffordIntertwinerError("RML4_TRANSITION_SCHEMA_REQUIRED")
    next_state = transition.get("next_state")
    if not isinstance(next_state, Mapping):
        raise PhaseCliffordIntertwinerError("RML4_TRANSITION_NEXT_STATE_REQUIRED")
    # Reconstruct the source phase coordinates exactly from the reversible delta
    # so the lift remains a read-only classification of the existing transition.
    deltas = _normalize_signed_steps(transition.get("signed_steps"))
    next_state = _require_state(next_state)
    source_phases = {
        channel: (int(next_state["phases"][channel]) - deltas[channel]) % PHASE_MODULUS
        for channel in CHANNELS
    }
    from hhs_runtime.pass219.dynamic_octonion_gyroscope import build_gyroscope_state

    source_state = build_gyroscope_state(
        source_phases,
        next_state["quarter_turn_signs"],
        state_id=f"rml11:reconstructed:{transition.get('transition_id')}",
        ancestry_root_sha256=transition.get("prior_state_sha256"),
        legacy_i148_product_phase72=next_state.get("legacy_i148_product_phase72"),
    )
    lift = build_phase_transport_clifford_lift(
        source_state,
        deltas,
        transport_id=f"rml11:{transition.get('transition_id')}",
    )
    result = {
        "schema": "HHS_PASS219_RML11_RML4_TRANSITION_CLIFFORD_CLASSIFICATION_V1",
        "source_transition_sha256": transition.get("transition_sha256"),
        "source_transition_id": transition.get("transition_id"),
        "source_prior_state_sha256": transition.get("prior_state_sha256"),
        "source_next_state_sha256": next_state.get("state_sha256"),
        "phase_transport_clifford_lift": lift,
        "rml4_transition_mutated": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["classification_sha256"] = _sha256(result)
    return result


def build_unified_phase_operation_clifford_bridge(
    state: Mapping[str, Any],
    *,
    operator: str,
    ordered_operands: list[str],
    signed_step: int = 0,
    repetitions: int = 1,
    product_channel: str | None = None,
) -> dict[str, Any]:
    """Bind RML4 +,*,^ operation witnesses to the same exact Clifford lift."""
    state = _require_state(state)
    operation = unified_phase_operation(
        state,
        operator=operator,
        ordered_operands=ordered_operands,
        signed_step=signed_step,
        repetitions=repetitions,
        product_channel=product_channel,
    )
    steps = {channel: 0 for channel in CHANNELS}
    if operator == "+":
        step = _exact_int(signed_step, "SIGNED_STEP")
        for channel in ordered_operands:
            steps[channel] += step
        bridge_mode = "COUPLED_PHASE_DISPLACEMENT_TO_ORDERED_CLIFFORD_ACTION"
    elif operator == "*":
        if product_channel not in PRODUCTS:
            raise PhaseCliffordIntertwinerError("RML11_PRODUCT_CHANNEL_REQUIRED")
        sign = _exact_int(state["quarter_turn_signs"][product_channel], "PRODUCT_QUARTER_TURN_SIGN")
        steps[product_channel] = sign * QUARTER_CYCLE_STEPS
        bridge_mode = "ORDERED_PRODUCT_BIVECTOR_QUARTER_TURN"
    elif operator == "^":
        if len(ordered_operands) != 1:
            raise PhaseCliffordIntertwinerError("RML11_POWER_SINGLE_OPERAND_REQUIRED")
        steps[ordered_operands[0]] = _exact_int(signed_step, "SIGNED_STEP") * _exact_int(repetitions, "REPETITIONS")
        bridge_mode = "RECURSIVE_PHASE_ORBIT_TO_REPEATED_CLIFFORD_ACTION"
    else:
        raise PhaseCliffordIntertwinerError("RML11_OPERATOR_UNSUPPORTED")

    lift = build_phase_transport_clifford_lift(
        state,
        steps,
        transport_id=f"operation:{operation['operation_sha256']}",
    )
    result = {
        "schema": OPERATION_BRIDGE_SCHEMA,
        "source_operation_sha256": operation["operation_sha256"],
        "source_operator": operator,
        "source_operation_mode": operation["mode"],
        "bridge_mode": bridge_mode,
        "ordered_operands": list(ordered_operands),
        "product_channel": product_channel,
        "phase_transport_clifford_lift": lift,
        "source_operator_identity_preserved": True,
        "operand_order_preserved": True,
        "coincident_clifford_projection_collapses_operator_identity": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["bridge_sha256"] = _sha256(result)
    return result


def classify_coupled_generator_clifford(
    state: Mapping[str, Any],
    *,
    generator: str,
    signed_steps: int,
    transition_id: str,
) -> dict[str, Any]:
    state = _require_state(state)
    if generator not in GENERATOR_TO_PRODUCT:
        raise PhaseCliffordIntertwinerError("RML11_GENERATOR_UNSUPPORTED")
    delta = _exact_int(signed_steps, "SIGNED_STEPS")
    product = GENERATOR_TO_PRODUCT[generator]
    steps = {channel: 0 for channel in CHANNELS}
    steps[generator] = delta
    steps[product] = delta
    transition = advance_gyroscope(state, steps, transition_id=transition_id)
    if transition["next_state"]["admissible_product_geometry"] is not True:
        raise AssertionError("RML11_COUPLED_GENERATOR_MOVE_LEFT_ADMISSIBLE_MANIFOLD")
    lift = build_phase_transport_clifford_lift(
        state,
        steps,
        transport_id=f"clifford:{transition_id}",
    )
    result = {
        "schema": COUPLED_CLASS_SCHEMA,
        "generator": generator,
        "dependent_product": product,
        "signed_steps": delta,
        "transition_sha256": transition["transition_sha256"],
        "target_state_sha256": transition["next_state"]["state_sha256"],
        "target_product_geometry_admissible": True,
        "clifford_lift": lift,
        "canonical_vm81_mutation_authority": False,
    }
    result["classification_sha256"] = _sha256(result)
    return result


def classify_chiral_pair_flip_clifford(
    state: Mapping[str, Any],
    *,
    pair_index: int,
    transition_id: str,
) -> dict[str, Any]:
    state = _require_state(state)
    index = _exact_int(pair_index, "PAIR_INDEX")
    if index < 0 or index >= len(CHIRAL_PAIRS):
        raise PhaseCliffordIntertwinerError("RML11_PAIR_INDEX_OUT_OF_RANGE")
    flip = flip_chiral_pair_half_turn(state, pair_index=index, transition_id=transition_id)
    steps = {channel: 0 for channel in CHANNELS}
    for product in CHIRAL_PAIRS[index]:
        steps[product] = PHASE_MODULUS // 2
    lift = build_phase_transport_clifford_lift(
        state,
        steps,
        transport_id=f"clifford:{transition_id}",
    )
    result = {
        "schema": PAIR_FLIP_CLASS_SCHEMA,
        "pair_index": index,
        "pair": list(CHIRAL_PAIRS[index]),
        "phase_inversion_steps": PHASE_MODULUS // 2,
        "transition_sha256": flip["transition_sha256"],
        "target_state_sha256": flip["next_state"]["state_sha256"],
        "clifford_lift": lift,
        "pair_flip_self_inverse": flip["operation_is_self_inverse"],
        "canonical_vm81_mutation_authority": False,
    }
    result["classification_sha256"] = _sha256(result)
    return result


def audit_rml5_generators_on_phase_clifford_bridge(state: Mapping[str, Any]) -> dict[str, Any]:
    """Classify the same finite 290-case RML5 generator family through RML11."""
    state = _require_state(state)
    complete = 0
    residual = 0
    full_intertwiners = 0
    even_sector_preserving = 0
    odd_sector_swapping = 0
    coupled_cases = 0
    for generator in PRIMITIVE_CHANNELS:
        for phase_step in range(PHASE_MODULUS):
            witness = classify_coupled_generator_clifford(
                state,
                generator=generator,
                signed_steps=phase_step,
                transition_id=f"rml11:audit:{generator}:{phase_step}",
            )
            lift = witness["clifford_lift"]
            coupled_cases += 1
            if lift["complete_clifford_lift"]:
                complete += 1
                if lift["full_cl08_module_intertwiner"]:
                    full_intertwiners += 1
                elif lift["full_transform_chirality_sector_preserving"]:
                    even_sector_preserving += 1
                elif lift["full_transform_chirality_sector_swapping"]:
                    odd_sector_swapping += 1
                else:
                    raise AssertionError("RML11_COMPLETE_LIFT_UNCLASSIFIED")
            else:
                residual += 1

    pair_cases = 0
    for pair_index in range(len(CHIRAL_PAIRS)):
        witness = classify_chiral_pair_flip_clifford(
            state,
            pair_index=pair_index,
            transition_id=f"rml11:audit:pair:{pair_index}",
        )
        pair_cases += 1
        lift = witness["clifford_lift"]
        if not lift["complete_clifford_lift"]:
            raise AssertionError("RML11_U36_PAIR_FLIP_MUST_HAVE_COMPLETE_CLIFFORD_LIFT")
        complete += 1
        if lift["full_cl08_module_intertwiner"]:
            full_intertwiners += 1
        elif lift["full_transform_chirality_sector_preserving"]:
            even_sector_preserving += 1
        elif lift["full_transform_chirality_sector_swapping"]:
            odd_sector_swapping += 1
        else:
            raise AssertionError("RML11_PAIR_FLIP_LIFT_UNCLASSIFIED")

    total = coupled_cases + pair_cases
    inherited = audit_rml5_generators_on_clifford_morita_bridge(state)
    if total != inherited["total_generator_cases"] or total != 290:
        raise AssertionError("RML11_RML5_GENERATOR_CARDINALITY_DRIFT")
    if complete + residual != total:
        raise AssertionError("RML11_CLIFFORD_LIFT_PARTITION_DRIFT")
    if full_intertwiners + even_sector_preserving + odd_sector_swapping != complete:
        raise AssertionError("RML11_COMPLETE_CLIFFORD_CLASS_PARTITION_DRIFT")

    packet = build_clifford_morita_native_packet(state)
    result = {
        "schema": AUDIT_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "rml10_correspondence_sha256": packet["correspondence_sha256"],
        "coupled_z72_cases": coupled_cases,
        "u36_pair_flip_cases": pair_cases,
        "total_generator_cases": total,
        "complete_clifford_lift_cases": complete,
        "residual_u72_phase_cases": residual,
        "full_cl08_module_intertwiner_cases": full_intertwiners,
        "even_chirality_sector_preserving_nonintertwiner_cases": even_sector_preserving,
        "odd_chirality_sector_swapping_cases": odd_sector_swapping,
        "complete_lift_partition_complete": full_intertwiners + even_sector_preserving + odd_sector_swapping == complete,
        "all_290_cases_partitioned": complete + residual == total,
        "inherited_same_hopf_base_cases": inherited["same_base_fiber_preserving_cases"],
        "inherited_base_moving_hopf_cases": inherited["base_moving_cases"],
        "inherited_inverse_hopf_restoration_failures": inherited["inverse_hopf_base_restoration_failures"],
        "hopf_and_clifford_classifications_are_orthogonal_not_substitutions": True,
        "phase_transition_authority_expanded": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "AUDIT_SCHEMA",
    "CHANNEL_ACTION_SCHEMA",
    "COUPLED_CLASS_SCHEMA",
    "OPERATION_BRIDGE_SCHEMA",
    "PAIR_FLIP_CLASS_SCHEMA",
    "QUARTER_CYCLE_STEPS",
    "TRANSPORT_SCHEMA",
    "PhaseCliffordIntertwinerError",
    "audit_rml5_generators_on_phase_clifford_bridge",
    "build_one_gyroscope_clifford_channel_actions",
    "build_phase_transport_clifford_lift",
    "build_unified_phase_operation_clifford_bridge",
    "classify_chiral_pair_flip_clifford",
    "classify_coupled_generator_clifford",
    "classify_rml4_transition_clifford",
    "decompose_signed_phase_step",
]
