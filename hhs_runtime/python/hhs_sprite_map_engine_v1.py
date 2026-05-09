# hhs_runtime/python/hhs_sprite_map_engine_v1.py
#
# HARMONICODE / HHS
# SpriteMap216 deterministic geometry engine
#
# PURPOSE:
#   Convert validated Hash72 receipt triplets into deterministic
#   executable geometry objects.
#
# INPUT:
#   PREV72
#   STATE72
#   RECEIPT72
#
# OUTPUT:
#   SpriteMap216 object
#   Deterministic geometry seed
#   Phase rings
#   Lo Shu core
#   Fusion/interactions
#   Replay-compatible structure
#
# DESIGN:
#   - deterministic
#   - replay stable
#   - no hidden randomness
#   - same receipt => same geometry
#
# ============================================================

from __future__ import annotations

import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

# ============================================================
# CONSTANTS
# ============================================================

HASH72 = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "-+*/()<>!?"
)

HASH72_INDEX = {c: i for i, c in enumerate(HASH72)}

HASH_LEN = 72
SPRITE216_LEN = 216

RECIPROCAL_PHASE_OFFSET = 36

LOSHU = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6],
]

# ============================================================
# UTILITIES
# ============================================================

def wrap72(v: int) -> int:
    return v % 72


def reciprocal_phase(v: int) -> int:
    return (v + RECIPROCAL_PHASE_OFFSET) % 72


def hash72_char_to_int(c: str) -> int:
    return HASH72_INDEX[c]


def hash72_int_to_char(v: int) -> str:
    return HASH72[wrap72(v)]


def decode_hash72(s: str) -> List[int]:

    if len(s) != HASH_LEN:
        raise ValueError(
            f"Hash72 must be {HASH_LEN} chars"
        )

    return [hash72_char_to_int(c) for c in s]


def encode_hash72(values: List[int]) -> str:

    if len(values) != HASH_LEN:
        raise ValueError(
            f"Expected {HASH_LEN} phase values"
        )

    return "".join(hash72_int_to_char(v) for v in values)


# ============================================================
# PHASE VECTOR
# ============================================================

@dataclass
class PhaseVector72:

    values: List[int]

    def reciprocal(self) -> "PhaseVector72":

        return PhaseVector72(
            [reciprocal_phase(v) for v in self.values]
        )

    def add(
        self,
        other: "PhaseVector72"
    ) -> "PhaseVector72":

        return PhaseVector72(
            [
                wrap72(a + b)
                for a, b in zip(self.values, other.values)
            ]
        )

    def subtract(
        self,
        other: "PhaseVector72"
    ) -> "PhaseVector72":

        return PhaseVector72(
            [
                wrap72(a - b)
                for a, b in zip(self.values, other.values)
            ]
        )

    def reciprocal_tension(
        self,
        other: "PhaseVector72"
    ) -> List[int]:

        out = []

        for a, b in zip(self.values, other.values):

            rb = reciprocal_phase(b)

            out.append(abs(a - rb) % 72)

        return out

    def average(self) -> float:

        return sum(self.values) / len(self.values)

    def orbit_signature(self) -> str:

        h = hashlib.sha256()

        h.update(bytes(self.values))

        return h.hexdigest()


# ============================================================
# GEOMETRY POINT
# ============================================================

@dataclass
class GeometryPoint:

    x: float
    y: float

    radius: float
    theta: float

    phase: int

    hue: float
    brightness: float

    reciprocal_phase: int


# ============================================================
# PHASE RING
# ============================================================

