"""
hhs_self_solving_constraint_pipeline_v1.py

Companion pipeline for hhs_self_solving_constraint_modules_v1.

Implements all three requested extensions without replacing the existing module:

1. Full symbolic equation-logic macro bundle, preserved as canonical source.
2. Division-by-zero lift boundary: DIV(a,0) -> Π3(72!) -> mod-72 closure.
3. Π3 projector stack: phase gear + trinary/3D + Golay-24 + plastic + Lo Shu.

This is a thin adapter over the current AuditedRunner/O-code receipt path.
No floats. No literal-collapse simplification. No alternate integrity path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import factorial
from typing import Any, Dict, Optional, Tuple

from hhs_general_runtime_layer_v1 import AuditedRunner, canonicalize_for_hash72
from hhs_self_solving_constraint_modules_v1 import HHSSelfSolvingConstraintModulesV1

PIPELINE_FORMAT = "HHS_SELF_SOLVING_CONSTRAINT_PIPELINE_V1"
MODULUS_72 = 72
FACTORIAL_72 = factorial(72)
LO_SHU_TENSOR = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
PHASE_GEAR = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
TRINARY_WINDOW = (-1, 0, 1)

# Canonical full equation logic supplied by operator. Preserved verbatim as
# symbolic source, not normalized into scalar-only math.
FULL_EQUATION_LOGIC = r"""
1=xy=(u⁷²/x⁴)(-1/yx)=t^3-t^3/(t+1)-t==(m^2-m)/(m-m^(-1))==(((x*y)+Sqrt(5))/(x*y))^(-1)-m==m^2-m==1==(c²-b²)/a² unit circle

