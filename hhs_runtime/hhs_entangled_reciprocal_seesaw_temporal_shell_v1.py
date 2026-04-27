"""
HHS Entangled Reciprocal Seesaw Temporal Shell v1
================================================

Deterministic pseudo-random temporal shell generator for ERS holography.

Purpose
-------
Generate replayable 72-step phase-filtered pseudo-random sequences while routing
each operation through the trinary ERS carrier set:

    x, y, xy

v1.1 adds bounded adaptive shell weighting:
- successful root/correction feedback adjusts carrier weights
- phase bias steers future shell sampling toward successful phase regions
- weights are capped so x/y/xy balance and replay determinism are preserved
- identical seed + feedback records + cycle count produces identical shells

This module does not mutate kernel state directly. It emits shell descriptors
that can later be passed into the consensus / commit pipeline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest


Z72 = 72
CARRIER_CYCLE = ("x", "y", "xy")
BASE_CARRIER_WEIGHTS = {"x": 24, "y": 24, "xy": 24}
CARRIER_WEIGHT_CAPS = {"x": (18, 30), "y": (18, 30), "xy": (18, 30)}


class ShellStatus(str, Enum):
    LOCKED = "LOCKED"
    QUARANTINED = "QUARANTINED"


@dataclass(frozen=True)
class ShellLearningReceipt:
    carrier_weights: Dict[str, int]
    phase_biases: Dict[int, int]
    feedback_hashes: List[str]
    capped: bool
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {"carrier_weights": self.carrier_weights, "phase_biases": {str(k): v for k, v in self.phase_biases.items()}, "feedback_hashes": self.feedback_hashes, "capped": self.capped, "receipt_hash72": self.receipt_hash72}


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
    learning: ShellLearningReceipt
    aggregate_hash72: str
    status: ShellStatus
    receipt_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return {"seed_hash72": self.seed_hash72, "cycles": self.cycles, "total_steps": self.total_steps, "steps": [s.to_dict() for s in self.steps], "carrier_balance": self.carrier_balance, "learning": self.learning.to_dict(), "aggregate_hash72": self.aggregate_hash72, "status": self.status.value, "receipt_hash72": self.receipt_hash72}


def _lcg_next(state: int) -> int:
    return (state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)


def _seed_to_int(seed: str) -> int:
    h = hash72_digest(("ers_temporal_shell_seed_v1", seed), width=24)
    acc = 0
    for ch in h:
        acc = ((acc << 5) ^ ord(ch)) & ((1 << 64) - 1)
    return acc or 1


def _clamp_weight(carrier: str, value: int) -> int:
    lo, hi = CARRIER_WEIGHT_CAPS[carrier]
    return max(lo, min(hi, value))


def _feedback_hash(record: Dict[str, Any]) -> str:
    return str(record.get("commit_hash72") or record.get("summary_hash72") or record.get("receipt_hash72") or record.get("execution_candidate_hash72") or hash72_digest(("shell_feedback_unknown_v1", record), width=18))


def learn_shell_weights(feedback_records: Sequence[Dict[str, Any]] | None = None) -> ShellLearningReceipt:
    weights = dict(BASE_CARRIER_WEIGHTS)
    phase_biases: Dict[int, int] = {}
    hashes: List[str] = []
    capped = False

    for record in feedback_records or []:
        h = _feedback_hash(record)
        hashes.append(h)
        commit = record.get("commit") or record
        candidate = record.get("candidate", {}).get("candidate", {}) if isinstance(record.get("candidate"), dict) else record.get("candidate", {})
        phases = candidate.get("equation", {}).get("phases") or record.get("phases") or []
        status = candidate.get("status") or commit.get("status")
        executions = commit.get("executions", []) if isinstance(commit, dict) else []
        applied = any(e.get("status") in {"APPLIED", "HELD"} for e in executions) or status == "STAGED"
        failed = any(e.get("status") in {"RELOCK_FAILED", "REJECTED_NO_CONSENSUS", "REPLAY_BLOCKED"} for e in executions) or status == "QUARANTINED"

        if applied:
            weights["xy"] += 2
            weights["x"] += 1
        if failed:
            weights["y"] += 2
            weights["xy"] -= 1
        for p in phases:
            idx = int(p) % Z72
            phase_biases[idx] = phase_biases.get(idx, 0) + (3 if applied else -2 if failed else 1)

    clamped = {}
    for c, v in weights.items():
        cv = _clamp_weight(c, v)
        capped = capped or cv != v
        clamped[c] = cv
    phase_biases = {k: max(-9, min(9, v)) for k, v in sorted(phase_biases.items()) if v != 0}
    receipt = hash72_digest(("shell_learning_receipt_v1", clamped, phase_biases, hashes, capped), width=24)
    return ShellLearningReceipt(clamped, phase_biases, hashes, capped, receipt)


def _phase_filter(prn_word: int, step: int, cycle: int, learning: ShellLearningReceipt) -> int:
    raw = (prn_word ^ (step * 17) ^ (cycle * 31)) % Z72
    if not learning.phase_biases:
        return raw
    # Deterministically bias toward learned regions without leaving Z72.
    target = sorted(learning.phase_biases.items(), key=lambda kv: (-kv[1], kv[0]))[prn_word % len(learning.phase_biases)][0]
    strength = learning.phase_biases.get(target, 0)
    return (raw + ((target - raw) * abs(strength)) // 12) % Z72


def _choose_carrier(prn_word: int, step: int, learning: ShellLearningReceipt) -> str:
    weights = learning.carrier_weights
    total = sum(weights.values()) or 72
    cursor = (prn_word + step * 7) % total
    acc = 0
    for carrier in CARRIER_CYCLE:
        acc += weights[carrier]
        if cursor < acc:
            return carrier
    return CARRIER_CYCLE[step % len(CARRIER_CYCLE)]


def _shell_width(prn_word: int, carrier: str, learning: ShellLearningReceipt) -> int:
    base = {"x": 1, "y": 2, "xy": 3}[carrier]
    carrier_gain = max(0, learning.carrier_weights.get(carrier, 24) - 24) // 3
    return base + carrier_gain + (prn_word % 9)


def generate_temporal_shells(seed: str, *, cycles: int = 1, feedback_records: Sequence[Dict[str, Any]] | None = None) -> TemporalShellRun:
    cycles = max(1, int(cycles))
    total = Z72 * cycles
    state = _seed_to_int(seed)
    seed_hash = hash72_digest(("ers_temporal_shell_seed_receipt_v1", seed, cycles), width=24)
    learning = learn_shell_weights(feedback_records)
    steps: List[TemporalShellStep] = []

    for i in range(total):
        cycle = i // Z72
        local = i % Z72
        state = _lcg_next(state)
        carrier = _choose_carrier(state, i, learning)
        filtered = _phase_filter(state, local, cycle, learning)
        phase_index = (local + filtered) % Z72
        width = _shell_width(state, carrier, learning)
        expansion = {"cycle": cycle, "local_step": local, "carrier": carrier, "ers_pair": {"x": "1/y", "y": "-x", "xy": "-1/yx"}.get(carrier), "temporal_shell": f"u^{phase_index}/72::{carrier}^{width}", "phase_refresh_rate": 72, "replay_word": str(state), "learning_receipt_hash72": learning.receipt_hash72}
        status = ShellStatus.LOCKED if 0 <= phase_index < Z72 and carrier in CARRIER_CYCLE else ShellStatus.QUARANTINED
        shell_hash = hash72_digest(("ers_temporal_shell_step_v1", seed_hash, learning.receipt_hash72, i, phase_index, carrier, state, filtered, width, expansion, status.value), width=24)
        steps.append(TemporalShellStep(i, phase_index, carrier, int(state), filtered, int(width), expansion, status, shell_hash))

    balance = {c: sum(1 for s in steps if s.carrier == c) for c in CARRIER_CYCLE}
    balance_ok = max(balance.values()) - min(balance.values()) <= max(12, total // 6)
    aggregate = hash72_digest(("ers_temporal_shell_aggregate_v1", seed_hash, cycles, learning.receipt_hash72, [s.shell_hash72 for s in steps], balance), width=24)
    status = ShellStatus.LOCKED if all(s.status == ShellStatus.LOCKED for s in steps) and balance_ok else ShellStatus.QUARANTINED
    receipt = hash72_digest(("ers_temporal_shell_run_receipt_v1", aggregate, learning.receipt_hash72, status.value, total, balance), width=24)
    return TemporalShellRun(seed_hash, cycles, total, steps, balance, learning, aggregate, status, receipt)


def main() -> None:
    demo_feedback = [{"candidate": {"candidate": {"status": "STAGED", "equation": {"phases": [4, 12, 20, 36]}}}, "commit_hash72": "H72-DEMO-FEEDBACK"}]
    print(json.dumps(generate_temporal_shells("HHS_ROOT_SEED", cycles=1, feedback_records=demo_feedback).to_dict(), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
