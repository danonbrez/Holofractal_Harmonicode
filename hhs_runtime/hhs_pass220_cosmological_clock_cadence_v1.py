"""Pass 220 I022 exact cosmological clock/cadence projection.

This module is projection-only. VM81/Delta admission and Hash72/Hash216
authority remain upstream. Host wall-clock time is never canonical input.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Iterable

SCHEMA = "HHS_PASS_220_I022_COSMOLOGICAL_CLOCK_CADENCE_V1"
PROFILE = "PASS220-I022-COSMOLOGICAL-CLOCK-CADENCE-v1"
PHASE_MODULUS = 72
PHASE_STRIDE = 16
PHASE_ORIGIN = 8
PHASE_PERIOD = 9
PHASE_ORBIT = (8, 24, 40, 56, 72, 16, 32, 48, 64)
G72_OPERATOR = "G72"
G72_IDENTITY = "G72^72==2"
HOST_WALL_CLOCK_AUTHORITY = False
FLOATING_POINT_AUTHORITY = False
CANONICAL_ADMISSION_AUTHORITY = False


class Pass220I022ClockError(ValueError):
    pass


@dataclass(frozen=True)
class CadenceTransition:
    transition_index: int
    sigma: int
    lambda_increment: Fraction
    theta: Fraction


def _i(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I022ClockError(f"{name} must be an exact integer")
    return value


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Pass220I022ClockError(f"{name} must be int or Fraction")
    return Fraction(value)


def _positive_q(value: Any, name: str) -> Fraction:
    q = _q(value, name)
    if q <= 0:
        raise Pass220I022ClockError(f"{name} must be positive")
    return q


def _text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {**payload, "receipt_sha256": sha256(encoded.encode("utf-8")).hexdigest()}


def sigma_formula(transition_index: int) -> int:
    n = _i(transition_index, "transition_index")
    residue = (PHASE_ORIGIN + PHASE_STRIDE * n) % PHASE_MODULUS
    return PHASE_MODULUS if residue == 0 else residue


def sigma_lookup(transition_index: int) -> int:
    n = _i(transition_index, "transition_index")
    return PHASE_ORBIT[n % PHASE_PERIOD]


def closure_duration(
    dependency_durations: Iterable[int | Fraction],
    closure_duration_value: int | Fraction,
) -> Fraction:
    deps = tuple(_q(value, "dependency_duration") for value in dependency_durations)
    if any(value < 0 for value in deps):
        raise Pass220I022ClockError("dependency durations cannot be negative")
    closure = _q(closure_duration_value, "closure_duration")
    if closure < 0:
        raise Pass220I022ClockError("closure duration cannot be negative")
    theta = (max(deps) if deps else Fraction(0)) + closure
    if theta <= 0:
        raise Pass220I022ClockError("logical phase duration must be positive")
    return theta


def make_transition(
    transition_index: int,
    lambda_increment: int | Fraction,
    theta: int | Fraction,
) -> CadenceTransition:
    n = _i(transition_index, "transition_index")
    return CadenceTransition(
        transition_index=n,
        sigma=sigma_lookup(n),
        lambda_increment=_q(lambda_increment, "lambda_increment"),
        theta=_positive_q(theta, "theta"),
    )


def h_p(sample: CadenceTransition, tau: int | Fraction) -> Fraction:
    scale = _positive_q(tau, "tau")
    return sample.lambda_increment / (scale * sample.theta)


def dot_h_p(
    previous: CadenceTransition,
    current: CadenceTransition,
    tau: int | Fraction,
) -> Fraction:
    if current.transition_index != previous.transition_index + 1:
        raise Pass220I022ClockError("cadence derivative requires adjacent transitions")
    scale = _positive_q(tau, "tau")
    hp_prev = h_p(previous, scale)
    hp_now = h_p(current, scale)
    return Fraction(2) * (hp_now - hp_prev) / (
        scale * (current.theta + previous.theta)
    )


def a_p(
    previous: CadenceTransition,
    current: CadenceTransition,
    tau: int | Fraction,
) -> Fraction:
    hp_now = h_p(current, tau)
    return hp_now * hp_now + dot_h_p(previous, current, tau)


def w_p(
    previous: CadenceTransition,
    current: CadenceTransition,
    tau: int | Fraction,
) -> Fraction:
    hp_now = h_p(current, tau)
    if hp_now == 0:
        raise Pass220I022ClockError("w_P is undefined when H_P is zero")
    derivative = dot_h_p(previous, current, tau)
    return Fraction(-1) - Fraction(2, 3) * derivative / (hp_now * hp_now)


def variable_cadence_closed_form(
    lambda_increment: int | Fraction,
    theta_previous: int | Fraction,
    theta_current: int | Fraction,
) -> Fraction:
    lam = _q(lambda_increment, "lambda_increment")
    if lam == 0:
        raise Pass220I022ClockError("lambda_increment must be nonzero")
    thm = _positive_q(theta_previous, "theta_previous")
    th = _positive_q(theta_current, "theta_current")
    return Fraction(-1) + (
        Fraction(4) * th * (th - thm)
        / (Fraction(3) * lam * thm * (th + thm))
    )


def cadence_observables(
    previous: CadenceTransition,
    current: CadenceTransition,
    tau: int | Fraction,
) -> dict[str, Fraction]:
    hp_now = h_p(current, tau)
    derivative = dot_h_p(previous, current, tau)
    acceleration = hp_now * hp_now + derivative
    if hp_now == 0:
        raise Pass220I022ClockError("w_P is undefined when H_P is zero")
    equation_of_state = Fraction(-1) - Fraction(2, 3) * derivative / (hp_now * hp_now)
    return {
        "h_p": hp_now,
        "dot_h_p": derivative,
        "a_p": acceleration,
        "w_p": equation_of_state,
    }


def clock_contract_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "phase_rule": "sigma_n=8+16n(mod72); residue0=>72",
        "phase_orbit": PHASE_ORBIT,
        "phase_period": PHASE_PERIOD,
        "clock_rule": "theta_n=max(theta_dependency)+theta_closure",
        "h_p_rule": "H_P,n=lambda_n/(tau*theta_n)",
        "dot_h_p_rule": "2*(H_P,n-H_P,n-1)/(tau*(theta_n+theta_n-1))",
        "w_p_rule": "-1-(2/3)*dotH_P/H_P^2",
        "g72_operator": G72_OPERATOR,
        "g72_identity": G72_IDENTITY,
        "g72_scalar_evaluation_allowed": False,
        "host_wall_clock_authority": HOST_WALL_CLOCK_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "projection_only": True,
        "canonical_admission_authority": CANONICAL_ADMISSION_AUTHORITY,
    })


def full_i022_witness() -> dict[str, Any]:
    previous = make_transition(0, Fraction(1), Fraction(1))
    constant = make_transition(1, Fraction(1), Fraction(1))
    variable = make_transition(1, Fraction(1), Fraction(2))
    constant_obs = cadence_observables(previous, constant, Fraction(1))
    variable_obs = cadence_observables(previous, variable, Fraction(1))
    variable_expected = variable_cadence_closed_form(
        Fraction(1), previous.theta, variable.theta
    )
    lookup_equivalent = all(
        sigma_lookup(index) == sigma_formula(index) for index in range(5184)
    )
    return _receipt({
        "schema": "HHS_PASS_220_I022_FULL_COSMOLOGICAL_CLOCK_CADENCE_V1",
        "profile": PROFILE,
        "phase_orbit": PHASE_ORBIT,
        "phase_period": PHASE_PERIOD,
        "phase_lookup_formula_equivalent_first_5184": lookup_equivalent,
        "constant_cadence_dot_h_p": _text(constant_obs["dot_h_p"]),
        "constant_cadence_w_p": _text(constant_obs["w_p"]),
        "constant_cadence_lambda_equal": (
            previous.lambda_increment == constant.lambda_increment
        ),
        "constant_cadence_theta_equal": previous.theta == constant.theta,
        "variable_cadence_w_p": _text(variable_obs["w_p"]),
        "variable_cadence_closed_form": _text(variable_expected),
        "variable_cadence_matches_closed_form": (
            variable_obs["w_p"] == variable_expected
        ),
        "tau_calibration_cancels_from_constant_increment_w_p": True,
        "host_wall_clock_authority": HOST_WALL_CLOCK_AUTHORITY,
        "g72_operator": G72_OPERATOR,
        "g72_identity": G72_IDENTITY,
        "g72_scalar_evaluation_allowed": False,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "projection_only": True,
        "canonical_admission_authority": CANONICAL_ADMISSION_AUTHORITY,
        "closed": (
            lookup_equivalent
            and constant_obs["dot_h_p"] == 0
            and constant_obs["w_p"] == -1
            and variable_obs["w_p"] == variable_expected
            and not HOST_WALL_CLOCK_AUTHORITY
            and not FLOATING_POINT_AUTHORITY
        ),
    })
