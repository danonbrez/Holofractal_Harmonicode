import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
from types import SimpleNamespace

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
    assert result["journal_metadata_preserved"] is True
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


def test_runtime_ledger_permission_normalizer_repairs_only_canonical_surfaces(tmp_path: Path, monkeypatch):
    runtime = tmp_path / "runtime"
    runtime.mkdir(mode=0o700)
    ledger_path = runtime / "hhs_unified_hash72_ledger.json"
    ledger_path.write_text("{}\n", encoding="utf-8")
    journal_path = Path(f"{ledger_path}.journal.jsonl")
    journal_path.write_text("{}\n", encoding="utf-8")
    unrelated = runtime / "unrelated-secret.bin"
    unrelated.write_bytes(b"untouched")

    runtime.chmod(0o700)
    ledger_path.chmod(0o600)
    journal_path.chmod(0o600)
    unrelated.chmod(0o600)
    unrelated_before = unrelated.stat()

    real_gid = runtime.stat().st_gid
    fake_uid = runtime.stat().st_uid + 100000
    monkeypatch.setattr(normalizer.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(
        normalizer.pwd,
        "getpwnam",
        lambda _name: SimpleNamespace(pw_name="svc-hhs", pw_uid=fake_uid, pw_gid=real_gid),
    )
    monkeypatch.setattr(
        normalizer.grp,
        "getgrnam",
        lambda _name: SimpleNamespace(gr_name="svc-hhs", gr_gid=real_gid),
    )
    monkeypatch.setattr(normalizer.grp, "getgrall", lambda: [])

    result = normalizer.normalize_unified_ledger_permissions(
        runtime,
        service_user="svc-hhs",
        service_group="svc-hhs",
        require_root=False,
    )

    assert result["status"] == "NORMALIZED"
    assert result["service_read_write_verified"] is True
    assert set(result["normalized_paths"]) == {
        str(runtime.resolve()),
        str(ledger_path),
        str(journal_path),
    }
    assert set(result["changed_paths"]) == set(result["normalized_paths"])
    assert stat.S_IMODE(runtime.stat().st_mode) & stat.S_IRWXG == stat.S_IRWXG
    for path in (ledger_path, journal_path):
        assert stat.S_IMODE(path.stat().st_mode) & (stat.S_IRGRP | stat.S_IWGRP) == (
            stat.S_IRGRP | stat.S_IWGRP
        )
    unrelated_after = unrelated.stat()
    assert stat.S_IMODE(unrelated_after.st_mode) == stat.S_IMODE(unrelated_before.st_mode)
    assert unrelated_after.st_gid == unrelated_before.st_gid
    assert unrelated.read_bytes() == b"untouched"


def test_runtime_ledger_permission_normalizer_refuses_symlink_boundary(tmp_path: Path, monkeypatch):
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    target = tmp_path / "target.json"
    target.write_text("{}\n", encoding="utf-8")
    ledger_path = runtime / "hhs_unified_hash72_ledger.json"
    ledger_path.symlink_to(target)

    real_gid = runtime.stat().st_gid
    monkeypatch.setattr(normalizer.os, "geteuid", lambda: 1000)
    monkeypatch.setattr(
        normalizer.pwd,
        "getpwnam",
        lambda _name: SimpleNamespace(
            pw_name="svc-hhs",
            pw_uid=os.getuid() + 100000,
            pw_gid=real_gid,
        ),
    )
    monkeypatch.setattr(
        normalizer.grp,
        "getgrnam",
        lambda _name: SimpleNamespace(gr_name="svc-hhs", gr_gid=real_gid),
    )
    monkeypatch.setattr(normalizer.grp, "getgrall", lambda: [])

    with pytest.raises(RuntimeError, match="refusing symlink"):
        normalizer.normalize_unified_ledger_permissions(
            runtime,
            service_user="svc-hhs",
            service_group="svc-hhs",
            require_root=False,
        )
