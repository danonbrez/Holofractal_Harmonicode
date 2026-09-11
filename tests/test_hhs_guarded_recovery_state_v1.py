from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "deployment/digitalocean/guarded_auto_update/recovery-state.py"
spec = importlib.util.spec_from_file_location("hhs_guarded_recovery_state", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PREVIOUS = "73652c122ffff6a8b9bde9de00020610964d704c"
CANDIDATE = "2def7910b99046821f34e1446bcec33ca4fd4090"
OTHER = "b33b079399146e3d145aa3f6839979c87baf9605"


def receipt(outcome: str = "VALIDATED") -> dict[str, str]:
    return {
        "schema": "HHS_GUARDED_UPDATE_RECEIPT_V2",
        "phase": "validation",
        "outcome": outcome,
        "previous_sha": PREVIOUS,
        "candidate_sha": CANDIDATE,
        "runtime_os_bundle_sha": CANDIDATE,
    }


def expect_refused(payload: dict[str, str], live_sha: str) -> None:
    try:
        module.classify_recovery(payload, live_sha)
    except module.RecoveryStateError:
        return
    raise AssertionError(f"expected recovery refusal for {payload!r} live={live_sha}")


def test_validated_interruption_is_restartable_only_at_previous_sha() -> None:
    state = module.classify_recovery(receipt(), PREVIOUS)
    assert state.classification == "INTERRUPTED_AFTER_VALIDATION_BEFORE_TERMINAL_PROMOTION"
    assert state.outcome == "VALIDATED"
    assert state.live_sha == PREVIOUS
    expect_refused(receipt(), OTHER)


def test_validated_interruption_requires_distinct_candidate_and_matching_bundle() -> None:
    same = receipt()
    same["candidate_sha"] = PREVIOUS
    same["runtime_os_bundle_sha"] = PREVIOUS
    expect_refused(same, PREVIOUS)

    mismatch = receipt()
    mismatch["runtime_os_bundle_sha"] = OTHER
    expect_refused(mismatch, PREVIOUS)


def test_rollback_health_failed_preserves_existing_exact_boundary() -> None:
    state = module.classify_recovery(receipt("ROLLBACK_HEALTH_FAILED"), PREVIOUS)
    assert state.classification == "ROLLBACK_BOUNDARY_RESTART_REQUIRED"
    expect_refused(receipt("ROLLBACK_HEALTH_FAILED"), OTHER)


def test_other_terminal_or_ambiguous_outcomes_fail_closed() -> None:
    for outcome in ("PROMOTED", "ROLLED_BACK", "NO_CHANGE", "REJECTED", "DRY_RUN", ""):
        expect_refused(receipt(outcome), PREVIOUS)


def test_receipt_log_parser_rejects_corrupt_or_empty_logs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "receipts.jsonl"
        path.write_text("\n", encoding="utf-8")
        try:
            module.load_latest_receipt(path)
        except module.RecoveryStateError:
            pass
        else:
            raise AssertionError("empty receipt log must fail closed")

        path.write_text("{not-json}\n", encoding="utf-8")
        try:
            module.load_latest_receipt(path)
        except module.RecoveryStateError:
            pass
        else:
            raise AssertionError("corrupt receipt log must fail closed")


def test_receipt_log_parser_uses_exact_latest_record() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "receipts.jsonl"
        path.write_text(
            json.dumps(receipt("ROLLBACK_HEALTH_FAILED"))
            + "\n"
            + json.dumps(receipt("VALIDATED"))
            + "\n",
            encoding="utf-8",
        )
        latest = module.load_latest_receipt(path)
        assert latest["outcome"] == "VALIDATED"
        state = module.classify_recovery(latest, PREVIOUS)
        assert state.classification == "INTERRUPTED_AFTER_VALIDATION_BEFORE_TERMINAL_PROMOTION"


def run_all() -> None:
    tests = sorted(
        (name, value)
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    for name, test in tests:
        test()
        print(f"{name}: PASS")


if __name__ == "__main__":
    run_all()