@dataclass
class PhaseRing72:

    points: List[GeometryPoint] = field(default_factory=list)

    radius_base: float = 100.0
    radius_mod: float = 50.0

    @classmethod
    def from_phase_vector(
        cls,
        vec: PhaseVector72
    ) -> "PhaseRing72":

        ring = cls()

        for i, phase in enumerate(vec.values):

            theta = (
                2.0 * math.pi * i
            ) / HASH_LEN

            normalized = phase / 71.0

            radius = (
                ring.radius_base
                + normalized * ring.radius_mod
            )

            x = radius * math.cos(theta)
            y = radius * math.sin(theta)

            hue = phase / 72.0

            brightness = 0.5 + normalized * 0.5

            ring.points.append(
                GeometryPoint(
                    x=x,
                    y=y,
                    radius=radius,
                    theta=theta,
                    phase=phase,
                    hue=hue,
                    brightness=brightness,
                    reciprocal_phase=reciprocal_phase(phase),
                )
            )

        return ring


# ============================================================
# LOSHU CORE
# ============================================================

@dataclass
class LoShuCore:

    values: List[List[int]]

    @classmethod
    def from_phase_vector(
        cls,
        vec: PhaseVector72
    ) -> "LoShuCore":

        vals = []

        for r in range(3):

            row = []

            for c in range(3):

                idx = LOSHU[r][c] - 1

                row.append(vec.values[idx])

            vals.append(row)

        return cls(vals)

    def closure_sum_rows(self) -> List[int]:

        return [sum(r) for r in self.values]

    def closure_sum_cols(self) -> List[int]:

        out = []

        for c in range(3):

            out.append(
                self.values[0][c]
                + self.values[1][c]
                + self.values[2][c]
            )

        return out


# ============================================================
# SPRITE MAP 216
# ============================================================

