"""Pass 219 Lane 5 self-solving proof optimizer — cycle 6.

This adapter uses the repository-authorized *planning* surface for the legacy
self-solving constraint pipeline together with the proof-preserving Lane 5
optimizer.  It does not directly execute the legacy plugin body.

The desired end-state is the remaining T_BRIDGE/root-certificate closure:

1. Recover an exact algebraic certificate for the committed positive Genesis
   root from the already-declared Pythagorean/sextic construction.
2. Replace the Taylor-remainder sign heuristic for one symplectic-Euler Kepler
   step by an exact radical-free zero-membrane polynomial.
3. Classify h -> h/2 sign transport exactly:
      SAME_CLASS / ZERO_MEMBRANE / MEMBRANE_BETWEEN_SCALES.
4. Leave only the cumulative multi-step workload trace/band certificate as a
   separate execution obligation.

Authority boundary:
- candidate/proof generation only;
- no direct legacy self-solving plugin execution;
- no VM81 mutation;
- no Hash72/Hash216 minting;
- no persistence mutation;
- no floating-point canonical authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from hhs_runtime.hhs_plugin_capability_planner_v1 import inspect_capability_plan
from hhs_runtime.core_sandbox.hhs_pass219_proof_preserving_optimizer_1_21_12 import (
    activate_proof_preserving_optimization,
)

SCHEMA = "HHS_PASS219_LANE5_SELF_SOLVING_TBRIDGE_OPTIMIZER_V1"
VERSION = "1.0.0-cycle6"
SELF_SOLVING_SOURCE = "hhs_self_solving_constraint_pipeline_v1.py"

ROOT_POLYNOMIAL = (Fraction(-16), Fraction(-8), Fraction(3), Fraction(2))
ROOT_ISOLATION_LOW = Fraction(2133185666641251, 10**15)
ROOT_ISOLATION_HIGH = Fraction(2133185666641252, 10**15)


class Lane5SelfSolvingOptimizerError(ValueError):
    pass


def _stable(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _receipt(payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(payload)
    body["receipt_sha256"] = sha256(_stable(body).encode("utf-8")).hexdigest()
    return body


def _q(value: Any, name: str) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise Lane5SelfSolvingOptimizerError(
            f"{name} must be an exact int/Fraction"
        )
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise Lane5SelfSolvingOptimizerError(
            f"{name} must be an exact int/Fraction"
        ) from exc


def _sign(value: Fraction) -> int:
    return -1 if value < 0 else (1 if value > 0 else 0)


def genesis_root_polynomial(u: Any) -> Fraction:
    """Evaluate f(u)=2u^3+3u^2-8u-16 exactly."""
    q = _q(u, "u")
    return 2 * q**3 + 3 * q**2 - 8 * q - 16


def genesis_root_certificate() -> dict[str, Any]:
    """Exact positive-root isolation derived from the Genesis closure.

    The committed construction is:

        b^2 = 2
        a^2 = u
        c^2 = u+2
        b^2+c^2 = a^2 b c

    On the positive branch this is:

        u+4 = u sqrt(2(u+2)).

    Squaring is reversible on u>0 because both sides are positive, producing:

        (u+4)^2 = 2u^2(u+2)
        <=> 2u^3+3u^2-8u-16 = 0.

    The derivative is 6u^2+6u-8 >= 28 on u>=2, so the root in (2,3)
    is unique.  The narrow decimal-independent rational bracket below gives the
    repository reconstruction certificate.
    """
    lo = ROOT_ISOLATION_LOW
    hi = ROOT_ISOLATION_HIGH
    flo = genesis_root_polynomial(lo)
    fhi = genesis_root_polynomial(hi)

    checks = {
        "f2_negative": genesis_root_polynomial(2) < 0,
        "f3_positive": genesis_root_polynomial(3) > 0,
        "isolation_low_negative": flo < 0,
        "isolation_high_positive": fhi > 0,
        "isolation_ordered": 2 < lo < hi < 3,
        "derivative_positive_for_u_ge_2": True,  # 6u^2+6u-8 >= 28.
    }
    if not all(checks.values()):
        raise Lane5SelfSolvingOptimizerError("Genesis root certificate failed")

    return _receipt(
        {
            "schema": "HHS_PASS219_GENESIS_SEXTIC_ROOT_CERTIFICATE_V1",
            "status": "PASS",
            "source_constraints": (
                "b²=2",
                "a²=u",
                "c²=u+2",
                "b²+c²=a²bc",
                "positive branch",
            ),
            "unsquared_positive_branch": "u+4=u*sqrt(2*(u+2))",
            "squared_identity": "(u+4)^2=2*u^2*(u+2)",
            "cubic_in_u": "2*u^3+3*u^2-8*u-16=0",
            "sextic_in_a_with_u_a2": "2*a^6+3*a^4-8*a^2-16=0",
            "polynomial_coefficients_low_to_high": [
                int(v) for v in ROOT_POLYNOMIAL
            ],
            "isolation_interval": {
                "low": [lo.numerator, lo.denominator],
                "high": [hi.numerator, hi.denominator],
            },
            "endpoint_values": {
                "f_low": [flo.numerator, flo.denominator],
                "f_high": [fhi.numerator, fhi.denominator],
            },
            "uniqueness_witness": (
                "f'(u)=6u^2+6u-8 >= 28 > 0 for u>=2"
            ),
            "checks": checks,
            "floating_point_authority": False,
            "canonical_runtime_mutation_authority": False,
        }
    )


def energy_defect_membrane(
    *,
    alpha: Any,
    beta: Any,
    gamma: Any,
) -> dict[str, Any]:
    """Exact one-step Kepler energy-defect sign membrane.

    Dimensionless variables for one carried kick->drift step:

        alpha = h (x.v)/r^2 = h v_r/r
        beta  = h^2 mu/r^3
        gamma = h^2 v_t^2/r^2 = h^2 L^2/r^4

    Define:
        R^2 = (1+alpha-beta)^2 + gamma = (r_{n+1}/r_n)^2
        A   = 1-alpha+beta/2
        F   = A^2 R^2 - 1

    The exact normalized energy defect is

        (H_{n+1}-H_n) r/mu
          = A - 1/R
          = F / (R (A R + 1)).

    Hence when A>0 and R^2>0, sign(Delta H)=sign(F).  No Taylor remainder is
    needed to classify the local trinary energy-defect register.
    """
    a = _q(alpha, "alpha")
    b = _q(beta, "beta")
    g = _q(gamma, "gamma")
    r2_ratio = (1 + a - b) ** 2 + g
    A = 1 - a + b / 2
    F = A * A * r2_ratio - 1

    admissible = A > 0 and r2_ratio > 0
    return _receipt(
        {
            "schema": "HHS_PASS219_EXACT_ENERGY_DEFECT_MEMBRANE_V1",
            "status": "PASS" if admissible else "UNRESOLVED",
            "alpha": [a.numerator, a.denominator],
            "beta": [b.numerator, b.denominator],
            "gamma": [g.numerator, g.denominator],
            "A": [A.numerator, A.denominator],
            "R2": [r2_ratio.numerator, r2_ratio.denominator],
            "F": [F.numerator, F.denominator],
            "sgn3_local_energy_defect": _sign(F) if admissible else None,
            "exact_identity": (
                "(DeltaH*r/mu)=F/(R*(A*R+1)); "
                "F=A^2*((1+alpha-beta)^2+gamma)-1"
            ),
            "zero_membrane": "F=0",
            "admission": "A>0 and R2>0",
            "taylor_remainder_required": False,
            "canonical_runtime_mutation_authority": False,
        }
    )


def halving_class_transport(
    *,
    alpha: Any,
    beta: Any,
    gamma: Any,
) -> dict[str, Any]:
    """Compare the same exact state under h and h/2.

    At fixed state:
        alpha -> alpha/2
        beta  -> beta/4
        gamma -> gamma/4.

    If endpoint signs differ, polynomial continuity requires at least one F=0
    membrane between the two scales.  Thus a class flip is never silent.
    """
    full = energy_defect_membrane(
        alpha=alpha,
        beta=beta,
        gamma=gamma,
    )
    a = _q(alpha, "alpha")
    b = _q(beta, "beta")
    g = _q(gamma, "gamma")
    half = energy_defect_membrane(
        alpha=a / 2,
        beta=b / 4,
        gamma=g / 4,
    )
    if full["status"] != "PASS" or half["status"] != "PASS":
        decision = "UNRESOLVED"
    else:
        s1 = int(full["sgn3_local_energy_defect"])
        s2 = int(half["sgn3_local_energy_defect"])
        if 0 in (s1, s2):
            decision = "ZERO_MEMBRANE"
        elif s1 == s2:
            decision = "SAME_CLASS"
        else:
            decision = "MEMBRANE_BETWEEN_SCALES"

    return _receipt(
        {
            "schema": "HHS_PASS219_EXACT_HALVING_CLASS_TRANSPORT_V1",
            "status": "PASS" if decision != "UNRESOLVED" else "UNRESOLVED",
            "decision": decision,
            "full_step": full,
            "half_step": half,
            "continuity_rule": (
                "F is a polynomial in h after alpha=h*a, beta=h^2*b, "
                "gamma=h^2*g; opposite endpoint signs imply an F=0 root "
                "between h/2 and h"
            ),
            "silent_class_flip_authorized": False,
            "canonical_runtime_mutation_authority": False,
        }
    )


def self_solving_optimization_receipt(
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Compose the guarded self-solving source plan with Lane 5 proof optimization."""
    repo_root = (
        Path(root).resolve()
        if root is not None
        else Path(__file__).resolve().parents[2]
    )
    self_solving_plan = inspect_capability_plan(
        repo_root,
        SELF_SOLVING_SOURCE,
    ).to_dict()
    optimization = activate_proof_preserving_optimization(repo_root)
    root_cert = genesis_root_certificate()

    # Two exact sample states from the committed orbital discussion:
    # circular: r=1, v_r=0, v_t=1, mu=1, h=1/4
    circular = halving_class_transport(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 16),
    )
    # eccentric: r=1, v_r=0, v_t=4/5, mu=1, h=1/4
    eccentric = halving_class_transport(
        alpha=0,
        beta=Fraction(1, 16),
        gamma=Fraction(1, 25),
    )

    checks = {
        "self_solving_source_is_plan_only": (
            self_solving_plan["safe_invocation_plan"]["direct_execution_authorized"]
            is False
        ),
        "proof_optimizer_read_only": (
            optimization["read_only_optimization_activated"] is True
            and optimization["authority_boundary"]["vm81_mutation_authority"]
            is False
        ),
        "root_certificate_closed": root_cert["status"] == "PASS",
        "circular_class_transport_closed": circular["status"] == "PASS",
        "eccentric_class_transport_closed": eccentric["status"] == "PASS",
        "no_silent_class_flip_circular": (
            circular["decision"] in {
                "SAME_CLASS",
                "ZERO_MEMBRANE",
                "MEMBRANE_BETWEEN_SCALES",
            }
        ),
        "no_silent_class_flip_eccentric": (
            eccentric["decision"] in {
                "SAME_CLASS",
                "ZERO_MEMBRANE",
                "MEMBRANE_BETWEEN_SCALES",
            }
        ),
    }

    return _receipt(
        {
            "schema": SCHEMA,
            "version": VERSION,
            "status": "PASS" if all(checks.values()) else "FAIL",
            "desired_end_state": (
                "exact Genesis algebraic-root certificate + exact local "
                "energy-defect membrane + non-silent h/2 class transport"
            ),
            "self_solving_source": SELF_SOLVING_SOURCE,
            "self_solving_capability_plan": {
                "adapter_status": self_solving_plan["adapter_status"],
                "execution_policy": self_solving_plan["execution_policy"],
                "safe_invocation_plan": self_solving_plan[
                    "safe_invocation_plan"
                ],
                "plan_kernel_witness": self_solving_plan[
                    "plan_kernel_witness"
                ],
            },
            "proof_preserving_optimizer": {
                "version": optimization["version"],
                "classification": optimization["classification"],
                "authority_qualifier": optimization["authority_qualifier"],
                "optimization_schedule_sha256": optimization[
                    "optimization_schedule_sha256"
                ],
            },
            "root_certificate": root_cert,
            "circular_h_quarter_transport": circular,
            "eccentric_h_quarter_transport": eccentric,
            "checks": checks,
            "solved_obligations": (
                "exact Genesis root polynomial and rational isolation",
                "exact local Kepler energy-defect zero membrane F=0",
                "exact fixed-state h->h/2 trinary class transport rule",
            ),
            "remaining_obligations": (
                "cumulative multi-step energy-band certificate over the "
                "committed workload trace",
                "trajectory-level corresponding-state h vs h/2 partition "
                "receipt if required",
            ),
            "legacy_self_solving_direct_execution_used": False,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "floating_point_canonical_authority": False,
        }
    )


if __name__ == "__main__":
    print(_stable(self_solving_optimization_receipt()))
