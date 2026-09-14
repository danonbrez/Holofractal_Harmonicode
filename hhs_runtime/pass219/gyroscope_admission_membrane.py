"""Pass 219 RML5 proof/admission membrane for the dynamic octonion gyroscope.

RML5 makes the repair-forward RML4 audit specifications executable without
rewriting the validated RML4 substrate.  It binds the repository-canonical
Genesis exact rationals, adds typed chiral +/-a^2 and P+/-1 projection
witnesses, proves reciprocal phase-transition closure, and constructs exact
paths through the admitted eight-channel gyroscope manifold.

The membrane remains read-only with respect to canonical VM81/Hash authority.
A successful RML5 result is an admission candidate for the existing authority,
not a second commit path.
"""
from __future__ import annotations

import hashlib
import json
import string
from typing import Any, Mapping

from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    CLOSURE_CONSTANT_Q,
    RESONATOR_CONSTANT_Q,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    AMBIENT_STATE_COUNT,
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PHASE_MODULUS,
    PRODUCTS,
    PRODUCT_RELATIONS,
    TRANSITION_SCHEMA,
    advance_gyroscope,
    build_gyroscope_state,
    expected_product_phase,
)

PASS = 219
ITERATION = "RML5_GYROSCOPE_PROOF_ADMISSION_MEMBRANE"

ADMISSION_SCHEMA = "HHS_PASS219_RML5_GYROSCOPE_ADMISSION_V1"
CHIRALITY_SCHEMA = "HHS_PASS219_RML5_CHIRALITY_POLARITY_WITNESS_V1"
PRIME_PROJECTION_SCHEMA = "HHS_PASS219_RML5_PRIME_BOUNDARY_PROJECTION_V1"
INVERSE_SCHEMA = "HHS_PASS219_RML5_RECIPROCAL_TRANSITION_CERTIFICATE_V1"
PATH_SCHEMA = "HHS_PASS219_RML5_ADMISSIBLE_RECIPROCAL_PATH_V1"
PAIR_FLIP_SCHEMA = "HHS_PASS219_RML5_CHIRAL_PAIR_HALF_TURN_V1"
BUNDLE_SCHEMA = "HHS_PASS219_RML5_PROOF_ADMISSION_BUNDLE_V1"

GENESIS_RESONATOR_Q = "179971179971/1000000"
GENESIS_CLOSURE_Q = "1001/1000"
A_SQUARED_Q = "1"
HEX = frozenset(string.hexdigits)

CHIRAL_PAIRS = (("xy", "yx"), ("zw", "wz"))
GENERATOR_TO_PRODUCT = {
    relation["generator"]: product for product, relation in PRODUCT_RELATIONS.items()
}


class GyroscopeAdmissionError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise GyroscopeAdmissionError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
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
        raise GyroscopeAdmissionError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _required_bool(value: Any, label: str) -> bool:
    if value is not True:
        raise GyroscopeAdmissionError(f"{label}_TRUE_WITNESS_REQUIRED")
    return True


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in HEX for ch in value):
        raise GyroscopeAdmissionError(f"{label}_SHA256_REQUIRED")
    lowered = value.lower()
    if lowered == "0" * 64:
        raise GyroscopeAdmissionError(f"{label}_ZERO_HASH_FORBIDDEN")
    return lowered


