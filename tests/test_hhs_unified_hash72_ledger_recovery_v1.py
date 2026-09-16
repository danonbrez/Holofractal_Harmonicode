import json
from pathlib import Path
import stat

import pytest

from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger
from hhs_runtime.hhs_unified_hash72_ledger_recovery_v1 import (
    UnifiedLedgerRecoveryError,
    inspect_transition_metadata_recovery,
    repair_transition_metadata,
)


def _journal_path(path: Path) -> Path:
    return Path(f"{path}.journal.jsonl")


def _records(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in _journal_path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_records(path: Path, records: list[dict]) -> None:
    _journal_path(path).write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def _make_ledger(path: Path, count: int = 3) -> None:
    for index in range(count):
        ledger.append_payload(
            "TEST_EVENT",
            "tests.unified-ledger-recovery",
            {"index": index},
            ledger_path=path,
        )
    assert ledger.verify_unified_ledger(path)["ok"] is True


def test_repairs_only_off_by_one_transition_metadata_and_preserves_entries(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    _make_ledger(path, 3)
    snapshot_before = path.read_bytes()
    records = _records(path)
    entries_before = [record["entry"] for record in records]

    # Reproduce the production journal:6930 fault shape on a bounded fixture:
    # the authoritative entry and ledger_hash72 are untouched while the count,
    # transition payload and its witness are one transition behind.
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
    _write_records(path, records)

    journal_path = _journal_path(path)
    journal_path.chmod(0o640)
    journal_stat_before = journal_path.stat()
    journal_identity_before = (
        journal_stat_before.st_uid,
        journal_stat_before.st_gid,
        stat.S_IMODE(journal_stat_before.st_mode),
    )

    verification = ledger.verify_unified_ledger(path)
    assert verification["ok"] is False
    reasons = {item["reason"] for item in verification["invalid"]}
    assert reasons == {
        "journal entry_count mismatch",
        "journal transition payload mismatch",
        "journal Hash72 accumulator witness mismatch",
    }

    inspection = inspect_transition_metadata_recovery(path)
    assert inspection["status"] == "RECOVERABLE_TRANSITION_METADATA"
    assert inspection["repairable"] is True

    receipt_path = tmp_path / "receipt.json"
    result = repair_transition_metadata(
        path,
        backup_root=tmp_path / "backups",
        receipt_path=receipt_path,
        require_repair=True,
    )

    journal_stat_after = journal_path.stat()
    journal_identity_after = (
        journal_stat_after.st_uid,
        journal_stat_after.st_gid,
        stat.S_IMODE(journal_stat_after.st_mode),
    )
    assert result["status"] == "REPAIRED_TRANSITION_METADATA"
    assert result["authoritative_entries_preserved"] is True
    assert result["entry_payloads_modified"] is False
    assert result["entry_hashes_modified"] is False
    assert result["journal_metadata_preserved"] is True
    assert journal_identity_after == journal_identity_before
    assert result["journal_metadata_before"] == {
        "uid": journal_identity_before[0],
        "gid": journal_identity_before[1],
        "mode": journal_identity_before[2],
    }
    assert result["journal_metadata_after"] == result["journal_metadata_before"]
    assert path.read_bytes() == snapshot_before
    assert [record["entry"] for record in _records(path)] == entries_before
    assert ledger.verify_unified_ledger(path)["ok"] is True
    assert receipt_path.is_file()
    backup_dir = Path(result["backup_directory"])
    assert (backup_dir / path.name).is_file()
    assert (backup_dir / _journal_path(path).name).is_file()


def test_refuses_authoritative_entry_payload_tampering_without_mutation(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    _make_ledger(path, 2)
    records = _records(path)
    records[-1]["entry"]["payload"]["index"] = 999
    _write_records(path, records)
    journal_before = _journal_path(path).read_bytes()

    with pytest.raises(UnifiedLedgerRecoveryError, match="authoritative entry chain is invalid"):
        repair_transition_metadata(
            path,
            backup_root=tmp_path / "backups",
            require_repair=True,
        )

    assert _journal_path(path).read_bytes() == journal_before
    assert not (tmp_path / "backups").exists()


def test_refuses_snapshot_authority_corruption(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    _make_ledger(path, 1)
    snapshot = json.loads(path.read_text(encoding="utf-8"))
    snapshot["entry_count"] = 4
    path.write_text(json.dumps(snapshot), encoding="utf-8")

    with pytest.raises(UnifiedLedgerRecoveryError, match="snapshot entry_count"):
        inspect_transition_metadata_recovery(path)


def test_valid_ledger_is_noop_and_can_be_required_to_be_invalid(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    _make_ledger(path, 2)
    journal_before = _journal_path(path).read_bytes()

    result = repair_transition_metadata(path, backup_root=tmp_path / "backups")
    assert result["status"] == "VALID_NO_REPAIR_REQUIRED"
    assert _journal_path(path).read_bytes() == journal_before
    assert not (tmp_path / "backups").exists()

    with pytest.raises(UnifiedLedgerRecoveryError, match="already valid"):
        repair_transition_metadata(
            path,
            backup_root=tmp_path / "backups",
            require_repair=True,
        )
