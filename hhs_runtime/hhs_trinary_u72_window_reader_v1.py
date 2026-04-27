"""
HHS Trinary u72 Holographic Window Reader v1
============================================

Reads trinary (previous, self, next) windows across the u^72 modular
holographic ring.

Canonical source identity
-------------------------

{Mod((List((60*x),(40*y),(100*xy))+List((100*xy),(60*x),(40*y)))/(I*u^72)*-((List((60*x),(40*y),(100*xy))+List((100*xy),(60*x),(40*y)))/((I^2*x)*y)),u^71)}
-
{{Mod(I*-1*(100*xy+60*x)^2/(u^72*x*y),u^71),
  Mod(I*-1*(40*y+60*x)^2/(u^72*x*y),u^71),
  Mod(I*-1*(40*y+100*xy)^2/(u^72*x*y),u^71)}}
==
(x+y)-u^71=xy

Interpretation
--------------
The ring is read through three ordered windows:

    previous = 100*xy
    self     = 60*x
    next     = 40*y

or rotated as:

    List(60*x, 40*y, 100*xy) + List(100*xy, 60*x, 40*y)

The reader preserves symbolic carrier identity and does not commute xy/yx.
It emits deterministic symbolic receipts rather than floating numeric collapse.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


U72 = "u^72"
U71 = "u^71"
CARRIERS = ("x", "y", "xy")
BASE_WINDOW = (("60", "x"), ("40", "y"), ("100", "xy"))
ROTATED_WINDOW = (("100", "xy"), ("60", "x"), ("40", "y"))


class WindowStatus(str, Enum):
    LOCKED = "LOCKED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class TrinaryWindowCell:
    role: str
    coefficient: str
    carrier: str
    expression: str
    phase_index: int
    cell_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TrinaryWindowRead:
    window_index: int
    previous: TrinaryWindowCell
    self_cell: TrinaryWindowCell
    next: TrinaryWindowCell
    summed_vector: List[str]
    mod_vector: List[str]
    comparison_vector: List[str]
    closure_identity: str
    status: WindowStatus
    read_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["self"] = data.pop("self_cell")
        return data


@dataclass(frozen=True)
class TrinaryRingReadReceipt:
    seed_hash72: str
    reads: List[TrinaryWindowRead]
    aggregate_hash72: str
    status: WindowStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hash72": self.seed_hash72,
            "reads": [r.to_dict() for r in self.reads],
            "aggregate_hash72": self.aggregate_hash72,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _phase_index(seed_hash72: str, window_index: int, role: str, carrier: str) -> int:
    acc = 0
    for ch in f"{seed_hash72}:{window_index}:{role}:{carrier}":
        acc = (acc * 131 + ord(ch)) % 72
    return acc


def _cell(seed_hash72: str, window_index: int, role: str, coeff: str, carrier: str) -> TrinaryWindowCell:
    expr = f"{coeff}*{carrier}"
    phase = _phase_index(seed_hash72, window_index, role, carrier)
    h = hash72_digest(("trinary_window_cell_v1", seed_hash72, window_index, role, coeff, carrier, expr, phase), width=24)
    return TrinaryWindowCell(role, coeff, carrier, expr, phase, h)


def _summed_vector() -> List[str]:
    return [
        "60*x + 100*xy",
        "40*y + 60*x",
        "100*xy + 40*y",
    ]


def _mod_vector(summed: Sequence[str]) -> List[str]:
    return [f"Mod(({term})/(I*{U72}) * -(({term})/((I^2*x)*y)), {U71})" for term in summed]


def _comparison_vector() -> List[str]:
    return [
        f"Mod(I*-1*(100*xy+60*x)^2/({U72}*x*y), {U71})",
        f"Mod(I*-1*(40*y+60*x)^2/({U72}*x*y), {U71})",
        f"Mod(I*-1*(40*y+100*xy)^2/({U72}*x*y), {U71})",
    ]


def read_trinary_window(seed: str, window_index: int = 0) -> TrinaryWindowRead:
    seed_hash = hash72_digest(("trinary_u72_window_seed_v1", seed), width=24)
    rotated = list(ROTATED_WINDOW)
    # previous/self/next read uses rotated identity order: 100xy, 60x, 40y.
    previous = _cell(seed_hash, window_index, "previous", rotated[0][0], rotated[0][1])
    self_cell = _cell(seed_hash, window_index, "self", rotated[1][0], rotated[1][1])
    next_cell = _cell(seed_hash, window_index, "next", rotated[2][0], rotated[2][1])
    summed = _summed_vector()
    mod_vector = _mod_vector(summed)
    comparison = _comparison_vector()
    closure = f"({mod_vector}) - ({comparison}) == (x+y)-{U71}=xy"
    carrier_ok = {previous.carrier, self_cell.carrier, next_cell.carrier} == set(CARRIERS)
    phase_ok = all(0 <= c.phase_index < 72 for c in [previous, self_cell, next_cell])
    status = WindowStatus.LOCKED if carrier_ok and phase_ok else WindowStatus.QUARANTINED
    h = hash72_digest(("trinary_u72_window_read_v1", seed_hash, window_index, previous.to_dict(), self_cell.to_dict(), next_cell.to_dict(), summed, mod_vector, comparison, closure, status.value), width=24)
    return TrinaryWindowRead(window_index, previous, self_cell, next_cell, summed, mod_vector, comparison, closure, status, h)


def read_trinary_ring(seed: str, *, windows: int = 72) -> TrinaryRingReadReceipt:
    windows = max(1, int(windows))
    seed_hash = hash72_digest(("trinary_u72_ring_seed_v1", seed, windows), width=24)
    reads = [read_trinary_window(seed_hash, i) for i in range(windows)]
    aggregate = hash72_digest(("trinary_u72_ring_aggregate_v1", seed_hash, [r.read_hash72 for r in reads]), width=24)
    status = WindowStatus.LOCKED if all(r.status == WindowStatus.LOCKED for r in reads) else WindowStatus.QUARANTINED
    receipt = hash72_digest(("trinary_u72_ring_receipt_v1", aggregate, status.value, windows), width=24)
    return TrinaryRingReadReceipt(seed_hash, reads, aggregate, status, receipt)


def trinary_read_to_training_feedback(read: TrinaryWindowRead) -> Dict[str, Any]:
    return {
        "summary_hash72": read.read_hash72,
        "phases": [read.previous.phase_index, read.self_cell.phase_index, read.next.phase_index],
        "carrier": "xy",
        "status": "STAGED" if read.status == WindowStatus.LOCKED else "QUARANTINED",
        "score": 96 if read.status == WindowStatus.LOCKED else 0,
        "operator_kind": "TRINARY_U72_WINDOW_READ",
        "symbolic_density": len(read.mod_vector) + len(read.comparison_vector),
    }


def main() -> None:
    print(json.dumps(read_trinary_ring("HHS_TRINARY_WINDOW", windows=3).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
