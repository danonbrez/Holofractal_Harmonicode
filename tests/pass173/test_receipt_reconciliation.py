from __future__ import annotations

from pathlib import Path

from hhs_installer.receipts import ReceiptChain
from hhs_verification.pass173.receipt_reconciler import ReceiptReconciler, TestEvent


def test_executed_counts_reconstructed_from_events() -> None:
    events = (
        TestEvent("a", "passed", 1, "oa"),
        TestEvent("b", "failed", 2, "ob"),
        TestEvent("c", "skipped", 3, "oc"),
        TestEvent("d", "xfailed", 4, "od"),
        TestEvent("e", "xpassed", 5, "oe"),
    )
    reported = {
        "collected": 5,
        "selected": 5,
        "executed": 5,
        "passed": 1,
        "failed": 1,
        "skipped": 1,
        "expected_failures": 1,
        "unexpected_passes": 1,
    }
    result = ReceiptReconciler.reconcile_counts(events, reported)
    assert result.matches is True
    assert result.test_set_identity
    assert result.output_identity


def test_stale_reported_count_detected() -> None:
    events = (TestEvent("a", "passed", 1, "oa"),)
    result = ReceiptReconciler.reconcile_counts(events, {"collected": 72})
    assert result.matches is False


def test_independent_receipt_chain_verification(tmp_path: Path) -> None:
    path = tmp_path / "chain.jsonl"
    chain = ReceiptChain(path)
    chain.append(
        receipt_class="P172_COMPLETION_RECEIPT",
        operation="install",
        requested_profile="core",
        resolved_profile="core",
        plan_identity="plan",
        platform="Linux",
        architecture="x86_64",
        result="SUCCESS",
        installation_identity="identity",
        execution_metadata={"test_counts": {}},
    )
    result = ReceiptReconciler.verify_receipt_chain(path)
    assert result["valid"] is True
    assert result["receipt_count"] == 1
    assert result["tip"] == chain.tip
