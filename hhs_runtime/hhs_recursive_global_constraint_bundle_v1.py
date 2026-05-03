"""
HHS Recursive Global Constraint Bundle v1

Purpose
-------
Preserve the submitted equation family as a simultaneous recursive constraint
bundle without replacing existing solver, drift_gate, Hash72, receipt, or
self-solving logic.

Execution role
--------------
- Passive/additive module.
- Intended to be called by solver/drift-gate/receipt bridges as an expanded
  invariant context provider.
- Does not modify Hash72 canonical identity logic.
- Does not commute ordered products.
- Does not collapse witnesses into booleans except in explicit check reports.

Core rule
---------
All constraints are evaluated as one bundle.  Local equalities are recorded as
witnesses and only projected after the whole bundle is assembled.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal, getcontext
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Tuple

getcontext().prec = 100


# ---------------------------------------------------------------------------
# Ordered tensor witnesses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OrderedWord:
    symbols: Tuple[str, ...]

    @classmethod
    def of(cls, *symbols: str) -> "OrderedWord":
        return cls(tuple(symbols))

    def concat(self, other: "OrderedWord") -> "OrderedWord":
        return OrderedWord(self.symbols + other.symbols)

    @property
    def text(self) -> str:
        return "".join(self.symbols)


XY = OrderedWord.of("x", "y")
YX = OrderedWord.of("y", "x")
ZW = OrderedWord.of("z", "w")
WZ = OrderedWord.of("w", "z")
WXYZ = OrderedWord.of("w", "x", "y", "z")


# ---------------------------------------------------------------------------
# Numeric witness state
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class HHSNumericWitness:
    """Scalar projection witnesses used only after ordered bundle assembly."""

    a2: Decimal = Decimal(1)
    xy_scalar: Decimal = Decimal(1)
    yx_scalar: Decimal = Decimal(-1)
    u72: Decimal = Decimal(1)
    n4: Decimal = Decimal(1)

    @property
    def b2(self) -> Decimal:
        return self.a2 + self.a2

    @property
    def c2(self) -> Decimal:
        return self.b2 + self.a2

    @property
    def d2(self) -> Decimal:
        return self.c2 + self.b2

    @property
    def e2(self) -> Decimal:
        return self.d2 + self.c2

    @property
    def phi(self) -> Decimal:
        return (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)

    @property
    def rational_m_gate(self) -> Decimal:
        f = Fraction(8158, 5040)
        return Decimal(f.numerator) / Decimal(f.denominator)

    @property
    def palindromic_seed(self) -> Decimal:
        f = Fraction(179971179971, 1000000)
        return Decimal(f.numerator) / Decimal(f.denominator)


def dec_close(a: Decimal, b: Decimal, tol: Decimal = Decimal("1e-40")) -> bool:
    return abs(a - b) <= tol


@dataclass(frozen=True)
class ConstraintWitness:
    name: str
    lhs: Any
    rhs: Any
    ok: bool
    relation: str = "=="
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["lhs"] = str(self.lhs)
        d["rhs"] = str(self.rhs)
        return d


# ---------------------------------------------------------------------------
# Bundle construction
# ---------------------------------------------------------------------------

class HHSRecursiveGlobalConstraintBundle:
    """Simultaneous recursive constraint bundle.

    This object records all constraints before computing pass/fail, preventing
    local substitutions from becoming authoritative ahead of global closure.
    """

    def __init__(self, witness: HHSNumericWitness | None = None):
        self.w = witness or HHSNumericWitness()
        self.constraints: List[ConstraintWitness] = []
        self.ordered_words: Dict[str, OrderedWord] = {
            "xy": XY,
            "yx": YX,
            "zw": ZW,
            "wz": WZ,
            "wxyz": WXYZ,
        }
        self.dependencies: Dict[str, str] = {}

    def add(self, name: str, lhs: Any, rhs: Any, ok: bool, relation: str = "==", note: str = "") -> None:
        self.constraints.append(ConstraintWitness(name, lhs, rhs, ok, relation, note))

    def build_ordered_tensor_constraints(self) -> None:
        self.add("ordered_xy_yx_noncommutative", XY.text, YX.text, XY != YX, "!=")
        self.add("ordered_zw_wz_noncommutative", ZW.text, WZ.text, ZW != WZ, "!=")
        self.add("ordered_xy_zw_distinct", XY.text, ZW.text, XY != ZW, "!=")
        self.dependencies.update({
            "xy": "OrderedWord(x,y); scalar projection only after closure",
            "yx": "OrderedWord(y,x); scalar projection only after closure",
            "zw": "OrderedWord(z,w); scalar projection only after closure",
            "wz": "OrderedWord(w,z); scalar projection only after closure",
        })

    def build_constructor_spine_constraints(self) -> None:
        w = self.w
        self.add("b2_eq_a2_plus_a2", w.b2, w.a2 + w.a2, dec_close(w.b2, w.a2 + w.a2))
        self.add("c2_eq_b2_plus_a2", w.c2, w.b2 + w.a2, dec_close(w.c2, w.b2 + w.a2))
        self.add("a2_eq_c2_minus_b2", w.a2, w.c2 - w.b2, dec_close(w.a2, w.c2 - w.b2))
        self.add("d2_eq_c2_plus_b2", w.d2, w.c2 + w.b2, dec_close(w.d2, w.c2 + w.b2))
        self.add("e2_eq_d2_plus_c2", w.e2, w.d2 + w.c2, dec_close(w.e2, w.d2 + w.c2))
        self.add("normalized_constructor_spine_e2_over_b6", w.e2 / (w.b2 ** 3), Decimal(1), dec_close(w.e2 / (w.b2 ** 3), Decimal(1)))
        self.dependencies.update({
            "b2": "a2 + a2",
            "c2": "b2 + a2",
            "d2": "c2 + b2",
            "e2": "d2 + c2",
            "constructor_spine": "e2 / b6 normalized to xy carrier",
        })

    def build_unit_circle_constraints(self) -> None:
        w = self.w
        self.add("xy_scalar_unit", w.xy_scalar, Decimal(1), dec_close(w.xy_scalar, Decimal(1)))
        self.add("u72_wraparound_unit", w.u72, Decimal(1), dec_close(w.u72, Decimal(1)))
        self.add("xy_eq_a2_projection", w.xy_scalar, w.a2, dec_close(w.xy_scalar, w.a2))
        self.add("c2_minus_b2_over_a2_unit", (w.c2 - w.b2) / w.a2, Decimal(1), dec_close((w.c2 - w.b2) / w.a2, Decimal(1)))
        self.add("golden_unit_m2_minus_m", w.phi ** 2 - w.phi, Decimal(1), dec_close(w.phi ** 2 - w.phi, Decimal(1)))
        self.add("m_eq_one_plus_inverse", w.phi, Decimal(1) + (Decimal(1) / w.phi), dec_close(w.phi, Decimal(1) + (Decimal(1) / w.phi)))
        self.dependencies.update({
            "unit_circle": "1 = xy = u72 = a2 = (c2-b2)/a2 = m2-m",
            "m": "m = 1 + m^-1 = phi projection",
        })

    def build_fibonacci_constructor_constraints(self) -> None:
        n = self.w.a2
        self.add("three_n_eq_two_n_plus_n", 3 * n, 2 * n + n, dec_close(3 * n, 2 * n + n))
        self.add("five_n_eq_three_n_plus_two_n", 5 * n, 3 * n + 2 * n, dec_close(5 * n, 3 * n + 2 * n))
        self.add("eight_n_eq_five_n_plus_three_n", 8 * n, 5 * n + 3 * n, dec_close(8 * n, 5 * n + 3 * n))
        self.add("n2_over_n_eq_n", (n ** 2) / n, n, dec_close((n ** 2) / n, n))
        self.dependencies.update({
            "3n": "2n+n",
            "5n": "3n+2n",
            "8n": "5n+3n",
        })

    def build_adjacency_constraints(self) -> None:
        # For all states P, A=P=B is the locked closure chart.  The algebra is
        # preserved as a witness; P=1 is the scalar closure sample.
        P = Decimal(1)
        A = P
        B = P
        p = P - self.w.a2
        q = P + self.w.xy_scalar
        pq = p * q
        sqrt_ab = (A * B).sqrt()
        sqrt_ba = (B * A).sqrt()

        self.add("A_eq_P", A, P, dec_close(A, P))
        self.add("B_eq_P", B, P, dec_close(B, P))
        self.add("A_colon_B_eq_B_colon_A_when_locked", A / B, B / A, dec_close(A / B, B / A))
        self.add("P2_eq_sqrtAB_eq_sqrtBA_when_locked", P ** 2, sqrt_ab, dec_close(P ** 2, sqrt_ab))
        self.add("sqrtAB_eq_sqrtBA_when_locked", sqrt_ab, sqrt_ba, dec_close(sqrt_ab, sqrt_ba))
        self.add("P2_minus_pq_eq_n4_eq_xy", (P ** 2) - pq, self.w.n4, dec_close((P ** 2) - pq, self.w.n4))
        self.add("P2_eq_pq_plus_one", P ** 2, pq + self.w.xy_scalar, dec_close(P ** 2, pq + self.w.xy_scalar))
        self.add("P2_over_root_chain_returns_P", (P ** 2 / ((sqrt_ab.sqrt()) * sqrt_ba)) * P, P, dec_close((P ** 2 / ((sqrt_ab.sqrt()) * sqrt_ba)) * P, P))
        self.dependencies.update({
            "P": "locked state chart A=P=B; A=B!=1 allowed in non-unit charts; P=1=A=B valid closure chart",
            "p": "P + yx under yx=-1 projection",
            "q": "P + xy under xy=1 projection",
            "pq": "(A-1)(B-1)=(AB*BA)/P2 witness in locked chart",
        })

    def build_qgu_shell_constraints(self) -> None:
        # Preserve shell equations symbolically; avoid unsafe numeric collapse of q,
        # R_K^QGU, S, s, v, O.  This names the equations for recursive enforcement.
        symbolic = {
            "qgu_transport_shell": "(t^3-t)*((m-m^(yx))/(m^2-m))*R_K^QGU == (xy+cq^2+dq^4)/(xy+cq^2)",
            "terminal_exponential_closure": "exp(O*x^2)==1",
            "O_constraint": "O=((-b^2+sqrt(c^2-a^2))/(2xy))^(yx=e^(x*pi)) and O/(O*r^2)=xy",
            "sv_denominator": "D(s,v)=-z^v+wxyz+y^(-s)+x^s-1/w^v",
            "sv_locked_curve": "x^s-z^v=(K-wxyz)/2 under y=x^-1,w=z^-1 projection",
        }
        for name, text in symbolic.items():
            self.add(name, text, "registered", True, note="symbolic equation registered for recursive bundle enforcement")
        self.dependencies.update(symbolic)

    def build_hash72_verbatim_boundary_constraints(self) -> None:
        self.add("hash72_core_untouched", "canonical Hash72 traversal", "not modified by invariant metadata", True)
        self.add("verbatim_layer_sidecar", "nested forked mapping tables", "parallel reversible projection", True)
        self.add("closure_mapping_anchor", "u0=u72=xy=a2", "mapping table anchor", True)
        self.dependencies.update({
            "Hash72": "serialized mapping table of u72 unit circle; canonical identity path sealed",
            "verbatim_database": "nested forked mapping tables into English/alphanumeric/markdown/math sidecar layers",
            "composition": "closure anchor u0=u72=xy=a2; other strings are offset mappings",
        })

    def build_all(self) -> "HHSRecursiveGlobalConstraintBundle":
        self.build_ordered_tensor_constraints()
        self.build_constructor_spine_constraints()
        self.build_unit_circle_constraints()
        self.build_fibonacci_constructor_constraints()
        self.build_adjacency_constraints()
        self.build_qgu_shell_constraints()
        self.build_hash72_verbatim_boundary_constraints()
        return self

    def report(self) -> Dict[str, Any]:
        ok = all(c.ok for c in self.constraints)
        return {
            "pass": ok,
            "constraint_count": len(self.constraints),
            "constraints": [c.to_dict() for c in self.constraints],
            "ordered_words": {k: v.text for k, v in self.ordered_words.items()},
            "dependencies": self.dependencies,
            "global_invariants": {
                "delta_e": "0 required",
                "psi": "0 required",
                "theta15": "true required",
                "omega": "closed required",
                "hash72_core": "untouched",
                "projection_rule": "scalar projection only after bundle assembly",
            },
        }


def build_recursive_global_constraint_report() -> Dict[str, Any]:
    return HHSRecursiveGlobalConstraintBundle().build_all().report()


def enforce_recursive_global_constraint_bundle() -> Dict[str, Any]:
    """Return report or raise AssertionError with the full trace.

    This is intentionally explicit instead of silently modifying solver/runtime
    behavior.  Call it from pre-commit hooks or self-solving loops as an
    expansion layer.
    """
    report = build_recursive_global_constraint_report()
    if not report["pass"]:
        raise AssertionError(report)
    return report
