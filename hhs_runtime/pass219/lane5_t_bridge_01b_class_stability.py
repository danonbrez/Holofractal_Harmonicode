"""Pass 219 Lane 5 — T_BRIDGE-01B sign-class stability core.

This is the exact-rational executable companion to the Wolfram universal proof.

The theorem core is deliberately narrower than the pending workload theorem:

    epsilon_h = c * h^p * (1 + r_h)

with
    h > 0,
    p >= 1 integer,
    c != 0,
    |r_h| < 1.

Then sign(epsilon_h)=sign(c).  If the same relative-remainder condition holds
at h/2, the {-1,0,+1} sign class is unchanged under halving.  Separately, the
admitted envelope B(h)=C*h^p contracts exactly by 2^-p:

    B(h/2) = B(h) / 2^p.

This module DOES NOT claim that a particular orbital/Kepler workload already
satisfies the relative-remainder bound on an entire global interval.  That
workload-specific interval certificate remains OPEN.

No VM81/Hash72/Hash216 mutation authority is introduced.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any

from hhs_runtime.hhs_pass220_144cell_epsilon_lo_shu_closure_v1 import sgn3

SCHEMA = "HHS_PASS219_T_BRIDGE_01B_CLASS_STABILITY_CORE_V1"
VERSION = "1.0.0-cycle5"


class TBridge01BError(ValueError):
    pass


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise TBridge01BError(f"{name} must be exact int/Fraction")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise TBridge01BError(f"{name} must be exact int/Fraction") from exc


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable(record).encode("utf-8")
    ).hexdigest()
    return record


def _positive_order(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TBridge01BError("p must be a positive exact integer")
    return value


def class_stability_witness(
    *,
    h: Any,
    p: int,
    leading_coefficient: Any,
    relative_remainder_h: Any,
    relative_remainder_half: Any,
    envelope_constant: Any,
) -> dict[str, Any]:
    step = _q(h, "h")
    order = _positive_order(p)
    coefficient = _q(leading_coefficient, "leading_coefficient")
    r_h = _q(relative_remainder_h, "relative_remainder_h")
    r_half = _q(relative_remainder_half, "relative_remainder_half")
    C = _q(envelope_constant, "envelope_constant")

    if step <= 0:
        raise TBridge01BError("h must be positive")
    if coefficient == 0:
        raise TBridge01BError(
            "nonzero leading coefficient required outside the zero membrane"
        )
    if not (-1 < r_h < 1):
        raise TBridge01BError("|relative_remainder_h| must be < 1")
    if not (-1 < r_half < 1):
        raise TBridge01BError("|relative_remainder_half| must be < 1")
    if C <= 0:
        raise TBridge01BError("envelope_constant must be positive")

    half = step / 2
    epsilon_h = coefficient * (step**order) * (1 + r_h)
    epsilon_half = coefficient * (half**order) * (1 + r_half)

    band_h = C * (step**order)
    band_half = C * (half**order)

    required_C = abs(coefficient) * max(1 + abs(r_h), 1 + abs(r_half))
    if C < required_C:
        raise TBridge01BError(
            "envelope_constant does not dominate the supplied relative remainders"
        )

    sign_h = sgn3(epsilon_h)
    sign_half = sgn3(epsilon_half)
    sign_c = sgn3(coefficient)

    checks = {
        "band_halves_by_exact_power": (
            band_half == band_h / (2**order)
        ),
        "band_strictly_contracts": band_half < band_h,
        "epsilon_h_inside_band": abs(epsilon_h) <= band_h,
        "epsilon_half_inside_band": abs(epsilon_half) <= band_half,
        "sign_h_matches_leading_coefficient": sign_h == sign_c,
        "sign_half_matches_leading_coefficient": sign_half == sign_c,
        "sign_class_stable_under_halving": sign_h == sign_half,
        "zero_class_not_entered_under_bound": sign_h != 0 and sign_half != 0,
    }

    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "theorem_scope": "EXACT_RELATIVE_REMAINDER_CORE",
            "h": _fraction_record(step),
            "half_h": _fraction_record(half),
            "order_p": order,
            "leading_coefficient": _fraction_record(coefficient),
            "relative_remainder_h": _fraction_record(r_h),
            "relative_remainder_half": _fraction_record(r_half),
            "envelope_constant": _fraction_record(C),
            "required_envelope_constant": _fraction_record(required_C),
            "epsilon_h": _fraction_record(epsilon_h),
            "epsilon_half": _fraction_record(epsilon_half),
            "band_h": _fraction_record(band_h),
            "band_half": _fraction_record(band_half),
            "sgn3_epsilon_h": sign_h,
            "sgn3_epsilon_half": sign_half,
            "sgn3_leading_coefficient": sign_c,
            "checks": checks,
            "zero_membrane_rule": (
                "a sign-class change requires leaving the admitted |r|<1 "
                "sector or passing through epsilon=0"
            ),
            "workload_interval_certificate": "OPEN",
            "global_actual_epsilon_monotonicity_claimed": False,
            "monotone_envelope_claimed": True,
            "canonical_runtime_mutation_authority": False,
        }
    )


def exact_halving_envelope(
    *,
    h: Any,
    p: int,
    envelope_constant: Any,
) -> dict[str, Any]:
    step = _q(h, "h")
    order = _positive_order(p)
    C = _q(envelope_constant, "envelope_constant")
    if step <= 0 or C <= 0:
        raise TBridge01BError("h and envelope_constant must be positive")
    band = C * step**order
    half_band = C * (step / 2) ** order
    return _receipt(
        {
            "schema": "HHS_PASS219_T_BRIDGE_01B_HALVING_ENVELOPE_V1",
            "band_h": _fraction_record(band),
            "band_half": _fraction_record(half_band),
            "contraction_ratio": _fraction_record(half_band / band),
            "expected_ratio": _fraction_record(Fraction(1, 2**order)),
            "exact": half_band * (2**order) == band,
            "actual_residue_monotonicity_inferred": False,
        }
    )


def self_test() -> dict[str, Any]:
    witness = class_stability_witness(
        h=Fraction(1, 4),
        p=2,
        leading_coefficient=Fraction(-3, 5),
        relative_remainder_h=Fraction(1, 4),
        relative_remainder_half=Fraction(-1, 4),
        envelope_constant=Fraction(1),
    )
    if witness["status"] != "PASS":
        raise TBridge01BError("class-stability self-test failed")
    return {
        "schema": "HHS_PASS219_T_BRIDGE_01B_CLASS_STABILITY_SELF_TEST_V1",
        "status": "PASS",
        "receipt_sha256": witness["receipt_sha256"],
    }


if __name__ == "__main__":
    print(_stable(self_test()))
