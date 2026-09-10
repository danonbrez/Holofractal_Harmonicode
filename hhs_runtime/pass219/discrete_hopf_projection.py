"""Pass 219 RML7 exact quaternionic Hopf projection candidate.

RML7 consumes the validated RML6 exact rational S^7 embedding and applies the
standard quaternionic Hopf construction

    H(q1,q2) = (2 q1 conjugate(q2), |q1|^2 - |q2|^2) in S^4.

All arithmetic is performed on integer numerators with one exact common
denominator.  No float, trigonometric approximation, or scalar replacement of
the HARMONICODE rotor state is introduced.

The module proves three bounded facts:
1. every accepted RML6 point maps to an exact rational unit S^4 point;
2. the standard simultaneous right action of the quaternion group Q8 on
   (q1,q2) preserves the exact Hopf base point, giving concrete fiber witnesses;
3. the existing RML5 generator classes can be classified exactly as either
   same-base/fiber-preserving for that move or base-moving, and their explicit
   inverses restore the exact original Hopf base.

This is not yet a proof that the full RML6 discrete image is closed under the
entire S^3 Hopf fiber action, nor that every RML5 generator is fiber-equivariant.
Bott-periodicity correspondence therefore remains repair-forward.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.discrete_s7_embedding import (
    S7_EMBEDDING_SCHEMA,
    build_discrete_s7_embedding,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PHASE_MODULUS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    CHIRAL_PAIRS,
    flip_chiral_pair_half_turn,
)

PASS = 219
ITERATION = "RML7_EXACT_HOPF_PROJECTION_CANDIDATE"

HOPF_SCHEMA = "HHS_PASS219_RML7_EXACT_RATIONAL_HOPF_S7_TO_S4_V1"
Q8_FIBER_SCHEMA = "HHS_PASS219_RML7_Q8_HOPF_FIBER_WITNESS_V1"
GENERATOR_CLASS_SCHEMA = "HHS_PASS219_RML7_HOPF_GENERATOR_CLASSIFICATION_V1"
GENERATOR_AUDIT_SCHEMA = "HHS_PASS219_RML7_HOPF_GENERATOR_AUDIT_V1"

GENERATOR_TO_PRODUCT = {
    relation["generator"]: product for product, relation in PRODUCT_RELATIONS.items()
}

Q8 = {
    "+1": (1, 0, 0, 0),
    "-1": (-1, 0, 0, 0),
    "+i": (0, 1, 0, 0),
    "-i": (0, -1, 0, 0),
    "+j": (0, 0, 1, 0),
    "-j": (0, 0, -1, 0),
    "+k": (0, 0, 0, 1),
    "-k": (0, 0, 0, -1),
}


class DiscreteHopfProjectionError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise DiscreteHopfProjectionError(f"FLOAT_HOPF_AUTHORITY_FORBIDDEN:{path}")
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
        raise DiscreteHopfProjectionError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _quat_mul(a: Sequence[int], b: Sequence[int]) -> tuple[int, int, int, int]:
    if len(a) != 4 or len(b) != 4:
        raise DiscreteHopfProjectionError("QUATERNION_LENGTH_FOUR_REQUIRED")
    a0, a1, a2, a3 = (_exact_int(v, "QUAT_A") for v in a)
    b0, b1, b2, b3 = (_exact_int(v, "QUAT_B") for v in b)
    return (
        a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
        a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
        a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
        a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
    )


def _quat_conj(a: Sequence[int]) -> tuple[int, int, int, int]:
    if len(a) != 4:
        raise DiscreteHopfProjectionError("QUATERNION_LENGTH_FOUR_REQUIRED")
    a0, a1, a2, a3 = (_exact_int(v, "QUAT_CONJ") for v in a)
    return (a0, -a1, -a2, -a3)


def _quat_norm_squared(a: Sequence[int]) -> int:
    if len(a) != 4:
        raise DiscreteHopfProjectionError("QUATERNION_LENGTH_FOUR_REQUIRED")
    return sum(_exact_int(v, "QUAT_NORM") ** 2 for v in a)


def _require_s7_point(point: Mapping[str, Any]) -> tuple[list[int], int]:
    _reject_float(point)
    numerators = point.get("coordinate_numerators")
    denominator = point.get("common_denominator")
    if not isinstance(numerators, list) or len(numerators) != 8:
        raise DiscreteHopfProjectionError("EXACT_S7_EIGHT_NUMERATORS_REQUIRED")
    nums = [_exact_int(value, f"S7_N{index}") for index, value in enumerate(numerators)]
    den = _exact_int(denominator, "S7_DENOMINATOR")
    if den <= 0:
        raise DiscreteHopfProjectionError("S7_POSITIVE_DENOMINATOR_REQUIRED")
    if sum(value * value for value in nums) != den * den:
        raise DiscreteHopfProjectionError("S7_EXACT_UNIT_NORM_REQUIRED")
    return nums, den


def hopf_project_s7_point(point: Mapping[str, Any]) -> dict[str, Any]:
    """Project one exact rational S^7 point to exact rational S^4."""
    nums, den = _require_s7_point(point)
    q1 = tuple(nums[:4])
    q2 = tuple(nums[4:])
    a = _quat_norm_squared(q1)
    b = _quat_norm_squared(q2)
    if a + b != den * den:
        raise AssertionError("RML7_S7_QUATERNION_SPLIT_NORM_DRIFT")

    product = _quat_mul(q1, _quat_conj(q2))
    product_norm = _quat_norm_squared(product)
    if product_norm != a * b:
        raise AssertionError("RML7_QUATERNION_PRODUCT_NORM_IDENTITY_FAILED")

    base_numerators = [2 * value for value in product] + [a - b]
    base_denominator = den * den
    base_norm_numerator = sum(value * value for value in base_numerators)
    base_norm_denominator = base_denominator * base_denominator
    if base_norm_numerator != base_norm_denominator:
        raise AssertionError("RML7_HOPF_S4_EXACT_UNIT_NORM_IDENTITY_FAILED")

    result = {
        "schema": HOPF_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "s7_point_sha256": point.get("s7_point_sha256"),
        "quaternion_split": {
            "q1_coordinate_numerators": list(q1),
            "q2_coordinate_numerators": list(q2),
            "common_denominator": den,
            "q1_norm_numerator": a,
            "q2_norm_numerator": b,
            "q1_plus_q2_norm_equals_s7_denominator_squared": True,
        },
        "hopf_quaternion_product_numerators": list(product),
        "s4_coordinate_order": ["h0", "h1", "h2", "h3", "h4"],
        "s4_coordinate_numerators": base_numerators,
        "s4_common_denominator": base_denominator,
        "s4_rational_coordinates": [
            f"{numerator}/{base_denominator}" for numerator in base_numerators
        ],
        "quaternion_product_norm_identity_verified": True,
        "s4_norm_numerator": base_norm_numerator,
        "s4_norm_denominator": base_norm_denominator,
        "exact_unit_s4_identity_verified": True,
        "floating_point_coordinates_used": False,
        "chart_dependent_hopf_candidate": True,
        "full_rml6_discrete_image_s3_fiber_closure_claimed": False,
        "bott_periodicity_correspondence_claimed": False,
    }
    result["s4_point_sha256"] = _sha256(
        {
            "numerators": base_numerators,
            "denominator": base_denominator,
        }
    )
    result["hopf_witness_sha256"] = _sha256(result)
    return result


def hopf_project_embedding(embedding: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(embedding)
    if embedding.get("schema") != S7_EMBEDDING_SCHEMA:
        raise DiscreteHopfProjectionError("RML6_S7_EMBEDDING_SCHEMA_REQUIRED")
    point = embedding.get("s7_point")
    if not isinstance(point, Mapping):
        raise DiscreteHopfProjectionError("RML6_S7_POINT_REQUIRED")
    result = hopf_project_s7_point(point)
    result["source_embedding_sha256"] = embedding.get("embedding_sha256")
    result["source_state_sha256"] = embedding.get("source_state_sha256")
    return result


def _right_multiply_q8_point(point: Mapping[str, Any], element: str) -> dict[str, Any]:
    nums, den = _require_s7_point(point)
    if element not in Q8:
        raise DiscreteHopfProjectionError("Q8_ELEMENT_UNSUPPORTED")
    h = Q8[element]
    q1 = _quat_mul(tuple(nums[:4]), h)
    q2 = _quat_mul(tuple(nums[4:]), h)
    transformed = list(q1 + q2)
    if sum(value * value for value in transformed) != den * den:
        raise AssertionError("RML7_Q8_FIBER_ACTION_LEFT_S7")
    result = {
        "coordinate_order": list(point.get("coordinate_order", [f"s{i}" for i in range(8)])),
        "common_denominator": den,
        "coordinate_numerators": transformed,
        "rational_coordinates": [f"{numerator}/{den}" for numerator in transformed],
        "sphere_norm_numerator": den * den,
        "sphere_norm_denominator": den * den,
        "exact_unit_s7_identity_verified": True,
        "floating_point_coordinates_used": False,
        "q8_right_action": element,
    }
    result["s7_point_sha256"] = _sha256(
        {"numerators": transformed, "denominator": den}
    )
    return result


def witness_q8_hopf_fiber(embedding: Mapping[str, Any], element: str) -> dict[str, Any]:
    """Prove one exact Q8 simultaneous-right-action remains in one Hopf fiber."""
    if embedding.get("schema") != S7_EMBEDDING_SCHEMA:
        raise DiscreteHopfProjectionError("RML6_S7_EMBEDDING_SCHEMA_REQUIRED")
    source_point = embedding.get("s7_point")
    if not isinstance(source_point, Mapping):
        raise DiscreteHopfProjectionError("RML6_S7_POINT_REQUIRED")
    source_hopf = hopf_project_s7_point(source_point)
    transformed_point = _right_multiply_q8_point(source_point, element)
    transformed_hopf = hopf_project_s7_point(transformed_point)
    same_base = source_hopf["s4_point_sha256"] == transformed_hopf["s4_point_sha256"]
    if not same_base:
        raise AssertionError("RML7_Q8_HOPF_FIBER_INVARIANCE_FAILED")
    result = {
        "schema": Q8_FIBER_SCHEMA,
        "q8_element": element,
        "source_s7_point_sha256": source_point.get("s7_point_sha256"),
        "transformed_s7_point_sha256": transformed_point["s7_point_sha256"],
        "source_s4_point_sha256": source_hopf["s4_point_sha256"],
        "transformed_s4_point_sha256": transformed_hopf["s4_point_sha256"],
        "same_hopf_base_exactly": True,
        "q8_is_unit_quaternion_action": True,
        "simultaneous_right_action_on_q1_q2": True,
        "transformed_point_claimed_inside_rml6_discrete_image": False,
        "full_s3_fiber_closure_claimed": False,
    }
    result["fiber_witness_sha256"] = _sha256(result)
    return result


def classify_coupled_generator_hopf(
    state: Mapping[str, Any],
    *,
    generator: str,
    signed_steps: int,
    transition_id: str,
) -> dict[str, Any]:
    if generator not in GENERATOR_TO_PRODUCT:
        raise DiscreteHopfProjectionError("RML7_GENERATOR_UNSUPPORTED")
    delta = _exact_int(signed_steps, "SIGNED_STEPS")
    product = GENERATOR_TO_PRODUCT[generator]
    steps = {channel: 0 for channel in CHANNELS}
    steps[generator] = delta
    steps[product] = delta
    source_embedding = build_discrete_s7_embedding(state)
    source_hopf = hopf_project_embedding(source_embedding)
    transition = advance_gyroscope(state, steps, transition_id=transition_id)
    target_state = transition["next_state"]
    target_embedding = build_discrete_s7_embedding(target_state)
    target_hopf = hopf_project_embedding(target_embedding)
    inverse = advance_gyroscope(
        target_state,
        {channel: -steps[channel] for channel in CHANNELS},
        transition_id=f"inverse:{transition_id}:hopf",
    )
    restored_embedding = build_discrete_s7_embedding(inverse["next_state"])
    restored_hopf = hopf_project_embedding(restored_embedding)
    same_base = source_hopf["s4_point_sha256"] == target_hopf["s4_point_sha256"]
    inverse_restores = source_hopf["s4_point_sha256"] == restored_hopf["s4_point_sha256"]
    if not inverse_restores:
        raise AssertionError("RML7_GENERATOR_INVERSE_DID_NOT_RESTORE_HOPF_BASE")
    result = {
        "schema": GENERATOR_CLASS_SCHEMA,
        "generator_class": "COUPLED_Z72_GENERATOR_PRODUCT_MOVE",
        "generator": generator,
        "dependent_product": product,
        "signed_steps": delta,
        "source_s4_point_sha256": source_hopf["s4_point_sha256"],
        "target_s4_point_sha256": target_hopf["s4_point_sha256"],
        "restored_s4_point_sha256": restored_hopf["s4_point_sha256"],
        "classification": (
            "FIBER_PRESERVING_SAME_HOPF_BASE"
            if same_base
            else "BASE_MOVING_HOPF_TRANSPORT"
        ),
        "same_hopf_base": same_base,
        "explicit_inverse_restores_exact_hopf_base": True,
        "source_target_exact_unit_s4": (
            source_hopf["exact_unit_s4_identity_verified"]
            and target_hopf["exact_unit_s4_identity_verified"]
        ),
        "full_fiber_equivariance_claimed": False,
    }
    result["classification_sha256"] = _sha256(result)
    return result


def classify_chiral_pair_flip_hopf(
    state: Mapping[str, Any],
    *,
    pair_index: int,
    transition_id: str,
) -> dict[str, Any]:
    index = _exact_int(pair_index, "PAIR_INDEX")
    if index < 0 or index >= len(CHIRAL_PAIRS):
        raise DiscreteHopfProjectionError("RML7_PAIR_INDEX_OUT_OF_RANGE")
    source_embedding = build_discrete_s7_embedding(state)
    source_hopf = hopf_project_embedding(source_embedding)
    first = flip_chiral_pair_half_turn(state, pair_index=index, transition_id=transition_id)
    target_state = first["next_state"]
    target_embedding = build_discrete_s7_embedding(target_state)
    target_hopf = hopf_project_embedding(target_embedding)
    second = flip_chiral_pair_half_turn(
        target_state,
        pair_index=index,
        transition_id=f"inverse:{transition_id}:hopf",
    )
    restored_embedding = build_discrete_s7_embedding(second["next_state"])
    restored_hopf = hopf_project_embedding(restored_embedding)
    same_base = source_hopf["s4_point_sha256"] == target_hopf["s4_point_sha256"]
    inverse_restores = source_hopf["s4_point_sha256"] == restored_hopf["s4_point_sha256"]
    if not inverse_restores:
        raise AssertionError("RML7_PAIR_FLIP_INVERSE_DID_NOT_RESTORE_HOPF_BASE")
    result = {
        "schema": GENERATOR_CLASS_SCHEMA,
        "generator_class": "U36_CHIRAL_PAIR_FLIP",
        "pair_index": index,
        "pair": list(CHIRAL_PAIRS[index]),
        "source_s4_point_sha256": source_hopf["s4_point_sha256"],
        "target_s4_point_sha256": target_hopf["s4_point_sha256"],
        "restored_s4_point_sha256": restored_hopf["s4_point_sha256"],
        "classification": (
            "FIBER_PRESERVING_SAME_HOPF_BASE"
            if same_base
            else "BASE_MOVING_HOPF_TRANSPORT"
        ),
        "same_hopf_base": same_base,
        "explicit_inverse_restores_exact_hopf_base": True,
        "source_target_exact_unit_s4": (
            source_hopf["exact_unit_s4_identity_verified"]
            and target_hopf["exact_unit_s4_identity_verified"]
        ),
        "full_fiber_equivariance_claimed": False,
    }
    result["classification_sha256"] = _sha256(result)
    return result


def audit_rml5_generators_on_hopf_candidate(state: Mapping[str, Any]) -> dict[str, Any]:
    """Classify the complete finite RML5 generator family on the Hopf candidate."""
    fiber_preserving = 0
    base_moving = 0
    coupled_cases = 0
    inverse_failures = 0
    for generator in ("x", "y", "z", "w"):
        for residue in range(PHASE_MODULUS):
            witness = classify_coupled_generator_hopf(
                state,
                generator=generator,
                signed_steps=residue,
                transition_id=f"rml7:audit:{generator}:{residue}",
            )
            coupled_cases += 1
            if witness["same_hopf_base"]:
                fiber_preserving += 1
            else:
                base_moving += 1
            if not witness["explicit_inverse_restores_exact_hopf_base"]:
                inverse_failures += 1
    pair_cases = 0
    for pair_index in range(len(CHIRAL_PAIRS)):
        witness = classify_chiral_pair_flip_hopf(
            state,
            pair_index=pair_index,
            transition_id=f"rml7:audit:pair:{pair_index}",
        )
        pair_cases += 1
        if witness["same_hopf_base"]:
            fiber_preserving += 1
        else:
            base_moving += 1
        if not witness["explicit_inverse_restores_exact_hopf_base"]:
            inverse_failures += 1

    total = coupled_cases + pair_cases
    result = {
        "schema": GENERATOR_AUDIT_SCHEMA,
        "source_state_sha256": state.get("state_sha256"),
        "coupled_z72_cases": coupled_cases,
        "u36_pair_flip_cases": pair_cases,
        "total_generator_cases": total,
        "same_base_fiber_preserving_cases": fiber_preserving,
        "base_moving_cases": base_moving,
        "classification_partition_complete": fiber_preserving + base_moving == total,
        "inverse_hopf_base_restoration_failures": inverse_failures,
        "all_explicit_inverses_restore_hopf_base": inverse_failures == 0,
        "rml5_generators_proven_to_map_exact_s7_points_to_exact_s4_base_points": True,
        "all_rml5_generators_claimed_fiber_preserving": False,
        "full_rml6_discrete_image_s3_fiber_equivariance_proven": False,
        "q8_fiber_invariance_available_as_exact_subgroup_witness": True,
        "bott_periodicity_correspondence_claimed": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "GENERATOR_AUDIT_SCHEMA",
    "GENERATOR_CLASS_SCHEMA",
    "HOPF_SCHEMA",
    "Q8",
    "Q8_FIBER_SCHEMA",
    "DiscreteHopfProjectionError",
    "audit_rml5_generators_on_hopf_candidate",
    "classify_chiral_pair_flip_hopf",
    "classify_coupled_generator_hopf",
    "hopf_project_embedding",
    "hopf_project_s7_point",
    "witness_q8_hopf_fiber",
]
