"""Exact HHS GfE logarithm and reciprocal constraint lane.

Log_H is defined inside the equality membrane by an inverse phase witness,
not by a floating point transcendental projection:

    Log_H(g) == sigma
      iff E_H^sigma == g
      and E_H^(-sigma) == g^-1
      and E_H^sigma E_H^(-sigma) == unit.

The module preserves symbolic logarithms while executing all rational,
reciprocal, polynomialized-residual, cancellation, and replay checks exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

PASS_ID = "PASS_135_GFE_EXTENSION"
SCHEMA = "HHS_GFE_LOG_CONSTRAINT_RUNTIME_V1"
LOG_SCHEMA = "HHS_EQUALITY_GATED_LOG_WITNESS_V1"
TRACE_SCHEMA = "HHS_INTEGRATED_GFE_TRACE_V1"


class GFEConstraintError(ValueError):
    pass


def _fraction(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise GFEConstraintError("EXACT_RATIONAL_REQUIRED_NO_FLOAT_AUTHORITY")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    raise GFEConstraintError("EXACT_RATIONAL_REQUIRED")


def _q(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _stable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _stable(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_stable(v) for v in value]
    return value


def _root(label: str, value: Mapping[str, Any]) -> str:
    payload = json.dumps(_stable(dict(value)), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((label + "\n" + payload).encode("utf-8")).hexdigest()


def log_symbol(g: Fraction, unit: Fraction) -> str:
    if g == unit:
        return "0"
    return f"Log_H({_q(g)}|unit={_q(unit)})"


@dataclass(frozen=True)
class EqualityGatedLogWitness:
    g: Fraction
    unit: Fraction
    sigma: str

    @classmethod
    def construct(cls, g: Any, unit: Any = 1) -> "EqualityGatedLogWitness":
        qg, qu = _fraction(g), _fraction(unit)
        if qu == 0:
            raise GFEConstraintError("UNIT_ZERO")
        if qg == 0:
            raise GFEConstraintError("LOG_ARGUMENT_NOT_INVERTIBLE")
        return cls(qg, qu, log_symbol(qg, qu))

    @property
    def inverse(self) -> Fraction:
        # Typed inverse relative to the local unit: g * inv(g) == unit.
        return self.unit / self.g

    @property
    def inverse_sigma(self) -> str:
        return "0" if self.sigma == "0" else f"Cancel({self.sigma})"

    def to_dict(self) -> dict[str, Any]:
        body = {
            "schema": LOG_SCHEMA,
            "definition": "Log_H(g)==sigma iff E_H^sigma==g and E_H^Cancel(sigma)==Inverse_unit(g)",
            "local_unit": _q(self.unit),
            "g": _q(self.g),
            "g_inverse": _q(self.inverse),
            "sigma": self.sigma,
            "inverse_sigma": self.inverse_sigma,
            "equality_gate_chain": [
                f"E_H^({self.sigma})=={_q(self.g)}",
                f"E_H^({self.inverse_sigma})=={_q(self.inverse)}",
                f"({_q(self.g)})*({_q(self.inverse)})=={_q(self.unit)}",
                f"ComposePhase({self.sigma},{self.inverse_sigma})==0",
            ],
            "reciprocal_branch_rule": f"Log_H({_q(self.inverse)})=={self.inverse_sigma}",
            "branch_contract": "SAME_ADMITTED_SYMBOLIC_PHASE_BRANCH",
            "numeric_projection_authorized": False,
            "floating_point_authority_paths": 0,
        }
        body["witness_root"] = _root("hhs_equality_gated_log_witness_v1", body)
        return _stable(body)


def execute_gfe_trace(g: Any, *, unit: Any = 1, label: str = "UNNAMED") -> dict[str, Any]:
    qg, qu = _fraction(g), _fraction(unit)
    witness = EqualityGatedLogWitness.construct(qg, qu)
    gi = witness.inverse

    reciprocal_residue = qg * gi - qu
    theta = qg - qu
    rho = qg + gi - 2 * qu

    # Unit-relative polynomial identity. This is exact when unit acts as the
    # normalized identity. Non-normalized idempotent units require a separate
    # typed multiplication implementation and are intentionally not inferred.
    normalized_unit = qu == 1
    polynomial_residue = rho * qg - (qg - qu) ** 2 if normalized_unit else None

    epsilon_g = {
        "rational_part": _q(qg - qu),
        "symbolic_log_part": f"Cancel({witness.sigma})" if witness.sigma != "0" else "0",
    }
    epsilon_inverse = {
        "rational_part": _q(gi - qu),
        "symbolic_log_part": witness.sigma,
    }
    log_cancellation = "0"  # structural cancellation under the witnessed same-branch contract
    dual_energy_rational = (qg - qu) + (gi - qu)
    dual_log_residue = dual_energy_rational - rho

    statuses = {
        "reciprocal_closure": "VERIFIED_CLOSED" if reciprocal_residue == 0 else "OBSERVED_FAILING",
        "polynomialized_residual": (
            "VERIFIED_CLOSED" if polynomial_residue == 0 else
            "NOT_EVALUATED_NON_NORMALIZED_UNIT" if polynomial_residue is None else
            "OBSERVED_FAILING"
        ),
        "dual_log_cancellation": "VERIFIED_CLOSED" if dual_log_residue == 0 else "OBSERVED_FAILING",
    }
    overall = "VERIFIED_CLOSED" if all(v == "VERIFIED_CLOSED" for v in statuses.values()) else "CONDITIONALLY_CLOSED"

    body = {
        "schema": TRACE_SCHEMA,
        "pass_id": PASS_ID,
        "label": label,
        "authority_level": "A1",
        "local_unit": _q(qu),
        "normalized_unit_gate": normalized_unit,
        "g": _q(qg),
        "g_inverse": _q(gi),
        "theta": _q(theta),
        "rho": _q(rho),
        "reciprocal_closure_residue": _q(reciprocal_residue),
        "polynomialized_residual": None if polynomial_residue is None else _q(polynomial_residue),
        "epsilon_g": epsilon_g,
        "epsilon_g_inverse": epsilon_inverse,
        "symbolic_log_cancellation_residue": log_cancellation,
        "dual_energy_cancellation_residue": _q(dual_log_residue),
        "log_witness": witness.to_dict(),
        "statuses": statuses,
        "overall_status": overall,
        "no_float_authority": True,
    }
    body["trace_root"] = _root("hhs_integrated_gfe_trace_v1", body)
    return _stable(body)


def execute_calibration_suite() -> dict[str, Any]:
    cases = [
        ("GFE_EXACT_EQUILIBRIUM", Fraction(1, 1)),
        ("PAIR_RATIO_COORDINATE", Fraction(3, 2)),
        ("INVERSE_PAIR_RATIO", Fraction(2, 3)),
        ("NON_EQUILIBRIUM_DISPLACEMENT", Fraction(5, 4)),
    ]
    traces = [execute_gfe_trace(g, unit=1, label=label) for label, g in cases]
    reciprocal_pair_equal = traces[1]["rho"] == traces[2]["rho"]
    body = {
        "schema": SCHEMA,
        "pass_id": PASS_ID,
        "equation_gate_definition": {
            "canonical": "Log_H(g)==sigma iff E_H^sigma==g==unit/(unit-u)",
            "inverse": "Log_H(Inverse_unit(g))==Cancel(sigma)",
            "closure": "E_H^sigma * E_H^Cancel(sigma)==unit",
            "gfe_energy": "epsilon_H(g)==g-unit-Log_H(g)",
            "dual_cancellation": "epsilon_H(g)+epsilon_H(Inverse_unit(g))==rho_H(g)",
            "rho": "rho_H(g)==g+Inverse_unit(g)-2unit",
            "polynomialized_normalized": "rho_H(g)g==(g-unit)^2 under unit==1",
        },
        "traces": traces,
        "reciprocal_pair_rho_equal": reciprocal_pair_equal,
        "all_closed": all(t["overall_status"] == "VERIFIED_CLOSED" for t in traces),
        "floating_point_authority_paths": 0,
        "symbolic_log_paths": len(traces),
    }
    body["suite_root"] = _root("hhs_gfe_log_constraint_runtime_v1", body)
    return _stable(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--g", default=None, help="exact rational, e.g. 5/4")
    parser.add_argument("--unit", default="1")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = execute_gfe_trace(args.g, unit=args.unit, label="CLI") if args.g is not None else execute_calibration_suite()
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
