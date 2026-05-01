"""
hhs_self_solving_constraint_modules_v1.py

Self-solving constraint modules for the HARMONICODE runtime.

This layer is intentionally a thin adapter over the existing kernel/runtime
receipt path. It does not create a second truth engine. It converts closed
constraint bundles into audited O-code style calls through AuditedRunner so each
state transition is Hash72 committed, replayable, and fail-closed.

Core rule
---------
The bilateral equation set is not solved by scalar simplification. It is solved
by enforcing coincidence of the equality node:

    A = P = B

A = B != 1 is allowed as a scaled local state. The unit state
A = P = B = 1 is the normalized special case, not the only legal state.

No floats are used. Radical terms are tracked as oriented branch witnesses, not
computed as floating square roots.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Optional

from hhs_general_runtime_layer_v1 import AuditedRunner, canonicalize_for_hash72


SELF_SOLVING_FORMAT = "HHS_SELF_SOLVING_CONSTRAINT_MODULES_V1"


class HHSSelfSolvingConstraintError(RuntimeError):
    """Raised for malformed constraint input before kernel audit."""


def _q(value: Any) -> Fraction:
    """Exact rational coercion boundary. Floats are rejected fail-closed."""
    if isinstance(value, float):
        raise HHSSelfSolvingConstraintError("float input rejected; use int, str, or Fraction")
    return Fraction(value)


@dataclass(frozen=True)
class BilateralConstraintWitnessV1:
    A: Fraction
    P: Fraction
    B: Fraction
    equality_lock: bool
    p_lock: bool
    unit_lock: bool
    reciprocal_lock: bool
    ordered_product_lock: bool
    radical_branch_lock: bool
    pq: Fraction
    pq_from_ordered_products: Fraction
    defect: Fraction
    scale: Fraction
    status: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return canonicalize_for_hash72(asdict(self))


@dataclass(frozen=True)
class SelfSolvingTransitionV1:
    ok: bool
    quarantine: bool
    witness: Dict[str, Any]
    receipt: Dict[str, Any]
    chain: Dict[str, Any]
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return canonicalize_for_hash72(asdict(self))


class HHSSelfSolvingConstraintModulesV1:
    """
    Constraint-enforcement adapter.

    Every public solve/enforce method produces an audited runner transition.
    The arithmetic witness is exact. Branch/radical expressions are represented
    as symbolic equality witnesses because the HHS algebra treats them as
    oriented branch locks, not scalar roots.
    """

    def __init__(self, runner: Optional[AuditedRunner] = None):
        self.runner = runner or AuditedRunner()

    # ------------------------------------------------------------------
    # Core bilateral fixed-point solver
    # ------------------------------------------------------------------

    def bilateral_witness(self, A: Any, P: Any, B: Any) -> BilateralConstraintWitnessV1:
        a = _q(A)
        p = _q(P)
        b = _q(B)

        equality_lock = a == b
        p_lock = equality_lock and p == a and p == b
        unit_lock = p_lock and a == 1

        # Reciprocals are only valid on nonzero scaled states.
        reciprocal_lock = False
        if a != 0 and b != 0:
            reciprocal_lock = (a / b == 1) and (b / a == 1)

        # Ordered product equality is permitted only after bilateral equality.
        ab = a * b
        ba = b * a
        ordered_product_lock = equality_lock and ab == ba

        # Radical witness is a branch-consistency witness, not a float sqrt.
        # Under A=P=B, the AB and BA branches are the same oriented branch.
        radical_branch_lock = p_lock and ordered_product_lock

        pq = (a - 1) * (b - 1)
        pq_from_ordered_products = Fraction(0)
        if p != 0:
            pq_from_ordered_products = (ab * ba) / (p * p)

        # defect measures distance from the self-solving coincidence state.
        defect = abs(a - b) + abs(a - p) + abs(p - b)
        scale = p

        if not equality_lock:
            status = "QUARANTINED"
            reason = "bilateral equality lock failed: A != B"
        elif not p_lock:
            status = "QUARANTINED"
            reason = "P coincidence lock failed: A = B but P differs"
        elif not reciprocal_lock:
            status = "QUARANTINED"
            reason = "reciprocal lock failed or zero denominator state"
        elif not ordered_product_lock:
            status = "QUARANTINED"
            reason = "ordered-product lock failed: AB != BA"
        elif not radical_branch_lock:
            status = "QUARANTINED"
            reason = "radical branch witness failed"
        else:
            status = "LOCKED"
            reason = "A = P = B fixed point locked"

        return BilateralConstraintWitnessV1(
            A=a,
            P=p,
            B=b,
            equality_lock=equality_lock,
            p_lock=p_lock,
            unit_lock=unit_lock,
            reciprocal_lock=reciprocal_lock,
            ordered_product_lock=ordered_product_lock,
            radical_branch_lock=radical_branch_lock,
            pq=pq,
            pq_from_ordered_products=pq_from_ordered_products,
            defect=defect,
            scale=scale,
            status=status,
            reason=reason,
        )

    def enforce_bilateral_fixed_point(self, A: Any, P: Any, B: Any) -> SelfSolvingTransitionV1:
        """
        Enforce the self-solving equality node:

            A = P = B

        This accepts scaled states such as A=P=B=5 and marks A=P=B=1 as the
        unit-normalized special case. Any non-coincident state is quarantined.
        """
        witness = self.bilateral_witness(A, P, B)
        w = witness.to_dict()
        audit = self.runner.execute(
            "SUM",
            [1] if witness.status == "LOCKED" else [0],
            input_payload={
                "format": SELF_SOLVING_FORMAT,
                "operation": "ENFORCE_BILATERAL_FIXED_POINT",
                "constraint": "A=P=B; A=B!=1 allowed; A=P=B=1 unit special case",
                "witness": w,
            },
        )

        # Runtime SUM([1]) locks the receipt path; this adapter adds the
        # constraint status so invalid constraints remain blocked even though the
        # carrier audit itself is exact.
        ok = bool(audit.get("ok")) and witness.status == "LOCKED"
        quarantine = not ok
        reason = "" if ok else witness.reason
        return SelfSolvingTransitionV1(
            ok=ok,
            quarantine=quarantine,
            witness=w,
            receipt=audit.get("receipt", {}),
            chain=audit.get("chain", self.runner.commitments.verify_chain()),
            reason=reason,
        )

    # ------------------------------------------------------------------
    # Batch/projector interface
    # ------------------------------------------------------------------

    def enforce_many(self, triples: Iterable[Iterable[Any]]) -> Dict[str, Any]:
        transitions: List[Dict[str, Any]] = []
        all_ok = True
        for triple in triples:
            values = list(triple)
            if len(values) != 3:
                transition = {
                    "ok": False,
                    "quarantine": True,
                    "reason": "triple must contain exactly A, P, B",
                    "input": canonicalize_for_hash72(values),
                }
            else:
                transition = self.enforce_bilateral_fixed_point(values[0], values[1], values[2]).to_dict()
            transitions.append(transition)
            all_ok = all_ok and bool(transition.get("ok"))
        return {
            "format": SELF_SOLVING_FORMAT,
            "operation": "ENFORCE_MANY",
            "all_ok": all_ok,
            "transitions": transitions,
            "chain": self.runner.commitments.verify_chain(),
        }

    # ------------------------------------------------------------------
    # O-code carrier interface
    # ------------------------------------------------------------------

    def o_code_call(self, op: str, *args: Any, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explicit O-code style bridge into the runtime.

        This keeps higher symbolic modules from calling unaudited Python helpers
        when they need a committed carrier transition.
        """
        return self.runner.execute(
            op,
            *args,
            input_payload={
                "format": SELF_SOLVING_FORMAT,
                "operation": "O_CODE_CALL",
                "op": op,
                "args": canonicalize_for_hash72(args),
                "payload": canonicalize_for_hash72(payload or {}),
            },
        )


def _demo() -> None:
    solver = HHSSelfSolvingConstraintModulesV1()
    print(solver.enforce_bilateral_fixed_point(5, 5, 5).to_dict())
    print(solver.enforce_bilateral_fixed_point(5, 1, 5).to_dict())


if __name__ == "__main__":
    _demo()
