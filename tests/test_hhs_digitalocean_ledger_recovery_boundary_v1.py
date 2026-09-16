import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger


REPO = Path(__file__).resolve().parents[1]
NORMALIZER_PATH = REPO / "deployment" / "digitalocean" / "guarded_auto_update" / "normalize-service-permissions.py"
SPEC = importlib.util.spec_from_file_location("hhs_production_boundary_normalizer_test", NORMALIZER_PATH)
assert SPEC is not None and SPEC.loader is not None
normalizer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(normalizer)


def _corrupt_transition_metadata(path: Path) -> None:
    for index in range(3):
        ledger.append_payload(
            "TEST_EVENT",
            "tests.digitalocean-ledger-recovery-boundary",
            {"index": index},
            ledger_path=path,
        )
    journal = Path(f"{path}.journal.jsonl")
    records = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines()]
    bad = records[-1]
    bad_count = int(bad["entry_count"]) - 1
    bad["entry_count"] = bad_count
    bad_payload = dict(bad["transition_payload"])
    bad_payload["entry_count"] = bad_count
    bad["transition_payload"] = bad_payload
    bad["tip_hash72_kernel_witness"] = ledger._ledger_witness(
        "hhs_unified_hash72_ledger_incremental_v1",
        bad_payload,
    )
    journal.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    assert ledger.verify_unified_ledger(path)["ok"] is False


def _write_terminal_receipt(state_root: Path, outcome: str) -> None:
    state_root.mkdir(parents=True, exist_ok=True)
    (state_root / "receipts.jsonl").write_text(
        json.dumps({"schema": "HHS_GUARDED_UPDATE_RECEIPT_V2", "outcome": outcome}) + "\n",
        encoding="utf-8",
    )


def test_recovery_boundary_requires_rollback_failure_and_restarts_service(tmp_path: Path, monkeypatch):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    path = runtime / "hhs_unified_hash72_ledger.json"
    _corrupt_transition_metadata(path)
    state = tmp_path / "guarded"
    _write_terminal_receipt(state, "ROLLBACK_HEALTH_FAILED")

    service_calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(normalizer, "_stop_production_service_and_verify_quiescent", lambda: None)

    def fake_run(command, *args, **kwargs):
        command_tuple = tuple(str(part) for part in command)
        service_calls.append(command_tuple)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(normalizer.subprocess, "run", fake_run)
    result = normalizer.recover_unified_ledger_rollback_boundary(
        REPO,
        state_root=state,
        runtime_output_dir=runtime,
    )

    assert result["status"] == "TRANSITION_METADATA_REPAIRED"
    assert result["terminal_guarded_update_outcome"] == "ROLLBACK_HEALTH_FAILED"
    assert result["service_restart_requested"] is True
    assert ("systemctl", "start", "hhs.service") in service_calls
    assert ledger.verify_unified_ledger(path)["ok"] is True
    assert Path(result["recovery_receipt_path"]).is_file()
    assert Path(result["backup_directory"]).is_dir()


def test_recovery_boundary_refuses_transition_repair_without_terminal_receipt(tmp_path: Path, monkeypatch):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    path = runtime / "hhs_unified_hash72_ledger.json"
    _corrupt_transition_metadata(path)
    state = tmp_path / "guarded"
    _write_terminal_receipt(state, "ROLLED_BACK")
    journal_before = Path(f"{path}.journal.jsonl").read_bytes()
    stopped = False

    def stop_marker():
        nonlocal stopped
        stopped = True

    monkeypatch.setattr(normalizer, "_stop_production_service_and_verify_quiescent", stop_marker)
    with pytest.raises(RuntimeError, match="ROLLBACK_HEALTH_FAILED"):
        normalizer.recover_unified_ledger_rollback_boundary(
            REPO,
            state_root=state,
            runtime_output_dir=runtime,
        )

    assert stopped is False
    assert Path(f"{path}.journal.jsonl").read_bytes() == journal_before
    assert ledger.verify_unified_ledger(path)["ok"] is False
