import json
from pathlib import Path

from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger


def test_append_uses_constant_size_journal_without_rewriting_snapshot(tmp_path: Path, monkeypatch):
    path = tmp_path / "unified-ledger.json"

    first = ledger.append_payload(
        "TEST_EVENT",
        "tests.incremental-ledger",
        {"index": 1},
        ledger_path=path,
    )
    assert first["entry_count"] == 1
    snapshot_bytes = path.read_bytes()

    def reject_snapshot_rewrite(*_args, **_kwargs):
        raise AssertionError("append path attempted to rewrite the compacted snapshot")

    monkeypatch.setattr(ledger, "_atomic_write_json", reject_snapshot_rewrite)
    second = ledger.append_payload(
        "TEST_EVENT",
        "tests.incremental-ledger",
        {"index": 2},
        ledger_path=path,
    )

    assert second["entry_count"] == 2
    assert path.read_bytes() == snapshot_bytes
    journal_path = Path(f"{path}.journal.jsonl")
    journal_records = [json.loads(line) for line in journal_path.read_text(encoding="utf-8").splitlines()]
    assert len(journal_records) == 2
    assert journal_records[-1]["entry_count"] == 2
    assert journal_records[-1]["schema"] == ledger.JOURNAL_SCHEMA
    assert ledger.verify_unified_ledger(path)["ok"] is True


def test_compaction_preserves_chain_and_clears_journal(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    for index in range(4):
        ledger.append_payload(
            "TEST_EVENT",
            "tests.incremental-ledger.compaction",
            {"index": index},
            ledger_path=path,
        )

    journal_path = Path(f"{path}.journal.jsonl")
    assert journal_path.exists()

    compacted = ledger.compact_unified_ledger(path)
    assert compacted["entry_count"] == 4
    assert compacted["journal_entry_count"] == 0
    assert journal_path.exists() is False

    verification = ledger.verify_unified_ledger(path)
    assert verification["ok"] is True
    assert verification["entry_count"] == 4
    assert verification["ledger_accumulator_version"] == ledger.ACCUMULATOR_VERSION


def test_verifier_rejects_tampered_journal_transition(tmp_path: Path):
    path = tmp_path / "unified-ledger.json"
    ledger.append_payload(
        "TEST_EVENT",
        "tests.incremental-ledger.tamper",
        {"index": 1},
        ledger_path=path,
    )

    journal_path = Path(f"{path}.journal.jsonl")
    record = json.loads(journal_path.read_text(encoding="utf-8"))
    record["ledger_hash72"] = "tampered"
    journal_path.write_text(json.dumps(record) + "\n", encoding="utf-8")

    verification = ledger.verify_unified_ledger(path)
    assert verification["ok"] is False
    assert any(item["reason"] == "journal ledger_hash72 mismatch" for item in verification["invalid"])
