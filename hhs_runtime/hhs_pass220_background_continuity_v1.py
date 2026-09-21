"""Pass 220 I024 exact cosmological background continuity.

T_COSMO-06 derives each Friedmann background H^2 contribution from a finite,
SHA-bound reference density state plus exact continuity exponents. No B(z)
function, interpolator, host time, or floating-point authority is admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any, Sequence

from hhs_runtime.hhs_pass220_cosmological_clock_cadence_v1 import sigma_lookup
from hhs_runtime.hhs_pass220_exact_friedmann_transfer_v1 import (
    ExactExpr,
    ExactValue,
    TransferReceipt,
    build_exact_trajectory,
    exact_add,
    exact_data,
    exact_exp,
    exact_mul,
    interval_log_scale_increment,
    make_transfer_receipt,
)

SCHEMA = "HHS_PASS_220_I024_BACKGROUND_CONTINUITY_V1"
PROFILE = "PASS220-I024-BACKGROUND-CONTINUITY-v1"
BARYON_EXPONENT = 3
DARK_EXPONENT = 3
RADIATION_EXPONENT = 4
CURVATURE_EXPONENT = 2
HOST_WALL_CLOCK_AUTHORITY = False
FLOATING_POINT_AUTHORITY = False
FREE_BACKGROUND_FUNCTION_AUTHORITY = False
INVERSE_HZ_STATE_AUTHORITY = False
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Pass220I024BackgroundError(ValueError):
    pass


@dataclass(frozen=True)
class BackgroundAnchors:
    rho_b_ref: Fraction
    rho_r_ref: Fraction
    rho_d_ref: Fraction
    gravity_coupling: Fraction
    curvature_sign: int
    anchor_receipt_sha256: str


@dataclass(frozen=True)
class CommittedPhaseInput:
    transition_index: int
    lambda_increment: Fraction
    theta: Fraction
    phase_receipt_sha256: str


@dataclass(frozen=True)
class BackgroundState:
    rho_b: ExactValue
    rho_r: ExactValue
    rho_d: ExactValue
    curvature_h2: ExactValue
    raw_log_scale: ExactValue
    previous_continuity_receipt_sha256: str


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Pass220I024BackgroundError(f"{name} must be int or Fraction")
    return Fraction(value)


def _nonnegative_q(value: Any, name: str) -> Fraction:
    q = _q(value, name)
    if q < 0:
        raise Pass220I024BackgroundError(f"{name} must be nonnegative")
    return q


def _positive_q(value: Any, name: str) -> Fraction:
    q = _q(value, name)
    if q <= 0:
        raise Pass220I024BackgroundError(f"{name} must be positive")
    return q


def _i(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I024BackgroundError(f"{name} must be an exact integer")
    return value


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise Pass220I024BackgroundError(
            f"{name} must be lowercase sha256 hex"
        )
    return value


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {
        **payload,
        "receipt_sha256": sha256(encoded.encode("utf-8")).hexdigest(),
    }


def make_background_anchors(
    *,
    rho_b_ref: int | Fraction,
    rho_r_ref: int | Fraction,
    rho_d_ref: int | Fraction,
    gravity_coupling: int | Fraction,
    curvature_sign: int,
    anchor_receipt_sha256: str,
) -> BackgroundAnchors:
    k = _i(curvature_sign, "curvature_sign")
    if k not in (-1, 0, 1):
        raise Pass220I024BackgroundError(
            "curvature_sign must be -1, 0, or 1"
        )
    return BackgroundAnchors(
        rho_b_ref=_nonnegative_q(rho_b_ref, "rho_b_ref"),
        rho_r_ref=_nonnegative_q(rho_r_ref, "rho_r_ref"),
        rho_d_ref=_nonnegative_q(rho_d_ref, "rho_d_ref"),
        gravity_coupling=_positive_q(
            gravity_coupling, "gravity_coupling"
        ),
        curvature_sign=k,
        anchor_receipt_sha256=_sha(
            anchor_receipt_sha256, "anchor_receipt_sha256"
        ),
    )


def make_phase_input(
    transition_index: int,
    lambda_increment: int | Fraction,
    theta: int | Fraction,
    phase_receipt_sha256: str,
) -> CommittedPhaseInput:
    n = _i(transition_index, "transition_index")
    if n < 0:
        raise Pass220I024BackgroundError(
            "transition_index must be nonnegative"
        )
    return CommittedPhaseInput(
        transition_index=n,
        lambda_increment=_q(lambda_increment, "lambda_increment"),
        theta=_positive_q(theta, "theta"),
        phase_receipt_sha256=_sha(
            phase_receipt_sha256, "phase_receipt_sha256"
        ),
    )


def initial_background_state(
    anchors: BackgroundAnchors,
    *,
    c0: int | Fraction,
) -> BackgroundState:
    light = _positive_q(c0, "c0")
    curvature = Fraction(-anchors.curvature_sign) * light * light
    return BackgroundState(
        rho_b=anchors.rho_b_ref,
        rho_r=anchors.rho_r_ref,
        rho_d=anchors.rho_d_ref,
        curvature_h2=curvature,
        raw_log_scale=Fraction(0),
        previous_continuity_receipt_sha256=anchors.anchor_receipt_sha256,
    )


def background_h2(
    state: BackgroundState,
    anchors: BackgroundAnchors,
) -> ExactValue:
    matter = exact_add(state.rho_b, state.rho_r, state.rho_d)
    return exact_add(
        exact_mul(anchors.gravity_coupling, matter),
        state.curvature_h2,
    )


def _scaled_by_log_increment(
    value: ExactValue,
    exponent: int,
    delta_log_scale: ExactValue,
) -> ExactValue:
    return exact_mul(
        value,
        exact_exp(
            exact_mul(Fraction(-exponent), delta_log_scale)
        ),
    )


def _background_input_receipt(
    *,
    phase: CommittedPhaseInput,
    anchors: BackgroundAnchors,
    state: BackgroundState,
    background: ExactValue,
) -> dict[str, Any]:
    return _receipt({
        "schema": "HHS_PASS_220_I024_BACKGROUND_INPUT_V1",
        "transition_index": phase.transition_index,
        "sigma": sigma_lookup(phase.transition_index),
        "phase_receipt_sha256": phase.phase_receipt_sha256,
        "anchor_receipt_sha256": anchors.anchor_receipt_sha256,
        "previous_continuity_receipt_sha256": (
            state.previous_continuity_receipt_sha256
        ),
        "rho_b": exact_data(state.rho_b),
        "rho_r": exact_data(state.rho_r),
        "rho_d": exact_data(state.rho_d),
        "curvature_h2": exact_data(state.curvature_h2),
        "raw_log_scale": exact_data(state.raw_log_scale),
        "background_h2": exact_data(background),
        "gravity_coupling": (
            f"{anchors.gravity_coupling.numerator}/"
            f"{anchors.gravity_coupling.denominator}"
        ),
        "continuity_exponents": {
            "baryon": BARYON_EXPONENT,
            "dark": DARK_EXPONENT,
            "radiation": RADIATION_EXPONENT,
            "curvature": CURVATURE_EXPONENT,
        },
        "free_background_function_authority": False,
        "projection_only": True,
    })


def advance_background_state(
    *,
    state: BackgroundState,
    anchors: BackgroundAnchors,
    phase: CommittedPhaseInput,
    tau: int | Fraction,
) -> tuple[BackgroundState, TransferReceipt, dict[str, Any]]:
    background = background_h2(state, anchors)
    input_receipt = _background_input_receipt(
        phase=phase,
        anchors=anchors,
        state=state,
        background=background,
    )
    transfer = make_transfer_receipt(
        phase.transition_index,
        phase.lambda_increment,
        phase.theta,
        background,
        input_receipt["receipt_sha256"],
    )
    delta_log_scale = interval_log_scale_increment(transfer, tau)

    rho_b_next = _scaled_by_log_increment(
        state.rho_b, BARYON_EXPONENT, delta_log_scale
    )
    rho_d_next = _scaled_by_log_increment(
        state.rho_d, DARK_EXPONENT, delta_log_scale
    )
    rho_r_next = _scaled_by_log_increment(
        state.rho_r, RADIATION_EXPONENT, delta_log_scale
    )
    curvature_next = _scaled_by_log_increment(
        state.curvature_h2, CURVATURE_EXPONENT, delta_log_scale
    )
    raw_log_next = exact_add(state.raw_log_scale, delta_log_scale)

    continuity = _receipt({
        "schema": "HHS_PASS_220_I024_CONTINUITY_STEP_V1",
        "transition_index": phase.transition_index,
        "sigma": sigma_lookup(phase.transition_index),
        "phase_receipt_sha256": phase.phase_receipt_sha256,
        "background_input_receipt_sha256": input_receipt[
            "receipt_sha256"
        ],
        "previous_continuity_receipt_sha256": (
            state.previous_continuity_receipt_sha256
        ),
        "delta_log_scale": exact_data(delta_log_scale),
        "rho_b_before": exact_data(state.rho_b),
        "rho_b_after": exact_data(rho_b_next),
        "rho_d_before": exact_data(state.rho_d),
        "rho_d_after": exact_data(rho_d_next),
        "rho_r_before": exact_data(state.rho_r),
        "rho_r_after": exact_data(rho_r_next),
        "curvature_h2_before": exact_data(state.curvature_h2),
        "curvature_h2_after": exact_data(curvature_next),
        "raw_log_scale_before": exact_data(state.raw_log_scale),
        "raw_log_scale_after": exact_data(raw_log_next),
        "continuity_exponents": {
            "baryon": BARYON_EXPONENT,
            "dark": DARK_EXPONENT,
            "radiation": RADIATION_EXPONENT,
            "curvature": CURVATURE_EXPONENT,
        },
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "free_background_function_authority": False,
        "inverse_hz_state_authority": False,
    })

    next_state = BackgroundState(
        rho_b=rho_b_next,
        rho_r=rho_r_next,
        rho_d=rho_d_next,
        curvature_h2=curvature_next,
        raw_log_scale=raw_log_next,
        previous_continuity_receipt_sha256=continuity[
            "receipt_sha256"
        ],
    )
    return next_state, transfer, continuity


def derive_background_transfer_receipts(
    phases: Sequence[CommittedPhaseInput],
    anchors: BackgroundAnchors,
    *,
    tau: int | Fraction,
    c0: int | Fraction,
) -> tuple[tuple[TransferReceipt, ...], dict[str, Any]]:
    if not phases:
        raise Pass220I024BackgroundError(
            "at least one committed phase input is required"
        )
    _positive_q(tau, "tau")
    _positive_q(c0, "c0")

    for expected, phase in enumerate(phases):
        if phase.transition_index != expected:
            raise Pass220I024BackgroundError(
                "phase inputs must be contiguous and zero-indexed"
            )

    state = initial_background_state(anchors, c0=c0)
    transfers: list[TransferReceipt] = []
    continuity_receipts: list[dict[str, Any]] = []

    for phase in phases:
        state, transfer, continuity = advance_background_state(
            state=state,
            anchors=anchors,
            phase=phase,
            tau=tau,
        )
        transfers.append(transfer)
        continuity_receipts.append(continuity)

    witness = _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "anchor_receipt_sha256": anchors.anchor_receipt_sha256,
        "phase_receipts": [
            phase.phase_receipt_sha256 for phase in phases
        ],
        "continuity_receipts": [
            receipt["receipt_sha256"]
            for receipt in continuity_receipts
        ],
        "final_background_state": {
            "rho_b": exact_data(state.rho_b),
            "rho_r": exact_data(state.rho_r),
            "rho_d": exact_data(state.rho_d),
            "curvature_h2": exact_data(state.curvature_h2),
            "raw_log_scale": exact_data(state.raw_log_scale),
            "continuity_receipt_sha256": (
                state.previous_continuity_receipt_sha256
            ),
        },
        "continuity_exponents": {
            "baryon": BARYON_EXPONENT,
            "dark": DARK_EXPONENT,
            "radiation": RADIATION_EXPONENT,
            "curvature": CURVATURE_EXPONENT,
        },
        "free_background_function_authority": (
            FREE_BACKGROUND_FUNCTION_AUTHORITY
        ),
        "host_wall_clock_authority": HOST_WALL_CLOCK_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "inverse_hz_state_authority": INVERSE_HZ_STATE_AUTHORITY,
        "projection_only": True,
    })
    return tuple(transfers), witness


def build_background_driven_trajectory(
    phases: Sequence[CommittedPhaseInput],
    anchors: BackgroundAnchors,
    *,
    tau: int | Fraction,
    c0: int | Fraction,
) -> dict[str, Any]:
    transfers, background_witness = derive_background_transfer_receipts(
        phases,
        anchors,
        tau=tau,
        c0=c0,
    )
    trajectory = build_exact_trajectory(
        transfers,
        tau=tau,
        c0=c0,
        curvature_sign=anchors.curvature_sign,
    )
    return _receipt({
        "schema": "HHS_PASS_220_I024_BACKGROUND_DRIVEN_TRAJECTORY_V1",
        "profile": PROFILE,
        "background_witness": background_witness,
        "trajectory": trajectory,
        "anchor_receipt_sha256": anchors.anchor_receipt_sha256,
        "free_background_function_authority": False,
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "inverse_hz_state_authority": False,
        "projection_only": True,
    })


def background_contract_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "reference_rule": (
            "finite SHA-bound density anchors at one selected reference epoch"
        ),
        "background_rule": (
            "B_n=gamma_G*(rho_b,n+rho_D,n+rho_r,n)+K_n"
        ),
        "baryon_continuity": (
            "rho_b,n+1=rho_b,n*ExpSym(-3*Deltaell_n)"
        ),
        "dark_continuity": (
            "rho_D,n+1=rho_D,n*ExpSym(-3*Deltaell_n)"
        ),
        "radiation_continuity": (
            "rho_r,n+1=rho_r,n*ExpSym(-4*Deltaell_n)"
        ),
        "curvature_continuity": (
            "K_n+1=K_n*ExpSym(-2*Deltaell_n)"
        ),
        "curvature_reference": "K_ref=-k*c0^2 at a_ref=1",
        "gravity_coupling": (
            "gamma_G is one SHA-bound exact egress constant; "
            "physically gamma_G=8*pi*G/3"
        ),
        "free_background_function_authority": False,
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "inverse_hz_state_authority": False,
        "projection_only": True,
    })
