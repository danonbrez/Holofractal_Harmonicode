"""
HHS Memory Ledger + Replay Engine v1
====================================

Append-only Hash72 memory ledger for PhaseTransportVM runs.

The ledger stores every VM transition receipt as an immutable block:

    parent_hash72 -> payload_hash72 -> block_hash72

Replay recomputes block hashes, validates parent linkage, validates gate/commit
status consistency, and emits an auditable replay receipt.

This module is dependency-free and JSON-file backed so it works in the current
repository scaffold before the full database/vault layer is hydrated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
import json

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_phase_transport_vm_v1 import (
    GateStatus,
    PhaseTransitionReceipt,
    TransitionStatus,
    VMRunReceipt,
    run_tokens,
)


GENESIS_HASH72 = hash72_digest(("HHS_MEMORY_LEDGER_GENESIS_V1", "u72", "loshu81", "xyzw", "hash72"))


class ReplayStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class LedgerBlock:
    """One append-only memory block."""

    index: int
    parent_hash72: str
    payload_type: str
    payload_hash72: str
    payload: Dict[str, object]
    block_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LedgerCommitReceipt:
    """Receipt emitted after appending blocks to a ledger."""

    module: str
    ledger_path: str
    appended: int
    head_hash72: str
    block_hashes: List[str]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReplayFinding:
    """Validation result for one ledger block."""

    index: int
    block_hash72: str
    status: ReplayStatus
    findings: List[str]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class ReplayReceipt:
    """Full replay validation receipt."""

    module: str
    ledger_path: str
    head_hash72: str | None
    blocks_checked: int
    valid: int
    invalid: int
    findings: List[ReplayFinding]
    receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "module": self.module,
            "ledger_path": self.ledger_path,
            "head_hash72": self.head_hash72,
            "blocks_checked": self.blocks_checked,
            "valid": self.valid,
            "invalid": self.invalid,
            "findings": [finding.to_dict() for finding in self.findings],
            "receipt_hash72": self.receipt_hash72,
        }


def canonical_json(payload: object) -> str:
    """Canonical JSON string for deterministic Hash72 receipts."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(payload: Dict[str, object]) -> str:
    return hash72_digest(("payload", canonical_json(payload)))


def compute_block_hash(index: int, parent_hash72: str, payload_type: str, payload_hash72: str) -> str:
    return hash72_digest(("ledger_block_v1", index, parent_hash72, payload_type, payload_hash72))


def make_block(index: int, parent_hash72: str, payload_type: str, payload: Dict[str, object]) -> LedgerBlock:
    p_hash = payload_hash(payload)
    b_hash = compute_block_hash(index, parent_hash72, payload_type, p_hash)
    return LedgerBlock(
        index=index,
        parent_hash72=parent_hash72,
        payload_type=payload_type,
        payload_hash72=p_hash,
        payload=payload,
        block_hash72=b_hash,
    )


class MemoryLedger:
    """JSON-backed append-only ledger."""

    def __init__(self, path: str | Path = "demo_reports/hhs_memory_ledger_v1.json") -> None:
        self.path = Path(path)

    def load(self) -> List[LedgerBlock]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [LedgerBlock(**item) for item in data.get("blocks", [])]

    def save(self, blocks: Sequence[LedgerBlock]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"module": "hhs_memory_ledger_replay_v1", "genesis_hash72": GENESIS_HASH72, "blocks": [b.to_dict() for b in blocks]}
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def head_hash(self, blocks: Sequence[LedgerBlock] | None = None) -> str:
        blocks = self.load() if blocks is None else blocks
        return blocks[-1].block_hash72 if blocks else GENESIS_HASH72

    def append_payloads(self, payload_type: str, payloads: Sequence[Dict[str, object]]) -> LedgerCommitReceipt:
        blocks = self.load()
        parent = self.head_hash(blocks)
        appended: List[LedgerBlock] = []
        for payload in payloads:
            block = make_block(len(blocks) + len(appended), parent, payload_type, payload)
            appended.append(block)
            parent = block.block_hash72
        all_blocks = list(blocks) + appended
        self.save(all_blocks)
        receipt = hash72_digest(("ledger_commit", str(self.path), [b.block_hash72 for b in appended], self.head_hash(all_blocks)))
        return LedgerCommitReceipt(
            module="hhs_memory_ledger_replay_v1",
            ledger_path=str(self.path),
            appended=len(appended),
            head_hash72=self.head_hash(all_blocks),
            block_hashes=[b.block_hash72 for b in appended],
            receipt_hash72=receipt,
        )

    def append_vm_run(self, vm_receipt: VMRunReceipt) -> LedgerCommitReceipt:
        payloads = [transition.to_dict() for transition in vm_receipt.transition_receipts]
        return self.append_payloads("phase_transition_receipt_v1", payloads)


