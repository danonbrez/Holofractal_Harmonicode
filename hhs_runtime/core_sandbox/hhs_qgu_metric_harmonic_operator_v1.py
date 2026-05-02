from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Dict, Optional, Sequence


class QGUOperatorError(ValueError):
    """Raised when the QGU operator cannot form an exact witness."""


def _fraction(value: Any, name: str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise QGUOperatorError(f"{name} must be numeric, not bool")
    try:
        return Fraction(value)
    except Exception as exc:
        raise QGUOperatorError(f"{name} is not exactly rationalizable: {value!r}") from exc


def _pow_fraction(base: Fraction, exponent: Fraction, name: str) -> Fraction:
    if exponent.denominator != 1:
        raise QGUOperatorError(f"{name} exponent must be integer: {exponent}")
    n = exponent.numerator
    if n >= 0:
        return base ** n
    if base == 0:
        raise QGUOperatorError(f"{name} cannot raise zero to a negative exponent")
    return Fraction(1, base ** (-n))


def _metric_interval(metric: Sequence[Sequence[Any]], dx: Sequence[Any]) -> Fraction:
    n = len(dx)
    if n == 0:
        raise QGUOperatorError("dx cannot be empty")
    if len(metric) != n:
        raise QGUOperatorError("metric row count must match dx dimension")
    dx_q = [_fraction(v, f"dx[{i}]") for i, v in enumerate(dx)]
    total = Fraction(0)
    for mu, row in enumerate(metric):
        if len(row) != n:
            raise QGUOperatorError("metric must be square and match dx dimension")
        for nu, entry in enumerate(row):
            total += _fraction(entry, f"g[{mu}][{nu}]") * dx_q[mu] * dx_q[nu]
    return total


def _canon(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"num": value.numerator, "den": value.denominator}
    if isinstance(value, tuple):
        return {"__tuple__": [_canon(v) for v in value]}
    if isinstance(value, list):
        return [_canon(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _canon(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    return value


@dataclass(frozen=True)
class QGUMetricHarmonicWitness:
    status: str
    projection_status: str
    ds2: Fraction
    balance: Fraction
    temporal_gate: Fraction
    phase_gate: Fraction
    left_generator: Fraction
    rhs_response: Optional[Fraction]
    solved_R_K_QGU: Optional[Fraction]
    provided_R_K_QGU: Optional[Fraction]
    residual: Optional[Fraction]
    guards: Dict[str, bool]
    closure_branch: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return _canon(asdict(self))


def evaluate_qgu_metric_harmonic_operator(
    *,
    t: Any,
    m: Any,
    yx: Any,
    xy: Any,
    c: Any,
    d: Any,
    ds2: Any = None,
    metric: Optional[Sequence[Sequence[Any]]] = None,
    dx: Optional[Sequence[Any]] = None,
    R_K_QGU: Any = None,
) -> Dict[str, Any]:
    """
    Exact QGU operator witness.

    Equation:
        [t(t^2 - 1)((1 - m^(yx - 1))/(m - 1))] R_K^QGU
        = 1 + d*S^4/(xy + c*S^2)

    where S = ds^2 = g_{mu nu} dx^mu dx^nu.

    The ordered product witness yx is preserved as the exponent carrier in
    m^(yx - 1). No xy/yx commutation is performed.
    """
    tq = _fraction(t, "t")
    mq = _fraction(m, "m")
    yxq = _fraction(yx, "yx")
    xyq = _fraction(xy, "xy")
    cq = _fraction(c, "c")
    dq = _fraction(d, "d")

    if ds2 is None:
        if metric is None or dx is None:
            raise QGUOperatorError("provide ds2 or both metric and dx")
        S = _metric_interval(metric, dx)
        ds2_source = "metric_contraction"
    else:
        S = _fraction(ds2, "ds2")
        ds2_source = "direct"

    temporal_gate = tq * (tq * tq - 1)
    guards = {
        "m_minus_1_nonzero": mq != 1,
        "temporal_gate_nonzero": temporal_gate != 0,
        "ordered_yx_preserved": True,
        "exact_fraction_arithmetic": True,
    }
    if not guards["m_minus_1_nonzero"]:
        raise QGUOperatorError("m - 1 = 0; phase quotient needs a resolved branch")
    if not guards["temporal_gate_nonzero"]:
        raise QGUOperatorError("t(t^2 - 1) = 0; temporal gate is fixed")

    m_power = _pow_fraction(mq, yxq - 1, "m^(yx-1)")
    phase_gate = (1 - m_power) / (mq - 1)
    left_generator = temporal_gate * phase_gate
    if left_generator == 0:
        raise QGUOperatorError("left generator is zero")

    S2 = S * S
    S4 = S2 * S2
    balance = xyq + cq * S2
    provided = None if R_K_QGU is None else _fraction(R_K_QGU, "R_K_QGU")

    if balance == 0:
        witness = QGUMetricHarmonicWitness(
            status="LOCKED",
            projection_status="BALANCED_ZERO_CLOSURE",
            ds2=S,
            balance=balance,
            temporal_gate=temporal_gate,
            phase_gate=phase_gate,
            left_generator=left_generator,
            rhs_response=None,
            solved_R_K_QGU=None,
            provided_R_K_QGU=provided,
            residual=None,
            guards=guards,
            closure_branch={
                "condition": "xy + c*(ds2)^2 = 0",
                "meaning": "balanced closure state, not magnitude loss",
                "constraint_substitution": "xy = -c*(ds2)^2",
                "quotient_projection": "blocked; evaluate on constraint manifold",
                "quartic_excitation": dq * S4,
                "ds2_source": ds2_source,
            },
        )
        return {
            "ok": True,
            "locked": True,
            "status": "LOCKED",
            "projection_status": "BALANCED_ZERO_CLOSURE",
            "audit_value": Fraction(0),
            "witness": witness.to_dict(),
        }

    rhs = 1 + (dq * S4) / balance
    solved = rhs / left_generator
    residual = None if provided is None else left_generator * provided - rhs
    locked = residual is None or residual == 0
    witness = QGUMetricHarmonicWitness(
        status="LOCKED" if locked else "QUARANTINED",
        projection_status="REGULAR_RESPONSE" if locked else "R_K_RESIDUAL_MISMATCH",
        ds2=S,
        balance=balance,
        temporal_gate=temporal_gate,
        phase_gate=phase_gate,
        left_generator=left_generator,
        rhs_response=rhs,
        solved_R_K_QGU=solved,
        provided_R_K_QGU=provided,
        residual=residual,
        guards=guards,
        closure_branch={
            "condition": "xy + c*(ds2)^2 != 0",
            "meaning": "regular metric harmonic response",
            "ds2_source": ds2_source,
        },
    )
    return {
        "ok": locked,
        "locked": locked,
        "status": witness.status,
        "projection_status": witness.projection_status,
        "audit_value": solved if locked else Fraction(0),
        "R_K_QGU": _canon(solved),
        "witness": witness.to_dict(),
    }


def qgu_metric_harmonic_operator(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise QGUOperatorError("QGU payload must be a dict")
    return evaluate_qgu_metric_harmonic_operator(
        t=payload["t"],
        m=payload["m"],
        yx=payload["yx"],
        xy=payload["xy"],
        c=payload["c"],
        d=payload["d"],
        ds2=payload.get("ds2"),
        metric=payload.get("metric"),
        dx=payload.get("dx"),
        R_K_QGU=payload.get("R_K_QGU"),
    )


def demo_payload() -> Dict[str, Any]:
    return {
        "t": 2,
        "m": 2,
        "yx": 2,
        "xy": 1,
        "c": 3,
        "d": 5,
        "metric": [[1, 0], [0, -1]],
        "dx": [3, 1],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(qgu_metric_harmonic_operator(demo_payload()), indent=2, ensure_ascii=False))
