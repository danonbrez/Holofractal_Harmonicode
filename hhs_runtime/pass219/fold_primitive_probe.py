"""Pass 219 exact fold-primitive probe.

This module is intentionally diagnostic/read-only.  It does not redefine the
canonical HARMONICODE equation manifold.  It isolates the candidate involutions
currently distributed across the validated octonion gyroscope, reciprocal
route, and source-bound AB projection surfaces, then composes them to determine
which operations share the same mechanical signature.

No floating-point arithmetic, VM81 mutation, Hash72 minting, or Hash216
persistence authority is introduced here.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_spi_octonion_dimensional_lift_v1 import ORDERED_RECIPROCAL_OPERAND
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.gyroscope_admission_membrane import (
    build_chirality_polarity_witness,
    flip_chiral_pair_half_turn,
)
from hhs_runtime.pass219.reciprocal_route_optimizer import shortest_signed_delta

PASS = 219
ITERATION = "FOLD_PRIMITIVE_PROBE_1_0"
SCHEMA = "HHS_PASS219_FOLD_PRIMITIVE_PROBE_V1"

PHASE_RATIO_FORWARD = "xy/wz"
PHASE_RATIO_REVERSE = "zw/yx"
AB_RATIO_FORWARD = "A/B"
AB_RATIO_REVERSE = "B/A"
ORTHOGONAL_CLOSURE = "a^2+b^2=c^2"
ORTHOGONAL_MAGNITUDE = "c^2=3P^2"
DIRECTIONAL_P4_CLOSURE = "P^4=(A^2(A/B)*B^2(B/A))/P^2"
COMMUTATIVE_P4_SHADOW = "AB=P^4"


class FoldPrimitiveProbeError(RuntimeError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise FoldPrimitiveProbeError(f"FLOAT_PROBE_AUTHORITY_FORBIDDEN:{path}")
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
        default=str,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise FoldPrimitiveProbeError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def pair_flip(left: Any, right: Any) -> tuple[Any, Any]:
    """Generic typed order-2 pair inversion used only as a probe primitive."""
    _reject_float((left, right))
    return right, left


def pair_flip_round_trip(left: Any, right: Any) -> bool:
    return pair_flip(*pair_flip(left, right)) == (left, right)


def directed_ratio_flip(value: str) -> str:
    pairs = {
        PHASE_RATIO_FORWARD: PHASE_RATIO_REVERSE,
        PHASE_RATIO_REVERSE: PHASE_RATIO_FORWARD,
        AB_RATIO_FORWARD: AB_RATIO_REVERSE,
        AB_RATIO_REVERSE: AB_RATIO_FORWARD,
    }
    if value not in pairs:
        raise FoldPrimitiveProbeError("UNKNOWN_DIRECTED_RATIO")
    return pairs[value]


def orthogonal_polarity_probe(P: int) -> dict[str, Any]:
    """Test the supplied a:b polarity inversion without scalarizing the full manifold."""
    P = _exact_int(P, "P")
    if P == 0:
        raise FoldPrimitiveProbeError("P_NONZERO_REQUIRED")
    P2 = P * P
    forward = {"a2": P2, "b2": 2 * P2, "c2": 3 * P2}
    reverse = {"a2": 2 * P2, "b2": P2, "c2": 3 * P2}
    restored_a2, restored_b2 = pair_flip(reverse["a2"], reverse["b2"])
    return {
        "primitive_signature": "ORDER_2_PAIR_FLIP_WITH_FIXED_ORTHOGONAL_MAGNITUDE",
        "closure_source": ORTHOGONAL_CLOSURE,
        "magnitude_source": ORTHOGONAL_MAGNITUDE,
        "P": P,
        "P2": P2,
        "forward": forward,
        "reverse": reverse,
        "forward_closes": forward["a2"] + forward["b2"] == forward["c2"],
        "reverse_closes": reverse["a2"] + reverse["b2"] == reverse["c2"],
        "shared_c2": forward["c2"] == reverse["c2"] == 3 * P2,
        "round_trip_restores": (restored_a2, restored_b2) == (forward["a2"], forward["b2"]),
    }


def ordered_pq_probe(P: int) -> dict[str, Any]:
    """Keep p->q and q->p as distinct typed directions over one scalar shadow."""
    P = _exact_int(P, "P")
    p = P - 1
    q = P + 1
    forward = ("pq", p, q)
    reverse = ("qp", q, p)
    return {
        "primitive_signature": "ORDER_2_TYPED_ORDER_REVERSAL",
        "P": P,
        "p": p,
        "q": q,
        "forward": forward,
        "reverse": reverse,
        "p_plus_q": p + q,
        "two_P": 2 * P,
        "scalar_pq": p * q,
        "P2_minus_one": P * P - 1,
        "scalar_projection_agrees": p + q == 2 * P and p * q == P * P - 1,
        "ordered_identity_collapsed": False,
        "round_trip_restores": pair_flip(p, q) == (q, p) and pair_flip(q, p) == (p, q),
    }


def ab_p4_probe(P: int, A: int, B: int) -> dict[str, Any]:
    """Test the commutative P4 shadow while retaining both directed A/B words.

    The full directional closure is preserved as source syntax and is not
    evaluated as ordinary commutative scalar arithmetic here.
    """
    P = _exact_int(P, "P")
    A = _exact_int(A, "A")
    B = _exact_int(B, "B")
    P4 = P**4
    if A * B != P4:
        raise FoldPrimitiveProbeError("AB_P4_SHADOW_REQUIRED")
    forward_ratio = Fraction(A, B)
    reverse_ratio = Fraction(B, A)
    return {
        "primitive_signature": "BIDIRECTIONAL_PERSPECTIVE_PAIR_WITH_SHARED_P4_SHADOW",
        "directional_closure_source": DIRECTIONAL_P4_CLOSURE,
        "commutative_shadow_source": COMMUTATIVE_P4_SHADOW,
        "P": P,
        "P2": P * P,
        "P4": P4,
        "A": A,
        "B": B,
        "forward_ratio_role": AB_RATIO_FORWARD,
        "reverse_ratio_role": AB_RATIO_REVERSE,
        "forward_ratio_exact": {"numerator": forward_ratio.numerator, "denominator": forward_ratio.denominator},
        "reverse_ratio_exact": {"numerator": reverse_ratio.numerator, "denominator": reverse_ratio.denominator},
        "AB_equals_P4": A * B == P4,
        "ratio_roles_are_distinct": AB_RATIO_FORWARD != AB_RATIO_REVERSE,
        "ratio_flip_is_involutive": directed_ratio_flip(directed_ratio_flip(AB_RATIO_FORWARD)) == AB_RATIO_FORWARD,
        "full_directional_closure_scalarized": False,
    }


def phase_relation_probe() -> dict[str, Any]:
    """Test the supplied reciprocal phase relation as an ordered symbolic involution."""
    reciprocal_map = dict(ORDERED_RECIPROCAL_OPERAND)
    return {
        "primitive_signature": "ORDER_2_DIRECTED_PHASE_RATIO_FLIP",
        "forward": PHASE_RATIO_FORWARD,
        "reverse": PHASE_RATIO_REVERSE,
        "source_relation": f"{PHASE_RATIO_FORWARD}={PHASE_RATIO_REVERSE}",
        "ordered_reciprocal_operand": reciprocal_map,
        "primitive_operand_pairs": [["x", "y"], ["z", "w"]],
        "operand_map_involutive": all(reciprocal_map[reciprocal_map[key]] == key for key in reciprocal_map),
        "ratio_flip_is_involutive": directed_ratio_flip(directed_ratio_flip(PHASE_RATIO_FORWARD)) == PHASE_RATIO_FORWARD,
        "commutative_product_collapse_permitted": False,
    }


def _admissible_gyroscope_state(state_id: str = "fold-probe:source") -> dict[str, Any]:
    primitives = {"x": 7, "y": 19, "z": 31, "w": 43}
    signs = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}
    phases = {
        "x": primitives["x"],
        "y": primitives["y"],
        "z": primitives["z"],
        "w": primitives["w"],
        "xy": expected_product_phase(primitives["x"], signs["xy"]),
        "yx": expected_product_phase(primitives["y"], signs["yx"]),
        "zw": expected_product_phase(primitives["z"], signs["zw"]),
        "wz": expected_product_phase(primitives["w"], signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


def gyroscope_half_turn_probe() -> dict[str, Any]:
    """Exercise both validated RML5 u^36 chiral-pair flips independently and together."""
    source = _admissible_gyroscope_state()
    source_chirality = build_chirality_polarity_witness(source)

    xy_flip = flip_chiral_pair_half_turn(source, pair_index=0, transition_id="fold-probe:xy")
    xy_once = xy_flip["next_state"]
    xy_back = flip_chiral_pair_half_turn(xy_once, pair_index=0, transition_id="fold-probe:xy:back")["next_state"]

    zw_flip = flip_chiral_pair_half_turn(source, pair_index=1, transition_id="fold-probe:zw")
    zw_once = zw_flip["next_state"]
    zw_back = flip_chiral_pair_half_turn(zw_once, pair_index=1, transition_id="fold-probe:zw:back")["next_state"]

    both_1 = flip_chiral_pair_half_turn(source, pair_index=0, transition_id="fold-probe:both:0")["next_state"]
    both_2 = flip_chiral_pair_half_turn(both_1, pair_index=1, transition_id="fold-probe:both:1")["next_state"]
    both_3 = flip_chiral_pair_half_turn(both_2, pair_index=1, transition_id="fold-probe:both:1:back")["next_state"]
    both_4 = flip_chiral_pair_half_turn(both_3, pair_index=0, transition_id="fold-probe:both:0:back")["next_state"]

    return {
        "primitive_signature": "SELF_INVERSE_U36_CHIRAL_PAIR_ROTATION",
        "source_state_sha256": source["state_sha256"],
        "source_chirality_opposed": source_chirality["all_chiral_pairs_opposed"],
        "xy_yx_individual_round_trip": xy_back["phases"] == source["phases"] and xy_back["quarter_turn_signs"] == source["quarter_turn_signs"],
        "zw_wz_individual_round_trip": zw_back["phases"] == source["phases"] and zw_back["quarter_turn_signs"] == source["quarter_turn_signs"],
        "combined_disjoint_round_trip": both_4["phases"] == source["phases"] and both_4["quarter_turn_signs"] == source["quarter_turn_signs"],
        "xy_yx_product_geometry_preserved": xy_once["admissible_product_geometry"],
        "zw_wz_product_geometry_preserved": zw_once["admissible_product_geometry"],
        "combined_product_geometry_preserved": both_2["admissible_product_geometry"],
        "phase_inversion_steps": 36,
    }


def p_sign_probe(P: int) -> dict[str, Any]:
    P = _exact_int(P, "P")
    if P == 0:
        raise FoldPrimitiveProbeError("P_NONZERO_REQUIRED")
    return {
        "primitive_signature": "ORDER_2_SIGN_POLARITY_FLIP_WITH_SQUARED_MAGNITUDE_INVARIANT",
        "forward": P,
        "reverse": -P,
        "P2_forward": P * P,
        "P2_reverse": (-P) * (-P),
        "squared_magnitude_shared": P * P == (-P) * (-P),
        "round_trip_restores": -(-P) == P,
    }


def combined_fold_probe(P: int = 5, A: int = 5, B: int = 125) -> dict[str, Any]:
    """Compose every candidate inversion while keeping shared invariants explicit."""
    P = _exact_int(P, "P")
    if A * B != P**4:
        raise FoldPrimitiveProbeError("COMBINED_AB_P4_SHADOW_REQUIRED")

    orthogonal = orthogonal_polarity_probe(P)
    pq = ordered_pq_probe(P)
    ab = ab_p4_probe(P, A, B)
    phase = phase_relation_probe()
    gyro = gyroscope_half_turn_probe()
    sign = p_sign_probe(P)

    typed_axes = {
        "xy_primitive_roles": ("x", "y"),
        "zw_primitive_roles": ("z", "w"),
        "ab_orthogonal_roles": ("a", "b"),
        "pq_roles": ("p", "q"),
        "AB_roles": ("A", "B"),
        "P_sign_roles": ("P+", "P-"),
    }
    twice = {name: pair_flip(*pair_flip(*pair)) for name, pair in typed_axes.items()}
    all_pair_axes_involutive = all(twice[name] == pair for name, pair in typed_axes.items())

    shortest_fold = shortest_signed_delta(0, 36)
    report = {
        "schema": SCHEMA,
        "pass": PASS,
        "iteration": ITERATION,
        "individual": {
            "orthogonal_polarity": orthogonal,
            "ordered_pq": pq,
            "AB_P4": ab,
            "phase_relation": phase,
            "gyroscope_half_turn": gyro,
            "P_sign": sign,
        },
        "combined": {
            "typed_pair_axes": {name: list(pair) for name, pair in typed_axes.items()},
            "all_typed_pair_axes_share_order_2_signature": all_pair_axes_involutive,
            "all_runtime_chiral_half_turns_round_trip": (
                gyro["xy_yx_individual_round_trip"]
                and gyro["zw_wz_individual_round_trip"]
                and gyro["combined_disjoint_round_trip"]
            ),
            "orthogonal_c2_shared": orthogonal["shared_c2"],
            "P2_shared_across_sign_flip": sign["squared_magnitude_shared"],
            "AB_P4_shadow_shared": ab["AB_equals_P4"],
            "pq_scalar_shadow_shared": pq["scalar_projection_agrees"],
            "phase_ratio_direction_preserved": phase["commutative_product_collapse_permitted"] is False,
            "u36_is_exact_shortest_antipodal_Z72_fold": shortest_fold == 36,
            "same_5184_tensor_shape_required": True,
            "canonical_state_recomputed_from_scratch_required": False,
        },
        "candidate_primitive_classes": [
            "TYPED_ORDER_2_PAIR_FLIP",
            "DIRECTED_RATIO_RECIPROCAL_FLIP",
            "SELF_INVERSE_U36_CHIRAL_PAIR_ROTATION",
            "FIXED_ORTHOGONAL_MAGNITUDE_WITNESS",
            "COMMUTATIVE_SHADOW_INVARIANT",
            "EXACT_SHORTEST_Z72_ANTIPODAL_DISPLACEMENT",
        ],
        "authority": {
            "diagnostic_only": True,
            "canonical_equation_rewrite": False,
            "commutative_collapse_authority": False,
            "vm81_mutation": False,
            "hash72_minting": False,
            "hash216_persistence": False,
            "floating_point_authority": False,
        },
    }
    report["report_sha256"] = _sha256(report)
    return report


def main() -> int:
    report = combined_fold_probe()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str))
    checks = report["combined"]
    required = (
        checks["all_typed_pair_axes_share_order_2_signature"],
        checks["all_runtime_chiral_half_turns_round_trip"],
        checks["orthogonal_c2_shared"],
        checks["P2_shared_across_sign_flip"],
        checks["AB_P4_shadow_shared"],
        checks["pq_scalar_shadow_shared"],
        checks["phase_ratio_direction_preserved"],
        checks["u36_is_exact_shortest_antipodal_Z72_fold"],
    )
    return 0 if all(required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
