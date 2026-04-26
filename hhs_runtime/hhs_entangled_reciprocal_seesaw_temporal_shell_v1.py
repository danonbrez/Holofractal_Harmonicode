"""
HHS Entangled Reciprocal Seesaw Temporal Shell v1
================================================

Deterministic pseudo-random temporal shell generator for ERS holography.

Purpose
-------
Generate a replayable 72-step phase-filtered pseudo-random sequence while
alternating each operation through the trinary ERS carrier cycle:

    x -> y -> xy -> x -> ...

Each step receives a unique temporal shell expansion receipt. The generator is
pseudo-random but deterministic: identical seed + cycle count produces identical
shells and aggregate receipts.

This module does not mutate kernel state directly. It emits shell descriptors
that can later be passed into the consensus / commit pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


Z72 = 72
CARRIER_CYCLE = ("x", "y", "xy")


class ShellStatus(str, Enum):
    LOCKED = "LOCKED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class TemporalShellStep:
    index: int
    phase_index: int
    carrier: str
    prn_word: int
    phase_filter: int
    shell_width: int
    expansion: Dict[str, Any]
    status: ShellStatus
    shell_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class TemporalShellRun:
    seed_hash72: str
    cycles: int
    total_steps: int
    steps: List[TemporalShellStep]
    carrier_balance: Dict[str, int]
    aggregate_hash72: str
    status: ShellStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed_hash72": self.seed_hash72,
            "cycles": self.cycles,
            "total_steps": self.total_steps,
            "steps": [s.to_dict() for s in self.steps],
            "carrier_balance": self.carrier_balance,
            "aggregate_hash72": self.aggregate_hash72,
            "status": self.status.value,
            "receipt_hash72": self.receipt_hash72,
        }


def _lcg_next(state: int) -> int:
    """Small deterministic PRNG step.

    This is not cryptographic. It is a replayable temporal shell source.
    Integrity still comes from hash72 receipts and kernel verification.
    """
    return (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)


def _seed_to_int(seed: str) -> int:
    h = hash72_digest(("ers_temporal_shell_seed_v1", seed), width=24)
    acc = 0
    for ch in h:
        acc = ((acc << 5) ^ ord(ch)) & ((1 << 64) - 1)
    return acc or 1


def _phase_filter(prn_word: int, step: int, cycle: int) -> int:
    return (prn_word ^ (step * 17) ^ (cycle * 31)) % Z72


def _shell_width(prn_word: int, carrier: str) -> int:
    base = {"x": 1, "y": 2, "xy": 3}[carrier]
    return base + (prn_word % 9)


def generate_temporal_shells(seed: str, *, cycles: int = 1) -> TemporalShellRun:
    cycles = max(1, int(cycles))
    total = Z72 * cycles
    state = _seed_to_int(seed)
    seed_hash = hash72_digest(("ers_temporal_shell_seed_receipt_v1", seed, cycles), width=24)
    steps: List[TemporalShellStep] = []

    for i in range(total):
        cycle = i // Z72
        local = i % Z72
        state = _lcg_next(state)
        carrier = CARRIER_CYCLE[i % len(CARRIER_CYCLE)]
        filtered = _phase_filter(state, local, cycle)
        phase_index = (local + filtered) % Z72
        width = _shell_width(state, carrier)
        expansion = {
            "cycle": cycle,
            "local_step": local,
            "carrier": carrier,
            "ers_pair": {"x": "1/y", "y": "-x", "xy": "-1/yx"}.get(carrier),
            "temporal_shell": f"u^{phase_index}/72::{carrier}^{width}",
            "phase_refresh_rate": 72,
            "replay_word": str(state),
        }
        status = ShellStatus.LOCKED if 0 <= phase_index < Z72 and carrier in CARRIER_CYCLE else ShellStatus.QUARANTINED
        shell_hash = hash72_digest(("ers_temporal_shell_step_v1", seed_hash, i, phase_index, carrier, state, filtered, width, expansion, status.value), width=24)
        steps.append(TemporalShellStep(i, phase_index, carrier, int(state), filtered, int(width), expansion, status, shell_hash))

    balance = {c: sum(1 for s in steps if s.carrier == c) for c in CARRIER_CYCLE}
    aggregate = hash72_digest(("ers_temporal_shell_aggregate_v1", seed_hash, cycles, [s.shell_hash72 for s in steps], balance), width=24)
    status = ShellStatus.LOCKED if all(s.status == ShellStatus.LOCKED for s in steps) and max(balance.values()) - min(balance.values()) <= 1 else ShellStatus.QUARANTINED
    receipt = hash72_digest(("ers_temporal_shell_run_receipt_v1", aggregate, status.value, total, balance), width=24)
    return TemporalShellRun(seed_hash, cycles, total, steps, balance, aggregate, status, receipt)


def main() -> None:
    print(json.dumps(generate_temporal_shells("HHS_ROOT_SEED", cycles=1).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
