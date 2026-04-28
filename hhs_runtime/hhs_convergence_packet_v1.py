from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from hhs_runtime.hhs_symbolic_quantum_algebra_v1 import build_algebra_witness
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


@dataclass
class ConvergencePacket:
    source_expression: str
    items: List[Dict[str, Any]]
    influences: List[Dict[str, Any]]
    invariants: Dict[str, Any]
    packet_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_convergence_packet(expression: str, items: List[Dict[str, Any]], influences: List[Dict[str, Any]]) -> ConvergencePacket:
    algebra = build_algebra_witness()

    invariants = algebra.invariants.copy()

    payload = {
        "expression": expression,
        "items": items,
        "influences": influences,
        "invariants": invariants,
    }

    h = hash72_digest(("hhs_convergence_packet_v1", payload), width=24)

    return ConvergencePacket(
        source_expression=expression,
        items=items,
        influences=influences,
        invariants=invariants,
        packet_hash72=h,
    )
