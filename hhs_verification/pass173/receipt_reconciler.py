from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json

from hhs_installer.canonical import hash216, stable
from hhs_installer.receipts import InstallationReceipt, ReceiptChain, ReceiptError


@dataclass(frozen=True)
class TestEvent:
    nodeid: str
    outcome: str
    duration_ns: int
    output_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class CountReconciliation:
    collected: int
    selected: int
    executed: int
    passed: int
    failed: int
    skipped: int
    expected_failures: int
    unexpected_passes: int
    reported: Mapping[str, int]
    matches: bool
    test_set_identity: str
    output_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class ReceiptReconciler:
    @staticmethod
    def load_events(path: str | Path) -> tuple[TestEvent, ...]:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        raw_events = payload.get("events", payload) if isinstance(payload, Mapping) else payload
        if not isinstance(raw_events, list):
            raise ValueError("P173_TEST_EVENT_SET_INVALID")
        events: list[TestEvent] = []
        for value in raw_events:
            events.append(
                TestEvent(
                    nodeid=str(value["nodeid"]),
                    outcome=str(value["outcome"]),
                    duration_ns=int(value.get("duration_ns", 0)),
                    output_identity=str(value.get("output_identity", "")),
                )
            )
        return tuple(events)

    @staticmethod
    def reconcile_counts(events: Iterable[TestEvent], reported: Mapping[str, int], *, collected: int | None = None, selected: int | None = None) -> CountReconciliation:
        ordered = tuple(sorted(events, key=lambda item: item.nodeid))
        counts = {
            "passed": sum(item.outcome == "passed" for item in ordered),
            "failed": sum(item.outcome == "failed" for item in ordered),
            "skipped": sum(item.outcome == "skipped" for item in ordered),
            "expected_failures": sum(item.outcome == "xfailed" for item in ordered),
            "unexpected_passes": sum(item.outcome == "xpassed" for item in ordered),
        }
        executed = len(ordered)
        collected_value = executed if collected is None else int(collected)
        selected_value = executed if selected is None else int(selected)
        expected_report = {
            "collected": collected_value,
            "selected": selected_value,
            "executed": executed,
            **counts,
        }
        normalized_reported = {key: int(reported.get(key, -1)) for key in expected_report}
        matches = expected_report == normalized_reported
        return CountReconciliation(
            collected=collected_value,
            selected=selected_value,
            executed=executed,
            passed=counts["passed"],
            failed=counts["failed"],
            skipped=counts["skipped"],
            expected_failures=counts["expected_failures"],
            unexpected_passes=counts["unexpected_passes"],
            reported=normalized_reported,
            matches=matches,
            test_set_identity=hash216([item.to_dict() for item in ordered], domain="HHS-P173-TEST-SET-V1"),
            output_identity=hash216([item.output_identity for item in ordered], domain="HHS-P173-TEST-OUTPUT-SET-V1"),
        )

    @staticmethod
    def verify_receipt_chain(path: str | Path) -> dict[str, Any]:
        try:
            chain = ReceiptChain(path)
        except ReceiptError as exc:
            return {
                "valid": False,
                "classification": str(exc),
                "receipt_count": 0,
                "tip": None,
            }
        return {
            "valid": True,
            "classification": "P173_HASH72_RECEIPT_CHAIN_VERIFIED",
            "receipt_count": len(chain.receipts),
            "tip": chain.tip,
            "chain_identity": hash216([receipt.to_dict() for receipt in chain.receipts], domain="HHS-P173-RECONSTRUCTED-RECEIPT-CHAIN-V1"),
        }

    @staticmethod
    def compare_completion_receipt(receipt: InstallationReceipt, reconciliation: CountReconciliation) -> dict[str, Any]:
        reported = receipt.execution_metadata.get("test_counts", {}) if isinstance(receipt.execution_metadata, Mapping) else {}
        receipt_matches = reconciliation.matches and all(int(reported.get(key, -1)) == value for key, value in {
            "collected": reconciliation.collected,
            "selected": reconciliation.selected,
            "executed": reconciliation.executed,
            "passed": reconciliation.passed,
            "failed": reconciliation.failed,
            "skipped": reconciliation.skipped,
            "expected_failures": reconciliation.expected_failures,
            "unexpected_passes": reconciliation.unexpected_passes,
        }.items())
        return {
            "matches": receipt_matches,
            "classification": "P173_RECEIPT_EXECUTION_COUNTS_VERIFIED" if receipt_matches else "P173_RECEIPT_EXECUTION_COUNT_MISMATCH",
            "receipt_identity": receipt.receipt_identity,
            "test_set_identity": reconciliation.test_set_identity,
            "output_identity": reconciliation.output_identity,
        }