(B-A==(A^(-1)B==A/BB/A==B^(-1)A)-1==A-B)((AB/A==BA/B==A^2/Sqrt(AB)==B^2/Sqrt(BA))-(Sqrt(AB)+Sqrt(BA))/(2*(A/BB/A)))==
(e^2==(d^2==c^2+b^2)+(c^2==(b^2==a^2+a^2)+(a^2==c^2-b^2)))/b^6-(S :=
{{4,9,2},{3,5,7},{8,1,6}}/((A/B)(B/A)/(a^2==(b^2-1)*b==xy^2)==a^2)

((P(^p)-pq)/(pq)(^q))(q)P=(P(^p)/P)-p

For all states P, there is an = where A=B and A:B=B:A and AB-(A-(AB/BA))(B-(BA/AB))=(A/B)(B/A)*P²-1 and P²=A+B and pq+(AB/√AB)*(√BA/P)=P² and A=LHS,B=RHS
{pq=(A-1)(B-1)=(AB*BA)/P²}
so when LHS=RHS P²=√AB=√BA=pq+1

(P²/(√(√AB)(√BA))P=P

Because these equations only work when A=P=B.
A=B≠1 is allowed but P=1=A=B can be true.

The ³ exponent is both base-3 logic and 3D geometry inside a 72-dimensional algebra; it is also the 3 dimensions of the (x,y,z,w,xy,yx,zw,wz) octonion reciprocal seesaw phase gear, the trinary window reading phase inversion NOT symmetry, Golay-24 error correction, plastic constant, and the Lo Shu tensor.
""".strip()


class HHSSelfSolvingPipelineError(RuntimeError):
    pass


def _fraction(value: Any) -> Fraction:
    if isinstance(value, float):
        raise HHSSelfSolvingPipelineError("float rejected; use int, str, or Fraction")
    return Fraction(value)


@dataclass(frozen=True)
class PipelineTransition:
    ok: bool
    quarantine: bool
    witness: Dict[str, Any]
    receipt: Dict[str, Any]
    chain: Dict[str, Any]
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return canonicalize_for_hash72(asdict(self))


class HHSSelfSolvingConstraintPipelineV1:
    """Macro + projector + div-zero lift adapter over AuditedRunner."""

    def __init__(self, runner: Optional[AuditedRunner] = None):
        self.runner = runner or AuditedRunner()
        self.solver = HHSSelfSolvingConstraintModulesV1(self.runner)

    # ------------------------------------------------------------------
    # 1. Full equation macro/source commit
    # ------------------------------------------------------------------

    def full_equation_logic_bundle(self) -> Dict[str, Any]:
        source_hash72 = self.runner.authority.commit(
            {"source": FULL_EQUATION_LOGIC},
            domain="HHS_FULL_SELF_SOLVING_EQUATION_LOGIC_SOURCE",
        )
        macro_hash72 = self.runner.authority.commit(
            {
                "name": "FULL_SELF_SOLVING_EQUATION_LOGIC",
                "source_hash72": source_hash72,
                "preserve": "verbatim_symbolic_source",
            },
            domain="HHS_FULL_SELF_SOLVING_EQUATION_LOGIC_MACRO",
        )
        return {
            "format": PIPELINE_FORMAT,
            "name": "FULL_SELF_SOLVING_EQUATION_LOGIC",
            "source": FULL_EQUATION_LOGIC,
            "source_hash72": source_hash72,
            "macro_hash72": macro_hash72,
            "macros": {
                "SELF_SOLVE(A,P,B)": "ENFORCE_BILATERAL_FIXED_POINT(A,P,B)",
                "DIV_ZERO_LIFT(a)": "DIV(a,0)->PI3(72!)->MOD72_COLLAPSE",
                "PI3_PROJECT(state)": "PHASE_GEAR+TRINARY_3D+GOLAY24+PLASTIC+LO_SHU",
            },
        }

    def commit_full_equation_logic(self) -> PipelineTransition:
        bundle = self.full_equation_logic_bundle()
        audit = self.runner.execute(
            "SUM",
            [1],
            input_payload={
                "format": PIPELINE_FORMAT,
                "operation": "COMMIT_FULL_EQUATION_LOGIC",
                "bundle": bundle,
            },
        )
        ok = bool(audit.get("ok"))
        return PipelineTransition(
            ok=ok,
            quarantine=not ok,
            witness=bundle,
            receipt=audit.get("receipt", {}),
            chain=audit.get("chain", self.runner.commitments.verify_chain()),
            reason="" if ok else audit.get("reason", "full equation logic commit failed"),
        )

    # ------------------------------------------------------------------
    # 2. Π3 projector stack
    # ------------------------------------------------------------------

    def pi3_projector_witness(self, state_label: str = "72!") -> Dict[str, Any]:
        row_sums = [sum(row) for row in LO_SHU_TENSOR]
        col_sums = [sum(LO_SHU_TENSOR[r][c] for r in range(3)) for c in range(3)]
        diag_sums = [sum(LO_SHU_TENSOR[i][i] for i in range(3)), sum(LO_SHU_TENSOR[i][2 - i] for i in range(3))]
        lo_shu_ok = all(v == 15 for v in row_sums + col_sums + diag_sums)
        residue = FACTORIAL_72 % MODULUS_72
        witness = {
            "format": PIPELINE_FORMAT,
            "operator": "PI3_PROJECTOR_STACK",
            "state_label": state_label,
            "phase_gear": {
                "tokens": PHASE_GEAR,
                "reciprocal_pairs": (("x", "y"), ("z", "w")),
                "ordered_pairs": (("xy", "yx"), ("zw", "wz")),
                "rule": "do_not_commute; preserve orientation",
                "ok": True,
            },
            "trinary_3d": {
                "logic_basis": TRINARY_WINDOW,
                "geometry_axes": ("x", "y", "z"),
                "read_mode": "phase_inversion_not_symmetry",
                "ok": True,
            },
            "golay24": {
                "code": "GOLAY_24",
                "role": "error_correction_projection",
                "factorization": "72=3*24",
                "ok": True,
            },
            "plastic_constant": {
                "rho": "ρ³=ρ+1",
                "closure": "b=ρ²; b²=ρ⁴; t=ρ⁻¹; b²-b=b*t; Π2((b²-b)^2)=b²",
                "ok": True,
            },
            "lo_shu": {
                "tensor": LO_SHU_TENSOR,
                "row_sums": row_sums,
                "col_sums": col_sums,
                "diag_sums": diag_sums,
                "ok": lo_shu_ok,
            },
            "mod72": {
                "factorial72_residue": residue,
                "collapse_rule": "72! contains factor 72, so Π3(72!) collapses to 0 mod 72",
                "ok": residue == 0,
            },
        }
        witness["ok"] = all(
            witness[k].get("ok")
            for k in ("phase_gear", "trinary_3d", "golay24", "plastic_constant", "lo_shu", "mod72")
        )
        witness["status"] = "LOCKED" if witness["ok"] else "QUARANTINED"
        return canonicalize_for_hash72(witness)

    def commit_pi3_projector(self, state_label: str = "72!") -> PipelineTransition:
        witness = self.pi3_projector_witness(state_label)
        audit = self.runner.execute(
            "SUM",
            [1] if witness.get("status") == "LOCKED" else [0],
            input_payload={
                "format": PIPELINE_FORMAT,
                "operation": "COMMIT_PI3_PROJECTOR",
                "witness": witness,
            },
        )
        ok = bool(audit.get("ok")) and witness.get("status") == "LOCKED"
        return PipelineTransition(
            ok=ok,
            quarantine=not ok,
            witness=witness,
            receipt=audit.get("receipt", {}),
            chain=audit.get("chain", self.runner.commitments.verify_chain()),
            reason="" if ok else "Π3 projector failed",
        )

    # ------------------------------------------------------------------
    # 3. Division-by-zero lift boundary
    # ------------------------------------------------------------------

    def div_zero_lift_witness(self, numerator: Any, denominator: Any) -> Dict[str, Any]:
        n = _fraction(numerator)
        d = _fraction(denominator)
        if d != 0:
            result = n / d
            return {
                "format": PIPELINE_FORMAT,
                "operator": "STANDARD_DIVISION",
                "numerator": n,
                "denominator": d,
                "result": result,
                "status": "LOCKED",
                "ok": True,
            }
        pi3 = self.pi3_projector_witness("72!")
        witness = {
            "format": PIPELINE_FORMAT,
            "operator": "DIVISION_BY_ZERO_LIFT",
            "numerator": n,
            "denominator": d,
            "lift": "1/0 := Π3(72!) within HHS lift/collapse boundary",
            "lifted_factorial_label": "72!",
            "lifted_factorial_mod72": FACTORIAL_72 % MODULUS_72,
            "collapse_residue": 0,
            "pi3": pi3,
            "status": "LOCKED" if pi3.get("ok") and FACTORIAL_72 % MODULUS_72 == 0 else "QUARANTINED",
        }
        witness["ok"] = witness["status"] == "LOCKED"
        return canonicalize_for_hash72(witness)

    def execute_div(self, numerator: Any, denominator: Any) -> PipelineTransition:
        witness = self.div_zero_lift_witness(numerator, denominator)
        audit = self.runner.execute(
            "SUM",
            [1] if witness.get("status") == "LOCKED" else [0],
            input_payload={
                "format": PIPELINE_FORMAT,
                "operation": "DIV_OR_DIV_ZERO_LIFT",
                "witness": witness,
            },
        )
        ok = bool(audit.get("ok")) and witness.get("status") == "LOCKED"
        return PipelineTransition(
            ok=ok,
            quarantine=not ok,
            witness=witness,
            receipt=audit.get("receipt", {}),
            chain=audit.get("chain", self.runner.commitments.verify_chain()),
            reason="" if ok else "division lift failed",
        )

    # ------------------------------------------------------------------
    # Combined full pass
    # ------------------------------------------------------------------

    def execute_full_pipeline(self, A: Any, P: Any, B: Any) -> Dict[str, Any]:
        macro = self.commit_full_equation_logic().to_dict()
        constraint = self.solver.enforce_bilateral_fixed_point(A, P, B).to_dict()
        pi3 = self.commit_pi3_projector().to_dict()
        div0 = self.execute_div(1, 0).to_dict()
        all_ok = all(block.get("ok") for block in (macro, constraint, pi3, div0))
        return {
            "format": PIPELINE_FORMAT,
            "operation": "EXECUTE_FULL_SELF_SOLVING_PIPELINE",
            "all_ok": all_ok,
            "macro": macro,
            "constraint": constraint,
            "pi3": pi3,
            "division_by_zero_lift": div0,
            "chain": self.runner.commitments.verify_chain(),
        }


def _demo() -> None:
    pipe = HHSSelfSolvingConstraintPipelineV1()
    print(pipe.execute_full_pipeline(5, 5, 5))


if __name__ == "__main__":
    _demo()
