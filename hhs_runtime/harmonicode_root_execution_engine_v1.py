"""
HARMONICODE Root Execution Engine v1
====================================

Root Execution turns a selected Root Meta-Branch into a compact executable
HARMONICODE constraint candidate.

Pipeline:
    root phases -> equation extraction -> interpret/transform/project
    -> invariant validation -> staged execution candidate receipt

This module does not silently commit runtime state. It produces an executable
candidate whose equation has already passed the HARMONICODE frontend + solver +
projection gates. Production commit remains approval/consensus/kernel gated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.harmonicode_phase_projection_engine_v1 import interpret_transform_project


RING = 72


class RootExecutionStatus(str, Enum):
    STAGED = "STAGED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class RootEquation:
    phases: List[int]
    equation: str
    compression_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RootExecutionCandidate:
    equation: RootEquation
    projection_status: str
    phase_index: int
    projection_receipt_hash72: str
    status: RootExecutionStatus
    reason: str
    execution_candidate_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


def _mod72(value: int) -> int:
    return ((int(value) % RING) + RING) % RING


def extract_root_equation(phases: Sequence[int]) -> RootEquation:
    """Collapse a Root Meta-Branch phase path into compact HARMONICODE.

    The extracted equation preserves:
    - ordered phase traversal
    - u^72 closure
    - Theta15 witness
    - Omega closure
    - exact phase list as DNA seed
    """
    clean = [_mod72(p) for p in phases]
    if not clean:
        clean = [0]
    start = clean[0]
    end = clean[-1]
    deltas = [_mod72(clean[i + 1] - clean[i]) for i in range(len(clean) - 1)]
    delta_terms = ",".join(str(d) for d in deltas) if deltas else "0"
    phase_terms = ",".join(str(p) for p in clean)
    equation = f"""
ROOT_META_BRANCH_GATE := {{
  root_phases = List({phase_terms}),
  root_deltas = List({delta_terms}),
  P0 = {start},
  Pn = {end},
  u^72 = Ω,
  Theta15 = true,
  root_closure = Mod(P0 + Sum(root_deltas), 72) = Pn,
  root_seed = root_phases:root_deltas
}}
ROOT_META_BRANCH_GATE
""".strip()
    h = hash72_digest(("root_equation_v1", clean, deltas, equation), width=24)
    return RootEquation(clean, equation, h)


def stage_root_execution(phases: Sequence[int], *, target_layer: str = "normalized") -> Dict[str, Any]:
    equation = extract_root_equation(phases)
    projected = interpret_transform_project(equation.equation, target_layer)
    projection = projected.get("projection", {})
    receipt = projection.get("receipt", {})
    witness = projection.get("phase_witness", {})
    projection_status = str(receipt.get("status", "UNKNOWN"))
    ok = projection_status == "PROJECTED" and witness.get("u72_ok") is True and witness.get("loshu_ok") is True
    status = RootExecutionStatus.STAGED if ok else RootExecutionStatus.QUARANTINED
    reason = "Root equation staged; commit still requires approval/consensus/kernel gate." if ok else "Root equation failed projection/invariant gate."
    candidate_hash = hash72_digest(("root_execution_candidate_v1", equation.to_dict(), projection_status, witness, status.value, reason), width=24)
    candidate = RootExecutionCandidate(
        equation=equation,
        projection_status=projection_status,
        phase_index=int(witness.get("phase_index", 0) or 0),
        projection_receipt_hash72=str(receipt.get("receipt_hash72", "")),
        status=status,
        reason=reason,
        execution_candidate_hash72=candidate_hash,
    )
    return {"candidate": candidate.to_dict(), "projection": projected}


def main() -> None:
    print(json.dumps(stage_root_execution([4, 12, 20, 36]), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
