"""
HHS Symbolic Quantum Algebra v1
===============================

Canonical internal schema for the 8-symbol phase alphabet, balanced trinary
multiplication tensor, quartic null-channel closure, and exact symbolic
computation layer.

This module is declarative and side-effect free.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


class ProductValue(int, Enum):
    ANTI_PHASE = -1
    NULL = 0
    CLOSURE = 1


PHASE_GENERATORS = ["x", "y", "z", "w"]
BOND_CARRIERS = ["xy", "yx", "zw", "wz"]
PHASE_ALPHABET_8 = ["x", "y", "z", "w", "xy", "yx", "zw", "wz"]

BALANCED_TRINARY_TABLE_4X4: Dict[str, Dict[str, int]] = {
    "x": {"x": -1, "y": 1, "z": 0, "w": 1},
    "y": {"x": -1, "y": -1, "z": -1, "w": 0},
    "z": {"x": 0, "y": 1, "z": -1, "w": 1},
    "w": {"x": -1, "y": 0, "z": -1, "w": -1},
}

ORDERED_PRODUCT_RULES: Dict[str, str] = {
    "xy": "+1",
    "yx": "-1",
    "zw": "+1",
    "wz": "-1",
    "xw": "xy",
    "wx": "wz",
    "yz": "yx",
    "zy": "zw",
}

NULL_CHANNELS = ["xz", "zx", "yw", "wy"]
NULL_BALANCE_PAIRS = [("xz", "zx"), ("yw", "wy")]

MASTER_INVARIANTS = {
    "xy": "1",
    "yx": "-1",
    "x_plus_y": "0",
    "x4": "1",
    "n4": "1",
    "u72": "1",
    "a2": "1",
    "theta15": True,
    "no_float_authority": True,
}

LO_SHU_DECIMAL_EMBEDDING = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]


@dataclass(frozen=True)
class AlgebraWitness:
    alphabet: List[str]
    table_4x4: Dict[str, Dict[str, int]]
    ordered_rules: Dict[str, str]
    null_channels: List[str]
    null_balance_pairs: List[Tuple[str, str]]
    invariants: Dict[str, Any]
    witness_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_algebra_witness() -> AlgebraWitness:
    payload = {
        "alphabet": PHASE_ALPHABET_8,
        "table_4x4": BALANCED_TRINARY_TABLE_4X4,
        "ordered_rules": ORDERED_PRODUCT_RULES,
        "null_channels": NULL_CHANNELS,
        "null_balance_pairs": NULL_BALANCE_PAIRS,
        "invariants": MASTER_INVARIANTS,
    }
    h = hash72_digest(("hhs_symbolic_quantum_algebra_v1", payload), width=24)
    return AlgebraWitness(
        alphabet=PHASE_ALPHABET_8,
        table_4x4=BALANCED_TRINARY_TABLE_4X4,
        ordered_rules=ORDERED_PRODUCT_RULES,
        null_channels=NULL_CHANNELS,
        null_balance_pairs=NULL_BALANCE_PAIRS,
        invariants=MASTER_INVARIANTS,
        witness_hash72=h,
    )


def product_value(left: str, right: str) -> int | None:
    if left in BALANCED_TRINARY_TABLE_4X4 and right in BALANCED_TRINARY_TABLE_4X4[left]:
        return BALANCED_TRINARY_TABLE_4X4[left][right]
    pair = f"{left}{right}"
    if pair in {"xy", "zw"}:
        return 1
    if pair in {"yx", "wz"}:
        return -1
    if pair in NULL_CHANNELS:
        return 0
    return None


def null_channels_balanced(channels: List[str] | None = None) -> bool:
    present = set(channels or NULL_CHANNELS)
    return all(a in present and b in present for a, b in NULL_BALANCE_PAIRS)


def main() -> None:
    print(json.dumps(build_algebra_witness().to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
