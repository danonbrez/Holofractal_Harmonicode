# hhs_runtime/python/hhs_predictive_sandbox_engine_v1.py
#
# HARMONICODE / HHS
# Predictive sandbox manifold execution layer
#
# PURPOSE:
#   - run virtual receipt-chain futures
#   - branch prediction from prior successful traces
#   - replay deterministic manifold states
#   - closure-oriented state search
#   - sandboxed adaptive learning
#
# CORE PRINCIPLE:
#   learning = replay + prediction + validation
#
# ============================================================

from __future__ import annotations

import copy
import math
import random

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ============================================================
# IMPORTS
# ============================================================

from hhs_receipt_vector_cache_v1 import (
    HHSReceiptVectorCache,
    ReceiptNode,
    hash72_distance,
)

# ============================================================
# HASH72
# ============================================================

HASH72 = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)

HASH72_INDEX = {
    c: i for i, c in enumerate(HASH72)
}

# ============================================================
# UTILITIES
# ============================================================

def wrap72(v: int) -> int:
    return v % 72


def blend_hash72(
    a: str,
    b: str,
    alpha: float,
) -> str:

    out = []

    for ca, cb in zip(a, b):

        va = HASH72_INDEX[ca]
        vb = HASH72_INDEX[cb]

        mix = int(
            round(
                (1.0 - alpha) * va
                + alpha * vb
            )
        )

        out.append(
            HASH72[wrap72(mix)]
        )

    return "".join(out)


def mutate_hash72(
    h: str,
    strength: int = 1,
) -> str:

    vals = list(h)

    for _ in range(strength):

        idx = random.randint(
            0,
            len(vals) - 1,
        )

        v = HASH72_INDEX[vals[idx]]

        delta = random.choice([
            -2,
            -1,
            1,
            2,
        ])

        vals[idx] = HASH72[
            wrap72(v + delta)
        ]

    return "".join(vals)


# ============================================================
# SANDBOX FRAME
# ============================================================

@dataclass
class SandboxFrame:

    state72: str

    receipt72: str

    witness_flags: int

    closure_score: float

    depth: int

    parent_state72: Optional[str] = None

    prediction_score: float = 0.0

    metadata: Dict = field(
        default_factory=dict
    )


# ============================================================
# SANDBOX ENGINE
# ============================================================