@dataclass
class SpriteMap216:

    prev_hash72: str
    state_hash72: str
    receipt_hash72: str

    prev_vector: PhaseVector72
    state_vector: PhaseVector72
    receipt_vector: PhaseVector72

    prev_ring: PhaseRing72
    state_ring: PhaseRing72
    receipt_ring: PhaseRing72

    loshu_core: LoShuCore

    geometry_seed: str

    witness_flags: int = 0

    metadata: Dict = field(default_factory=dict)

    # ========================================================
    # CONSTRUCTORS
    # ========================================================

    @classmethod
    def from_receipt_triplet(
        cls,
        prev72: str,
        state72: str,
        receipt72: str,
        witness_flags: int = 0,
    ) -> "SpriteMap216":

        pv = PhaseVector72(decode_hash72(prev72))
        sv = PhaseVector72(decode_hash72(state72))
        rv = PhaseVector72(decode_hash72(receipt72))

        seed_input = (
            prev72 + state72 + receipt72
        ).encode()

        geometry_seed = hashlib.sha256(
            seed_input
        ).hexdigest()

        return cls(
            prev_hash72=prev72,
            state_hash72=state72,
            receipt_hash72=receipt72,

            prev_vector=pv,
            state_vector=sv,
            receipt_vector=rv,

            prev_ring=PhaseRing72.from_phase_vector(pv),
            state_ring=PhaseRing72.from_phase_vector(sv),
            receipt_ring=PhaseRing72.from_phase_vector(rv),

            loshu_core=LoShuCore.from_phase_vector(sv),

            geometry_seed=geometry_seed,

            witness_flags=witness_flags,
        )

    # ========================================================
    # FUSION
    # ========================================================

    def fuse_constructive(
        self,
        other: "SpriteMap216"
    ) -> "SpriteMap216":

        new_state = []

        for a, b in zip(
            self.state_vector.values,
            other.state_vector.values
        ):

            new_state.append(
                wrap72(a + b)
            )

        fused_state = encode_hash72(new_state)

        receipt_source = (
            self.receipt_hash72
            + other.receipt_hash72
            + fused_state
        )

        fused_receipt = self._hash_to_72(
            receipt_source
        )

        return SpriteMap216.from_receipt_triplet(
            self.state_hash72,
            fused_state,
            fused_receipt,
            witness_flags=(
                self.witness_flags
                | other.witness_flags
            )
        )

    def fuse_reciprocal(
        self,
        other: "SpriteMap216"
    ) -> "SpriteMap216":

        new_state = []

        for a, b in zip(
            self.state_vector.values,
            other.state_vector.values
        ):

            new_state.append(
                wrap72(a + b + 36)
            )

        fused_state = encode_hash72(new_state)

        receipt_source = (
            self.receipt_hash72
            + other.receipt_hash72
            + fused_state
            + "RECIPROCAL"
        )

        fused_receipt = self._hash_to_72(
            receipt_source
        )

        return SpriteMap216.from_receipt_triplet(
            self.state_hash72,
            fused_state,
            fused_receipt,
            witness_flags=(
                self.witness_flags
                | other.witness_flags
            )
        )

    # ========================================================
    # INTERACTION FIELD
    # ========================================================

    def interaction_tension(
        self,
        other: "SpriteMap216"
    ) -> List[int]:

        return self.state_vector.reciprocal_tension(
            other.state_vector
        )

    def closure_score(
        self,
        other: "SpriteMap216"
    ) -> float:

        tension = self.interaction_tension(other)

        avg = sum(tension) / len(tension)

        return 1.0 - (avg / 72.0)

    # ========================================================
    # REPLAY
    # ========================================================

    def replay_signature(self) -> str:

        return hashlib.sha256(
            (
                self.prev_hash72
                + self.state_hash72
                + self.receipt_hash72
            ).encode()
        ).hexdigest()

    # ========================================================
    # EXPORT
    # ========================================================

    def to_dict(self) -> Dict:

        return {
            "prev_hash72": self.prev_hash72,
            "state_hash72": self.state_hash72,
            "receipt_hash72": self.receipt_hash72,

            "geometry_seed": self.geometry_seed,

            "witness_flags": self.witness_flags,

            "loshu_core": self.loshu_core.values,

            "replay_signature": self.replay_signature(),
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    @staticmethod
    def _hash_to_72(s: str) -> str:

        digest = hashlib.sha256(
            s.encode()
        ).digest()

        out = []

        for i in range(HASH_LEN):

            b = digest[i % len(digest)]

            out.append(
                HASH72[b % 72]
            )

        return "".join(out)


# ============================================================
# SPRITE DATABASE OBJECT
# ============================================================

@dataclass
class SpriteMapDatabase:

    sprites: Dict[str, SpriteMap216] = field(
        default_factory=dict
    )

    def add(
        self,
        sprite: SpriteMap216
    ) -> None:

        self.sprites[
            sprite.replay_signature()
        ] = sprite

    def get(
        self,
        replay_signature: str
    ) -> Optional[SpriteMap216]:

        return self.sprites.get(replay_signature)

    def search_by_closure(
        self,
        threshold: float = 0.9
    ) -> List[SpriteMap216]:

        out = []

        for s in self.sprites.values():

            avg = s.state_vector.average()

            if avg / 71.0 >= threshold:
                out.append(s)

        return out


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    PREV = (
        "2jDWVX51QbuxI6>1pQ0y?oVxa4BELNQR2Q8ki)vi9X3tFrzLuC5JxQBpOUVm(ARNW8cEOYMW"
    )

    STATE = (
        "EYavwAcdQcwAMb3cxQ1A2s-DhcBFNQUuNrTWUA2*UAaBFsBOyHbQFQCtRY-s1IRRYbgfpznr"
    )

    RECEIPT = (
        "cVzbjxzEONoD!3(fQybgrehO>(Y3qDSBZphEI9j4Phf4s9y)qP(b<yd0F-1cBWkoo5mVdFpL"
    )

    sprite = SpriteMap216.from_receipt_triplet(
        PREV,
        STATE,
        RECEIPT,
    )

    print("\n=== SPRITE MAP 216 ===")
    print(sprite.to_dict())

    reciprocal = sprite.fuse_reciprocal(sprite)

    print("\n=== RECIPROCAL FUSION ===")
    print(reciprocal.to_dict())