def _validate_transition_payload(payload: Dict[str, object]) -> List[str]:
    """Validate commit/quarantine semantics inside a transition payload."""

    findings: List[str] = []
    gates = payload.get("gates", [])
    if not isinstance(gates, list) or not gates:
        findings.append("missing_gate_receipts")
        return findings

    gate_statuses = [gate.get("status") for gate in gates if isinstance(gate, dict)]
    all_pass = all(status == GateStatus.PASS.value for status in gate_statuses)
    status = payload.get("status")
    committed = payload.get("committed_hash72")
    quarantine = payload.get("quarantine_hash72")

    if all_pass and status != TransitionStatus.COMMITTED.value:
        findings.append("all_gates_pass_but_not_committed")
    if (not all_pass) and status != TransitionStatus.QUARANTINED.value:
        findings.append("gate_failure_but_not_quarantined")
    if status == TransitionStatus.COMMITTED.value and not committed:
        findings.append("committed_missing_commit_hash")
    if status == TransitionStatus.COMMITTED.value and quarantine:
        findings.append("committed_has_quarantine_hash")
    if status == TransitionStatus.QUARANTINED.value and not quarantine:
        findings.append("quarantined_missing_quarantine_hash")
    if status == TransitionStatus.QUARANTINED.value and committed:
        findings.append("quarantined_has_commit_hash")

    transition = payload.get("transition", {})
    if not isinstance(transition, dict) or not transition.get("operation_hash72"):
        findings.append("missing_transition_operation_hash72")

    return findings


def replay_ledger(path: str | Path = "demo_reports/hhs_memory_ledger_v1.json") -> ReplayReceipt:
    """Replay and validate an existing ledger."""

    ledger = MemoryLedger(path)
    blocks = ledger.load()
    findings: List[ReplayFinding] = []
    expected_parent = GENESIS_HASH72

    for block in blocks:
        block_findings: List[str] = []
        recomputed_payload_hash = payload_hash(block.payload)
        recomputed_block_hash = compute_block_hash(block.index, block.parent_hash72, block.payload_type, block.payload_hash72)

        if block.parent_hash72 != expected_parent:
            block_findings.append("parent_hash_mismatch")
        if block.payload_hash72 != recomputed_payload_hash:
            block_findings.append("payload_hash_mismatch")
        if block.block_hash72 != recomputed_block_hash:
            block_findings.append("block_hash_mismatch")
        if block.payload_type == "phase_transition_receipt_v1":
            block_findings.extend(_validate_transition_payload(block.payload))

        status = ReplayStatus.VALID if not block_findings else ReplayStatus.INVALID
        receipt = hash72_digest(("replay_finding", block.index, block.block_hash72, status.value, block_findings))
        findings.append(ReplayFinding(block.index, block.block_hash72, status, block_findings, receipt))
        expected_parent = block.block_hash72

    valid_count = sum(1 for finding in findings if finding.status == ReplayStatus.VALID)
    invalid_count = len(findings) - valid_count
    head = blocks[-1].block_hash72 if blocks else None
    receipt_hash = hash72_digest(("ledger_replay", str(path), head, [finding.receipt_hash72 for finding in findings], valid_count, invalid_count))
    return ReplayReceipt(
        module="hhs_memory_ledger_replay_v1",
        ledger_path=str(path),
        head_hash72=head,
        blocks_checked=len(blocks),
        valid=valid_count,
        invalid=invalid_count,
        findings=findings,
        receipt_hash72=receipt_hash,
    )


def run_and_record_tokens(
    tokens: Sequence[str],
    d_model: int = 72,
    dimensions: int = 4,
    top_k: int = 1,
    ledger_path: str | Path = "demo_reports/hhs_memory_ledger_v1.json",
) -> Dict[str, object]:
    """Convenience path: VM run -> ledger append -> replay validation."""

    vm_receipt = run_tokens(tokens=tokens, d_model=d_model, dimensions=dimensions, top_k=top_k)
    ledger = MemoryLedger(ledger_path)
    commit_receipt = ledger.append_vm_run(vm_receipt)
    replay_receipt = replay_ledger(ledger_path)
    report_hash = hash72_digest(("run_record_replay", vm_receipt.receipt_hash72, commit_receipt.receipt_hash72, replay_receipt.receipt_hash72))
    return {
        "module": "hhs_memory_ledger_replay_v1",
        "vm_receipt_hash72": vm_receipt.receipt_hash72,
        "commit_receipt": commit_receipt.to_dict(),
        "replay_receipt": replay_receipt.to_dict(),
        "report_hash72": report_hash,
    }


def demo() -> Dict[str, object]:
    path = Path("demo_reports/hhs_memory_ledger_demo_v1.json")
    if path.exists():
        path.unlink()
    return run_and_record_tokens(["HHS", "Hash72", "LoShu", "xyzw"], d_model=72, dimensions=3, top_k=1, ledger_path=path)


if __name__ == "__main__":
    print(json.dumps(demo(), indent=2, sort_keys=True, ensure_ascii=False))
