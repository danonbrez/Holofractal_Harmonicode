"""
hhs_receipt_replay_verifier_v1.py

Receipt-chain replay verifier for HARMONICODE general runtime.

Purpose
-------
Verify that a program execution trace remains continuous from genesis to tip.

Checks
------
1. parent_receipt_hash72 linkage
2. receipt_hash72 recomputation using authoritative Hash72
3. input/pre/op/post/witness hash presence
4. locked receipt completeness
5. quarantine receipt containment
6. final tip hash agreement

This verifier assumes receipts were emitted by hhs_general_runtime_layer_v1.py.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import json

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
    GENESIS_RECEIPT_HASH72,
    Hash72Authority,
    canonicalize_for_hash72,
    load_authoritative_kernel,
)


RECEIPT_REQUIRED_FIELDS = [
    "phase",
    "operation",
    "parent_receipt_hash72",
    "input_hash72",
    "pre_state_hash72",
    "operation_hash72",
    "post_state_hash72",
    "witness_hash72",
    "receipt_hash72",
    "integrity_hash72",
    "gate_status",
    "locked",
]


RECEIPT_CORE_FIELDS = [
    "phase",
    "operation",
    "parent_receipt_hash72",
    "input_hash72",
    "pre_state_hash72",
    "operation_hash72",
    "post_state_hash72",
    "witness_hash72",
    "gate_status",
    "locked",
    "quarantine",
    "reason",
]


@dataclass
class ReplayVerificationResult:
    ok: bool
    count: int
    tip_hash72: str
    failed_index: Optional[int] = None
    reason: str = ""
    details: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data["details"] is None:
            data["details"] = {}
        return data


class HHSReceiptReplayVerifierV1:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.kernel = load_authoritative_kernel(kernel_path)
        self.authority = Hash72Authority(self.kernel)

    @staticmethod
    def normalize_receipt(receipt: Any) -> Dict[str, Any]:
        if hasattr(receipt, "to_dict") and callable(getattr(receipt, "to_dict")):
            receipt = receipt.to_dict()
        elif hasattr(receipt, "__dict__") and not isinstance(receipt, dict):
            receipt = dict(receipt.__dict__)

        if not isinstance(receipt, dict):
            raise TypeError(f"Unsupported receipt type: {type(receipt).__name__}")

        return canonicalize_for_hash72(receipt)

    @staticmethod
    def receipt_core(receipt: Dict[str, Any]) -> Dict[str, Any]:
        core = {}
        for field in RECEIPT_CORE_FIELDS:
            if field in receipt:
                core[field] = receipt[field]
            else:
                # V2 receipts should include quarantine/reason.
                # Older receipts can be normalized here.
                if field == "quarantine":
                    core[field] = not bool(receipt.get("locked", False))
                elif field == "reason":
                    core[field] = ""
                else:
                    raise KeyError(f"Receipt missing core field: {field}")
        return core

    def verify(self, receipts: Iterable[Any], *, expected_tip_hash72: Optional[str] = None) -> ReplayVerificationResult:
        normalized: List[Dict[str, Any]] = []
        for raw in receipts:
            try:
                r = self.normalize_receipt(raw)
            except Exception as exc:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=GENESIS_RECEIPT_HASH72,
                    failed_index=len(normalized),
                    reason=f"receipt normalization failed: {type(exc).__name__}: {exc}",
                    details={},
                )
            normalized.append(r)

        expected_parent = GENESIS_RECEIPT_HASH72

        for idx, receipt in enumerate(normalized):
            missing = [field for field in RECEIPT_REQUIRED_FIELDS if field not in receipt]
            if missing:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="missing required receipt fields",
                    details={"missing": missing, "receipt": receipt},
                )

            if receipt["parent_receipt_hash72"] != expected_parent:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="parent_receipt_hash72 mismatch",
                    details={
                        "expected_parent": expected_parent,
                        "actual_parent": receipt["parent_receipt_hash72"],
                    },
                )

            if receipt["locked"] and receipt["gate_status"] != "LOCKED":
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="locked flag inconsistent with gate_status",
                    details={"receipt": receipt},
                )

            if receipt["locked"] and not receipt["receipt_hash72"]:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="LOCKED receipt missing receipt_hash72",
                    details={"receipt": receipt},
                )

            if not receipt["witness_hash72"]:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="receipt missing witness_hash72",
                    details={"receipt": receipt},
                )

            try:
                core = self.receipt_core(receipt)
                recomputed = self.authority.commit(core, domain="HHS_RECEIPT")
            except Exception as exc:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason=f"receipt recomputation failed: {type(exc).__name__}: {exc}",
                    details={"receipt": receipt},
                )

            if recomputed != receipt["receipt_hash72"]:
                return ReplayVerificationResult(
                    ok=False,
                    count=len(normalized),
                    tip_hash72=expected_parent,
                    failed_index=idx,
                    reason="receipt_hash72 recomputation mismatch",
                    details={
                        "expected_recomputed": recomputed,
                        "actual_receipt_hash72": receipt["receipt_hash72"],
                        "receipt_core": core,
                    },
                )

            expected_parent = receipt["receipt_hash72"]

        if expected_tip_hash72 is not None and expected_parent != expected_tip_hash72:
            return ReplayVerificationResult(
                ok=False,
                count=len(normalized),
                tip_hash72=expected_parent,
                failed_index=None,
                reason="final tip hash mismatch",
                details={
                    "expected_tip_hash72": expected_tip_hash72,
                    "actual_tip_hash72": expected_parent,
                },
            )

        return ReplayVerificationResult(
            ok=True,
            count=len(normalized),
            tip_hash72=expected_parent,
            failed_index=None,
            reason="receipt chain verified",
            details={"expected_tip_hash72": expected_tip_hash72 or expected_parent},
        )

    def verify_runner(self, runner: AuditedRunner) -> ReplayVerificationResult:
        return self.verify(
            runner.commitments.receipts,
            expected_tip_hash72=runner.commitments.tip_hash72,
        )


def demo() -> Dict[str, Any]:
    runner = AuditedRunner()
    runner.execute("ADD", 2, 3)
    runner.execute("SORT", [5, 3, 1, 3])
    runner.execute("BINARY_SEARCH", [1, 3, 5, 7, 9], 7)

    verifier = HHSReceiptReplayVerifierV1()
    report = verifier.verify_runner(runner)
    return report.to_dict()


def main() -> None:
    print(json.dumps(demo(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
