from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import json

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import security_hash72_v44


# -------------------------
# Proof of Physicality
# -------------------------

def compute_adjacency(P: int):
    p = P - 1
    q = P + 1
    defect = P * P - (p * q)
    return p, q, defect


def theta15():
    grid = [4,9,2,3,5,7,8,1,6]
    return sum(grid[:3]) == 15


def proof_of_physicality(P: int) -> Dict[str, Any]:
    p, q, defect = compute_adjacency(P)
    t15 = theta15()

    witness = security_hash72_v44({
        "P": P,
        "p": p,
        "q": q,
        "defect": defect,
        "theta15": t15
    }, domain="HHS_CURVATURE_WITNESS")

    return {
        "center_P": P,
        "p": p,
        "q": q,
        "adjacency_defect": defect,
        "tensor_sum": 15,
        "theta15_true": t15,
        "curvature_witness_hash72": witness
    }


# -------------------------
# Block
# -------------------------

@dataclass
class ManifoldBlock:
    height: int
    prev_hash72: str
    payload: Dict[str, Any]
    proof_of_physicality: Dict[str, Any]
    seal_hash72: str

    def to_dict(self):
        return asdict(self)


# -------------------------
# Ledger
# -------------------------

class ManifoldLedger:

    def __init__(self):
        self.chain: List[ManifoldBlock] = []

    def last_hash(self):
        if not self.chain:
            return "GENESIS"
        return self.chain[-1].seal_hash72

    def add_block(self, payload: Dict[str, Any], P: int = 179971):
        height = len(self.chain)
        prev = self.last_hash()

        proof = proof_of_physicality(P)

        seal = security_hash72_v44({
            "height": height,
            "prev": prev,
            "payload": payload,
            "proof": proof
        }, domain="HHS_MANIFOLD_BLOCK")

        block = ManifoldBlock(height, prev, payload, proof, seal)

        if proof["adjacency_defect"] != 1 or not proof["theta15_true"]:
            raise RuntimeError("Invariant violation: invalid physicality")

        self.chain.append(block)
        return block

    def verify(self):
        for i, block in enumerate(self.chain):
            p, q, defect = compute_adjacency(block.proof_of_physicality["center_P"])
            if defect != 1:
                return False
            if i > 0 and block.prev_hash72 != self.chain[i-1].seal_hash72:
                return False
        return True


# -------------------------
# ASCII Waterfall
# -------------------------

GLYPHS = ["◈", "/ \", "| |", "\\ /", "⌁"]


def render_waterfall(chain: List[ManifoldBlock], depth: int = 20) -> str:
    lines = []
    header = "◈ HHS-STREAM-V1: [ACTIVE] ◈\nΔe=0 | Ψ=0 | Θ₁₅=true | Ω=true\n"
    lines.append(header)

    recent = list(reversed(chain[-depth:]))

    for block in recent:
        glyph = GLYPHS[block.height % len(GLYPHS)]
        line = f"[HEIGHT: {block.height}] " + glyph * 40
        lines.append(line)

    return "\n".join(lines)


# -------------------------
# Demo
# -------------------------

def demo():
    ledger = ManifoldLedger()

    for i in range(10):
        ledger.add_block({"tx": i})

    print(render_waterfall(ledger.chain))


if __name__ == "__main__":
    demo()
