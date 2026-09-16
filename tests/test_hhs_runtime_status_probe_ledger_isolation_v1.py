from pathlib import Path

from hhs_backend import runtime_status_probe
from hhs_runtime import hhs_unified_hash72_ledger_v1 as ledger


def test_status_probe_projection_cannot_append_production_unified_ledger(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HHS_RUNTIME_OUTPUT_DIR", str(tmp_path))
    path = tmp_path / "hhs_unified_hash72_ledger.json"
    ledger.append_payload(
        "BASELINE",
        "tests.status-probe-ledger-isolation",
        {"index": 1},
        ledger_path=path,
    )
    journal = Path(f"{path}.journal.jsonl")
    before = journal.read_bytes()
    original_append = ledger.append_payload

    try:
        isolation = runtime_status_probe.install_read_only_unified_ledger_projection()
        projected = ledger.append_payload(
            "PROBE_SYNTHETIC_READ",
            "tests.status-probe-ledger-isolation.probe",
            {"method": "GET"},
            ledger_path=path,
        )
    finally:
        ledger.append_payload = original_append

    assert isolation["mode"] == "READ_ONLY_UNIFIED_LEDGER"
    assert isolation["canonical_ledger_mutated"] is False
    assert projected["probe_read_only"] is True
    assert projected["canonical_ledger_mutated"] is False
    assert projected["entry_count"] == 1
    assert journal.read_bytes() == before
    assert ledger.verify_unified_ledger(path)["ok"] is True
