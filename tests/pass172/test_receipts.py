from __future__ import annotations

from pathlib import Path
import json

import pytest

from hhs_installer.receipts import ReceiptChain, ReceiptError


def _append(chain: ReceiptChain, operation: str = "probe") -> None:
    chain.append(
        receipt_class="P172_ENVIRONMENT_PROBE_RECEIPT",
        operation=operation,
        requested_profile="auto",
        resolved_profile="core",
        plan_identity="plan-id",
        platform="Linux",
        architecture="x86_64",
        mutation_scope=(),
        result="SUCCESS",
        output_identities={"probe": "probe-id"},
        execution_metadata={"attempt": 1},
    )


def test_receipt_chain_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "receipts.jsonl"
    chain = ReceiptChain(path)
    _append(chain)
    _append(chain, "verify")
    loaded = ReceiptChain(path)
    assert len(loaded.receipts) == 2
    assert loaded.tip == chain.tip
    assert loaded.receipts[1].prior_tip == loaded.receipts[0].receipt_tip


def test_receipt_tamper_rejected(tmp_path: Path) -> None:
    path = tmp_path / "receipts.jsonl"
    chain = ReceiptChain(path)
    _append(chain)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["result"] = "FAILURE"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    with pytest.raises(ReceiptError):
        ReceiptChain(path)


def test_invalid_receipt_result_rejected(tmp_path: Path) -> None:
    chain = ReceiptChain(tmp_path / "receipts.jsonl")
    with pytest.raises(ReceiptError):
        chain.append(
            receipt_class="P172_TEST",
            operation="test",
            requested_profile="core",
            resolved_profile="core",
            plan_identity="plan",
            platform="Linux",
            architecture="x86_64",
            result="MAYBE",
        )