@dataclass
class HHSPredictiveSandboxEngine:

    cache: HHSReceiptVectorCache

    active_frames: List[SandboxFrame] = field(
        default_factory=list
    )

    completed_frames: List[SandboxFrame] = field(
        default_factory=list
    )

    sandbox_name: str = "default"

    # ========================================================
    # INITIALIZE
    # ========================================================

    def seed_from_receipt(
        self,
        state72: str,
        receipt72: str,
        witness_flags: int = 0,
    ) -> SandboxFrame:

        frame = SandboxFrame(
            state72=state72,
            receipt72=receipt72,
            witness_flags=witness_flags,
            closure_score=0.0,
            depth=0,
        )

        self.active_frames.append(frame)

        return frame

    # ========================================================
    # EXPAND
    # ========================================================

    def expand_frame(
        self,
        frame: SandboxFrame,
        top_k: int = 6,
    ) -> List[SandboxFrame]:

        predictions = self.cache.predict_next_receipts(
            frame.state72,
            top_k=top_k,
        )

        new_frames = []

        for score, node in predictions:

            blended_state = blend_hash72(
                frame.state72,
                node.state_hash72,
                0.5,
            )

            new_frame = SandboxFrame(
                state72=blended_state,
                receipt72=node.receipt_hash72,
                witness_flags=node.witness_flags,
                closure_score=node.closure_score,
                depth=frame.depth + 1,
                parent_state72=frame.state72,
                prediction_score=score,
                metadata={
                    "replay_signature":
                        node.replay_signature,
                }
            )

            new_frames.append(new_frame)

        return new_frames

    # ========================================================
    # STEP
    # ========================================================

    def step(
        self,
        expansion_width: int = 4,
    ) -> None:

        next_frames = []

        for frame in self.active_frames:

            children = self.expand_frame(
                frame,
                top_k=expansion_width,
            )

            next_frames.extend(children)

            self.completed_frames.append(frame)

        next_frames.sort(
            key=lambda f: (
                f.prediction_score
                + f.closure_score
            ),
            reverse=True,
        )

        self.active_frames = next_frames[
            :expansion_width
        ]

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        steps: int = 4,
        expansion_width: int = 4,
    ) -> None:

        for _ in range(steps):

            if not self.active_frames:
                break

            self.step(
                expansion_width=
                    expansion_width
            )

    # ========================================================
    # SEARCH
    # ========================================================

    def best_frame(
        self
    ) -> Optional[SandboxFrame]:

        if not self.active_frames:
            return None

        ranked = sorted(
            self.active_frames,
            key=lambda f: (
                f.closure_score
                + f.prediction_score
            ),
            reverse=True,
        )

        return ranked[0]

    def closure_frames(
        self,
        threshold: float = 0.8,
    ) -> List[SandboxFrame]:

        out = []

        for frame in (
            self.active_frames
            + self.completed_frames
        ):

            if frame.closure_score >= threshold:
                out.append(frame)

        return out

    # ========================================================
    # VIRTUAL MEMORY
    # ========================================================

    def build_virtual_memory_layer(
        self,
        layer_name: str,
        threshold: float = 0.7,
    ) -> List[ReceiptNode]:

        closures = self.closure_frames(
            threshold=threshold
        )

        out = []

        for frame in closures:

            nearest = self.cache.search_prediction_candidates(
                frame.state72,
                top_k=1,
            )

            if not nearest:
                continue

            node = nearest[0]

            node.sandbox_layers.add(
                layer_name
            )

            out.append(node)

        return out

    # ========================================================
    # DIVERGENCE
    # ========================================================

    def entropy_score(
        self,
        frame: SandboxFrame,
    ) -> float:

        total = 0.0

        vals = [
            HASH72_INDEX[c]
            for c in frame.state72
        ]

        for i in range(1, len(vals)):

            total += abs(
                vals[i] - vals[i - 1]
            )

        return total / len(vals)

    def stabilize_frame(
        self,
        frame: SandboxFrame,
        iterations: int = 8,
    ) -> SandboxFrame:

        best = copy.deepcopy(frame)

        best_entropy = self.entropy_score(
            best
        )

        for _ in range(iterations):

            candidate = copy.deepcopy(best)

            candidate.state72 = mutate_hash72(
                candidate.state72,
                strength=1,
            )

            e = self.entropy_score(
                candidate
            )

            if e < best_entropy:

                best = candidate
                best_entropy = e

        return best

    # ========================================================
    # EXPORT
    # ========================================================

    def export_summary(self) -> Dict:

        return {

            "sandbox_name":
                self.sandbox_name,

            "active_frames":
                len(self.active_frames),

            "completed_frames":
                len(self.completed_frames),

            "best_frame":
                (
                    self.best_frame().state72
                    if self.best_frame()
                    else None
                ),

            "closure_frames":
                len(
                    self.closure_frames()
                ),
        }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    from hhs_receipt_vector_cache_v1 import (
        HHSReceiptVectorCache,
    )

    cache = HHSReceiptVectorCache()

    PREV = (
        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW"
    )

    STATE = (
        "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUuNrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRRYbgfpznr"
    )

    RECEIPT = (
        "cVzbjxzEONoD!3(fQybgrehO>(Y3qDSBZphEI9j4Phf4s9y)qP(b<yd0F-1cBWkoo5mVdFpL"
    )

    cache.insert_receipt(
        prev72=PREV,
        state72=STATE,
        receipt72=RECEIPT,
        witness_flags=0xFFFF,
        sandbox_layer="root",
    )

    engine = HHSPredictiveSandboxEngine(
        cache=cache,
        sandbox_name="predictive_A",
    )

    engine.seed_from_receipt(
        state72=STATE,
        receipt72=RECEIPT,
        witness_flags=0xFFFF,
    )

    engine.run(
        steps=4,
        expansion_width=4,
    )

    print("\n=== SANDBOX SUMMARY ===")
    print(
        engine.export_summary()
    )

    print("\n=== BEST FRAME ===")

    best = engine.best_frame()

    if best:

        print(best.state72)
        print(best.closure_score)
        print(best.prediction_score)

    print("\n=== VIRTUAL MEMORY ===")

    mem = engine.build_virtual_memory_layer(
        "adaptive_layer",
        threshold=0.0,
    )

    print(len(mem))