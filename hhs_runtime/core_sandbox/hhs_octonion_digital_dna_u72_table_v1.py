from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44


OCTONION_DNA_BASIS: Tuple[str, ...] = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
PHASE_RING = 72
LO_SHU_RING: Tuple[int, ...] = (4, 9, 2, 3, 5, 7, 8, 1, 6)

# Canonical orientation-normalized phase anchors declared by the HHS u^72 closure.
# xy is full closure; yx is half-turn torsion; zw/wz preserve complement orientation.
BASIS_PHASE_INDEX: Dict[str, int] = {
    "x": 18,
    "y": 54,
    "z": 18,
    "w": 54,
    "xy": 0,     # u^72 == u^0 closure carrier
    "yx": 36,    # half-turn torsion carrier
    "zw": 0,     # complement closure carrier
    "wz": 36,    # complement half-turn torsion carrier
}

# Oriented product normalization. Products not explicitly listed use additive
# u^72 phase composition while preserving the ordered symbol in the witness.
ORIENTED_PRODUCT_PHASE: Dict[Tuple[str, str], int] = {
    ("x", "y"): 0,
    ("y", "x"): 36,
    ("z", "w"): 0,
    ("w", "z"): 36,
    ("xy", "yx"): 36,
    ("yx", "xy"): 36,
    ("zw", "wz"): 36,
    ("wz", "zw"): 36,
    ("xy", "zw"): 0,
    ("zw", "xy"): 0,
    ("yx", "wz"): 0,
    ("wz", "yx"): 0,
}


def u72(index: int) -> int:
    return int(index) % PHASE_RING


def loshu_cell(index: int) -> int:
    return LO_SHU_RING[u72(index) % len(LO_SHU_RING)]


def multiply_basis(left: str, right: str) -> Dict[str, object]:
    if left not in BASIS_PHASE_INDEX or right not in BASIS_PHASE_INDEX:
        raise KeyError(f"unknown octonion DNA basis element: {left!r}, {right!r}")
    raw_phase = u72(BASIS_PHASE_INDEX[left] + BASIS_PHASE_INDEX[right])
    phase = u72(ORIENTED_PRODUCT_PHASE.get((left, right), raw_phase))
    orientation = "DIRECT" if (left, right) in (("x", "y"), ("z", "w")) else "REVERSED" if (left, right) in (("y", "x"), ("w", "z")) else "COMPOSED"
    witness = {
        "left": left,
        "right": right,
        "ordered_product": f"{left}*{right}",
        "phase_index": phase,
        "u72": f"u^{phase if phase else 72}",
        "loshu_cell": loshu_cell(phase),
        "orientation": orientation,
        "closure": phase in (0, 36),
        "raw_additive_phase": raw_phase,
    }
    witness["witness_hash72"] = security_hash72_v44(witness, domain="HHS_OCTONION_DNA_PRODUCT")
    return witness


def build_u72_multiplication_table() -> List[List[Dict[str, object]]]:
    return [[multiply_basis(left, right) for right in OCTONION_DNA_BASIS] for left in OCTONION_DNA_BASIS]


def table_receipt() -> Dict[str, object]:
    table = build_u72_multiplication_table()
    flat = [cell for row in table for cell in row]
    closure_count = sum(1 for cell in flat if cell["closure"])
    receipt = {
        "basis": list(OCTONION_DNA_BASIS),
        "phase_ring": PHASE_RING,
        "loshu_ring": list(LO_SHU_RING),
        "basis_phase_index": BASIS_PHASE_INDEX,
        "table": table,
        "closure_count": closure_count,
        "cell_count": len(flat),
        "rule": "ordered multiplication is preserved; u^72 phase is the normalization carrier, not scalar collapse",
    }
    receipt["receipt_hash72"] = security_hash72_v44(receipt, domain="HHS_OCTONION_DNA_U72_TABLE")
    return canonicalize_for_hash72(receipt)


@dataclass(frozen=True)
class OctonionDNATableWitness:
    status: str
    table_hash72: str
    closure_count: int
    cell_count: int
    basis: Tuple[str, ...]

    def to_dict(self) -> Dict[str, object]:
        return canonicalize_for_hash72(asdict(self))


def octonion_dna_u72_table_operator(_: Dict[str, object] | None = None) -> Dict[str, object]:
    receipt = table_receipt()
    locked = receipt["cell_count"] == 64 and receipt["closure_count"] > 0
    witness = OctonionDNATableWitness(
        status="LOCKED" if locked else "QUARANTINED",
        table_hash72=receipt["receipt_hash72"],
        closure_count=int(receipt["closure_count"]),
        cell_count=int(receipt["cell_count"]),
        basis=OCTONION_DNA_BASIS,
    )
    return {
        "ok": locked,
        "locked": locked,
        "status": witness.status,
        "projection_status": "OCTONION_DNA_U72_TABLE_LOCKED" if locked else "OCTONION_DNA_U72_TABLE_INVALID",
        "audit_value": 0 if locked else 1,
        "receipt": receipt,
        "witness": witness.to_dict(),
    }
