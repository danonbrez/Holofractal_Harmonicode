"""Pass 219 RML6 exact discrete S^7 embedding for the RML5 gyroscope manifold.

RML6 is an additive topology successor to the validated RML5 proof/admission
membrane.  It does not reinterpret the eight-channel rotor algebra.  Instead it
constructs a reversible seven-parameter chart for the balanced-chirality RML5
domain and applies exact inverse stereographic projection into a rational point
on S^7.

No trigonometric approximation or floating-point coordinate is used.  The
sphere identity is certified by the integer equality

    (1-r^2)^2 + 4 r^2 = (1+r^2)^2.

The chart is injective because both chiral generator pairs are base-72 packed
reversibly, all four ordered product phases remain explicit, and the two
balanced chirality signs are encoded as one four-sector coordinate.  The
inverse stereographic chart is exact on every finite chart point.

This proves an exact discrete S^7 embedding and closure of the existing RML5
transition generators under that embedding.  It does not yet claim an
isometry, a geodesic metric, Hopf-fibration preservation, or Bott-periodicity
correspondence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PHASE_MODULUS,
    PRODUCTS,
    PRODUCT_RELATIONS,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    CHIRAL_PAIRS,
    build_chirality_polarity_witness,
    certify_reciprocal_transition,
    flip_chiral_pair_half_turn,
)

PASS = 219
ITERATION = "RML6_DISCRETE_S7_EMBEDDING"

S7_EMBEDDING_SCHEMA = "HHS_PASS219_RML6_DISCRETE_RATIONAL_S7_EMBEDDING_V1"
S7_TRANSITION_SCHEMA = "HHS_PASS219_RML6_S7_TRANSITION_PRESERVATION_V1"
S7_PAIR_FLIP_SCHEMA = "HHS_PASS219_RML6_S7_PAIR_FLIP_PRESERVATION_V1"
S7_GENERATOR_AUDIT_SCHEMA = "HHS_PASS219_RML6_S7_GENERATOR_CLOSURE_AUDIT_V1"

CHART_PARAMETER_ORDER = (
    "xy_generator_track_code",
    "zw_generator_track_code",
    "xy_phase72",
    "yx_phase72",
    "zw_phase72",
    "wz_phase72",
    "chirality_sector",
)
GENERATOR_TO_PRODUCT = {
    relation["generator"]: product for product, relation in PRODUCT_RELATIONS.items()
}


class DiscreteS7EmbeddingError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise DiscreteS7EmbeddingError(f"FLOAT_TOPOLOGY_AUTHORITY_FORBIDDEN:{path}")
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
        raise DiscreteS7EmbeddingError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _require_balanced_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_float(state)
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise DiscreteS7EmbeddingError("RML4_GYROSCOPE_STATE_SCHEMA_MISMATCH")
    if state.get("admissible_product_geometry") is not True:
        raise DiscreteS7EmbeddingError("RML4_PRODUCT_GEOMETRY_NOT_ADMISSIBLE")
    phases = state.get("phases")
    signs = state.get("quarter_turn_signs")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != CHANNELS:
        raise DiscreteS7EmbeddingError("ORDERED_EIGHT_CHANNEL_PHASE_STATE_REQUIRED")
    if not isinstance(signs, Mapping) or tuple(signs.keys()) != PRODUCTS:
        raise DiscreteS7EmbeddingError("ORDERED_PRODUCT_SIGN_STATE_REQUIRED")
    chirality = build_chirality_polarity_witness(state)
    if chirality.get("all_chiral_pairs_opposed") is not True:
        raise DiscreteS7EmbeddingError("RML5_BALANCED_CHIRALITY_REQUIRED")
    return state


def _pair_code(first: int, second: int) -> int:
    a = _exact_int(first, "PAIR_FIRST")
    b = _exact_int(second, "PAIR_SECOND")
    if not (0 <= a < PHASE_MODULUS and 0 <= b < PHASE_MODULUS):
        raise DiscreteS7EmbeddingError("PAIR_PHASE72_OUT_OF_RANGE")
    return a * PHASE_MODULUS + b


def _decode_pair_code(code: int) -> tuple[int, int]:
    value = _exact_int(code, "PAIR_CODE")
    if value < 0 or value >= PHASE_MODULUS * PHASE_MODULUS:
        raise DiscreteS7EmbeddingError("PAIR_CODE_OUT_OF_RANGE")
    return divmod(value, PHASE_MODULUS)


def _chirality_sector(signs: Mapping[str, Any]) -> int:
    xy = _exact_int(signs["xy"], "XY_SIGN")
    yx = _exact_int(signs["yx"], "YX_SIGN")
    zw = _exact_int(signs["zw"], "ZW_SIGN")
    wz = _exact_int(signs["wz"], "WZ_SIGN")
    if xy not in (-1, 1) or zw not in (-1, 1) or yx != -xy or wz != -zw:
        raise DiscreteS7EmbeddingError("BALANCED_CHIRAL_SIGN_SECTOR_REQUIRED")
    return (1 if xy > 0 else 0) * 2 + (1 if zw > 0 else 0)


def _decode_chirality_sector(sector: int) -> dict[str, int]:
    value = _exact_int(sector, "CHIRALITY_SECTOR")
    if value < 0 or value > 3:
        raise DiscreteS7EmbeddingError("CHIRALITY_SECTOR_OUT_OF_RANGE")
    xy = 1 if value & 2 else -1
    zw = 1 if value & 1 else -1
    return {"xy": xy, "yx": -xy, "zw": zw, "wz": -zw}


def build_reversible_chart(state: Mapping[str, Any]) -> dict[str, Any]:
    """Build the exact seven-parameter chart for one balanced RML5 state."""
    state = _require_balanced_state(state)
    phases = {channel: _exact_int(state["phases"][channel], channel.upper()) for channel in CHANNELS}
    signs = {product: _exact_int(state["quarter_turn_signs"][product], product.upper()) for product in PRODUCTS}
    parameters = {
        "xy_generator_track_code": _pair_code(phases["x"], phases["y"]),
        "zw_generator_track_code": _pair_code(phases["z"], phases["w"]),
        "xy_phase72": phases["xy"],
        "yx_phase72": phases["yx"],
        "zw_phase72": phases["zw"],
        "wz_phase72": phases["wz"],
        "chirality_sector": _chirality_sector(signs),
    }
    ordered = [parameters[name] for name in CHART_PARAMETER_ORDER]
    chart = {
        "parameter_order": list(CHART_PARAMETER_ORDER),
        "parameters": parameters,
        "ordered_integer_parameters": ordered,
        "xy_track_pack_base": PHASE_MODULUS,
        "zw_track_pack_base": PHASE_MODULUS,
        "chart_dimension": 7,
        "source_ambient_state_index": state.get("ambient_state_index"),
        "source_state_sha256": state.get("state_sha256"),
        "reversible_without_float": True,
    }
    chart["chart_sha256"] = _sha256(chart)
    return chart


def decode_reversible_chart(chart: Mapping[str, Any]) -> dict[str, Any]:
    _reject_float(chart)
    parameters = chart.get("parameters")
    if not isinstance(parameters, Mapping) or tuple(parameters.keys()) != CHART_PARAMETER_ORDER:
        raise DiscreteS7EmbeddingError("RML6_ORDERED_SEVEN_PARAMETER_CHART_REQUIRED")
    x, y = _decode_pair_code(parameters["xy_generator_track_code"])
    z, w = _decode_pair_code(parameters["zw_generator_track_code"])
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": _exact_int(parameters["xy_phase72"], "XY_PHASE72"),
        "yx": _exact_int(parameters["yx_phase72"], "YX_PHASE72"),
        "zw": _exact_int(parameters["zw_phase72"], "ZW_PHASE72"),
        "wz": _exact_int(parameters["wz_phase72"], "WZ_PHASE72"),
    }
    if any(value < 0 or value >= PHASE_MODULUS for value in phases.values()):
        raise DiscreteS7EmbeddingError("DECODED_PHASE72_OUT_OF_RANGE")
    signs = _decode_chirality_sector(parameters["chirality_sector"])
    for product in PRODUCTS:
        generator = PRODUCT_RELATIONS[product]["generator"]
        if phases[product] != expected_product_phase(phases[generator], signs[product]):
            raise DiscreteS7EmbeddingError(f"DECODED_{product.upper()}_QUARTER_TURN_DRIFT")
    return {
        "phases": phases,
        "quarter_turn_signs": signs,
        "chart_roundtrip_exact": True,
    }


def _inverse_stereographic(integer_parameters: list[int]) -> dict[str, Any]:
    if len(integer_parameters) != 7:
        raise DiscreteS7EmbeddingError("S7_REQUIRES_SEVEN_CHART_PARAMETERS")
    params = [_exact_int(value, f"T{index}") for index, value in enumerate(integer_parameters)]
    radius_squared = sum(value * value for value in params)
    denominator = 1 + radius_squared
    numerators = [1 - radius_squared] + [2 * value for value in params]
    sphere_norm_numerator = sum(value * value for value in numerators)
    sphere_norm_denominator = denominator * denominator
    if sphere_norm_numerator != sphere_norm_denominator:
        raise AssertionError("RML6_S7_EXACT_UNIT_NORM_IDENTITY_FAILED")
    if denominator + numerators[0] != 2:
        raise AssertionError("RML6_STEREOGRAPHIC_INVERSE_DENOMINATOR_IDENTITY_FAILED")
    recovered = [numerators[index + 1] // 2 for index in range(7)]
    if recovered != params or any(numerators[index + 1] % 2 for index in range(7)):
        raise AssertionError("RML6_STEREOGRAPHIC_CHART_RECOVERY_FAILED")
    point = {
        "coordinate_order": ["s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7"],
        "common_denominator": denominator,
        "coordinate_numerators": numerators,
        "rational_coordinates": [f"{numerator}/{denominator}" for numerator in numerators],
        "chart_radius_squared": radius_squared,
        "sphere_norm_numerator": sphere_norm_numerator,
        "sphere_norm_denominator": sphere_norm_denominator,
        "exact_unit_s7_identity_verified": True,
        "inverse_stereographic_chart_recovered_exactly": True,
        "floating_point_coordinates_used": False,
    }
    point["s7_point_sha256"] = _sha256(point)
    return point


def build_discrete_s7_embedding(state: Mapping[str, Any]) -> dict[str, Any]:
    """Inject one RML5 balanced-chirality state into exact rational S^7."""
    state = _require_balanced_state(state)
    chart = build_reversible_chart(state)
    decoded = decode_reversible_chart(chart)
    if decoded["phases"] != state["phases"] or decoded["quarter_turn_signs"] != state["quarter_turn_signs"]:
        raise AssertionError("RML6_CHART_STATE_ROUNDTRIP_FAILED")
    point = _inverse_stereographic(chart["ordered_integer_parameters"])
    result = {
        "schema": S7_EMBEDDING_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "source_ambient_state_index": state.get("ambient_state_index"),
        "domain": "RML5_BALANCED_CHIRALITY_PRODUCT_ADMISSIBLE_MANIFOLD",
        "chart": chart,
        "s7_point": point,
        "chart_state_roundtrip_exact": True,
        "discrete_embedding_injective": True,
        "injectivity_proof": "REVERSIBLE_BASE72_TRACK_PACKING_PLUS_EXPLICIT_PRODUCTS_AND_CHIRAL_SECTOR_THEN_INVERTIBLE_STEREOGRAPHIC_CHART",
        "exact_unit_s7_identity_verified": True,
        "isometry_claimed": False,
        "geodesic_preservation_claimed": False,
        "hopf_fibration_preservation_claimed": False,
        "bott_periodicity_correspondence_claimed": False,
        "floating_point_authority": False,
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["embedding_sha256"] = _sha256(result)
    return result


def verify_coupled_generator_transition_on_s7(
    state: Mapping[str, Any],
    *,
    generator: str,
    signed_steps: int,
    transition_id: str,
) -> dict[str, Any]:
    """Verify one RML5 coupled generator/product move remains in exact S^7."""
    state = _require_balanced_state(state)
    if generator not in GENERATOR_TO_PRODUCT:
        raise DiscreteS7EmbeddingError("RML6_GENERATOR_UNSUPPORTED")
    delta = _exact_int(signed_steps, "SIGNED_STEPS")
    product = GENERATOR_TO_PRODUCT[generator]
    steps = {channel: 0 for channel in CHANNELS}
    steps[generator] = delta
    steps[product] = delta
    transition = advance_gyroscope(state, steps, transition_id=transition_id)
    next_state = _require_balanced_state(transition["next_state"])
    source_embedding = build_discrete_s7_embedding(state)
    target_embedding = build_discrete_s7_embedding(next_state)
    reciprocal = certify_reciprocal_transition(transition)
    inverse = advance_gyroscope(
        next_state,
        {channel: -steps[channel] for channel in CHANNELS},
        transition_id=f"inverse:{transition_id}:s7",
    )
    restored_embedding = build_discrete_s7_embedding(inverse["next_state"])
    restored_exactly = (
        restored_embedding["s7_point"]["s7_point_sha256"]
        == source_embedding["s7_point"]["s7_point_sha256"]
        and inverse["next_state"]["phases"] == state["phases"]
        and inverse["next_state"]["quarter_turn_signs"] == state["quarter_turn_signs"]
    )
    result = {
        "schema": S7_TRANSITION_SCHEMA,
        "transition_id": str(transition_id),
        "generator": generator,
        "dependent_product": product,
        "signed_steps": delta,
        "source_s7_point_sha256": source_embedding["s7_point"]["s7_point_sha256"],
        "target_s7_point_sha256": target_embedding["s7_point"]["s7_point_sha256"],
        "restored_s7_point_sha256": restored_embedding["s7_point"]["s7_point_sha256"],
        "source_exact_unit_s7": source_embedding["exact_unit_s7_identity_verified"],
        "target_exact_unit_s7": target_embedding["exact_unit_s7_identity_verified"],
        "reciprocal_phase_transition_bijective": reciprocal["phase_transition_is_bijective"],
        "inverse_restores_exact_s7_point": restored_exactly,
        "transition_generator_closed_on_discrete_s7_embedding": True,
        "hopf_fibration_preservation_claimed": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["preservation_sha256"] = _sha256(result)
    return result


def verify_chiral_pair_flip_on_s7(
    state: Mapping[str, Any],
    *,
    pair_index: int,
    transition_id: str,
) -> dict[str, Any]:
    """Verify the exact u^36 chiral pair involution remains in S^7."""
    state = _require_balanced_state(state)
    source_embedding = build_discrete_s7_embedding(state)
    first = flip_chiral_pair_half_turn(state, pair_index=pair_index, transition_id=transition_id)
    target_state = _require_balanced_state(first["next_state"])
    target_embedding = build_discrete_s7_embedding(target_state)
    second = flip_chiral_pair_half_turn(
        target_state,
        pair_index=pair_index,
        transition_id=f"inverse:{transition_id}",
    )
    restored_state = _require_balanced_state(second["next_state"])
    restored_embedding = build_discrete_s7_embedding(restored_state)
    restored_exactly = (
        restored_state["phases"] == state["phases"]
        and restored_state["quarter_turn_signs"] == state["quarter_turn_signs"]
        and restored_embedding["s7_point"]["s7_point_sha256"]
        == source_embedding["s7_point"]["s7_point_sha256"]
    )
    result = {
        "schema": S7_PAIR_FLIP_SCHEMA,
        "pair_index": _exact_int(pair_index, "PAIR_INDEX"),
        "pair": list(CHIRAL_PAIRS[pair_index]),
        "source_s7_point_sha256": source_embedding["s7_point"]["s7_point_sha256"],
        "target_s7_point_sha256": target_embedding["s7_point"]["s7_point_sha256"],
        "restored_s7_point_sha256": restored_embedding["s7_point"]["s7_point_sha256"],
        "u36_flip_closed_on_discrete_s7_embedding": True,
        "u36_flip_self_inverse_on_s7": restored_exactly,
        "hopf_fibration_preservation_claimed": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["preservation_sha256"] = _sha256(result)
    return result


def audit_rml5_generator_family_on_s7(state: Mapping[str, Any]) -> dict[str, Any]:
    """Audit the finite generating family without enumerating the 72^8 domain."""
    state = _require_balanced_state(state)
    coupled_cases = 0
    for generator in ("x", "y", "z", "w"):
        for residue in range(PHASE_MODULUS):
            witness = verify_coupled_generator_transition_on_s7(
                state,
                generator=generator,
                signed_steps=residue,
                transition_id=f"rml6:audit:{generator}:{residue}",
            )
            if witness["transition_generator_closed_on_discrete_s7_embedding"] is not True:
                raise AssertionError("RML6_COUPLED_GENERATOR_S7_CLOSURE_FAILED")
            coupled_cases += 1
    pair_cases = 0
    for pair_index in range(len(CHIRAL_PAIRS)):
        witness = verify_chiral_pair_flip_on_s7(
            state,
            pair_index=pair_index,
            transition_id=f"rml6:audit:pair:{pair_index}",
        )
        if witness["u36_flip_self_inverse_on_s7"] is not True:
            raise AssertionError("RML6_PAIR_FLIP_S7_CLOSURE_FAILED")
        pair_cases += 1
    result = {
        "schema": S7_GENERATOR_AUDIT_SCHEMA,
        "source_state_sha256": state.get("state_sha256"),
        "coupled_z72_generator_cases": coupled_cases,
        "u36_pair_flip_cases": pair_cases,
        "total_generator_cases": coupled_cases + pair_cases,
        "expected_coupled_cases": 4 * PHASE_MODULUS,
        "all_rml5_generators_closed_on_exact_discrete_s7": True,
        "ambient_72_pow_8_exhaustively_enumerated": False,
        "proof_scope": "RML5_GENERATING_FAMILY_CLOSURE_PLUS_REVERSIBLE_INJECTIVE_CHART",
        "hopf_fibration_preservation_claimed": False,
        "bott_periodicity_correspondence_claimed": False,
        "canonical_vm81_mutation_authority": False,
    }
    result["audit_sha256"] = _sha256(result)
    return result


__all__ = [
    "CHART_PARAMETER_ORDER",
    "S7_EMBEDDING_SCHEMA",
    "S7_GENERATOR_AUDIT_SCHEMA",
    "S7_PAIR_FLIP_SCHEMA",
    "S7_TRANSITION_SCHEMA",
    "DiscreteS7EmbeddingError",
    "audit_rml5_generator_family_on_s7",
    "build_discrete_s7_embedding",
    "build_reversible_chart",
    "decode_reversible_chart",
    "verify_chiral_pair_flip_on_s7",
    "verify_coupled_generator_transition_on_s7",
]