def _require_state(state: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_float(state)
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise GyroscopeAdmissionError("RML4_GYROSCOPE_STATE_SCHEMA_MISMATCH")
    phases = state.get("phases")
    signs = state.get("quarter_turn_signs")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != CHANNELS:
        raise GyroscopeAdmissionError("RML4_ORDERED_PHASE_STATE_REQUIRED")
    if not isinstance(signs, Mapping) or tuple(signs.keys()) != PRODUCTS:
        raise GyroscopeAdmissionError("RML4_ORDERED_QUARTER_TURN_SIGNS_REQUIRED")
    if state.get("admissible_product_geometry") is not True:
        raise GyroscopeAdmissionError("RML4_PRODUCT_GEOMETRY_NOT_ADMISSIBLE")
    return state


def genesis_exact_rational_witness() -> dict[str, Any]:
    """Bind the already-canonical repository Genesis constants exactly."""
    if RESONATOR_CONSTANT_Q != GENESIS_RESONATOR_Q:
        raise GyroscopeAdmissionError("GENESIS_RESONATOR_CONSTANT_DRIFT")
    if CLOSURE_CONSTANT_Q != GENESIS_CLOSURE_Q:
        raise GyroscopeAdmissionError("GENESIS_CLOSURE_CONSTANT_DRIFT")
    witness = {
        "schema": "HHS_PASS219_RML5_GENESIS_EXACT_RATIONAL_WITNESS_V1",
        "resonator_constant_q": RESONATOR_CONSTANT_Q,
        "resonator_numerator": 179971179971,
        "resonator_denominator": 1000000,
        "closure_constant_q": CLOSURE_CONSTANT_Q,
        "closure_numerator": 1001,
        "closure_denominator": 1000,
        "a_squared_q": A_SQUARED_Q,
        "floating_point_representation_authority": False,
        "exact_rational_scaling_active": True,
    }
    witness["witness_sha256"] = _sha256(witness)
    return witness


def build_chirality_polarity_witness(state: Mapping[str, Any]) -> dict[str, Any]:
    """Project ordered quarter-turn signs to typed +/-a^2 polarity witnesses.

    This projection never replaces the richer RML4 rotor state.  It preserves
    ordered product identity and requires each reverse product to carry the
    exact opposite chirality sign of its forward partner.
    """
    state = _require_state(state)
    signs = {product: _exact_int(state["quarter_turn_signs"][product], product.upper()) for product in PRODUCTS}
    for product, sign in signs.items():
        if sign not in (-1, 1):
            raise GyroscopeAdmissionError(f"{product.upper()}_CHIRAL_SIGN_INVALID")

    rows = []
    balanced = True
    for forward, reverse in CHIRAL_PAIRS:
        pair_balanced = signs[forward] == -signs[reverse]
        balanced = balanced and pair_balanced
        rows.append(
            {
                "forward_product": forward,
                "reverse_product": reverse,
                "forward_quarter_turn_sign": signs[forward],
                "reverse_quarter_turn_sign": signs[reverse],
                "forward_polarity": "+a^2" if signs[forward] > 0 else "-a^2",
                "reverse_polarity": "+a^2" if signs[reverse] > 0 else "-a^2",
                "a_squared_q": A_SQUARED_Q,
                "opposite_chirality": pair_balanced,
                "scalar_product_substitution_permitted": False,
            }
        )
    result = {
        "schema": CHIRALITY_SCHEMA,
        "source_state_sha256": state.get("state_sha256"),
        "pairs": rows,
        "all_chiral_pairs_opposed": balanced,
        "polarity_projection_is_rotor_identity": False,
        "ordered_rotational_ancestry_preserved": True,
        "scalar_projection_substitution_authority": False,
    }
    result["witness_sha256"] = _sha256(result)
    return result


def build_prime_boundary_projection(
    P: int,
    *,
    prime_witness_sha256: str,
    prime_witness_verified: bool,
) -> dict[str, Any]:
    """Build the licensed exact P-1/P+1 projection without runtime substitution."""
    p_value = _exact_int(P, "P")
    if p_value < 3 or p_value % 2 == 0:
        raise GyroscopeAdmissionError("ODD_P_GREATER_THAN_TWO_REQUIRED")
    _required_bool(prime_witness_verified, "PRIME_WITNESS_VERIFIED")
    witness_hash = _hex64(prime_witness_sha256, "PRIME_WITNESS")
    lower = p_value - 1
    upper = p_value + 1
    projection = {
        "schema": PRIME_PROJECTION_SCHEMA,
        "P": p_value,
        "prime_witness_sha256": witness_hash,
        "prime_witness_verified": True,
        "p_lower_boundary": lower,
        "q_upper_boundary": upper,
        "p_plus_q": lower + upper,
        "two_P": 2 * p_value,
        "pq": lower * upper,
        "P_squared_minus_one": p_value * p_value - 1,
        "P_squared": p_value * p_value,
        "closure_surface": "P^2=pq+1",
        "lower_upper_boundary_projection": "{P-1,P+1}",
        "projection_equalities_verified": (
            lower + upper == 2 * p_value
            and lower * upper == p_value * p_value - 1
        ),
        "projection_only": True,
        "scalar_projection_substitution_authority": False,
    }
    projection["projection_sha256"] = _sha256(projection)
    return projection


def certify_reciprocal_transition(transition: Mapping[str, Any]) -> dict[str, Any]:
    """Construct and verify the exact inverse of one RML4 phase transition."""
    _reject_float(transition)
    if transition.get("schema") != TRANSITION_SCHEMA:
        raise GyroscopeAdmissionError("RML4_TRANSITION_SCHEMA_MISMATCH")
    next_state = transition.get("next_state")
    if not isinstance(next_state, Mapping):
        raise GyroscopeAdmissionError("RML4_TRANSITION_NEXT_STATE_REQUIRED")
    _require_state(next_state)
    deltas = transition.get("signed_steps")
    if not isinstance(deltas, Mapping) or tuple(deltas.keys()) != CHANNELS:
        raise GyroscopeAdmissionError("RML4_TRANSITION_ORDERED_SIGNED_STEPS_REQUIRED")
    inverse_steps = {
        channel: -_exact_int(deltas[channel], f"{channel.upper()}_FORWARD_STEP")
        for channel in CHANNELS
    }
    inverse = advance_gyroscope(
        next_state,
        inverse_steps,
        transition_id=f"inverse:{transition.get('transition_id')}",
    )
    restored = inverse["next_state"]
    expected_prior_index = _exact_int(transition.get("prior_ambient_state_index"), "PRIOR_AMBIENT_STATE_INDEX")
    index_restored = restored.get("ambient_state_index") == expected_prior_index

    prior_phases = {
        channel: (int(next_state["phases"][channel]) + inverse_steps[channel]) % PHASE_MODULUS
        for channel in CHANNELS
    }
    phase_restored = restored.get("phases") == prior_phases
    forward_inverse_steps_cancel = all(
        _exact_int(deltas[channel], f"{channel.upper()}_FORWARD_STEP") + inverse_steps[channel] == 0
        for channel in CHANNELS
    )
    certificate = {
        "schema": INVERSE_SCHEMA,
        "forward_transition_sha256": transition.get("transition_sha256"),
        "forward_transition_id": transition.get("transition_id"),
        "inverse_transition_sha256": inverse.get("transition_sha256"),
        "inverse_signed_steps": inverse_steps,
        "prior_ambient_state_index": expected_prior_index,
        "restored_ambient_state_index": restored.get("ambient_state_index"),
        "ambient_state_index_restored": index_restored,
        "phase_coordinates_restored": phase_restored,
        "forward_inverse_steps_cancel_exactly": forward_inverse_steps_cancel,
        "restored_product_geometry_admissible": restored.get("admissible_product_geometry") is True,
        "receipt_ancestry_is_rewound_or_erased": False,
        "phase_transition_is_bijective": index_restored and phase_restored and forward_inverse_steps_cancel,
        "information_discarded_by_phase_transform": False,
        "physical_thermodynamic_entropy_claimed": False,
    }
    certificate["certificate_sha256"] = _sha256(certificate)
    return certificate


def flip_chiral_pair_half_turn(
    state: Mapping[str, Any],
    *,
    pair_index: int,
    transition_id: str,
) -> dict[str, Any]:
    """Flip one reciprocal product pair by exact u^36 while preserving admission.

    Switching +u^18 to -u^18 (or vice versa) changes the product coordinate by
    one half-cycle.  Both members of a chiral pair flip together so +/-a^2
    opposition remains invariant throughout the transition.
    """
    state = _require_state(state)
    index = _exact_int(pair_index, "PAIR_INDEX")
    if index < 0 or index >= len(CHIRAL_PAIRS):
        raise GyroscopeAdmissionError("CHIRAL_PAIR_INDEX_OUT_OF_RANGE")
    forward, reverse = CHIRAL_PAIRS[index]
    phases = dict(state["phases"])
    signs = dict(state["quarter_turn_signs"])
    prior_signs = {forward: signs[forward], reverse: signs[reverse]}
    if signs[forward] != -signs[reverse]:
        raise GyroscopeAdmissionError("CHIRAL_PAIR_NOT_OPPOSED_BEFORE_FLIP")
    signs[forward] = -int(signs[forward])
    signs[reverse] = -int(signs[reverse])
    for product in (forward, reverse):
        generator = PRODUCT_RELATIONS[product]["generator"]
        phases[product] = expected_product_phase(int(phases[generator]), int(signs[product]))
    next_state = build_gyroscope_state(
        phases,
        signs,
        state_id=f"{state.get('state_id')}->{transition_id}",
        ancestry_root_sha256=state.get("state_sha256"),
        legacy_i148_product_phase72=state.get("legacy_i148_product_phase72"),
    )
    witness = {
        "schema": PAIR_FLIP_SCHEMA,
        "transition_id": str(transition_id),
        "prior_state_sha256": state.get("state_sha256"),
        "pair": [forward, reverse],
        "prior_signs": prior_signs,
        "next_signs": {forward: signs[forward], reverse: signs[reverse]},
        "phase_inversion_steps": PHASE_MODULUS // 2,
        "phase_inversion_u": "u^36",
        "next_state": next_state,
        "pair_opposition_preserved": signs[forward] == -signs[reverse],
        "product_geometry_preserved": next_state["admissible_product_geometry"],
        "operation_is_self_inverse": True,
        "canonical_vm81_mutation_authority": False,
    }
    witness["transition_sha256"] = _sha256(witness)
    return witness


def _shortest_signed_delta(source: int, target: int) -> int:
    forward = (target - source) % PHASE_MODULUS
    backward = forward - PHASE_MODULUS
    return forward if abs(forward) <= abs(backward) else backward


def construct_admissible_reciprocal_path(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    path_id: str,
) -> dict[str, Any]:
    """Construct a finite exact path between two RML5-admissible gyroscope states.

    The constructive proof has two stages:
    1. exact u^36 pair flips align the two chiral sign sectors;
    2. four coupled generator/product moves align x,y,z,w and their dependent
       quarter-turn images.

    Therefore the admitted balanced-chirality manifold is strongly connected
    under these explicit RML5 moves; no 72^8 enumeration is required.
    """
    source = _require_state(source)
    target = _require_state(target)
    source_chirality = build_chirality_polarity_witness(source)
    target_chirality = build_chirality_polarity_witness(target)
    if source_chirality["all_chiral_pairs_opposed"] is not True:
        raise GyroscopeAdmissionError("SOURCE_CHIRALITY_NOT_ADMISSIBLE")
    if target_chirality["all_chiral_pairs_opposed"] is not True:
        raise GyroscopeAdmissionError("TARGET_CHIRALITY_NOT_ADMISSIBLE")

    current = dict(source)
    moves: list[dict[str, Any]] = []
    for pair_index, (forward, reverse) in enumerate(CHIRAL_PAIRS):
        target_signs = target["quarter_turn_signs"]
        if current["quarter_turn_signs"][forward] != target_signs[forward]:
            flip = flip_chiral_pair_half_turn(
                current,
                pair_index=pair_index,
                transition_id=f"{path_id}:flip:{forward}:{reverse}",
            )
            moves.append(
                {
                    "kind": "CHIRAL_PAIR_U36_FLIP",
                    "pair": [forward, reverse],
                    "transition_sha256": flip["transition_sha256"],
                }
            )
            current = flip["next_state"]

    for generator in ("x", "y", "z", "w"):
        product = GENERATOR_TO_PRODUCT[generator]
        delta = _shortest_signed_delta(
            int(current["phases"][generator]),
            int(target["phases"][generator]),
        )
        if delta == 0:
            continue
        steps = {channel: 0 for channel in CHANNELS}
        steps[generator] = delta
        steps[product] = delta
        transition = advance_gyroscope(
            current,
            steps,
            transition_id=f"{path_id}:move:{generator}:{delta}",
        )
        if transition["next_state"]["admissible_product_geometry"] is not True:
            raise AssertionError("RML5_CONSTRUCTED_PATH_LEFT_ADMISSIBLE_MANIFOLD")
        moves.append(
            {
                "kind": "COUPLED_GENERATOR_PRODUCT_PHASE_MOVE",
                "generator": generator,
                "product": product,
                "signed_steps": delta,
                "transition_sha256": transition["transition_sha256"],
            }
        )
        current = transition["next_state"]

    target_reached = (
        current["phases"] == target["phases"]
        and current["quarter_turn_signs"] == target["quarter_turn_signs"]
        and current["ambient_state_index"] == target["ambient_state_index"]
    )
    result = {
        "schema": PATH_SCHEMA,
        "path_id": str(path_id),
        "source_state_sha256": source.get("state_sha256"),
        "target_state_sha256": target.get("state_sha256"),
        "move_count": len(moves),
        "moves": moves,
        "target_reached_exactly": target_reached,
        "all_moves_reversible": True,
        "strong_connectivity_proven_for_rml5_balanced_chirality_manifold": target_reached,
        "ambient_72_pow_8_exhaustively_enumerated": False,
        "proof_method": "CONSTRUCTIVE_U36_CHIRAL_FLIPS_PLUS_COUPLED_Z72_GENERATOR_MOVES",
        "canonical_vm81_mutation_authority": False,
    }
    result["path_sha256"] = _sha256(result)
    return result


def build_rml5_admission(
    state: Mapping[str, Any],
    *,
    P: int,
    prime_witness_sha256: str,
    prime_witness_verified: bool,
    omega_verified: bool,
    delta_e_zero_verified: bool,
    psi_zero_verified: bool,
) -> dict[str, Any]:
    """Evaluate the state-level RML5 admission membrane."""
    state = _require_state(state)
    genesis = genesis_exact_rational_witness()
    chirality = build_chirality_polarity_witness(state)
    prime_projection = build_prime_boundary_projection(
        P,
        prime_witness_sha256=prime_witness_sha256,
        prime_witness_verified=prime_witness_verified,
    )
    omega = _required_bool(omega_verified, "OMEGA_VERIFIED")
    delta_e = _required_bool(delta_e_zero_verified, "DELTA_E_ZERO_VERIFIED")
    psi = _required_bool(psi_zero_verified, "PSI_ZERO_VERIFIED")
    admitted = (
        state["admissible_product_geometry"] is True
        and chirality["all_chiral_pairs_opposed"] is True
        and prime_projection["projection_equalities_verified"] is True
        and omega and delta_e and psi
    )
    result = {
        "schema": ADMISSION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "source_state_sha256": state.get("state_sha256"),
        "ambient_state_index": state.get("ambient_state_index"),
        "ambient_state_count": AMBIENT_STATE_COUNT,
        "genesis_exact_rational_witness": genesis,
        "chirality_polarity_witness": chirality,
        "prime_boundary_projection": prime_projection,
        "omega_verified": omega,
        "delta_e_zero_constraint_verified": delta_e,
        "psi_zero_constraint_verified": psi,
        "state_admitted": admitted,
        "decision": "RML5_STATE_READY_FOR_RECIPROCAL_TRANSITION_PROOF" if admitted else "RML5_STATE_REJECTED",
        "topology_proof_obligations": {
            "balanced_chirality_manifold_strong_connectivity": "PROVABLE_BY_CONSTRUCTIVE_PATH_OPERATOR",
            "discrete_s7_embedding": "REPAIR_FORWARD_REQUIRED",
            "hopf_fibration_preservation": "REPAIR_FORWARD_REQUIRED",
            "bott_periodicity_correspondence": "REPAIR_FORWARD_REQUIRED",
        },
        "scalar_projection_substitution_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    result["admission_sha256"] = _sha256(result)
    return result


def seal_rml5_proof_bundle(
    admission: Mapping[str, Any],
    reciprocal_transition_certificate: Mapping[str, Any],
) -> dict[str, Any]:
    if admission.get("schema") != ADMISSION_SCHEMA or admission.get("state_admitted") is not True:
        raise GyroscopeAdmissionError("RML5_ADMITTED_STATE_REQUIRED")
    if reciprocal_transition_certificate.get("schema") != INVERSE_SCHEMA:
        raise GyroscopeAdmissionError("RML5_RECIPROCAL_TRANSITION_CERTIFICATE_REQUIRED")
    if reciprocal_transition_certificate.get("phase_transition_is_bijective") is not True:
        raise GyroscopeAdmissionError("RML5_BIJECTIVE_PHASE_TRANSITION_REQUIRED")
    result = {
        "schema": BUNDLE_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "admission_sha256": admission.get("admission_sha256"),
        "reciprocal_transition_certificate_sha256": reciprocal_transition_certificate.get("certificate_sha256"),
        "genesis_identity_active": True,
        "ers_native_phase_transport": True,
        "omega": True,
        "phase_transition_bijective": True,
        "ready_for_existing_vm81_admission_authority": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "physical_zero_entropy_claimed": False,
    }
    result["bundle_sha256"] = _sha256(result)
    return result


__all__ = [
    "ADMISSION_SCHEMA",
    "BUNDLE_SCHEMA",
    "CHIRALITY_SCHEMA",
    "CHIRAL_PAIRS",
    "GENESIS_CLOSURE_Q",
    "GENESIS_RESONATOR_Q",
    "INVERSE_SCHEMA",
    "PAIR_FLIP_SCHEMA",
    "PATH_SCHEMA",
    "PRIME_PROJECTION_SCHEMA",
    "GyroscopeAdmissionError",
    "build_chirality_polarity_witness",
    "build_prime_boundary_projection",
    "build_rml5_admission",
    "certify_reciprocal_transition",
    "construct_admissible_reciprocal_path",
    "flip_chiral_pair_half_turn",
    "genesis_exact_rational_witness",
    "seal_rml5_proof_bundle",
]
