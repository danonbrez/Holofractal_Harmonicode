"""
HHS Runtime Authority Gate v1
=============================

Central non-bypass guard for runtime execution.

Every automatic execution chain must be able to prove:
- Δe = 0
- Ψ = 0
- Θ15 = true
- Ω = true
- canonical algebraic seed closure holds: a²=1, b²=2, c²=3, d²=5
- Hash72 state/receipt lineage is present for committed execution

This module is intentionally deterministic and integer/rational-only. It does
not replace the C kernel, Hash72 ledger, or symbolic engine; it is the Python
runtime enforcement seam that prevents GUI/API/emulator/service paths from
bypassing kernel authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping, Optional


HASH72_LEN = 72
LO_SHU_3X3 = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
CANONICAL_SQUARES = {"a2": 1, "b2": 2, "c2": 3, "d2": 5}


class HHSAuthorityViolation(RuntimeError):
    """Raised when a runtime path violates HHS execution authority."""


@dataclass(frozen=True)
class HHSAuthorityAudit:
    ok: bool
    source: str
    delta_e: int
    psi: int
    theta15: bool
    omega: bool
    hash72_state_ok: bool
    hash72_receipt_ok: bool
    algebraic_closure: bool
    reasons: List[str]
    runtime_step: Optional[int] = None
    state_hash72: str = ""
    receipt_hash72: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _is_hash72(value: Any) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LEN


def _loshu_theta15(grid: Iterable[Iterable[int]] = LO_SHU_3X3) -> bool:
    rows = [tuple(row) for row in grid]
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        return False
    row_ok = all(sum(row) == 15 for row in rows)
    col_ok = all(sum(rows[r][c] for r in range(3)) == 15 for c in range(3))
    diag_ok = (rows[0][0] + rows[1][1] + rows[2][2] == 15) and (
        rows[0][2] + rows[1][1] + rows[2][0] == 15
    )
    return row_ok and col_ok and diag_ok


def _canonical_algebraic_closure() -> bool:
    a2 = Fraction(CANONICAL_SQUARES["a2"], 1)
    b2 = Fraction(CANONICAL_SQUARES["b2"], 1)
    c2 = Fraction(CANONICAL_SQUARES["c2"], 1)
    d2 = Fraction(CANONICAL_SQUARES["d2"], 1)

    # User-locked canonical closure:
    # ((a²+b²)² + a²)/b² = b² + c² = d²
    left = ((a2 + b2) ** 2 + a2) / b2
    middle = b2 + c2
    return left == middle == d2


def _runtime_delta_e(runtime_state: Mapping[str, Any]) -> int:
    if "entropy_delta" in runtime_state:
        return int(runtime_state.get("entropy_delta") or 0)
    return int(runtime_state.get("transport_flux") or 0)


def _runtime_psi(runtime_state: Mapping[str, Any]) -> int:
    if "semantic_drift" in runtime_state:
        return int(runtime_state.get("semantic_drift") or 0)
    return int(runtime_state.get("orientation_flux") or 0) + int(runtime_state.get("constraint_flux") or 0)


def audit_runtime_authority(
    runtime_state: Mapping[str, Any],
    *,
    source: str,
    receipt: Optional[Mapping[str, Any]] = None,
    require_receipt: bool = True,
) -> HHSAuthorityAudit:
    """Return a deterministic authority audit for a runtime transition."""

    reasons: List[str] = []
    delta_e = _runtime_delta_e(runtime_state)
    psi = _runtime_psi(runtime_state)
    theta15 = _loshu_theta15()
    algebraic_closure = _canonical_algebraic_closure()

    state_hash72 = str(runtime_state.get("state_hash72") or "")
    receipt_hash72 = str(runtime_state.get("receipt_hash72") or "")

    if receipt is not None:
        state_hash72 = str(receipt.get("state_hash72") or state_hash72)
        receipt_hash72 = str(receipt.get("receipt_hash72") or receipt_hash72)

    hash72_state_ok = _is_hash72(state_hash72)
    hash72_receipt_ok = _is_hash72(receipt_hash72)

    # Ω is closure over replay/receipt lineage for committed execution. For
    # non-mutating boot/status checks, callers may set require_receipt=False.
    omega = (hash72_state_ok and hash72_receipt_ok) if require_receipt else True

    if delta_e != 0:
        reasons.append("Δe invariant failed: entropy/transport drift is non-zero")
    if psi != 0:
        reasons.append("Ψ invariant failed: semantic/orientation/constraint drift is non-zero")
    if not theta15:
        reasons.append("Θ15 invariant failed: Lo Shu balance witness is false")
    if not algebraic_closure:
        reasons.append("Core algebraic closure failed for a²=1,b²=2,c²=3,d²=5")
    if require_receipt and not hash72_state_ok:
        reasons.append("Hash72 state lineage missing or malformed")
    if require_receipt and not hash72_receipt_ok:
        reasons.append("Hash72 receipt lineage missing or malformed")
    if not omega:
        reasons.append("Ω invariant failed: committed transition lacks receipt closure")

    ok = not reasons
    return HHSAuthorityAudit(
        ok=ok,
        source=source,
        delta_e=delta_e,
        psi=psi,
        theta15=theta15,
        omega=omega,
        hash72_state_ok=hash72_state_ok,
        hash72_receipt_ok=hash72_receipt_ok,
        algebraic_closure=algebraic_closure,
        reasons=reasons,
        runtime_step=int(runtime_state.get("step")) if runtime_state.get("step") is not None else None,
        state_hash72=state_hash72,
        receipt_hash72=receipt_hash72,
    )


def assert_runtime_authorized(
    runtime_state: Mapping[str, Any],
    *,
    source: str,
    receipt: Optional[Mapping[str, Any]] = None,
    require_receipt: bool = True,
) -> HHSAuthorityAudit:
    """Raise on authority violation; otherwise return the audit packet."""

    audit = audit_runtime_authority(
        runtime_state,
        source=source,
        receipt=receipt,
        require_receipt=require_receipt,
    )
    if not audit.ok:
        raise HHSAuthorityViolation(f"HHS authority gate blocked {source}: " + "; ".join(audit.reasons))
    return audit


def authority_gate_self_test() -> Dict[str, Any]:
    fake_hash = "H" * HASH72_LEN
    audit = assert_runtime_authorized(
        {
            "step": 1,
            "transport_flux": 0,
            "orientation_flux": 0,
            "constraint_flux": 0,
            "state_hash72": fake_hash,
            "receipt_hash72": fake_hash,
        },
        source="authority_gate_self_test",
    )
    return audit.to_dict()


if __name__ == "__main__":
    print(authority_gate_self_test())
