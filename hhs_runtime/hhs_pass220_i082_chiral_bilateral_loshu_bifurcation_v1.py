"""Pass 220 I082: ordered chiral/bilateral polynomial Lo Shu bifurcation.

ADDITIVE typed exact projection and existing I070/I071 phase gear binding.
No scalarization of HHS source tensor variables, no arbitrary rewrite of
equality chains, reciprocal operator divisions or -List validation masks.
The scalar projection has no VM81/Hash72/Hash216 authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from typing import Any

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import LO_SHU
from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    PHASE_BASIS, phase_gear_invariants,
)

SCHEMA = "HHS_PASS_220_I082_CHIRAL_BILATERAL_LO_SHU_BIFURCATION_V1"
PROFILE = "I082-EXACT-POLYNOMIAL-LO-SHU-PROJECTION-ONLY-v1"
ROOT_SEED = "179971.179971"
BASELINE_GATE = "1.001"
SOURCE_EQUATION = """List((u^72==xy)/List(List(x==-y,x+y==0,xy,y==a^2/x),List(z==-w,z+w==0,zw,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==xy+zw,c^2==a^2+b^2)/((xy+zw)/b^2==a^2+x+y-z-w)),-List(1==zw,1==xy,6==b^2c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))==xA==-yB*(List(List(List(x==-y,x+y==0,xy,y==a^2/x),List(z==-w,z+w==0,zw,w==a^2/w),List(c^2-b^2-a^2,a^2==c^2-b^2,b^2==c^2-a^2==xy+zw,c^2==a^2+b^2)/((xy+zw)/b^2==a^2+x+y-z-w)),-List(1==zw,1==xy,6==b^2c^2==b^2+c^2+a^2,(-(e^2==c^2+d^2==b^6==8))))/(u^36==(yxwz)/a^2))"""
FINAL_LO_SHU_SOURCE = """((b⁴,P⁴=AB=c⁴,b²=c²-a²),(c²=a²+b²,d²=b²+c²,((b⁶-a²)(c²+b⁴))/(d²+b²)),(e²=b⁶=c²+d²,a²=(xy+zw)/(c²-a²),b²c²=a²+b²+c²))"""
CANONICAL_VALUES = {
    "a²": 1, "b²": 2, "c²": 3, "d²": 5, "e²": 8,
    "xy": 1, "zw": 1,
}

# The nine source expressions are ordered by explicit Lo Shu address.
# Numeric equality is a projection only, NEVER native object identity.
CELL_EXPRESSIONS = (
    ("b⁴", "P⁴=AB=c⁴", "b²=c²-a²"),
    ("c²=a²+b²", "d²=b²+c²", "((b⁶-a²)(c²+b⁴))/(d²+b²)"),
    ("e²=b⁶=c²+d²", "a²=(xy+zw)/(c²-a²)", "b²c²=a²+b²+c²"),
)
MASK_SOURCE_ORDER = (
    "1==zw",
    "1==xy",
    "6==b²c²==b²+c²+a²",
    "-(e²==c²+d²==b⁶==8)",
)
NATIVE_OPERATOR_OBLIGATIONS = (
    "xA==-yB:typed-ordered-equality",
    "A/B!=B/A:directional-native-division",
    "P⁴=AB=c⁴:operator-product-provenance",
    "u^72==xy:72-state-phase-torus",
    "u^36==(yxwz)/a²:ordered-reciprocal-half-turn",
    "-List:typed-negative-validation-mask",
    "x==-y and xy==1:phase-specific-inverse",
    "z==-w and zw==1 and w==a²/w:typed-cell-phase-consistency",
    "Δe==0:full-nested-evaluation-and-closure",
)


class I082BifurcationError(ValueError):
    pass


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise I082BifurcationError("exact rational required: no floats")
    return Fraction(value)


def _fr(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class QuadraticSurd3:
    """Exact scalar projection a + b*sqrt(3), not a native tensor symbol."""
    rational: Fraction
    sqrt3: Fraction

    def __post_init__(self) -> None:
        object.__setattr__(self, "rational", _fraction(self.rational))
        object.__setattr__(self, "sqrt3", _fraction(self.sqrt3))

    def __add__(self, other: "QuadraticSurd3") -> "QuadraticSurd3":
        return QuadraticSurd3(self.rational + other.rational, self.sqrt3 + other.sqrt3)

    def __neg__(self) -> "QuadraticSurd3":
        return QuadraticSurd3(-self.rational, -self.sqrt3)

    def __sub__(self, other: "QuadraticSurd3") -> "QuadraticSurd3":
        return self + -other

    def __mul__(self, other: "QuadraticSurd3") -> "QuadraticSurd3":
        return QuadraticSurd3(
            self.rational * other.rational + 3 * self.sqrt3 * other.sqrt3,
            self.rational * other.sqrt3 + self.sqrt3 * other.rational,
        )

    def inverse(self) -> "QuadraticSurd3":
        denominator = self.rational**2 - 3 * self.sqrt3**2
        if denominator == 0:
            raise I082BifurcationError("noninvertible exact quadratic surd")
        return QuadraticSurd3(
            self.rational / denominator,
            -self.sqrt3 / denominator,
        )

    def __truediv__(self, other: "QuadraticSurd3") -> "QuadraticSurd3":
        return self * other.inverse()

    def to_dict(self) -> dict[str, dict[str, int]]:
        return {"rational": _fr(self.rational), "sqrt3": _fr(self.sqrt3)}


def scalar_vertices() -> tuple[tuple[Fraction, ...], ...]:
    """Only exact rational projection of original nine positional formulas."""
    r = {name: _fraction(value) for name, value in CANONICAL_VALUES.items()}
    a, b, c, d, e = (r[x] for x in ("a²", "b²", "c²", "d²", "e²"))
    xy, zw = r["xy"], r["zw"]
    # Ordered expressions follow CELL_EXPRESSIONS one-to-one.
    values = (
        (b**2, c**2, c - a),
        (a + b, b + c, ((b**3 - a) * (c + b**2)) / (d + b)),
        (c + d, (xy + zw) / (c - a), b * c),
    )
    if values != tuple(tuple(Fraction(v) for v in row) for row in LO_SHU):
        raise I082BifurcationError("exact polynomial root projection/Lo Shu address mismatch")
    if e != b**3 or e != c + d or c != a + b or b*c != a+b+c:
        raise I082BifurcationError("inherited powers or additive roots disagree")
    return values


def positive_geometric_c_root() -> QuadraticSurd3:
    """Canonical c=+sqrt(a²+b²)=+sqrt(3), with provenance kept in source.

    This is the explicit exact quadratic-surd PROJECTION of the typed
    geometric root c, not a new free scalar or a native tensor replacement.
    """
    a2, b2, c2 = (CANONICAL_VALUES[key] for key in ("a²", "b²", "c²"))
    c_root = QuadraticSurd3(0, 1)
    if c2 != a2 + b2 or c_root*c_root != QuadraticSurd3(c2, 0):
        raise I082BifurcationError("canonical positive c root does not square to a²+b²")
    return c_root


def bifurcation_branches() -> tuple[dict[str, Any], ...]:
    """Four signed P=±c branches with c=+sqrt(a²+b²)=+sqrt(3)."""
    two, one, zero = QuadraticSurd3(2, 0), QuadraticSurd3(1, 0), QuadraticSurd3(0, 0)
    c_root = positive_geometric_c_root()
    records: list[dict[str, Any]] = []
    for sign_p in (1, -1):
        P = c_root if sign_p == 1 else -c_root
        for sign_delta in (1, -1):
            D = QuadraticSurd3(2*sign_delta, 0)
            S = P * D
            p = (S-D) / two
            q = (S+D) / two
            if not (
                p*q == two
                and (p+q) / (P*(q-p)) == one
                and P*P == QuadraticSurd3(3, 0)
                and P*P*P*P == QuadraticSurd3(9, 0)
                and (P*P-p*q) == one
            ):
                raise I082BifurcationError("exact bifurcation branch not closed")
            records.append({
                "P_sign": sign_p, "q_minus_p_sign": sign_delta,
                "P_relative_to_c": "P=c" if sign_p == 1 else "P=-c",
                "canonical_geometric_c": c_root.to_dict(),
                "P": P.to_dict(), "p": p.to_dict(), "q": q.to_dict(),
                "pq": (p*q).to_dict(),
                "P2_minus_pq": (P*P-p*q).to_dict(),
                "phase_ratio": ((p+q)/(P*(q-p))).to_dict(),
                "branch_scoped": True,
            })
    assert zero != one
    return tuple(records)


def original_typed_topology() -> dict[str, Any]:
    """Source-faithful envelope. Opaque native operators are NEVER evaluated."""
    return {
        "source_equation": SOURCE_EQUATION,
        "source_equation_sha256": sha256(SOURCE_EQUATION.encode("utf-8")).hexdigest(),
        "final_three_tuple_source": FINAL_LO_SHU_SOURCE,
        "original_head": "List",
        "ordered_top_equality_operands": [
            "(u^72==xy)/List(positive-ordered-constraints,-List(validation-mask))",
            "xA",
            "-yB*(List(original-ordered-constraints,-List(mask))/(u^36==(yxwz)/a^2))",
        ],
        "ordered_negative_list_mask": list(MASK_SOURCE_ORDER),
        "phase_product_channels": list(PHASE_BASIS),
        "positioned_equality_is_not_scalar_symmetric_substitution": True,
        "preserve_original_list_and_noncommutative_division": True,
        "mask_truth_values_not_evaluated_as_numbers": True,
        "native_proof_obligations": list(NATIVE_OPERATOR_OBLIGATIONS),
    }


def formalize_i082(*, hydrate_existing_phase_gear: bool = False) -> dict[str, Any]:
    """Strict exact projection + optional live existing I070/I071 Lane 5 geometry."""
    matrix = scalar_vertices()
    branches = bifurcation_branches()
    row_sum = tuple(sum(row, Fraction(0)) for row in matrix)
    column_sum = tuple(sum(matrix[i][j] for i in range(3)) for j in range(3))
    diagonal = (
        matrix[0][0] + matrix[1][1] + matrix[2][2],
        matrix[0][2] + matrix[1][1] + matrix[2][0],
    )
    if row_sum != (15, 15, 15) or column_sum != (15, 15, 15) or diagonal != (15, 15):
        raise I082BifurcationError("exact Lo Shu 15/45 closure failed")
    if sum(row_sum) != 45:
        raise I082BifurcationError("Lo Shu global scalar 45 closure failed")
    if sorted(v for row in matrix for v in row) != list(map(Fraction, range(1,10))):
        raise I082BifurcationError("Lo Shu position/magnitude bijection failed")
    gear = phase_gear_invariants()
    if gear["qudit_phase_slots"] != 72 or gear["coordinate_closure"] is not True:
        raise I082BifurcationError("inherited I071 phase-gear invariant failure")
    topology = original_typed_topology()
    root = topology["source_equation_sha256"]
    hydration: dict[str, Any] = {
        "executed": False,
        "source": "existing I070/I071 candidate geometry",
        "candidate_only": True,
    }
    if hydrate_existing_phase_gear:
        from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
            build_nucleus_qudit_surface,
        )
        surface = build_nucleus_qudit_surface(shared_root_sha256=root, nucleus_index=0)
        if len(surface) != 72:
            raise I082BifurcationError("inherited I071 hydration count mismatch")
        for position in range(9):
            subset = [item for item in surface if item.outcome == position]
            if (
                len(subset) != 8
                or any(item.lo_shu_value != int(matrix[position//3][position%3]) for item in subset)
                or any(item.vm81_cell_id != position for item in subset)
                or tuple(item.phase_symbol for item in subset) != PHASE_BASIS
            ):
                raise I082BifurcationError("I070/I071 native Lane5 phase-address binding failed")
        hydration = {
            "executed": True,
            "source": "build_nucleus_qudit_surface via I070 Lane5 VM81 candidate",
            "shared_root_sha256": root,
            "nucleus": 0, "phase_slots": len(surface),
            "ordered_phase_basis": list(PHASE_BASIS),
            "candidate_only": True,
        }
    return {
        "schema": SCHEMA, "profile": PROFILE,
        "root_metadata_seed": ROOT_SEED, "invariant_gate_metadata": BASELINE_GATE,
        "scalar_unit_invariant": _fr(Fraction(1)),
        "metadata_gate_is_not_scalar_unit": Fraction(1001,1000) != Fraction(1),
        "source_topology": topology,
        "matrix_exact": [[_fr(v) for v in row] for row in matrix],
        "cell_witnesses": [
            {
                "row": i, "column": j, "lo_shu_address": 3*i+j,
                "nucleus_vm81_address": 3*i+j,
                "source_polynomial": CELL_EXPRESSIONS[i][j],
                "projected_exact": _fr(matrix[i][j]),
                "native_tensor_identity_reduced_to_scalar": False,
            }
            for i in range(3) for j in range(3)
        ],
        "eight_outer_vertices": sorted(int(matrix[i][j]) for i in range(3) for j in range(3) if (i,j)!=(1,1)),
        "center_vertex": {"address": 4, "value": 5, "polynomial": "d²=b²+c²"},
        "row_sums": [_fr(v) for v in row_sum],
        "column_sums": [_fr(v) for v in column_sum],
        "diagonal_sums": [_fr(v) for v in diagonal],
        "sum45": True, "magic15": True,
        "P2_branch_selected": 3,
        "P4_outer_scale": 9,
        "canonical_geometric_c_relation": "c=+sqrt(a²+b²)=+sqrt(3)",
        "canonical_geometric_c_projection": positive_geometric_c_root().to_dict(),
        "c_squared_equals_a_squared_plus_b_squared": True,
        "P_squared_equals_c_squared": True,
        "positive_P_branch_equals_c": True,
        "negative_P_branch_equals_minus_c": True,
        "native_c_tensor_address_identity_preserved": True,
        "bifurcation_exact_branches": list(branches),
        "inherited_phase_gear": gear,
        "phase_gear_hydration": hydration,
        "unresolved_native_operator_obligations": list(NATIVE_OPERATOR_OBLIGATIONS),
        "commutative_scalar_diagnostic_only": {
            "source": "z==-w && zw==1 && w==a²/w && a²==1",
            "z_minus_w_and_zw_plus_one_imply_w_squared": -1,
            "w_equals_a_squared_over_w_implies_w_squared": 1,
            "ordinary_commutative_single_w_projection_consistent": False,
            "native_address_phase_resolution_required": True,
            "not_used_to_reinterpret_hhs_typed_constraints": True,
            "reciprocal_A_over_B_inequality_alone_proves_noncommutation": False,
        },
        "typed_mask_collapse_to_one_proven": False,
        "delta_e_zero_for_full_tensor_proven": False,
        "ordered_chiral_A_over_B_phase_transport_proven": False,
        "u36_half_turn_proven": False,
        "P_n_plus_1_equals_q_n_proven": False,
        "candidate_only": True,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_commit_authority": False,
        "canonical_persistence_authority": False,
    }
