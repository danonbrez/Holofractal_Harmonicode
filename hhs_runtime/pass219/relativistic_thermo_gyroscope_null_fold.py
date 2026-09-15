"""Pass 219 exact relativistic/thermodynamic scalar projections over the RML4/RML5 gyroscope.

This additive layer binds the already-canonical dynamic octonion gyroscope to
exact scalar projection witnesses without granting scalar projections authority
to rewrite gyroscope state.

The relativistic ingress is the common complement-square surface

    rho^2 = 1 - kappa

where kappa is supplied as an exact non-negative rational.  The square root is
not evaluated.  Instead the sign of the exact complement selects the typed
projection branch:

    +1 : commutative metric projection
     0 : hyperbolic zero-sum fold
    -1 : non-commutative phase projection

A null crossing is witnessed by the inherited exact self-inverse RML5 u^36
chiral-pair half-turn.  Ordered phase identity is preserved and the original
phase payload is exactly recoverable by applying the same half-turn twice.

The thermodynamic ingress reuses the existing exact reciprocal closure

    Phi(G) + Phi(G^-1) = (G-1)^2/G

for positive rational G without evaluating logarithms.

This module is candidate/projection logic only.  It does not mutate canonical
VM81 state, mint Hash72/Hash216, or persist canonical state.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    GYROSCOPE_SCHEMA,
    PRODUCTS,
    evaluate_product_constraints,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    PAIR_FLIP_SCHEMA,
    flip_chiral_pair_half_turn,
)

PASS = 219
ITERATION = "RELATIVISTIC_THERMO_GYROSCOPE_NULL_FOLD"

RELATIVISTIC_PROJECTION_SCHEMA = "HHS_PASS219_RELATIVISTIC_GYROSCOPE_PROJECTION_V1"
NULL_FOLD_SCHEMA = "HHS_PASS219_RELATIVISTIC_GYROSCOPE_NULL_FOLD_V1"
THERMO_PROJECTION_SCHEMA = "HHS_PASS219_THERMO_RECIPROCAL_GYROSCOPE_PROJECTION_V1"

PROJECTION_KINDS = (
    "VELOCITY_TIME_DILATION",
    "GRAVITATIONAL_TIME_DILATION",
    "GENERIC_RELATIVISTIC_COMPLEMENT",
)

BRANCH_LABELS = {
    1: "COMMUTATIVE_METRIC_PROJECTION",
    0: "HYPERBOLIC_ZERO_SUM_FOLD",
    -1: "NONCOMMUTATIVE_PHASE_PROJECTION",
}


class RelativisticGyroscopeError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise RelativisticGyroscopeError(f"FLOAT_CANONICAL_AUTHORITY_FORBIDDEN:{path}")
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
        raise RelativisticGyroscopeError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise RelativisticGyroscopeError(f"{label}_NONEMPTY_STRING_REQUIRED")
    return value


def _reduced_rational(
    numerator: Any,
    denominator: Any,
    label: str,
    *,
    nonnegative: bool = False,
    positive: bool = False,
) -> tuple[int, int]:
    n = _exact_int(numerator, f"{label}_NUMERATOR")
    d = _exact_int(denominator, f"{label}_DENOMINATOR")
    if d == 0:
        raise RelativisticGyroscopeError(f"{label}_DENOMINATOR_ZERO")
    if d < 0:
        n = -n
        d = -d
    if positive and n <= 0:
        raise RelativisticGyroscopeError(f"{label}_POSITIVE_REQUIRED")
    if nonnegative and n < 0:
        raise RelativisticGyroscopeError(f"{label}_NONNEGATIVE_REQUIRED")
    common = math.gcd(abs(n), d)
    return n // common, d // common


def _require_gyroscope(state: Mapping[str, Any]) -> Mapping[str, Any]:
    _reject_float(state)
    if state.get("schema") != GYROSCOPE_SCHEMA:
        raise RelativisticGyroscopeError("RML4_GYROSCOPE_STATE_SCHEMA_MISMATCH")
    phases = state.get("phases")
    signs = state.get("quarter_turn_signs")
    if not isinstance(phases, Mapping) or tuple(phases.keys()) != CHANNELS:
        raise RelativisticGyroscopeError("ORDERED_EIGHT_CHANNEL_PHASE_STATE_REQUIRED")
    if not isinstance(signs, Mapping) or tuple(signs.keys()) != PRODUCTS:
        raise RelativisticGyroscopeError("ORDERED_PRODUCT_SIGN_STATE_REQUIRED")
    if state.get("admissible_product_geometry") is not True:
        raise RelativisticGyroscopeError("ADMISSIBLE_PRODUCT_GEOMETRY_REQUIRED")
    state_sha256 = state.get("state_sha256")
    if not isinstance(state_sha256, str) or len(state_sha256) != 64:
        raise RelativisticGyroscopeError("GYROSCOPE_STATE_SHA256_REQUIRED")
    unsigned = dict(state)
    unsigned.pop("state_sha256", None)
    if _sha256(unsigned) != state_sha256:
        raise RelativisticGyroscopeError("GYROSCOPE_STATE_SHA256_MISMATCH")
    recomputed_constraints = evaluate_product_constraints(phases, signs)
    if recomputed_constraints.get("all_product_quarter_turn_relations_satisfied") is not True:
        raise RelativisticGyroscopeError("RML4_PRODUCT_GEOMETRY_RECOMPUTE_FAILED")
    return state


def _state_snapshot(state: Mapping[str, Any]) -> dict[str, Any]:
    state = _require_gyroscope(state)
    return {
        "state_sha256": state["state_sha256"],
        "ambient_state_index": _exact_int(state.get("ambient_state_index"), "AMBIENT_STATE_INDEX"),
        "channel_order": list(CHANNELS),
        "phases": {channel: _exact_int(state["phases"][channel], channel.upper()) for channel in CHANNELS},
        "product_order": list(PRODUCTS),
        "quarter_turn_signs": {
            product: _exact_int(state["quarter_turn_signs"][product], product.upper())
            for product in PRODUCTS
        },
    }


def build_relativistic_projection(
    state: Mapping[str, Any],
    *,
    projection_id: str,
    projection_kind: str,
    kappa_numerator: int,
    kappa_denominator: int,
) -> dict[str, Any]:
    """Bind exact kappa to rho^2 = 1-kappa without evaluating a square root."""
    state = _require_gyroscope(state)
    pid = _nonempty(projection_id, "PROJECTION_ID")
    if projection_kind not in PROJECTION_KINDS:
        raise RelativisticGyroscopeError("RELATIVISTIC_PROJECTION_KIND_UNSUPPORTED")
    k_num, k_den = _reduced_rational(
        kappa_numerator,
        kappa_denominator,
        "KAPPA",
        nonnegative=True,
    )
    r_num, r_den = _reduced_rational(k_den - k_num, k_den, "COMPLEMENT")
    branch = 1 if r_num > 0 else -1 if r_num < 0 else 0

    projection = {
        "schema": RELATIVISTIC_PROJECTION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "projection_id": pid,
        "projection_kind": projection_kind,
        "source_expression": (
            "1-v^2/c^2"
            if projection_kind == "VELOCITY_TIME_DILATION"
            else "1-2GM/(rc^2)"
            if projection_kind == "GRAVITATIONAL_TIME_DILATION"
            else "1-kappa"
        ),
        "common_constructor": "rho^2=1-kappa",
        "kappa": {"numerator": k_num, "denominator": k_den},
        "rho_squared": {"numerator": r_num, "denominator": r_den},
        "branch": branch,
        "branch_label": BRANCH_LABELS[branch],
        "square_root_evaluated": False,
        "scalar_projection_is_complete_gyroscope_state": False,
        "typed_projection_zero_is_state_zero": False,
        "gyroscope": _state_snapshot(state),
        "ordered_phase_identity_preserved": True,
        "commutative_reorder_permitted": False,
        "floating_point_canonical_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    projection["projection_sha256"] = _sha256(projection)
    return projection


def build_null_fold_transition(
    state: Mapping[str, Any],
    *,
    transition_id: str,
    projection_kind: str,
    before_kappa_numerator: int,
    before_kappa_denominator: int,
    after_kappa_numerator: int,
    after_kappa_denominator: int,
    pair_index: int,
) -> dict[str, Any]:
    """Witness +1 -> 0 -> -1 projection crossing through exact u^36 phase transport."""
    state = _require_gyroscope(state)
    tid = _nonempty(transition_id, "TRANSITION_ID")
    before = build_relativistic_projection(
        state,
        projection_id=f"{tid}:before",
        projection_kind=projection_kind,
        kappa_numerator=before_kappa_numerator,
        kappa_denominator=before_kappa_denominator,
    )
    if before["branch"] != 1:
        raise RelativisticGyroscopeError("NULL_FOLD_REQUIRES_POSITIVE_BEFORE_BRANCH")

    at_fold = build_relativistic_projection(
        state,
        projection_id=f"{tid}:fold",
        projection_kind=projection_kind,
        kappa_numerator=1,
        kappa_denominator=1,
    )
    if at_fold["branch"] != 0:
        raise AssertionError("NULL_FOLD_INTERNAL_BRANCH")

    flip = flip_chiral_pair_half_turn(
        state,
        pair_index=_exact_int(pair_index, "PAIR_INDEX"),
        transition_id=f"{tid}:u36",
    )
    if flip.get("schema") != PAIR_FLIP_SCHEMA:
        raise RelativisticGyroscopeError("RML5_PAIR_FLIP_SCHEMA_MISMATCH")
    next_state = flip.get("next_state")
    if not isinstance(next_state, Mapping):
        raise RelativisticGyroscopeError("RML5_PAIR_FLIP_NEXT_STATE_REQUIRED")
    _require_gyroscope(next_state)

    after = build_relativistic_projection(
        next_state,
        projection_id=f"{tid}:after",
        projection_kind=projection_kind,
        kappa_numerator=after_kappa_numerator,
        kappa_denominator=after_kappa_denominator,
    )
    if after["branch"] != -1:
        raise RelativisticGyroscopeError("NULL_FOLD_REQUIRES_NEGATIVE_AFTER_BRANCH")

    inverse = flip_chiral_pair_half_turn(
        next_state,
        pair_index=_exact_int(pair_index, "PAIR_INDEX"),
        transition_id=f"{tid}:u36:inverse",
    )
    restored = inverse.get("next_state")
    if not isinstance(restored, Mapping):
        raise RelativisticGyroscopeError("RML5_PAIR_FLIP_INVERSE_STATE_REQUIRED")
    _require_gyroscope(restored)

    original_snapshot = _state_snapshot(state)
    restored_snapshot = _state_snapshot(restored)
    payload_restored = (
        original_snapshot["phases"] == restored_snapshot["phases"]
        and original_snapshot["quarter_turn_signs"] == restored_snapshot["quarter_turn_signs"]
        and original_snapshot["ambient_state_index"] == restored_snapshot["ambient_state_index"]
        and original_snapshot["channel_order"] == restored_snapshot["channel_order"]
        and original_snapshot["product_order"] == restored_snapshot["product_order"]
    )
    if not payload_restored:
        raise RelativisticGyroscopeError("NULL_FOLD_U36_RECIPROCAL_CLOSURE_FAILED")

    witness = {
        "schema": NULL_FOLD_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "transition_id": tid,
        "branch_sequence": [1, 0, -1],
        "branch_labels": [BRANCH_LABELS[1], BRANCH_LABELS[0], BRANCH_LABELS[-1]],
        "before_projection": before,
        "fold_projection": at_fold,
        "phase_transport": flip,
        "after_projection": after,
        "inverse_phase_transport": {
            "schema": inverse.get("schema"),
            "transition_sha256": inverse.get("transition_sha256"),
            "restored_ambient_state_index": restored.get("ambient_state_index"),
        },
        "null_fold_operator": "u^36",
        "zero_sum_fold_is_projection_not_state_annihilation": True,
        "ordered_phase_identity_preserved": True,
        "ordered_noncommutative_products_preserved": True,
        "reciprocal_phase_transport_self_inverse": True,
        "original_phase_payload_exactly_restored_by_inverse": payload_restored,
        "information_discarded_by_fold": False,
        "floating_point_canonical_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    witness["witness_sha256"] = _sha256(witness)
    return witness


def build_thermodynamic_reciprocal_projection(
    state: Mapping[str, Any],
    *,
    projection_id: str,
    G_numerator: int,
    G_denominator: int,
) -> dict[str, Any]:
    """Bind exact positive rational G to the reciprocal thermodynamic closure."""
    state = _require_gyroscope(state)
    pid = _nonempty(projection_id, "PROJECTION_ID")
    g_num, g_den = _reduced_rational(
        G_numerator,
        G_denominator,
        "G",
        positive=True,
    )
    theta_num, theta_den = _reduced_rational(g_num - g_den, g_den, "THETA")
    e_num, e_den = _reduced_rational(
        (g_num - g_den) * (g_num - g_den),
        g_num * g_den,
        "RECIPROCAL_ENERGY",
        nonnegative=True,
    )
    projection = {
        "schema": THERMO_PROJECTION_SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "projection_id": pid,
        "G": {"numerator": g_num, "denominator": g_den},
        "G_inverse": {"numerator": g_den, "denominator": g_num},
        "sigma_symbolic": "ln(G)",
        "theta": {"numerator": theta_num, "denominator": theta_den},
        "epsilon_symbolic": "G-1-ln(G)",
        "phi_G_symbolic": "G-1-ln(G)",
        "phi_G_inverse_symbolic": "G^-1-1+ln(G)",
        "reciprocal_closure": {"numerator": e_num, "denominator": e_den},
        "reciprocal_closure_identity": "Phi(G)+Phi(G^-1)=(G-1)^2/G",
        "logarithms_evaluated": False,
        "reciprocal_log_terms_cancel_symbolically": True,
        "fixed_point_G_equals_one": g_num == g_den,
        "reciprocal_closure_zero": e_num == 0,
        "first_law_symbolic_identity": "d_epsilon=theta*d_sigma",
        "gyroscope": _state_snapshot(state),
        "scalar_projection_is_complete_gyroscope_state": False,
        "floating_point_canonical_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    projection["projection_sha256"] = _sha256(projection)
    return projection


__all__ = [
    "BRANCH_LABELS",
    "NULL_FOLD_SCHEMA",
    "PROJECTION_KINDS",
    "RELATIVISTIC_PROJECTION_SCHEMA",
    "THERMO_PROJECTION_SCHEMA",
    "RelativisticGyroscopeError",
    "build_null_fold_transition",
    "build_relativistic_projection",
    "build_thermodynamic_reciprocal_projection",
]
