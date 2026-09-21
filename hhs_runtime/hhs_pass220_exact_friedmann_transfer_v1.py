"""Pass 220 I023 exact Friedmann transfer projection.

T_COSMO-05 consumes committed transition-receipt projections and produces
an exact symbolic expansion trajectory. Canonical VM81/Delta/Hash authority
remains upstream. No host wall-clock or floating-point arithmetic is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from math import isqrt
import json
import re
from typing import Any, Sequence

from hhs_runtime.hhs_pass220_cosmological_clock_cadence_v1 import (
    PHASE_ORBIT,
    h_p,
    make_transition,
    sigma_lookup,
)

SCHEMA = "HHS_PASS_220_I023_EXACT_FRIEDMANN_TRANSFER_V1"
PROFILE = "PASS220-I023-EXACT-FRIEDMANN-TRANSFER-v1"
INTERPOLATION = "ZERO_ORDER_HOLD"
G72_OPERATOR = "G72"
G72_IDENTITY = "G72^72==2"
HOST_WALL_CLOCK_AUTHORITY = False
FLOATING_POINT_AUTHORITY = False
CANONICAL_ADMISSION_AUTHORITY = False
INVERSE_HZ_STATE_AUTHORITY = False
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Pass220I023TransferError(ValueError):
    pass


@dataclass(frozen=True)
class ExactExpr:
    op: str
    args: tuple[Any, ...]


ExactValue = Fraction | ExactExpr


@dataclass(frozen=True)
class TransferReceipt:
    transition_index: int
    sigma: int
    lambda_increment: Fraction
    theta: Fraction
    background_h2: Fraction
    source_receipt_sha256: str


def _i(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I023TransferError(f"{name} must be an exact integer")
    return value


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise Pass220I023TransferError(f"{name} must be int or Fraction")
    return Fraction(value)


def _positive_q(value: Any, name: str) -> Fraction:
    q = _q(value, name)
    if q <= 0:
        raise Pass220I023TransferError(f"{name} must be positive")
    return q


def _sha(value: Any, name: str = "source_receipt_sha256") -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise Pass220I023TransferError(f"{name} must be lowercase sha256 hex")
    return value


def _expr_data(value: ExactValue) -> Any:
    if isinstance(value, Fraction):
        return {"q": [value.numerator, value.denominator]}
    if not isinstance(value, ExactExpr):
        raise Pass220I023TransferError("non-exact expression value")
    return {"op": value.op, "args": [_expr_data(v) for v in value.args]}


def _add(*values: ExactValue) -> ExactValue:
    flat: list[ExactValue] = []
    qsum = Fraction(0)
    for value in values:
        if isinstance(value, Fraction):
            qsum += value
        elif isinstance(value, ExactExpr) and value.op == "add":
            for arg in value.args:
                if isinstance(arg, Fraction):
                    qsum += arg
                else:
                    flat.append(arg)
        else:
            flat.append(value)
    if qsum:
        flat.insert(0, qsum)
    if not flat:
        return Fraction(0)
    if len(flat) == 1:
        return flat[0]
    return ExactExpr("add", tuple(flat))


def _mul(*values: ExactValue) -> ExactValue:
    flat: list[ExactValue] = []
    qprod = Fraction(1)
    for value in values:
        if isinstance(value, Fraction):
            if value == 0:
                return Fraction(0)
            qprod *= value
        elif isinstance(value, ExactExpr) and value.op == "mul":
            for arg in value.args:
                if isinstance(arg, Fraction):
                    if arg == 0:
                        return Fraction(0)
                    qprod *= arg
                else:
                    flat.append(arg)
        else:
            flat.append(value)
    if qprod != 1 or not flat:
        flat.insert(0, qprod)
    if len(flat) == 1:
        return flat[0]
    return ExactExpr("mul", tuple(flat))


def _neg(value: ExactValue) -> ExactValue:
    if isinstance(value, Fraction):
        return -value
    return _mul(Fraction(-1), value)


def _sub(left: ExactValue, right: ExactValue) -> ExactValue:
    return _add(left, _neg(right))


def _div(numerator: ExactValue, denominator: ExactValue) -> ExactValue:
    if isinstance(denominator, Fraction) and denominator == 0:
        raise Pass220I023TransferError("exact expression division by zero")
    if isinstance(numerator, Fraction) and isinstance(denominator, Fraction):
        return numerator / denominator
    return ExactExpr("div", (numerator, denominator))


def _sqrt(value: ExactValue) -> ExactValue:
    if isinstance(value, Fraction):
        if value < 0:
            raise Pass220I023TransferError(
                "positive Hubble branch requires nonnegative H^2"
            )
        nr = isqrt(value.numerator)
        dr = isqrt(value.denominator)
        if nr * nr == value.numerator and dr * dr == value.denominator:
            return Fraction(nr, dr)
    return ExactExpr("sqrt", (value,))


def _exp(value: ExactValue) -> ExactValue:
    if isinstance(value, Fraction) and value == 0:
        return Fraction(1)
    return ExactExpr("exp", (value,))


def _curvature_map(curvature_sign: int, dc: ExactValue) -> ExactValue:
    k = _i(curvature_sign, "curvature_sign")
    if k not in (-1, 0, 1):
        raise Pass220I023TransferError("curvature_sign must be -1, 0, or 1")
    if k == 0:
        return dc
    return ExactExpr("S_k", (Fraction(k), dc))


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return {
        **payload,
        "receipt_sha256": sha256(encoded.encode("utf-8")).hexdigest(),
    }


def make_transfer_receipt(
    transition_index: int,
    lambda_increment: int | Fraction,
    theta: int | Fraction,
    background_h2: int | Fraction,
    source_receipt_sha256: str,
) -> TransferReceipt:
    n = _i(transition_index, "transition_index")
    return TransferReceipt(
        transition_index=n,
        sigma=sigma_lookup(n),
        lambda_increment=_q(lambda_increment, "lambda_increment"),
        theta=_positive_q(theta, "theta"),
        background_h2=_q(background_h2, "background_h2"),
        source_receipt_sha256=_sha(source_receipt_sha256),
    )


def total_h2(
    receipt: TransferReceipt,
    tau: int | Fraction,
) -> tuple[Fraction, Fraction]:
    scale = _positive_q(tau, "tau")
    sample = make_transition(
        receipt.transition_index,
        receipt.lambda_increment,
        receipt.theta,
    )
    phase = h_p(sample, scale)
    h2 = receipt.background_h2 + phase * phase
    if h2 < 0:
        raise Pass220I023TransferError(
            "Friedmann H^2 is negative on the expanding branch"
        )
    return phase, h2


def interval_log_scale_increment(
    receipt: TransferReceipt,
    tau: int | Fraction,
) -> ExactValue:
    scale = _positive_q(tau, "tau")
    _, h2 = total_h2(receipt, scale)
    return _mul(scale * receipt.theta, _sqrt(h2))


def phase_only_increment(
    receipt: TransferReceipt,
    tau: int | Fraction,
) -> ExactValue:
    if receipt.background_h2 != 0:
        raise Pass220I023TransferError(
            "phase_only_increment requires background_h2 == 0"
        )
    return interval_log_scale_increment(receipt, tau)


def build_exact_trajectory(
    receipts: Sequence[TransferReceipt],
    *,
    tau: int | Fraction,
    c0: int | Fraction,
    curvature_sign: int = 0,
) -> dict[str, Any]:
    if not receipts:
        raise Pass220I023TransferError(
            "at least one committed transfer receipt is required"
        )
    scale = _positive_q(tau, "tau")
    light = _positive_q(c0, "c0")
    k = _i(curvature_sign, "curvature_sign")
    if k not in (-1, 0, 1):
        raise Pass220I023TransferError("curvature_sign must be -1, 0, or 1")

    for expected, receipt in enumerate(receipts):
        if receipt.transition_index != expected:
            raise Pass220I023TransferError(
                "receipts must be contiguous and zero-indexed"
            )
        if receipt.sigma != sigma_lookup(expected):
            raise Pass220I023TransferError(
                "receipt sigma does not match canonical phase route"
            )

    logical_times: list[Fraction] = [Fraction(0)]
    physical_times: list[Fraction] = [Fraction(0)]
    raw_logs: list[ExactValue] = [Fraction(0)]
    phase_h_values: list[Fraction] = []
    total_h2_values: list[Fraction] = []
    hubble_values: list[ExactValue] = []

    for receipt in receipts:
        phase_h_value, h2 = total_h2(receipt, scale)
        hubble = _sqrt(h2)
        increment = _mul(scale * receipt.theta, hubble)
        phase_h_values.append(phase_h_value)
        total_h2_values.append(h2)
        hubble_values.append(hubble)
        logical_times.append(logical_times[-1] + receipt.theta)
        physical_times.append(
            physical_times[-1] + scale * receipt.theta
        )
        raw_logs.append(_add(raw_logs[-1], increment))

    present_log = raw_logs[-1]
    normalized_logs = [_sub(value, present_log) for value in raw_logs]
    one_plus_z = [_exp(_neg(value)) for value in normalized_logs]

    interval_dc: list[ExactValue] = []
    for i, receipt in enumerate(receipts):
        hubble = hubble_values[i]
        dt = scale * receipt.theta
        ell_i = normalized_logs[i]
        if isinstance(hubble, Fraction) and hubble == 0:
            step = _mul(light, dt, _exp(_neg(ell_i)))
        else:
            step = _mul(
                light,
                _exp(_neg(ell_i)),
                _div(
                    _sub(
                        Fraction(1),
                        _exp(_neg(_mul(hubble, dt))),
                    ),
                    hubble,
                ),
            )
        interval_dc.append(step)

    dc_to_present: list[ExactValue] = [
        Fraction(0) for _ in range(len(receipts) + 1)
    ]
    running: ExactValue = Fraction(0)
    for i in range(len(receipts) - 1, -1, -1):
        running = _add(interval_dc[i], running)
        dc_to_present[i] = running

    nodes: list[dict[str, Any]] = []
    for i in range(len(receipts) + 1):
        if i < len(receipts):
            phase_h_value = phase_h_values[i]
            h2 = total_h2_values[i]
            hubble = hubble_values[i]
            if isinstance(hubble, Fraction) and hubble == 0:
                dh: ExactValue = ExactExpr("infinity", ())
            else:
                dh = _div(light, hubble)
        else:
            phase_h_value = Fraction(0)
            h2 = Fraction(0)
            hubble = Fraction(0)
            dh = ExactExpr("present_endpoint", ())

        dm = _curvature_map(k, dc_to_present[i])
        da = _div(dm, one_plus_z[i])
        dl = _mul(one_plus_z[i], dm)

        nodes.append({
            "transition_index": i,
            "sigma": sigma_lookup(i) if i < len(receipts) else None,
            "logical_time": (
                f"{logical_times[i].numerator}/{logical_times[i].denominator}"
            ),
            "physical_time": (
                f"{physical_times[i].numerator}/{physical_times[i].denominator}"
            ),
            "phase_h": (
                f"{phase_h_value.numerator}/{phase_h_value.denominator}"
            ),
            "total_h2": f"{h2.numerator}/{h2.denominator}",
            "hubble": _expr_data(hubble),
            "raw_log_scale": _expr_data(raw_logs[i]),
            "normalized_log_scale": _expr_data(normalized_logs[i]),
            "one_plus_z": _expr_data(one_plus_z[i]),
            "hubble_distance": _expr_data(dh),
            "comoving_distance_to_present": _expr_data(dc_to_present[i]),
            "transverse_comoving_distance": _expr_data(dm),
            "angular_diameter_distance": _expr_data(da),
            "luminosity_distance": _expr_data(dl),
        })

    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "interpolation": INTERPOLATION,
        "receipt_count": len(receipts),
        "tau": f"{scale.numerator}/{scale.denominator}",
        "c0": f"{light.numerator}/{light.denominator}",
        "curvature_sign": k,
        "phase_orbit": PHASE_ORBIT,
        "source_receipts": [
            receipt.source_receipt_sha256 for receipt in receipts
        ],
        "nodes": nodes,
        "g72_operator": G72_OPERATOR,
        "g72_identity": G72_IDENTITY,
        "g72_scalar_evaluation_allowed": False,
        "host_wall_clock_authority": HOST_WALL_CLOCK_AUTHORITY,
        "floating_point_authority": FLOATING_POINT_AUTHORITY,
        "projection_only": True,
        "canonical_admission_authority": CANONICAL_ADMISSION_AUTHORITY,
        "inverse_hz_state_authority": INVERSE_HZ_STATE_AUTHORITY,
    })


def transfer_contract_descriptor() -> dict[str, Any]:
    return _receipt({
        "schema": SCHEMA,
        "profile": PROFILE,
        "interpolation": INTERPOLATION,
        "time_rule": "dt_n=tau*theta_n",
        "friedmann_rule": (
            "H_n^2=background_h2_n+(lambda_n/(tau*theta_n))^2"
        ),
        "scale_rule": (
            "log(a_n+1/a_n)=H_n*dt_n under committed-interval "
            "zero-order hold"
        ),
        "redshift_rule": (
            "1+z_n=exp(log(a_present)-log(a_n))"
        ),
        "distance_rule": (
            "DeltaDc=c0*exp(-ell_n)*(1-exp(-H_n*dt_n))/H_n"
        ),
        "symbolic_exp_required": True,
        "symbolic_sqrt_required": True,
        "trapezoid_is_canonical": False,
        "g72_scalar_evaluation_allowed": False,
        "host_wall_clock_authority": False,
        "floating_point_authority": False,
        "projection_only": True,
        "canonical_admission_authority": False,
        "inverse_hz_state_authority": False,
    })
